from typing import List, Union, Optional

from fastapi import HTTPException, status
from psycopg2 import errors
from psycopg2.errorcodes import UNIQUE_VIOLATION, FOREIGN_KEY_VIOLATION, NUMERIC_VALUE_OUT_OF_RANGE
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.orm import Session

from app.database import models
from app.database.enums import UserRole
from app.database.models import Base


def get_in_db(
        session: Session,
        model: Base,
        ident: int
):
    obj = session.query(model).get(ident)
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Запись с идентификатором {ident} нет в базе!"
        )
    return obj


def save_in_db(
        session: Session,
        obj: Base
):
    session.add(obj)
    check_unique(session)
    session.refresh(obj)


def update_in_db(
        session: Session,
        obj: Base
):
    check_unique(session)
    session.refresh(obj)


def delete_in_db(
        session: Session,
        obj: Base
):
    session.delete(obj)
    session.commit()


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
                status_code=status.HTTP_409_CONFLICT,
                detail="Целое число вне диапазона",
            )


def check_user(session: Session, user_id: int) -> models.User:
    user: models.User = get_in_db(
        session=session,
        model=models.User,
        ident=user_id
    )
    if user.company_id is None and user.worker_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь не состоит в компании!"
        )

    return user


def check_user_permission(
        session: Session,
        permissions: Union[List[UserRole], str],
        user_id: Optional[int] = None,
        user: Optional[models.User] = None
):
    if not user and user_id:
        user = check_user(session, user_id)

    if '__all__' in permissions:
        return user

    if user.role not in permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на это действие!"
        )

    return user


def check_user_company(
        session: Session,
        user_id: int
) -> models.User:
    user: models.User = get_in_db(
        session=session,
        model=models.User,
        ident=user_id
    )
    if user.company_id or user.worker_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь уже состоит в компании!"
        )
    return user


def check_delete_status(
        admin_user_id: int,
        company: models.Company,
        old_user: models.User
):
    if old_user in company.users:
        if old_user.id == admin_user_id or \
                old_user.role == UserRole.DIRECTOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы не сможете удалить самого себя"
                       "или директора из компании!"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь не ноходится в компании!"
        )
