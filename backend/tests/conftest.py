from typing import Generator

import pytest

from db.session import Base, test_engine, TestSessionLocal


@pytest.fixture()
def db() -> Generator:
    Base.metadata.create_all(bind=test_engine)
    yield TestSessionLocal()
    TestSessionLocal().close_all()
    Base.metadata.drop_all(bind=test_engine)


def override_get_db():
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()
