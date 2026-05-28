from typing import List, Optional

from pydantic import BaseModel, Field


class ContactSyncEntry(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    label: Optional[str] = Field(default=None, max_length=120)


class ContactSyncRequest(BaseModel):
    contacts: List[ContactSyncEntry]


class ContactResponse(BaseModel):
    user_id: int
    display_name: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    status_text: Optional[str] = None
    label: Optional[str] = None


class ContactSyncResponse(BaseModel):
    matched: List[ContactResponse]
