from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PriorityResult:
    """Deterministic prioritization result."""

    category: str
    priority: str
    score: int
    reasons: list[str]


SECURITY_CATEGORY: dict[str, object] = {
    "keywords": {
        "hack",
        "hacked",
        "unauthorized",
        "fraud",
        "breach",
        "compromised",
        "stolen",
    },
    "score": 35,
    "reason": "Potential security incident",
}

PAYMENT_CATEGORY: dict[str, object] = {
    "keywords": {
        "payment",
        "refund",
        "charged",
        "deducted",
        "billing",
        "invoice",
        "transaction",
    },
    "score": 20,
    "reason": "Payment or billing related issue",
}

ACCOUNT_CATEGORY: dict[str, object] = {
    "keywords": {"login", "password", "otp", "signin", "locked", "account"},
    "score": 15,
    "reason": "Account access issue",
}

TECHNICAL_CATEGORY: dict[str, object] = {
    "keywords": {"error", "bug", "crash", "loading", "slow", "failed"},
    "score": 15,
    "reason": "Technical issue",
}

CATEGORY_RULES: dict[str, dict[str, object]] = {
    "Security": SECURITY_CATEGORY,
    "Payment": PAYMENT_CATEGORY,
    "Account": ACCOUNT_CATEGORY,
    "Technical": TECHNICAL_CATEGORY,
}

CATEGORY_ORDER: tuple[str, ...] = ("Security", "Payment", "Account", "Technical")

URGENT_WORDS: frozenset[str] = frozenset(
    {"urgent", "immediately", "critical", "blocked", "emergency", "asap"}
)


def normalize_text(text: str) -> set[str]:
    """Lowercase, remove punctuation, and return a set of whole-word tokens."""
    lowered = text.lower()
    # Replace any non-alphanumeric character with whitespace, then split.
    cleaned = re.sub(r"[^a-z0-9\s]+", " ", lowered)
    words = cleaned.split()
    return set(words)


def calculate_priority(
    subject: str,
    description: str,
    existing_open_tickets: int,
    total_customer_tickets: int,
) -> PriorityResult:
    """Calculate ticket category, priority band, and deterministic reasons."""
    score = 10
    reasons: list[str] = []
    reasons_set: set[str] = set()

    text_words = normalize_text(subject) | normalize_text(description)

    category = "General"
    category_score = 0
    category_reason = "No category detected."

    for name in CATEGORY_ORDER:
        rule = CATEGORY_RULES[name]
        keywords: set[str] = rule["keywords"]  # type: ignore[assignment]
        if text_words & keywords:
            category = name
            category_score = int(rule["score"])  # type: ignore[arg-type]
            category_reason = str(rule["reason"])  # type: ignore[arg-type]
            break

    score += category_score
    if category_reason not in reasons_set:
        reasons.append(category_reason)
        reasons_set.add(category_reason)

    urgent = bool(text_words & URGENT_WORDS)
    if urgent:
        score += 20
        reason = "Contains urgent language"
        if reason not in reasons_set:
            reasons.append(reason)
            reasons_set.add(reason)

    if existing_open_tickets > 0:
        score += 15
        reason = "Customer already has unresolved tickets"
        if reason not in reasons_set:
            reasons.append(reason)
            reasons_set.add(reason)

    if total_customer_tickets >= 3:
        score += 10
        reason = "Customer frequently contacts support"
        if reason not in reasons_set:
            reasons.append(reason)
            reasons_set.add(reason)

    score = min(score, 100)

    if 0 <= score <= 29:
        priority = "Low"
    elif 30 <= score <= 49:
        priority = "Medium"
    elif 50 <= score <= 74:
        priority = "High"
    else:
        priority = "Critical"

    return PriorityResult(category=category, priority=priority, score=score, reasons=reasons)

