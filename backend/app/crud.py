from __future__ import annotations

import json
import re

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from backend.app.models import Note, Ticket, utc_now
from backend.app.schemas import TicketCreate, TicketUpdate
from backend.app.services.priority_service import calculate_priority


def serialize_priority_reasons(reasons: list[str]) -> str:
    """Serialize priority reasons into deterministic JSON array text."""
    return json.dumps(reasons, ensure_ascii=False, separators=(",", ":"))


def deserialize_priority_reasons(value: str | None) -> list[str]:
    """Deserialize priority reasons JSON text into a list of strings."""
    if not value:
        return []
    try:
        decoded = json.loads(value)
    except (json.JSONDecodeError, TypeError, ValueError):
        return []
    if not isinstance(decoded, list):
        return []
    return [item for item in decoded if isinstance(item, str)]


def generate_ticket_id(db: Session) -> str:
    """Generate the next public ticket ID (e.g. TKT-0001).

    Sequential ID generation is acceptable for a small app, but at scale it
    would need a database sequence or a stronger concurrency strategy to
    avoid collisions under concurrent inserts.
    """
    existing_ticket_ids = db.scalars(select(Ticket.ticket_id)).all()

    max_suffix: int | None = None
    for value in existing_ticket_ids:
        if not isinstance(value, str):
            continue
        match = re.match(r"^TKT-(\d+)$", value.strip())
        if not match:
            continue
        suffix = int(match.group(1))
        max_suffix = suffix if max_suffix is None else max(max_suffix, suffix)

    next_suffix = 1 if max_suffix is None else max_suffix + 1
    return f"TKT-{next_suffix:04d}"


def get_customer_ticket_counts(
    db: Session,
    customer_email: str,
) -> tuple[int, int, int]:
    """Return (total_count, open_count, closed_count) for a customer email."""
    email_norm = customer_email.strip().lower()
    email_condition = func.lower(Ticket.customer_email) == email_norm

    total_count = db.scalar(
        select(func.count()).select_from(Ticket).where(email_condition)
    ) or 0
    open_count = db.scalar(
        select(func.count())
        .select_from(Ticket)
        .where(email_condition, Ticket.status.in_(("Open", "In Progress")))
    ) or 0
    closed_count = db.scalar(
        select(func.count()).select_from(Ticket).where(
            email_condition, Ticket.status == "Closed"
        )
    ) or 0

    return int(total_count), int(open_count), int(closed_count)


def create_ticket(db: Session, ticket_data: TicketCreate) -> Ticket:
    """Create a new ticket and persist it with computed priority fields."""
    normalized_email = ticket_data.customer_email.strip().lower()

    total_count, open_count, _closed_count = get_customer_ticket_counts(
        db, normalized_email
    )

    priority = calculate_priority(
        subject=ticket_data.subject,
        description=ticket_data.description,
        existing_open_tickets=open_count,
        total_customer_tickets=total_count,
    )

    public_ticket_id = generate_ticket_id(db)

    ticket = Ticket(
        ticket_id=public_ticket_id,
        customer_name=ticket_data.customer_name,
        customer_email=normalized_email,
        subject=ticket_data.subject,
        description=ticket_data.description,
        status="Open",
        category=priority.category,
        priority=priority.priority,
        priority_score=priority.score,
        priority_reasons=serialize_priority_reasons(priority.reasons),
    )

    db.add(ticket)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(ticket)
    return ticket


def list_tickets(
    db: Session,
    search: str | None = None,
    status_filter: str | None = None,
    priority_filter: str | None = None,
) -> list[Ticket]:
    """Return tickets matching optional search and filter criteria."""
    statement = select(Ticket)

    search_value = search.strip() if search else ""
    if search_value:
        normalized_search = search_value.lower()
        statement = statement.where(
            or_(
                func.lower(Ticket.ticket_id).contains(
                    normalized_search, autoescape=True
                ),
                func.lower(Ticket.customer_name).contains(
                    normalized_search, autoescape=True
                ),
                func.lower(Ticket.customer_email).contains(
                    normalized_search, autoescape=True
                ),
                func.lower(Ticket.subject).contains(
                    normalized_search, autoescape=True
                ),
                func.lower(Ticket.description).contains(
                    normalized_search, autoescape=True
                ),
            )
        )

    if status_filter:
        statement = statement.where(Ticket.status == status_filter)

    if priority_filter:
        statement = statement.where(Ticket.priority == priority_filter)

    statement = statement.order_by(Ticket.created_at.desc(), Ticket.id.desc())
    return list(db.scalars(statement).all())


def get_ticket_by_public_id(
    db: Session,
    ticket_id: str,
) -> Ticket | None:
    """Return a ticket and its ordered notes by public ticket ID."""
    normalized_ticket_id = ticket_id.strip().lower()
    if not normalized_ticket_id:
        return None

    statement = (
        select(Ticket)
        .options(selectinload(Ticket.notes))
        .where(func.lower(Ticket.ticket_id) == normalized_ticket_id)
    )
    return db.scalar(statement)


def update_ticket(
    db: Session,
    ticket: Ticket,
    update_data: TicketUpdate,
) -> Ticket:
    """Update ticket status and/or add an ordered note."""
    if update_data.status is not None:
        ticket.status = update_data.status

    if update_data.note_text is not None:
        db.add(Note(ticket=ticket, note_text=update_data.note_text))

    ticket.updated_at = utc_now()

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(ticket)
    db.refresh(ticket, attribute_names=["notes"])
    return ticket

