from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PostCreateRequest(BaseModel):
    body: str = Field(min_length=1, max_length=5000)
    media_url: Optional[str] = None


class PostUpdateRequest(BaseModel):
    body: Optional[str] = Field(default=None, min_length=1, max_length=5000)
    media_url: Optional[str] = None


class CommentCreateRequest(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    id: int
    user_id: int
    display_name: str
    body: str
    created_at: datetime


class PostResponse(BaseModel):
    id: int
    user_id: int
    display_name: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    body: str
    media_url: Optional[str] = None
    like_count: int
    comment_count: int
    liked_by_me: bool
    created_at: datetime
    updated_at: datetime


class FeedResponse(BaseModel):
    posts: List[PostResponse]
