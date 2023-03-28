from fastapi import HTTPException, status
from psycopg2 import errors
from psycopg2.errorcodes import UNIQUE_VIOLATION, FOREIGN_KEY_VIOLATION, NUMERIC_VALUE_OUT_OF_RANGE
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.orm import Session

from app.database.models import Base


def check_unique(session: Session) -> None:
    try:
        session.commit()
    except (DataError, IntegrityError) as err:
        if isinstance(err.orig, errors.lookup(UNIQUE_VIOLATION)):
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Такое имя уже занято"
            )
        if isinstance(err.orig, errors.lookup(FOREIGN_KEY_VIOLATION)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь с таким именем удалён из базы данных",
                headers={'WWW-Authenticate': 'Bearer'},
            )
        if isinstance(err.orig, errors.lookup(NUMERIC_VALUE_OUT_OF_RANGE)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Целое число вне диапазона",
                headers={'WWW-Authenticate': 'Bearer'},
            )


def is_none_check(obj: Base):
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такой записи нет в базе данных"
        )
