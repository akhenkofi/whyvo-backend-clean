import random
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.otp_code import OTPCode
from app.models.profile import Profile
from app.models.user import User


def _generate_code() -> str:
    return f'{random.randint(0, 999999):06d}'


from typing import Optional


def register_user(db: Session, *, full_name: str, username: Optional[str], phone: Optional[str], email: Optional[str], password: str):
    existing = db.query(User).filter(
        or_(
            User.email == email if email else False,
            User.phone == phone if phone else False,
            User.username == username if username else False,
        )
    ).first()
    if existing:
        raise ValueError('A user with that email, phone, or username already exists')

    user = User(
        full_name=full_name,
        username=username,
        phone=phone,
        email=email,
        password_hash=hash_password(password),
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    db.flush()

    profile = Profile(
        user_id=user.id,
        display_name=full_name,
        username=username,
        bio='',
        avatar_url=None,
        status_text='Available',
    )
    db.add(profile)

    destination = email or phone
    otp = OTPCode(destination=destination, code=_generate_code(), is_used=False)
    db.add(otp)
    db.commit()
    db.refresh(user)
    return user, otp


def login_user(db: Session, identifier: str, password: str):
    user = db.query(User).filter(or_(User.email == identifier, User.phone == identifier, User.username == identifier)).first()
    if not user or not verify_password(password, user.password_hash):
        raise ValueError('Invalid credentials')
    token = create_access_token(str(user.id))
    return user, token


def verify_otp(db: Session, destination: str, code: str, bypass_code: str):
    otp = db.query(OTPCode).filter(OTPCode.destination == destination, OTPCode.is_used == False).order_by(OTPCode.created_at.desc()).first()
    if code != bypass_code and (not otp or otp.code != code):
        raise ValueError('Invalid verification code')
    if otp:
        otp.is_used = True
    user = db.query(User).filter(or_(User.email == destination, User.phone == destination)).first()
    if not user:
        raise ValueError('User not found for verification destination')
    user.is_verified = True
    db.commit()
    db.refresh(user)
    token = create_access_token(str(user.id))
    return user, token
