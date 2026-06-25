import json
from context import TicketContext
from subagents import run_classifier, run_crm_enricher, run_drafter, run_validator

TICKET = """From: [REDACTED_EMAIL_ADDRESS_2]
Subject: Cannot access SSO login — entire team locked out

Our team of 40 has been unable to log in via SSO since 09:00 this morning.
We have a client demo in 3 hours. This is completely blocking us."""

CUSTOMER_EMAIL = "[REDACTED_EMAIL_ADDRESS_2]"


def main():
    ctx = TicketContext(
        ticket_id="TKT-001",
        raw_ticket=TICKET,
        customer_email=CUSTOMER_EMAIL,
    )

    print("=" * 60)

    print("\n[Classifier]")
    classification = run_classifier(ctx.raw_ticket)
    ctx.product_area = classification.get("product_area")
    ctx.severity = classification.get("severity")
    ctx.intent = classification.get("intent")
    print(json.dumps(classification, indent=2))

    print("\n[CRM Enricher]")
    crm = run_crm_enricher(ctx.customer_email, classification)
    ctx.account_tier = crm.get("account_tier")
    ctx.sla_tier = crm.get("sla_tier")
    ctx.account_manager = crm.get("account_manager")
    print(json.dumps(crm, indent=2))

    print("\n[Drafter]")
    ctx.draft_response = run_drafter(
        ctx.raw_ticket,
        {"product_area": ctx.product_area, "severity": ctx.severity, "intent": ctx.intent},
        {"account_tier": ctx.account_tier, "sla_tier": ctx.sla_tier, "account_manager": ctx.account_manager},
    )
    print(ctx.draft_response)

    print("\n[Validator]")
    ctx.validation_result = run_validator(
        ctx.draft_response,
        {"product_area": ctx.product_area, "severity": ctx.severity, "intent": ctx.intent},
        {"account_tier": ctx.account_tier, "sla_tier": ctx.sla_tier, "account_manager": ctx.account_manager},
    )
    print(ctx.validation_result)

    print("\n" + "=" * 60)
    print("\n[Final TicketContext]")
    print(ctx)


if __name__ == "__main__":
    main()
