from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    username: Optional[str] = Field(default=None, min_length=3, max_length=80)
    bio: Optional[str] = Field(default=None, max_length=500)
    avatar_url: Optional[str] = None
    status_text: Optional[str] = Field(default=None, max_length=160)


class ProfileResponse(BaseModel):
    user_id: int
    display_name: str
    username: Optional[str] = None
    bio: str
    avatar_url: Optional[str] = None
    status_text: str
    updated_at: datetime
