from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.user import UserCreate, UserResponse, UserLogin
from app.core.dependencies import get_user_repository
from app.core.security import get_password_hash, authenticate_user, create_jwt_token
from app.db.repositories.user_repository import UserRepository

router = APIRouter()


@router.post(
    "/auth/register/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse
)
async def register(
        user: UserCreate,
        user_repo: UserRepository = Depends(get_user_repository)
):
    db_user = await user_repo.get_user_by_username(username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    hashed_password = get_password_hash(user.password)
    user.password = hashed_password

    db_user = await user_repo.create_user(user)

    return db_user


@router.post("/auth/login/")
async def login(
        user: UserLogin,
        user_repo: UserRepository = Depends(get_user_repository)
):
    authenticated_user = await authenticate_user(user_repo, user.username, user.password)

    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {"sub": authenticated_user.username}
    access_token = create_jwt_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
