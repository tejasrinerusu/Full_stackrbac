import logging
import sys
from uuid import UUID

from sqlalchemy.orm import Session

from db.session import SessionLocal
from models.rbac import User
from utils.security import get_password_hash


logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
    datefmt="%Y-%m-%d %H:%M:%S",
)


def seed_user(db: Session, email: str, password: str) -> UUID:
    logging.info("Seeding normal user")
    db_obj = User(email=email, hashed_password=get_password_hash(password))
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    logging.info("Normal user has been seeded")


def main(email: str, password: str) -> None:
    logging.info("Start seeding")
    db = SessionLocal()
    seed_user(db, email, password)
    logging.info("Finish seeding")


if __name__ == "__main__":
    email, password = sys.argv[1], sys.argv[2]
    main(email, password)
