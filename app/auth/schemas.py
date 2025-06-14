from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from app.auth.models import UserRole
from typing import Optional
from fastapi import HTTPException, status

class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str  = Field(..., min_length=6)
    role: Optional[UserRole] = UserRole.USER

    @field_validator("name")
    @classmethod
    def check_name_not_empty(cls, v):
        if not v.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": True, "message": "Name cannot be empty", "code": 400}
            )
        return v
    
    @model_validator(mode="before")
    @classmethod  
    def check_email_not_empty(cls, v):
        email = v.get("email", "")
        if not email.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": True, "message": "Email cannot be empty", "code": 400}
            )
        return v
    
class UserSignin(BaseModel):
    email: EmailStr
    password: str

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse