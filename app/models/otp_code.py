from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.core.database import Base


class OTPCode(Base):
    __tablename__ = 'otp_codes'

    id = Column(Integer, primary_key=True)
    destination = Column(String(160), index=True, nullable=False)
    code = Column(String(6), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
