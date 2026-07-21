from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, model_validator

ALLOWED_STATUSES = frozenset({"Open", "In Progress", "Closed"})


class TicketCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    subject: str
    description: str

    @field_validator("customer_name", "subject", "description", mode="before")
    @classmethod
    def strip_whitespace(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("customer_name")
    @classmethod
    def validate_customer_name(cls, value: str) -> str:
        if not value:
            raise ValueError("customer_name cannot be empty or whitespace-only")
        if len(value) < 2 or len(value) > 100:
            raise ValueError("customer_name must be between 2 and 100 characters")
        return value

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, value: str) -> str:
        if not value:
            raise ValueError("subject cannot be empty or whitespace-only")
        if len(value) < 3 or len(value) > 200:
            raise ValueError("subject must be between 3 and 200 characters")
        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        if not value:
            raise ValueError("description cannot be empty or whitespace-only")
        if len(value) < 10 or len(value) > 5000:
            raise ValueError("description must be between 10 and 5000 characters")
        return value


class NoteCreate(BaseModel):
    note_text: str

    @field_validator("note_text", mode="before")
    @classmethod
    def strip_whitespace(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("note_text")
    @classmethod
    def validate_note_text(cls, value: str) -> str:
        if not value:
            raise ValueError("note_text cannot be empty or whitespace-only")
        if len(value) < 2 or len(value) > 2000:
            raise ValueError("note_text must be between 2 and 2000 characters")
        return value


class TicketUpdate(BaseModel):
    status: str | None = None
    note_text: str | None = None

    @field_validator("status", "note_text", mode="before")
    @classmethod
    def strip_whitespace(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is not None and value not in ALLOWED_STATUSES:
            allowed = ", ".join(sorted(ALLOWED_STATUSES))
            raise ValueError(f"status must be one of: {allowed}")
        return value

    @field_validator("note_text")
    @classmethod
    def validate_note_text(cls, value: str | None) -> str | None:
        if value is not None:
            if not value:
                raise ValueError("note_text cannot be empty or whitespace-only when provided")
            if len(value) < 2 or len(value) > 2000:
                raise ValueError("note_text must be between 2 and 2000 characters")
        return value

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> TicketUpdate:
        if self.status is None and self.note_text is None:
            raise ValueError("at least one of status or note_text must be provided")
        return self


class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    note_text: str
    created_at: datetime


class TicketListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_id: str
    customer_name: str
    customer_email: EmailStr
    subject: str
    status: str
    category: str
    priority: str
    priority_score: int
    created_at: datetime
    updated_at: datetime


class TicketDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticket_id: str
    customer_name: str
    customer_email: EmailStr
    subject: str
    description: str
    status: str
    category: str
    priority: str
    priority_score: int
    priority_reasons: list[str]
    created_at: datetime
    updated_at: datetime
    notes: list[NoteResponse]


class TicketCreateResponse(BaseModel):
    ticket_id: str
    created_at: datetime
    category: str
    priority: str
    priority_score: int
    priority_reasons: list[str]


class TicketUpdateResponse(BaseModel):
    success: bool
    updated_at: datetime
    ticket: TicketDetailResponse
