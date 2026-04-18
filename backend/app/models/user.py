# app/models/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Literal
from datetime import datetime
from bson import ObjectId


class UserModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    clerk_user_id: str
    email: str
    name: str
    age: Optional[int] = Field(default=None, ge=0, le=120)
    gender: Optional[str] = None
    conditions: List[str] = []
    allergies: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    plan: Literal["free", "pro"] = "free"

    model_config = {
        "populate_by_name": True,
        "str_strip_whitespace": True,
        "arbitrary_types_allowed": True,
    }