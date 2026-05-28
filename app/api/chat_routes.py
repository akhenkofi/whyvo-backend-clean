from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.chat import MessageCreateRequest, MessageResponse, MessagesResponse, ThreadResponse
from app.services.chat_service import list_messages, list_threads, send_message

router = APIRouter(prefix='/api/v1/chats', tags=['chats'])


@router.get('/threads', response_model=list[ThreadResponse])
def get_threads(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = list_threads(db, current_user.id)
    return [ThreadResponse(user_id=user.id, display_name=(profile.display_name if profile else user.full_name), username=(profile.username if profile else user.username), avatar_url=(profile.avatar_url if profile else None), last_message=message.body, last_message_at=message.created_at) for user, profile, message in rows]


@router.get('/{user_id}/messages', response_model=MessagesResponse)
def get_messages(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = list_messages(db, current_user.id, user_id)
    return MessagesResponse(messages=[MessageResponse(id=item.id, sender_user_id=item.sender_user_id, recipient_user_id=item.recipient_user_id, body=item.body, created_at=item.created_at) for item in items])


@router.post('/{user_id}/messages', response_model=MessageResponse)
def post_message(user_id: int, payload: MessageCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail='Cannot message yourself')
    message = send_message(db, current_user.id, user_id, payload.body)
    return MessageResponse(id=message.id, sender_user_id=message.sender_user_id, recipient_user_id=message.recipient_user_id, body=message.body, created_at=message.created_at)
