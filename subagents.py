import re
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

HAIKU = "claude-haiku-4-5-20251001"

client = anthropic.Anthropic()


def run_classifier(ticket: str) -> dict:
    response = client.messages.create(
        model=HAIKU,
        max_tokens=256,
        system=(
            "Classify the support ticket into product_area, severity, and intent. "
            "Respond only in JSON."
        ),
        messages=[{"role": "user", "content": ticket}],
    )
    raw = response.content[0].text.strip()
    # Strip markdown code fences (```json ... ``` or ``` ... ```)
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


def run_crm_enricher(customer_email: str, classification: dict) -> dict:
    # Hardcoded for this exercise — in production this would call a CRM API via an MCP tool
    client.messages.create(
        model=HAIKU,
        max_tokens=64,
        system="Simulate a CRM lookup. Return account_tier, sla_tier, account_manager, contract_value.",
        messages=[
            {
                "role": "user",
                "content": (
                    f"Customer email: {customer_email}\n"
                    f"Classification: {json.dumps(classification)}"
                ),
            }
        ],
    )
    return {
        "account_tier": "Enterprise",
        "sla_tier": "Gold",
        "account_manager": "Jordan Rivera",
        "contract_value": "$120,000",
    }


def run_drafter(ticket: str, classification: dict, crm: dict) -> str:
    context = (
        f"Support ticket:\n{ticket}\n\n"
        f"Classification:\n{json.dumps(classification, indent=2)}\n\n"
        f"CRM data:\n{json.dumps(crm, indent=2)}"
    )
    response = client.messages.create(
        model=HAIKU,
        max_tokens=512,
        system=(
            "Draft a professional first-response email to the customer. "
            "Reference the SLA tier and acknowledge the severity. "
            "Be concise, empathetic, and action-oriented."
        ),
        messages=[{"role": "user", "content": context}],
    )
    return response.content[0].text


def run_validator(draft: str, classification: dict, crm: dict) -> str:
    user_message = (
        f"Draft email to review:\n{draft}\n\n"
        f"Expected product area: {classification.get('product_area')}\n"
        f"Expected severity: {classification.get('severity')}\n"
        f"Account tier: {crm.get('account_tier')}\n"
        f"SLA tier: {crm.get('sla_tier')}\n"
    )
    response = client.messages.create(
        model=HAIKU,
        max_tokens=256,
        system=(
            "You are a quality reviewer for support email drafts. "
            "Check that the draft correctly references the product area, matches the SLA tier "
            "commitments, and maintains a professional tone. "
            "Reply with APPROVED if all checks pass, or list specific issues if not."
        ),
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text
