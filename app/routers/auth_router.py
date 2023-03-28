from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm


from app.serializers.user_serializer import UpdateUser, Token, User, CreateUser
from app.services.auth_service import AuthService, get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Авторизация"]
)


@router.post("/sign-up", response_model=Token)
async def sign_up(
        user: CreateUser,
        service: AuthService = Depends()
):
    return service.sign_up(user)


@router.post("/sign-in", response_model=Token)
async def sign_in(
        form_data: OAuth2PasswordRequestForm = Depends(),
        service: AuthService = Depends()
):
    return service.sign_in(form_data.username, form_data.password)


# It's not correct work need fix
@router.get("/get_user", response_model=User)
def get_user(
        user_id: int = Depends(get_current_user),
        service: AuthService = Depends()
):
    return service.get_user(user_id)


@router.put("/update_user", response_model=Token)
async def update_user(
        user_data: UpdateUser,
        user_id: int = Depends(get_current_user),
        service: AuthService = Depends()
):
    return service.update_user(user_id, user_data)


@router.delete("/delete_user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: int = Depends(get_current_user),
        service: AuthService = Depends()
):
    service.delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
