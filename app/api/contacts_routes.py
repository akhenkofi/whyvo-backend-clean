from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.contact import ContactResponse, ContactSyncRequest, ContactSyncResponse
from app.services.contacts_service import list_contacts, sync_contacts

router = APIRouter(prefix='/api/v1/contacts', tags=['contacts'])


@router.post('/sync', response_model=ContactSyncResponse)
def sync(payload: ContactSyncRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    matched = sync_contacts(db, current_user.id, [item.model_dump() for item in payload.contacts])
    items = [ContactResponse(user_id=user.id, display_name=(profile.display_name if profile else user.full_name), username=(profile.username if profile else user.username), avatar_url=(profile.avatar_url if profile else None), status_text=(profile.status_text if profile else None), label=contact.label) for contact, user, profile in matched]
    return ContactSyncResponse(matched=items)


@router.get('', response_model=list[ContactResponse])
def get_contacts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = list_contacts(db, current_user.id)
    return [ContactResponse(user_id=user.id, display_name=(profile.display_name if profile else user.full_name), username=(profile.username if profile else user.username), avatar_url=(profile.avatar_url if profile else None), status_text=(profile.status_text if profile else None), label=contact.label) for contact, user, profile in rows]
