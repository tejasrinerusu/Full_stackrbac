import os

from dotenv import load_dotenv

load_dotenv()
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}",
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine)

test_engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_TEST_PORT')}/{os.getenv('POSTGRES_TEST_DB')}",
    pool_pre_ping=True,
)
TestSessionLocal = sessionmaker(bind=test_engine)
