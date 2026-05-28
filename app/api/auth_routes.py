from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, MessageResponse, RegisterRequest, RequestOtpRequest, TokenResponse, UserResponse, VerifyOtpRequest
from app.services.auth_service import login_user, register_user, request_otp, verify_otp

router = APIRouter(prefix='/api/v1/auth', tags=['auth'])


@router.post('/register', response_model=AuthResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user, _otp = register_user(db, full_name=payload.full_name, username=payload.username, phone=payload.phone, email=payload.email, password=payload.password)
        user, token = login_user(db, payload.email or payload.phone or payload.username or '', payload.password)
        return AuthResponse(access_token=token, user=user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post('/login', response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        user, token = login_user(db, payload.identifier, payload.password)
        return AuthResponse(access_token=token, user=user)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))


@router.post('/request-otp', response_model=MessageResponse)
def request_otp_route(payload: RequestOtpRequest, db: Session = Depends(get_db)):
    try:
        request_otp(db, payload.destination)
        return MessageResponse(message='OTP requested')
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post('/verify-otp', response_model=AuthResponse)
def verify(payload: VerifyOtpRequest, db: Session = Depends(get_db)):
    try:
        user, token = verify_otp(db, payload.destination, payload.code, settings.OTP_BYPASS_CODE)
        return AuthResponse(access_token=token, user=user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get('/me', response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put('/me', response_model=UserResponse)
def update_me(payload: RegisterRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.full_name = payload.full_name
    current_user.username = payload.username
    current_user.phone = payload.phone
    current_user.email = payload.email
    db.commit()
    db.refresh(current_user)
    return current_user
