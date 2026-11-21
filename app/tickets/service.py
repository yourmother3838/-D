from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import User
from app.tickets.models import Ticket
from app.tickets.schemas import TicketCreate


def create_ticket(db: Session, data: TicketCreate, author: User) -> Ticket:
    ticket = Ticket(title=data.title, description=data.description, author_id=author.id)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def list_tickets(db: Session, user: User) -> list[Ticket]:
    query = select(Ticket).order_by(Ticket.id.desc())
    if user.role != "admin":
        query = query.where(Ticket.author_id == user.id)
    return list(db.scalars(query))


def get_ticket(db: Session, ticket_id: int) -> Ticket | None:
    return db.get(Ticket, ticket_id)


def update_status(db: Session, ticket: Ticket, status: str) -> Ticket:
    ticket.status = status
    db.commit()
    db.refresh(ticket)
    return ticket


def delete_ticket(db: Session, ticket: Ticket) -> None:
    db.delete(ticket)
    db.commit()