from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.post import Post
from app.models.user import User
from app.schemas.update import CommentCreateRequest, CommentResponse, FeedResponse, PostCreateRequest, PostResponse, PostUpdateRequest
from app.services.updates_service import add_comment, author_bundle, create_post, list_comments, list_posts, post_stats, toggle_like, update_post

router = APIRouter(prefix='/api/v1/updates', tags=['updates'])


def _serialize_post(db: Session, post: Post, viewer_user_id: int) -> PostResponse:
    user, profile = author_bundle(db, post.user_id)
    like_count, comment_count, liked_by_me = post_stats(db, post.id, viewer_user_id)
    return PostResponse(
        id=post.id,
        user_id=post.user_id,
        display_name=(profile.display_name if profile else user.full_name),
        username=(profile.username if profile else user.username),
        avatar_url=(profile.avatar_url if profile else None),
        body=post.body,
        media_url=post.media_url,
        like_count=like_count,
        comment_count=comment_count,
        liked_by_me=liked_by_me,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


@router.get('/feed', response_model=FeedResponse)
def get_feed(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    posts = list_posts(db)
    return FeedResponse(posts=[_serialize_post(db, post, current_user.id) for post in posts])


@router.get('/posts', response_model=list[PostResponse])
def get_posts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    posts = list_posts(db)
    return [_serialize_post(db, post, current_user.id) for post in posts]


@router.post('/posts', response_model=PostResponse)
def post_updates(payload: PostCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = create_post(db, current_user.id, payload.body, payload.media_url)
    return _serialize_post(db, post, current_user.id)


@router.put('/posts/{post_id}', response_model=PostResponse)
def put_post(post_id: int, payload: PostUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == current_user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail='Post not found')
    update_post(post, payload.model_dump())
    db.commit()
    db.refresh(post)
    return _serialize_post(db, post, current_user.id)


@router.delete('/posts/{post_id}')
def delete_post(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id, Post.user_id == current_user.id).first()
    if not post:
        raise HTTPException(status_code=404, detail='Post not found')
    db.delete(post)
    db.commit()
    return {'deleted': True}


@router.post('/posts/{post_id}/like')
def like_post(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail='Post not found')
    liked = toggle_like(db, current_user.id, post_id)
    return {'liked': liked}


@router.get('/posts/{post_id}/comments', response_model=list[CommentResponse])
def get_post_comments(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = list_comments(db, post_id)
    result = []
    for item in items:
        user, profile = author_bundle(db, item.user_id)
        result.append(CommentResponse(id=item.id, user_id=item.user_id, display_name=(profile.display_name if profile else user.full_name), body=item.body, created_at=item.created_at))
    return result


@router.post('/posts/{post_id}/comments', response_model=CommentResponse)
def add_post_comment(post_id: int, payload: CommentCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail='Post not found')
    item = add_comment(db, current_user.id, post_id, payload.body)
    user, profile = author_bundle(db, item.user_id)
    return CommentResponse(id=item.id, user_id=item.user_id, display_name=(profile.display_name if profile else user.full_name), body=item.body, created_at=item.created_at)
