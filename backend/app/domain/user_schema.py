from pydantic import BaseModel, Field
from typing import Optional


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=8)
    roles: list[str] = ["fraud_analyst"]


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    roles: list[str]
    is_active: bool = True
    created_at: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[str] = None
    is_active: Optional[bool] = None
    roles: Optional[list[str]] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
