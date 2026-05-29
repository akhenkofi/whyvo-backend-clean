from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.profile import Profile
from app.models.user import User
from app.services.chat_service import list_messages, list_threads, send_message
from app.services.profile_service import get_or_create_profile, update_profile

router = APIRouter(prefix='/api/v1/community', tags=['community'])


def _username_for(user: User, profile: Profile | None) -> str:
    if profile and profile.username:
        return profile.username
    if user.username:
        return user.username
    base = ''.join(ch for ch in str(user.full_name or 'whyvouser').lower() if ch.isalnum())[:14] or 'whyvouser'
    return f'{base}{user.id}'


def _community_user_card(user: User, profile: Profile | None):
    return {
        'user_id': user.id,
        'full_name': user.full_name,
        'username': _username_for(user, profile),
        'avatar_url': profile.avatar_url if profile else None,
        'bio': profile.bio if profile and profile.bio else '',
        'status_text': profile.status_text if profile and profile.status_text else 'Available',
        'country': None,
        'is_following': False,
        'is_followed_by': False,
        'is_muted': False,
    }


@router.get('/profile/me')
def community_profile_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = get_or_create_profile(db, current_user.id, current_user.full_name, current_user.username)
    username = _username_for(current_user, profile)
    if profile.username != username:
        profile.username = username
        db.commit()
        db.refresh(profile)
    return {
        'full_name': current_user.full_name,
        'username': username,
        'avatar_url': profile.avatar_url,
        'cover_image_url': None,
        'bio': profile.bio or '',
        'farm_life': '',
        'interests': '',
        'visibility': 'public',
        'message_privacy': 'everyone',
        'followers_count': 0,
        'following_count': 0,
    }


@router.post('/profile/me')
def community_profile_upsert(payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = get_or_create_profile(db, current_user.id, current_user.full_name, current_user.username)
    next_full_name = str(payload.get('full_name') or '').strip()
    next_username = str(payload.get('username') or '').strip() or None
    next_bio = payload.get('bio')
    next_avatar_url = payload.get('avatar_url')
    if next_full_name:
        current_user.full_name = next_full_name[:120]
        profile.display_name = current_user.full_name
    update_profile(profile, {
        'username': next_username,
        'bio': next_bio,
        'avatar_url': next_avatar_url,
        'status_text': payload.get('status_text'),
    })
    if next_username is not None:
        current_user.username = next_username
    db.commit()
    db.refresh(profile)
    return {
        'full_name': current_user.full_name,
        'username': _username_for(current_user, profile),
        'avatar_url': profile.avatar_url,
        'cover_image_url': None,
        'bio': profile.bio or '',
        'farm_life': '',
        'interests': '',
        'visibility': 'public',
        'message_privacy': 'everyone',
        'followers_count': 0,
        'following_count': 0,
    }


@router.get('/messages')
def community_message_threads(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = list_threads(db, current_user.id)
    items = []
    for user, profile, message in rows:
        items.append({
            'user': _community_user_card(user, profile),
            'last_message': {
                'id': message.id,
                'text': message.body,
                'sender_user_id': message.sender_user_id,
                'recipient_user_id': message.recipient_user_id,
                'created_at': message.created_at,
                'is_mine': int(message.sender_user_id) == int(current_user.id),
            }
        })
    return items


@router.get('/messages/{other_user_id}')
def community_message_thread(other_user_id: int, limit: int = 80, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    other = db.query(User).filter(User.id == other_user_id).first()
    if not other:
        raise HTTPException(status_code=404, detail='User not found')
    profile = db.query(Profile).filter(Profile.user_id == other_user_id).first()
    rows = list_messages(db, current_user.id, other_user_id)[: max(1, min(limit, 200))]
    return {
        'user': _community_user_card(other, profile),
        'messages': [{
            'id': row.id,
            'text': row.body,
            'media_url': row.media_url,
            'media_type': row.media_type,
            'sender_user_id': row.sender_user_id,
            'recipient_user_id': row.recipient_user_id,
            'created_at': row.created_at,
            'is_mine': int(row.sender_user_id) == int(current_user.id),
        } for row in rows]
    }


@router.post('/messages/{other_user_id}')
def community_send_message(other_user_id: int, payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    text = str(payload.get('text') or payload.get('body') or '').strip()
    media_url = str(payload.get('media_url') or '').strip() or None
    media_type = str(payload.get('media_type') or '').strip() or None
    if not text and not media_url:
        raise HTTPException(status_code=400, detail='Message text or media is required')
    if other_user_id == current_user.id:
        raise HTTPException(status_code=400, detail='Cannot message yourself')
    row = send_message(db, current_user.id, other_user_id, text, media_url=media_url, media_type=media_type)
    return {
        'id': row.id,
        'text': row.body,
        'media_url': row.media_url,
        'media_type': row.media_type,
        'sender_user_id': row.sender_user_id,
        'recipient_user_id': row.recipient_user_id,
        'created_at': row.created_at,
        'is_mine': True,
    }
