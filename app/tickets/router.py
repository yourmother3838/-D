from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_role
from app.auth.models import User
from app.core.database import get_db
from app.tickets import service
from app.tickets.dependencies import get_accessible_ticket
from app.tickets.models import Ticket
from app.tickets.schemas import TicketCreate, TicketRead, TicketStatusUpdate

import logging

from app.tickets.tasks import notify_ticket_created

router = APIRouter(prefix="/tickets", tags=["tickets"])

logger = logging.getLogger(__name__)

@router.post("", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
def create_ticket(
    data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = service.create_ticket(db, data, current_user)
    try:
        notify_ticket_created.delay(ticket.id)
    except Exception:
        logger.exception("Failed to enqueue notification for ticket %s", ticket.id)
    return ticket


@router.get("", response_model=list[TicketRead])
def list_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.list_tickets(db, current_user)


@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket(ticket: Ticket = Depends(get_accessible_ticket)):
    return ticket


@router.patch("/{ticket_id}/status", response_model=TicketRead)
def update_ticket_status(
    data: TicketStatusUpdate,
    ticket: Ticket = Depends(get_accessible_ticket),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    return service.update_status(db, ticket, data.status)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket: Ticket = Depends(get_accessible_ticket),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    service.delete_ticket(db, ticket)