"""
User and Authentication Schemas for PocketSmart AI.
Matches PDF pages 10, 11, 19.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class RegisterUser(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserInDB(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    hashed_password: str
    disabled: bool = False


class UserResponse(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
