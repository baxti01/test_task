from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.settings import settings

DATABASE_URL = f'postgresql://' \
               f'{settings.postgres_user}:{settings.postgres_password}@' \
               f'{settings.postgres_host}/{settings.postgres_db}'

engine = create_engine(
    DATABASE_URL
)

Session = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()
