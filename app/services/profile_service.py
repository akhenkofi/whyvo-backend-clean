from sqlalchemy.orm import Session

from app.models.profile import Profile


from typing import Optional


def get_or_create_profile(db: Session, user_id: int, fallback_name: str, fallback_username: Optional[str]):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if profile:
        return profile
    profile = Profile(user_id=user_id, display_name=fallback_name, username=fallback_username, bio='', avatar_url=None, status_text='Available')
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_profile(profile: Profile, payload: dict):
    for key, value in payload.items():
        if value is not None and hasattr(profile, key):
            setattr(profile, key, value)
    return profile
