from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.models.profile import Profile
from app.models.user import User


def sync_contacts(db: Session, owner_user_id: int, entries: list[dict]):
    matched = []
    for entry in entries:
        phone = entry.get('phone')
        email = entry.get('email')
        label = entry.get('label')
        if not phone and not email:
            continue
        user = db.query(User).filter(or_(User.phone == phone if phone else False, User.email == email if email else False)).first()
        if not user or user.id == owner_user_id:
            continue
        contact = db.query(Contact).filter(Contact.owner_user_id == owner_user_id, Contact.contact_user_id == user.id).first()
        if not contact:
            contact = Contact(owner_user_id=owner_user_id, contact_user_id=user.id, label=label)
            db.add(contact)
        elif label:
            contact.label = label
        profile = db.query(Profile).filter(Profile.user_id == user.id).first()
        matched.append((contact, user, profile))
    db.commit()
    return matched


def list_contacts(db: Session, owner_user_id: int):
    rows = db.query(Contact, User, Profile).join(User, User.id == Contact.contact_user_id).outerjoin(Profile, Profile.user_id == User.id).filter(Contact.owner_user_id == owner_user_id).order_by(Contact.created_at.desc()).all()
    return rows
