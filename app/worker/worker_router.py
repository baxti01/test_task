from typing import Optional

from fastapi import APIRouter, Depends, status, Response

from app.auth.service import get_current_user
from app.worker.serializer import Worker, CreateWorker, UpdateWorker
from app.worker.service import WorkerService

router = APIRouter(
    prefix='/worker',
    tags=['Филиалы']
)


@router.get('/', response_model=Worker)
def get_worker(
        worker_id: Optional[int] = None,
        user_id: int = Depends(get_current_user),
        service: WorkerService = Depends()
):
    return service.get_worker(user_id, worker_id)


@router.post('/{worker_user_id}', response_model=Worker)
def create_worker(
        worker_user_id: int,
        data: CreateWorker,
        user_id: int = Depends(get_current_user),
        service: WorkerService = Depends()
):
    return service.create_worker(
        main_user_id=user_id,
        worker_user_id=worker_user_id,
        data=data
    )


@router.put('/', response_model=Worker)
def update_worker(
        data: UpdateWorker,
        worker_id: Optional[int] = None,
        user_id: int = Depends(get_current_user),
        service: WorkerService = Depends()
):
    return service.update_worker(
        user_id=user_id,
        worker_id=worker_id,
        data=data
    )


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
def delete_worker(
        worker_id: Optional[int] = None,
        user_id: int = Depends(get_current_user),
        service: WorkerService = Depends()
):
    service.delete_worker(user_id, worker_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post('/add_user/{new_user_id}', status_code=status.HTTP_200_OK)
def add_user(
        new_user_id: int,
        user_id: int = Depends(get_current_user),
        service: WorkerService = Depends()
):
    service.add_user(new_user_id, user_id)
    return {"message": "Пользователь успешно добавлен!"}


@router.delete(
    '/delete_user/{old_user_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_user(
        old_user_id: int,
        user_id: int = Depends(get_current_user),
        service: WorkerService = Depends()
):
    service.delete_user(old_user_id, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
