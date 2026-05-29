from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class MessageCreateRequest(BaseModel):
    body: str = Field(default='', max_length=4000)
    media_url: Optional[str] = None
    media_type: Optional[str] = None


class MessageResponse(BaseModel):
    id: int
    sender_user_id: int
    recipient_user_id: int
    body: str
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    created_at: datetime


class ThreadResponse(BaseModel):
    user_id: int
    display_name: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None


class MessagesResponse(BaseModel):
    messages: List[MessageResponse]
