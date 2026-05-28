from datetime import datetime

from pydantic import BaseModel, Field


class DeviceTokenCreateRequest(BaseModel):
    platform: str = Field(default='web', max_length=20)
    token: str = Field(min_length=1, max_length=500)


class DeviceTokenResponse(BaseModel):
    id: int
    platform: str
    token: str
    created_at: datetime
