from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import User
from app.comments.models import Comment
from app.comments.schemas import CommentCreate
from app.tickets.models import Ticket


def create_comment(db: Session, ticket: Ticket, data: CommentCreate, author: User) -> Comment:
    comment = Comment(text=data.text, ticket_id=ticket.id, author_id=author.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def list_comments(db: Session, ticket: Ticket) -> list[Comment]:
    return list(db.scalars(select(Comment).where(Comment.ticket_id == ticket.id).order_by(Comment.id)))