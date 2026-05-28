from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import ProfileResponse
from app.schemas.user import UserSearchItem

router = APIRouter(prefix='/api/v1/users', tags=['users'])


@router.get('/search', response_model=list[UserSearchItem])
def search_users(q: str = '', db: Session = Depends(get_db), _current_user: User = Depends(get_current_user)):
    rows = db.query(User, Profile).outerjoin(Profile, Profile.user_id == User.id).filter(User.is_active == True).order_by(User.full_name.asc()).all()
    query = (q or '').strip().lower()
    result = []
    for user, profile in rows:
        hay = ' '.join(filter(None, [user.full_name, user.username, user.email, user.phone, getattr(profile, 'display_name', None), getattr(profile, 'username', None)])).lower()
        if query and query not in hay:
            continue
        result.append(UserSearchItem(id=user.id, full_name=profile.display_name if profile else user.full_name, username=(profile.username if profile else user.username), avatar_url=(profile.avatar_url if profile else None), status_text=(profile.status_text if profile else None)))
    return result


@router.get('/{user_id}/profile', response_model=ProfileResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db), _current_user: User = Depends(get_current_user)):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail='Profile not found')
    return ProfileResponse(
        user_id=profile.user_id,
        display_name=profile.display_name,
        username=profile.username,
        bio=profile.bio or '',
        avatar_url=profile.avatar_url,
        status_text=profile.status_text or 'Available',
        updated_at=profile.updated_at,
    )
