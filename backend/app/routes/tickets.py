import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app import crud
from backend.app.database import get_db
from backend.app.models import Ticket
from backend.app.schemas import (
    TicketCreate,
    TicketCreateResponse,
    TicketDetailResponse,
    TicketListResponse,
    TicketUpdate,
    TicketUpdateResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])

StatusFilter = Literal["Open", "In Progress", "Closed"]
PriorityFilter = Literal["Low", "Medium", "High", "Critical"]


@router.get("", response_model=list[TicketListResponse])
def list_tickets(
    db: Annotated[Session, Depends(get_db)],
    search: Annotated[str | None, Query()] = None,
    status_filter: Annotated[StatusFilter | None, Query(alias="status")] = None,
    priority_filter: Annotated[
        PriorityFilter | None, Query(alias="priority")
    ] = None,
) -> list[Ticket]:
    """Return tickets matching optional search and filters."""
    try:
        return crud.list_tickets(
            db,
            search=search,
            status_filter=status_filter,
            priority_filter=priority_filter,
        )
    except SQLAlchemyError:
        logger.exception("Unable to retrieve tickets due to a database error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve tickets",
        ) from None


@router.post(
    "",
    response_model=TicketCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    ticket_data: TicketCreate,
    db: Annotated[Session, Depends(get_db)],
) -> TicketCreateResponse:
    """Create and automatically prioritize a support ticket."""
    try:
        ticket = crud.create_ticket(db, ticket_data)
    except SQLAlchemyError:
        logger.exception("Unable to create ticket due to a database error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create ticket",
        ) from None

    return TicketCreateResponse(
        ticket_id=ticket.ticket_id,
        created_at=ticket.created_at,
        category=ticket.category,
        priority=ticket.priority,
        priority_score=ticket.priority_score,
        priority_reasons=crud.deserialize_priority_reasons(
            ticket.priority_reasons
        ),
    )


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
def get_ticket_detail(
    ticket_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> TicketDetailResponse:
    """Return one ticket with its ordered notes and priority reasons."""
    try:
        ticket = crud.get_ticket_by_public_id(db, ticket_id)
    except SQLAlchemyError:
        logger.exception("Unable to retrieve ticket due to a database error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve ticket",
        ) from None

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    return TicketDetailResponse(
        ticket_id=ticket.ticket_id,
        customer_name=ticket.customer_name,
        customer_email=ticket.customer_email,
        subject=ticket.subject,
        description=ticket.description,
        status=ticket.status,
        category=ticket.category,
        priority=ticket.priority,
        priority_score=ticket.priority_score,
        priority_reasons=crud.deserialize_priority_reasons(
            ticket.priority_reasons
        ),
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        notes=ticket.notes,
    )


@router.put("/{ticket_id}", response_model=TicketUpdateResponse)
def update_ticket(
    ticket_id: str,
    update_data: TicketUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> TicketUpdateResponse:
    """Update ticket status and/or add an internal note."""
    try:
        ticket = crud.get_ticket_by_public_id(db, ticket_id)
        if ticket is not None:
            ticket = crud.update_ticket(db, ticket, update_data)
    except SQLAlchemyError:
        logger.exception("Unable to update ticket due to a database error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update ticket",
        ) from None

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )

    ticket_detail = TicketDetailResponse(
        ticket_id=ticket.ticket_id,
        customer_name=ticket.customer_name,
        customer_email=ticket.customer_email,
        subject=ticket.subject,
        description=ticket.description,
        status=ticket.status,
        category=ticket.category,
        priority=ticket.priority,
        priority_score=ticket.priority_score,
        priority_reasons=crud.deserialize_priority_reasons(
            ticket.priority_reasons
        ),
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        notes=ticket.notes,
    )

    return TicketUpdateResponse(
        success=True,
        updated_at=ticket.updated_at,
        ticket=ticket_detail,
    )
