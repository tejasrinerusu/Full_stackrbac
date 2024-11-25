import logging
import sys
from uuid import UUID

from sqlalchemy.orm import Session

from db.session import SessionLocal
from models.rbac import Role, User, UserHasRole
from utils.security import get_password_hash


logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
    datefmt="%Y-%m-%d %H:%M:%S",
)


def seed_superuser(db: Session, email: str, password: str) -> UUID:
    logging.info("Seeding super user")
    db_obj = User(email=email, hashed_password=get_password_hash(password))
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    logging.info("Super user has been seeded")
    return db_obj.id


def seed_admin_role(db: Session) -> UUID:
    role: Role = db.query(Role).filter(Role.name == "admin").first()
    if not role:
        logging.info("Seeding admin role")
        db_obj = Role(name="admin")
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        logging.info("Admin role has been seeded")
        return db_obj.id
    return role.id


def map_user_role(db: Session, user_id: UUID, role_id: UUID) -> None:
    logging.info("Mapping super user with admin role")
    db_obj = UserHasRole(user_id=user_id, role_id=role_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    logging.info("Super user and admin role has been mapped")


def main(email: str, password: str) -> None:
    logging.info("Start seeding")
    db = SessionLocal()
    user_id = seed_superuser(db, email, password)
    role_id = seed_admin_role(db)
    map_user_role(db, user_id=user_id, role_id=role_id)
    logging.info("Finish seeding")


if __name__ == "__main__":
    email, password = sys.argv[1], sys.argv[2]
    main(email, password)
