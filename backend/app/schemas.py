from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class WardrobeItemResponse(BaseModel):
    id: str
    user_id: str
    category: str
    name: Optional[str] = None
    image_url: str
    ai_label: str
    ai_confidence: float
    created_at: datetime
