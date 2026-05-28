from sqlalchemy.orm import Session

from app.models.device_token import DeviceToken


def upsert_device_token(db: Session, user_id: int, platform: str, token: str):
    existing = db.query(DeviceToken).filter(DeviceToken.token == token).first()
    if existing:
        existing.user_id = user_id
        existing.platform = platform
        db.commit()
        db.refresh(existing)
        return existing
    item = DeviceToken(user_id=user_id, platform=platform, token=token)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_device_tokens(db: Session, user_id: int):
    return db.query(DeviceToken).filter(DeviceToken.user_id == user_id).order_by(DeviceToken.created_at.desc()).all()
