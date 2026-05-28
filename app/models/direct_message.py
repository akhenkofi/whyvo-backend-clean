from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text

from app.core.database import Base


class DirectMessage(Base):
    __tablename__ = 'direct_messages'

    id = Column(Integer, primary_key=True)
    sender_user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    recipient_user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
