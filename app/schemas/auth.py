from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    username: Optional[str] = Field(default=None, min_length=3, max_length=80)
    phone: Optional[str] = Field(default=None, max_length=30)
    email: Optional[EmailStr] = None
    password: str = Field(min_length=6, max_length=120)


class LoginRequest(BaseModel):
    identifier: str
    password: str


class VerifyOtpRequest(BaseModel):
    destination: str
    code: str = Field(min_length=4, max_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class UserResponse(BaseModel):
    id: int
    full_name: str
    username: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user: UserResponse
