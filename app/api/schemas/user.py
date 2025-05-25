from pydantic import BaseModel, Field, ConfigDict


class UserCreate(BaseModel):
    """Schema for user registration input"""
    username: str = Field(..., min_length=3, max_length=50, description="Username for the user")
    password: str = Field(..., min_length=8, description="Password for the user")


class UserLogin(BaseModel):
    """Schema for user login input"""
    username: str = Field(..., min_length=3, max_length=50, description="Username for the user")
    password: str = Field(..., min_length=8, description="Password for the user")


class UserResponse(BaseModel):
    """Schema for user response output (omit password hash)"""
    id: int
    username: str

    # Allows creating Pydantic model from SQLAlchemy instance
    model_config = ConfigDict(from_attributes=True)
