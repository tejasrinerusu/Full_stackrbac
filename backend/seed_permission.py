import logging
import sys
from uuid import UUID

from sqlalchemy.orm import Session

from db.session import SessionLocal
from models.rbac import Permission, Role, RoleHasPermission


logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
    datefmt="%Y-%m-%d %H:%M:%S",
)


def seed_permissions(db: Session, permissions: list[str]) -> list[UUID]:
    logging.info("Seeding permissions")
    db_objs = [Permission(name=permission) for permission in permissions]
    db.add_all(db_objs)
    db.commit()
    for db_obj in db_objs:
        db.refresh(db_obj)
    logging.info("Permissions has been seeded")
    return [obj.id for obj in db_objs]


def map_role_permission(db: Session, permission_ids: list[UUID]) -> None:
    logging.info("Mapping admin role with permissions")
    role: Role = db.query(Role).filter(Role.name == "admin").first()
    db_objs = [
        RoleHasPermission(role_id=role.id, permission_id=permission_id)
        for permission_id in permission_ids
    ]
    db.add_all(db_objs)
    db.commit()
    logging.info("Admin role and permissions has been mapped")


def main(permissions: list[str]) -> None:
    logging.info("Start seeding")
    db = SessionLocal()
    permission_ids = seed_permissions(db, permissions=permissions)
    map_role_permission(db, permission_ids=permission_ids)
    logging.info("Finish seeding")


if __name__ == "__main__":
    permissions = sys.argv[1:]
    main(permissions)
