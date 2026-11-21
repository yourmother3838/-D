from celery.utils.log import get_task_logger

import app.models
from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.tickets.models import Ticket

logger = get_task_logger(__name__)


@celery_app.task(name="tickets.notify_ticket_created")
def notify_ticket_created(ticket_id: int) -> None:
    with SessionLocal() as db:
        ticket = db.get(Ticket, ticket_id)
        if ticket is None:
            logger.warning("Ticket %s not found", ticket_id)
            return
        logger.info(
            "Notification: new ticket #%s '%s' from user %s",
            ticket.id,
            ticket.title,
            ticket.author_id,
        )