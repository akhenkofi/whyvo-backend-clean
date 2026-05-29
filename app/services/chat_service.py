import base64
import uuid
from pathlib import Path

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.direct_message import DirectMessage
from app.models.profile import Profile
from app.models.user import User

_MESSAGE_MEDIA_DIR = Path(__file__).resolve().parents[1] / 'static' / 'message-media'
_MESSAGE_MEDIA_DIR.mkdir(parents=True, exist_ok=True)


def _persist_message_media(value: str) -> str:
    raw = str(value or '').strip()
    if not raw.startswith('data:image/') or ',' not in raw:
        return raw
    header, encoded = raw.split(',', 1)
    ext = 'jpg'
    if ';' in header:
        mime = header.split(';', 1)[0]
        if '/' in mime:
            ext = mime.rsplit('/', 1)[-1].replace('jpeg', 'jpg') or 'jpg'
    filename = f'message-{uuid.uuid4().hex}.{ext}'
    target = _MESSAGE_MEDIA_DIR / filename
    target.write_bytes(base64.b64decode(encoded))
    return f'/static/message-media/{filename}'


def list_threads(db: Session, owner_user_id: int):
    messages = db.query(DirectMessage).filter(or_(DirectMessage.sender_user_id == owner_user_id, DirectMessage.recipient_user_id == owner_user_id)).order_by(DirectMessage.created_at.desc()).all()
    seen = set()
    threads = []
    for item in messages:
        other_user_id = item.recipient_user_id if item.sender_user_id == owner_user_id else item.sender_user_id
        if other_user_id in seen:
            continue
        seen.add(other_user_id)
        user = db.query(User).filter(User.id == other_user_id).first()
        profile = db.query(Profile).filter(Profile.user_id == other_user_id).first()
        if user:
            threads.append((user, profile, item))
    return threads


def list_messages(db: Session, owner_user_id: int, other_user_id: int):
    return db.query(DirectMessage).filter(
        or_(
            and_(DirectMessage.sender_user_id == owner_user_id, DirectMessage.recipient_user_id == other_user_id),
            and_(DirectMessage.sender_user_id == other_user_id, DirectMessage.recipient_user_id == owner_user_id),
        )
    ).order_by(DirectMessage.created_at.asc()).all()


def send_message(db: Session, sender_user_id: int, recipient_user_id: int, body: str, media_url: str | None = None, media_type: str | None = None):
    persisted_media_url = _persist_message_media(media_url) if media_url else None
    normalized_media_type = str(media_type or '').strip().upper() or None
    message = DirectMessage(
        sender_user_id=sender_user_id,
        recipient_user_id=recipient_user_id,
        body=str(body or ''),
        media_url=persisted_media_url,
        media_type=normalized_media_type,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
