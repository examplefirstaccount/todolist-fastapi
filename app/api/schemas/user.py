from pydantic import BaseModel, Field, ConfigDict


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    """Schema for user registration input"""
    password: str = Field(..., min_length=8)


class UserLogin(UserBase):
    """Schema for user login input"""
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    """Schema for user response output (omit password hash)"""
    id: int

    model_config = ConfigDict(from_attributes=True)
