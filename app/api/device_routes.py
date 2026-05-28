from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.device import DeviceTokenCreateRequest, DeviceTokenResponse
from app.services.device_service import list_device_tokens, upsert_device_token

router = APIRouter(prefix='/api/v1/device-token', tags=['device-token'])


@router.post('', response_model=DeviceTokenResponse)
def create_device_token(payload: DeviceTokenCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = upsert_device_token(db, current_user.id, payload.platform, payload.token)
    return DeviceTokenResponse(id=item.id, platform=item.platform, token=item.token, created_at=item.created_at)


@router.get('', response_model=list[DeviceTokenResponse])
def get_device_tokens(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = list_device_tokens(db, current_user.id)
    return [DeviceTokenResponse(id=item.id, platform=item.platform, token=item.token, created_at=item.created_at) for item in items]
