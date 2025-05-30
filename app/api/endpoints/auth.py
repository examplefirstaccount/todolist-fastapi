from fastapi import APIRouter, Depends, status

from app.api.schemas.user import UserCreate, UserResponse, UserLogin
from app.api.dependencies.dependencies import get_auth_service, AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse
)
async def register(
        user: UserCreate,
        auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.register(user)


@router.post("/login")
async def login(
        user: UserLogin,
        auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.login(user)
