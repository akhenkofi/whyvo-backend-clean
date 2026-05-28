from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.core.database import Base


class Profile(Base):
    __tablename__ = 'profiles'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, index=True, nullable=False)
    display_name = Column(String(120), nullable=False)
    username = Column(String(80), unique=True, nullable=True, index=True)
    bio = Column(Text, default='')
    avatar_url = Column(Text, nullable=True)
    status_text = Column(String(160), default='Available')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
