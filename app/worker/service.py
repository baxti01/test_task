from typing import List, Union

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import utils
from app.database import models
from app.database.database import get_session
from app.database.enums import UserRole
from app.worker.serializer import CreateWorker, UpdateWorker


class WorkerService:

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_worker(
            self,
            user_id: int,
            worker_id: int = None
    ) -> models.Worker:
        user = self._get_user(
            user_id=user_id,
            permissions=[
                UserRole.WORKER_DIRECTOR, UserRole.WORKER_ADMIN,
                UserRole.ADMIN, UserRole.DIRECTOR
            ]
        )

        return self._get_worker(user, worker_id)

    def create_worker(
            self,
            main_user_id: int,
            worker_user_id: int,
            data: CreateWorker
    ) -> models.Worker:
        main_user = self._get_user(
            user_id=main_user_id,
            permissions=[UserRole.DIRECTOR]
        )

        worker_user = utils.check_user_company(
            session=self.session,
            user_id=worker_user_id
        )

        worker = models.Worker(
            **data.dict(exclude={'worker_user_id'}),
            company_id=main_user.company_id
        )
        utils.save_in_db(self.session, worker)

        worker_user.worker_id = worker.id
        worker_user.role = UserRole.WORKER_DIRECTOR
        utils.update_in_db(self.session, worker_user)

        return worker

    def update_worker(
            self,
            user_id: int,
            worker_id: int,
            data: UpdateWorker
    ) -> models.Worker:
        user = self._get_user(
            user_id=user_id,
            permissions=[
                UserRole.DIRECTOR, UserRole.WORKER_DIRECTOR,
            ]
        )

        worker = self._get_worker(user, worker_id)

        for field, value in data:
            setattr(worker, field, value)

        utils.update_in_db(self.session, worker)

        return worker

    def delete_worker(
            self,
            user_id: int,
            worker_id: int
    ):
        user = self._get_user(user_id, [UserRole.DIRECTOR])
        worker = self._get_worker(user, worker_id)
        for user in worker.users:
            user.role = UserRole.CUSTOMER

        utils.delete_in_db(self.session, worker)

    def add_user(
            self,
            new_user_id: int,
            user_id: int,
    ):
        user = self._get_user(
            user_id=user_id,
            permissions=[UserRole.WORKER_DIRECTOR, UserRole.WORKER_ADMIN]
        )

        new_user = utils.check_user_company(self.session, new_user_id)

        new_user.worker_id = user.worker_id
        new_user.role = UserRole.WORKER_ADMIN
        utils.update_in_db(self.session, new_user)

    def delete_user(
            self,
            old_user_id: int,
            user_id: int,
    ):
        user = self._get_user(
            user_id=user_id,
            permissions=[UserRole.WORKER_DIRECTOR, UserRole.WORKER_ADMIN]
        )
        print("sdsd")
        old_user = self._get_user(old_user_id, '__all__')

        utils.check_delete_status(
            admin_user_id=user_id,
            company=user.worker,
            old_user=old_user
        )

        old_user.worker_id = None
        old_user.role = UserRole.CUSTOMER
        utils.update_in_db(self.session, old_user)

    def _get_user(
            self,
            user_id: int,
            permissions: Union[List[UserRole], str]
    ) -> models.User:
        user = utils.check_user_permission(
            session=self.session,
            user_id=user_id,
            permissions=permissions
        )
        return user

    def _get_worker(
            self,
            user: models.User,
            worker_id: int
    ) -> models.Worker:
        if user.role == UserRole.WORKER_DIRECTOR:
            worker = user.worker
        elif worker_id:
            worker: models.Worker = utils.get_in_db(
                session=self.session,
                model=models.Worker,
                ident=worker_id
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="У вас нет доступа на это действие либо "
                       "вы не указали идентификатор филиала в запросе."
            )
        return worker
