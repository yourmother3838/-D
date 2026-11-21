from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.comments import service
from app.comments.schemas import CommentCreate, CommentRead
from app.core.database import get_db
from app.tickets.dependencies import get_accessible_ticket
from app.tickets.models import Ticket

router = APIRouter(prefix="/tickets/{ticket_id}/comments", tags=["comments"])


@router.post("", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def create_comment(
    data: CommentCreate,
    ticket: Ticket = Depends(get_accessible_ticket),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.create_comment(db, ticket, data, current_user)


@router.get("", response_model=list[CommentRead])
def list_comments(
    ticket: Ticket = Depends(get_accessible_ticket),
    db: Session = Depends(get_db),
):
    return service.list_comments(db, ticket)