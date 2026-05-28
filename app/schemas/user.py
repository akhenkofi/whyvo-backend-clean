from typing import Optional

from pydantic import BaseModel


class UserSearchItem(BaseModel):
    id: int
    full_name: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    status_text: Optional[str] = None
