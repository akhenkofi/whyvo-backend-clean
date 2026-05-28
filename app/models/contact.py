from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from app.core.database import Base


class Contact(Base):
    __tablename__ = 'contacts'
    __table_args__ = (UniqueConstraint('owner_user_id', 'contact_user_id', name='uq_contacts_owner_contact'),)

    id = Column(Integer, primary_key=True)
    owner_user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    contact_user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    label = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
