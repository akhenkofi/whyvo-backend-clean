from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.direct_message import DirectMessage
from app.models.profile import Profile
from app.models.user import User


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


def send_message(db: Session, sender_user_id: int, recipient_user_id: int, body: str):
    message = DirectMessage(sender_user_id=sender_user_id, recipient_user_id=recipient_user_id, body=body)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
