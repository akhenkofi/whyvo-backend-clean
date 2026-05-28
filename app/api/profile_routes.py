from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import ProfileResponse, ProfileUpdateRequest
from app.services.profile_service import get_or_create_profile, update_profile

router = APIRouter(prefix='/api/v1/profile', tags=['profile'])


def _serialize(profile: Profile) -> ProfileResponse:
    return ProfileResponse(user_id=profile.user_id, display_name=profile.display_name, username=profile.username, bio=profile.bio or '', avatar_url=profile.avatar_url, status_text=profile.status_text or 'Available', updated_at=profile.updated_at)


@router.get('/me', response_model=ProfileResponse)
def get_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = get_or_create_profile(db, current_user.id, current_user.full_name, current_user.username)
    return _serialize(profile)


@router.put('/me', response_model=ProfileResponse)
def put_my_profile(payload: ProfileUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = get_or_create_profile(db, current_user.id, current_user.full_name, current_user.username)
    update_profile(profile, payload.model_dump())
    if payload.username is not None:
        current_user.username = payload.username
    db.commit()
    db.refresh(profile)
    return _serialize(profile)


@router.get('/user/{user_id}', response_model=ProfileResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db), _current_user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail='Profile not found')
    return _serialize(profile)
