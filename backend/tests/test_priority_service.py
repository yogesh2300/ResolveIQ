from backend.app.services.priority_service import calculate_priority, normalize_text


# ---------------------------------------------------------------------------
# Normalization tests
# ---------------------------------------------------------------------------


def test_normalize_text_lowercases_removes_punctuation_and_returns_whole_words() -> None:
    tokens = normalize_text("Payment FAILED! Please help.")

    assert "payment" in tokens
    assert "failed" in tokens
    assert "please" in tokens
    assert "help" in tokens
    assert "payment!" not in tokens
    assert "failed!" not in tokens


def test_normalize_text_prevents_substring_keyword_matches() -> None:
    tokens = normalize_text("Company hackathon registration")

    assert "hackathon" in tokens
    assert "hack" not in tokens

    result = calculate_priority(
        subject="Company hackathon registration",
        description="",
        existing_open_tickets=0,
        total_customer_tickets=0,
    )

    assert result.category == "General"
    assert "Potential security incident" not in result.reasons


# ---------------------------------------------------------------------------
# Category tests
# ---------------------------------------------------------------------------


def test_security_category() -> None:
    result = calculate_priority(
        subject="Unauthorized account access",
        description="My account may have been compromised.",
        existing_open_tickets=0,
        total_customer_tickets=0,
    )

    assert result.category == "Security"
    assert result.score == 45
    assert result.priority == "Medium"
    assert "Potential security incident" in result.reasons


def test_payment_category() -> None:
    result = calculate_priority(
        subject="Payment deducted",
        description="The transaction failed.",
        existing_open_tickets=0,
        total_customer_tickets=0,
    )

    assert result.category == "Payment"
    assert result.score == 30
    assert result.priority == "Medium"


def test_account_category() -> None:
    result = calculate_priority(
        subject="Login problem",
        description="My password is not working.",
        existing_open_tickets=0,
        total_customer_tickets=0,
    )

    assert result.category == "Account"
    assert result.score == 25
    assert result.priority == "Low"


def test_technical_category() -> None:
    result = calculate_priority(
        subject="Application crash",
        description="The application shows an error.",
        existing_open_tickets=0,
        total_customer_tickets=0,
    )

    assert result.category == "Technical"
    assert result.score == 25
    assert result.priority == "Low"


def test_general_category() -> None:
    result = calculate_priority(
        subject="Product information",
        description="I would like to know more about your services.",
        existing_open_tickets=0,
        total_customer_tickets=0,
    )

    assert result.category == "General"
    assert result.score == 10
    assert result.priority == "Low"
    assert "No category detected." in result.reasons


# ---------------------------------------------------------------------------
# Modifier tests
# ---------------------------------------------------------------------------


def test_urgent_language_adds_twenty_once() -> None:
    result = calculate_priority(
        subject="URGENT critical emergency",
        description="Please respond immediately asap",
        existing_open_tickets=0,
        total_customer_tickets=0,
    )

    assert result.score == 30
    assert result.reasons.count("Contains urgent language") == 1


def test_existing_open_tickets_adds_fifteen() -> None:
    result = calculate_priority(
        subject="Product information",
        description="General inquiry",
        existing_open_tickets=1,
        total_customer_tickets=0,
    )

    assert result.score == 25
    assert "Customer already has unresolved tickets" in result.reasons


def test_total_customer_tickets_three_or_more_adds_ten() -> None:
    result = calculate_priority(
        subject="Product information",
        description="General inquiry",
        existing_open_tickets=0,
        total_customer_tickets=3,
    )

    assert result.score == 20
    assert "Customer frequently contacts support" in result.reasons


def test_multiple_customer_history_conditions_both_apply() -> None:
    result = calculate_priority(
        subject="Product information",
        description="General inquiry",
        existing_open_tickets=2,
        total_customer_tickets=5,
    )

    assert result.score == 35
    assert "Customer already has unresolved tickets" in result.reasons
    assert "Customer frequently contacts support" in result.reasons


# ---------------------------------------------------------------------------
# Combined-rule tests
# ---------------------------------------------------------------------------


def test_security_plus_urgency() -> None:
    result = calculate_priority(
        subject="Unauthorized access",
        description="This is critical",
        existing_open_tickets=0,
        total_customer_tickets=0,
    )

    assert result.category == "Security"
    assert result.score == 65
    assert result.priority == "High"


def test_payment_plus_urgency_plus_open_ticket() -> None:
    result = calculate_priority(
        subject="Payment refund",
        description="Urgent billing issue",
        existing_open_tickets=1,
        total_customer_tickets=0,
    )

    assert result.category == "Payment"
    assert result.score == 65
    assert result.priority == "High"


def test_security_plus_all_modifiers() -> None:
    result = calculate_priority(
        subject="Unauthorized breach",
        description="Emergency fraud report",
        existing_open_tickets=1,
        total_customer_tickets=4,
    )

    assert result.category == "Security"
    assert result.score == 90
    assert result.priority == "Critical"


# ---------------------------------------------------------------------------
# Determinism and limits
# ---------------------------------------------------------------------------


def test_multiple_keywords_from_same_category_add_score_once() -> None:
    result = calculate_priority(
        subject="Unauthorized fraud breach",
        description="Account compromised and stolen",
        existing_open_tickets=0,
        total_customer_tickets=0,
    )

    assert result.category == "Security"
    assert result.score == 45
    assert result.reasons.count("Potential security incident") == 1


def test_multiple_urgent_keywords_add_urgency_once() -> None:
    result = calculate_priority(
        subject="urgent critical",
        description="emergency asap immediately",
        existing_open_tickets=0,
        total_customer_tickets=0,
    )

    assert result.score == 30
    assert result.reasons.count("Contains urgent language") == 1


def test_score_never_exceeds_one_hundred() -> None:
    result = calculate_priority(
        subject="Unauthorized fraud breach",
        description="Emergency critical asap",
        existing_open_tickets=5,
        total_customer_tickets=10,
    )

    assert result.score <= 100
    assert result.priority == "Critical"


def test_matching_is_case_insensitive() -> None:
    lower = calculate_priority(
        subject="payment deducted",
        description="transaction failed",
        existing_open_tickets=0,
        total_customer_tickets=0,
    )
    upper = calculate_priority(
        subject="PAYMENT DEDUCTED",
        description="TRANSACTION FAILED",
        existing_open_tickets=0,
        total_customer_tickets=0,
    )

    assert lower.category == upper.category == "Payment"
    assert lower.score == upper.score == 30
    assert lower.priority == upper.priority == "Medium"


def test_same_inputs_return_identical_priority_result() -> None:
    kwargs = {
        "subject": "Login problem",
        "description": "Password reset needed",
        "existing_open_tickets": 1,
        "total_customer_tickets": 2,
    }

    first = calculate_priority(**kwargs)
    second = calculate_priority(**kwargs)

    assert first == second


def test_reasons_do_not_contain_duplicates() -> None:
    result = calculate_priority(
        subject="Unauthorized fraud",
        description="Emergency critical",
        existing_open_tickets=2,
        total_customer_tickets=4,
    )

    assert len(result.reasons) == len(set(result.reasons))


def test_category_order_security_wins_over_payment() -> None:
    result = calculate_priority(
        subject="Unauthorized payment fraud",
        description="Billing breach transaction",
        existing_open_tickets=0,
        total_customer_tickets=0,
    )

    assert result.category == "Security"
    assert result.score == 45
    assert "Potential security incident" in result.reasons
    assert "Payment or billing related issue" not in result.reasons
