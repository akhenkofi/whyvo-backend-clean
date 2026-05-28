from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.post import Post, PostComment, PostLike
from app.models.profile import Profile
from app.models.user import User


def list_posts(db: Session):
    return db.query(Post).order_by(Post.created_at.desc()).all()


from typing import Optional


def create_post(db: Session, user_id: int, body: str, media_url: Optional[str]):
    post = Post(user_id=user_id, body=body, media_url=media_url)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update_post(post: Post, payload: dict):
    for key, value in payload.items():
        if value is not None and hasattr(post, key):
            setattr(post, key, value)
    return post


def toggle_like(db: Session, user_id: int, post_id: int):
    existing = db.query(PostLike).filter(PostLike.user_id == user_id, PostLike.post_id == post_id).first()
    if existing:
        db.delete(existing)
        db.commit()
        return False
    like = PostLike(user_id=user_id, post_id=post_id)
    db.add(like)
    db.commit()
    return True


def list_comments(db: Session, post_id: int):
    return db.query(PostComment).filter(PostComment.post_id == post_id).order_by(PostComment.created_at.asc()).all()


def add_comment(db: Session, user_id: int, post_id: int, body: str):
    comment = PostComment(user_id=user_id, post_id=post_id, body=body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def post_stats(db: Session, post_id: int, viewer_user_id: int):
    like_count = db.query(func.count(PostLike.id)).filter(PostLike.post_id == post_id).scalar() or 0
    comment_count = db.query(func.count(PostComment.id)).filter(PostComment.post_id == post_id).scalar() or 0
    liked_by_me = db.query(PostLike).filter(PostLike.post_id == post_id, PostLike.user_id == viewer_user_id).first() is not None
    return int(like_count), int(comment_count), liked_by_me


def author_bundle(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    return user, profile
