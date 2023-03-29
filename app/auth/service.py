from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.hash import bcrypt
from sqlalchemy.orm import Session

from app.database.database import get_session
from app.database import models
from app.database.enums import UserRole
from app.auth.serializer import UpdateUser, CreateUser, Token, User
from app import utils
from app.settings import settings

auth = OAuth2PasswordBearer(tokenUrl="/auth/sign-in")


def get_current_user(token: str = Depends(auth)):
    return AuthService.verify_token(token)


class AuthService:

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def sign_up(self, user_data: CreateUser) -> Token:
        password_hash = self.hash_password(user_data.password)
        user = models.User(
            username=user_data.username,
            email=user_data.email,
            role=user_data.role.value,
            password=password_hash
        )
        utils.save_in_db(self.session, user)
        return self.create_token(user)

    def sign_in(self, username: str, password: str) -> Token:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

        user = (
            self.session
            .query(models.User)
            .filter_by(username=username)
            .first()
        )

        if not user:
            raise exception
        if not self.verify_password(password, user.password):
            raise exception

        return self.create_token(user)

    def get_user(self, user_id: int) -> models.User:
        user = self.session.query(models.User).get(user_id)
        a = UserRole.CUSTOMER
        print('asdasdasd', user.role == a, user.role.value, a.value)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Пользователя с идентификатором {user_id} нет в базе!"
            )
        return user

    def update_user(
            self,
            user_id: int,
            user_data: UpdateUser
    ) -> Token:
        user = self.get_user(user_id)
        for field, value in user_data:
            setattr(user, field, value)

        user.password = self.hash_password(user_data.password)
        utils.check_unique(self.session)
        self.session.refresh(user)
        return self.create_token(user)

    def delete_user(self, user_id: int) -> None:
        user = self.get_user(user_id)
        if user.role == UserRole.ADMIN:
            company = self.session.query(models.Company).get(user.company_id)
            self.session.delete(company)
            self.session.commit()
        self.session.delete(user)
        self.session.commit()

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password) -> bool:
        return bcrypt.verify(plain_password, hashed_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt.hash(password)

    @classmethod
    def verify_token(cls, token: str) -> int:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

        try:
            payload = jwt.decode(
                token=token,
                key=settings.jwt_secret,
                algorithms=settings.jwt_algorithm
            )
        except JWTError:
            raise exception

        user_id = payload.get("sub", None)

        return int(user_id)

    @classmethod
    def create_token(cls, user: models.User) -> Token:
        user_data = User.from_orm(user)

        date = datetime.utcnow()
        payload = {
            "iat": date,
            "nbf": date,
            "exp": date + timedelta(minutes=settings.jwt_expire_minutes),
            "sub": str(user_data.id)
        }

        token = jwt.encode(
            payload,
            key=settings.jwt_secret,
            algorithm=settings.jwt_algorithm,

        )

        return Token(access_token=token)
