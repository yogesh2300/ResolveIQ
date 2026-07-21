from __future__ import annotations

import json

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.crud import (
    create_ticket,
    deserialize_priority_reasons,
    generate_ticket_id,
    get_customer_ticket_counts,
    serialize_priority_reasons,
)
from backend.app.database import Base
from backend.app.models import Ticket
from backend.app.schemas import TicketCreate


@pytest.fixture
def db_session(tmp_path):
    """Provide an isolated temporary SQLite session for each test."""
    db_path = tmp_path / "test_ticket_creation.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    session = TestingSessionLocal()
    try:
        yield session, TestingSessionLocal
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _make_ticket(
    *,
    ticket_id: str,
    customer_email: str = "user@example.com",
    status: str = "Open",
    customer_name: str = "Jane Doe",
    subject: str = "Sample subject",
    description: str = "Sample description text.",
) -> Ticket:
    return Ticket(
        ticket_id=ticket_id,
        customer_name=customer_name,
        customer_email=customer_email,
        subject=subject,
        description=description,
        status=status,
        category="General",
        priority="Low",
        priority_score=10,
        priority_reasons="[]",
    )


# ---------------------------------------------------------------------------
# Serialization / deserialization
# ---------------------------------------------------------------------------


def test_serialize_priority_reasons_returns_valid_json_array_text() -> None:
    reasons = ["Potential security incident", "Contains urgent language"]
    encoded = serialize_priority_reasons(reasons)

    assert isinstance(encoded, str)
    decoded = json.loads(encoded)
    assert decoded == reasons
    assert encoded.startswith("[")
    assert encoded.endswith("]")


def test_serialize_priority_reasons_preserves_unicode() -> None:
    reasons = ["Accès non autorisé", "紧急", "pagamento falhou"]
    encoded = serialize_priority_reasons(reasons)

    assert "Accès non autorisé" in encoded
    assert "紧急" in encoded
    assert json.loads(encoded) == reasons


def test_deserialize_priority_reasons_decodes_valid_string_list() -> None:
    value = '["Potential security incident","Contains urgent language"]'
    assert deserialize_priority_reasons(value) == [
        "Potential security incident",
        "Contains urgent language",
    ]


def test_deserialize_priority_reasons_returns_empty_for_invalid_inputs() -> None:
    assert deserialize_priority_reasons(None) == []
    assert deserialize_priority_reasons("") == []
    assert deserialize_priority_reasons("{not-json") == []
    assert deserialize_priority_reasons('{"a": 1}') == []
    assert deserialize_priority_reasons('"just-a-string"') == []


def test_deserialize_priority_reasons_removes_non_string_elements() -> None:
    value = '["ok", 1, null, true, {"a": 1}, "also-ok"]'
    assert deserialize_priority_reasons(value) == ["ok", "also-ok"]


# ---------------------------------------------------------------------------
# generate_ticket_id
# ---------------------------------------------------------------------------


def test_generate_ticket_id_returns_tkt_0001_when_empty(db_session) -> None:
    session, _ = db_session
    assert generate_ticket_id(session) == "TKT-0001"


def test_generate_ticket_id_increments_existing_ids(db_session) -> None:
    session, _ = db_session
    session.add(_make_ticket(ticket_id="TKT-0001"))
    session.add(_make_ticket(ticket_id="TKT-0002", customer_email="other@example.com"))
    session.commit()

    assert generate_ticket_id(session) == "TKT-0003"


def test_generate_ticket_id_ignores_malformed_ids(db_session) -> None:
    session, _ = db_session
    session.add(_make_ticket(ticket_id="INVALID"))
    session.add(_make_ticket(ticket_id="TKT-ABC", customer_email="a@example.com"))
    session.add(_make_ticket(ticket_id="OTHER-9999", customer_email="b@example.com"))
    session.add(_make_ticket(ticket_id="TKT-0002", customer_email="c@example.com"))
    session.commit()

    assert generate_ticket_id(session) == "TKT-0003"


def test_generate_ticket_id_supports_values_beyond_four_digits(db_session) -> None:
    session, _ = db_session
    session.add(_make_ticket(ticket_id="TKT-9999"))
    session.commit()

    assert generate_ticket_id(session) == "TKT-10000"


# ---------------------------------------------------------------------------
# get_customer_ticket_counts
# ---------------------------------------------------------------------------


def test_customer_email_matching_is_case_insensitive(db_session) -> None:
    session, _ = db_session
    session.add(_make_ticket(ticket_id="TKT-0001", customer_email="User@Example.com"))
    session.commit()

    total, open_count, closed = get_customer_ticket_counts(session, "user@example.com")

    assert total == 1
    assert open_count == 1
    assert closed == 0


def test_get_customer_ticket_counts_returns_correct_totals(db_session) -> None:
    session, _ = db_session
    email = "counts@example.com"
    session.add(_make_ticket(ticket_id="TKT-0001", customer_email=email, status="Open"))
    session.add(
        _make_ticket(ticket_id="TKT-0002", customer_email=email, status="In Progress")
    )
    session.add(_make_ticket(ticket_id="TKT-0003", customer_email=email, status="Closed"))
    session.add(
        _make_ticket(
            ticket_id="TKT-0004",
            customer_email="someone.else@example.com",
            status="Open",
        )
    )
    session.commit()

    total, open_count, closed = get_customer_ticket_counts(session, email)

    assert total == 3
    assert open_count == 2
    assert closed == 1


# ---------------------------------------------------------------------------
# create_ticket
# ---------------------------------------------------------------------------


def test_create_ticket_normalizes_email_to_lowercase(db_session) -> None:
    session, _ = db_session
    ticket = create_ticket(
        session,
        TicketCreate(
            customer_name="Jane Doe",
            customer_email="Jane.Doe@Example.COM",
            subject="Product information",
            description="I would like to know more about your services.",
        ),
    )

    assert ticket.customer_email == "jane.doe@example.com"


def test_create_ticket_generates_first_public_ticket_id(db_session) -> None:
    session, _ = db_session
    ticket = create_ticket(
        session,
        TicketCreate(
            customer_name="Jane Doe",
            customer_email="jane@example.com",
            subject="Product information",
            description="I would like to know more about your services.",
        ),
    )

    assert ticket.ticket_id == "TKT-0001"


def test_create_ticket_stores_status_as_open(db_session) -> None:
    session, _ = db_session
    ticket = create_ticket(
        session,
        TicketCreate(
            customer_name="Jane Doe",
            customer_email="jane@example.com",
            subject="Product information",
            description="I would like to know more about your services.",
        ),
    )

    assert ticket.status == "Open"


def test_create_ticket_stores_security_priority_fields(db_session) -> None:
    session, _ = db_session
    ticket = create_ticket(
        session,
        TicketCreate(
            customer_name="Jane Doe",
            customer_email="jane@example.com",
            subject="Unauthorized account access",
            description="My account may have been compromised.",
        ),
    )

    assert ticket.category == "Security"
    assert ticket.priority == "Medium"
    assert ticket.priority_score == 45
    assert "Potential security incident" in deserialize_priority_reasons(
        ticket.priority_reasons
    )


def test_create_ticket_stores_priority_reasons_as_valid_json_text(db_session) -> None:
    session, _ = db_session
    ticket = create_ticket(
        session,
        TicketCreate(
            customer_name="Jane Doe",
            customer_email="jane@example.com",
            subject="Unauthorized account access",
            description="My account may have been compromised.",
        ),
    )

    decoded = json.loads(ticket.priority_reasons)
    assert isinstance(decoded, list)
    assert all(isinstance(item, str) for item in decoded)
    assert decoded == deserialize_priority_reasons(ticket.priority_reasons)


def test_second_ticket_applies_unresolved_ticket_history_modifier(db_session) -> None:
    session, _ = db_session
    email = "repeat@example.com"

    first = create_ticket(
        session,
        TicketCreate(
            customer_name="Jane Doe",
            customer_email=email,
            subject="Product information",
            description="I would like to know more about your services.",
        ),
    )
    second = create_ticket(
        session,
        TicketCreate(
            customer_name="Jane Doe",
            customer_email=email,
            subject="Unauthorized account access",
            description="My account may have been compromised.",
        ),
    )

    assert first.priority_score == 10
    # base 10 + security 35 + unresolved open tickets 15 = 60
    assert second.category == "Security"
    assert second.priority_score == 60
    assert second.priority == "High"
    assert "Customer already has unresolved tickets" in deserialize_priority_reasons(
        second.priority_reasons
    )


def test_created_ticket_is_persisted_and_queryable_in_new_session(db_session) -> None:
    session, SessionLocal = db_session
    created = create_ticket(
        session,
        TicketCreate(
            customer_name="Jane Doe",
            customer_email="persist@example.com",
            subject="Unauthorized account access",
            description="My account may have been compromised.",
        ),
    )
    ticket_id = created.ticket_id
    session.close()

    new_session: Session = SessionLocal()
    try:
        loaded = new_session.scalar(
            select(Ticket).where(Ticket.ticket_id == ticket_id)
        )
        assert loaded is not None
        assert loaded.ticket_id == "TKT-0001"
        assert loaded.customer_email == "persist@example.com"
        assert loaded.category == "Security"
    finally:
        new_session.close()


def test_create_ticket_persists_customer_name_subject_and_description(
    db_session,
) -> None:
    session, _ = db_session
    ticket = create_ticket(
        session,
        TicketCreate(
            customer_name="Alex Rivera",
            customer_email="alex@example.com",
            subject="Login problem",
            description="My password is not working correctly.",
        ),
    )

    assert ticket.customer_name == "Alex Rivera"
    assert ticket.subject == "Login problem"
    assert ticket.description == "My password is not working correctly."


def test_two_sequential_creations_receive_different_ticket_ids(db_session) -> None:
    session, _ = db_session
    first = create_ticket(
        session,
        TicketCreate(
            customer_name="Jane Doe",
            customer_email="one@example.com",
            subject="Product information",
            description="I would like to know more about your services.",
        ),
    )
    second = create_ticket(
        session,
        TicketCreate(
            customer_name="John Smith",
            customer_email="two@example.com",
            subject="Product information",
            description="I would like to know more about your services.",
        ),
    )

    assert first.ticket_id == "TKT-0001"
    assert second.ticket_id == "TKT-0002"
    assert first.ticket_id != second.ticket_id
