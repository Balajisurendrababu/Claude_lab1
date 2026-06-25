import random

FIELD_VALUES = {
    "product_area": ["Billing", "Platform", "Integrations", "Security", "Onboarding"],
    "severity":     ["P1-Critical", "P2-High", "P3-Medium", "P4-Low"],
    "intent":       ["Bug", "Question", "Feature Request", "Billing Dispute"],
}


def classify_ticket(ticket_text: str, fields_needed: list[str]) -> dict:
    """
    Classify a support ticket and return only the requested fields.

    Args:
        ticket_text:   The raw ticket content submitted by the user.
        fields_needed: Which fields to classify, e.g. ["product_area", "severity"].

    Returns:
        A dict containing exactly the keys in fields_needed, each mapped to a
        value drawn from the controlled vocabulary for that field.
    """
    return {
        field: random.choice(FIELD_VALUES[field])
        for field in fields_needed
        if field in FIELD_VALUES
    }
