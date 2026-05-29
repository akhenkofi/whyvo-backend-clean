import base64
import os
import uuid
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.models.profile import Profile

_MEDIA_DIR = Path(__file__).resolve().parents[1] / 'static' / 'profile-media'
_MEDIA_DIR.mkdir(parents=True, exist_ok=True)


def _persist_avatar_data_url(user_id: int, value: str) -> str:
    raw = str(value or '').strip()
    if not raw.startswith('data:image/') or ',' not in raw:
        return raw
    header, encoded = raw.split(',', 1)
    ext = 'jpg'
    if ';' in header:
        mime = header.split(';', 1)[0]
        if '/' in mime:
            ext = mime.rsplit('/', 1)[-1].replace('jpeg', 'jpg') or 'jpg'
    filename = f'user-{int(user_id)}-{uuid.uuid4().hex}.{ext}'
    target = _MEDIA_DIR / filename
    binary = base64.b64decode(encoded)
    target.write_bytes(binary)
    return f'/static/profile-media/{filename}'


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
        if value is None or not hasattr(profile, key):
            continue
        if key == 'avatar_url':
            value = _persist_avatar_data_url(profile.user_id, value)
        setattr(profile, key, value)
    return profile
