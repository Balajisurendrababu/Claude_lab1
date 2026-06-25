import json
from context import TicketContext
from gates import PipelineGateError, gate_classification, gate_enrichment, gate_draft
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

    try:
        print("\n[Classifier]")
        classification = run_classifier(ctx.raw_ticket)
        ctx.product_area = classification.get("product_area")
        ctx.severity = classification.get("severity")
        ctx.intent = classification.get("intent")
        print(json.dumps(classification, indent=2))

        ctx.severity = None  # sabotage: force Gate 1 to fire

        gate_classification(ctx)
        print("Gate 1 passed")

        print("\n[CRM Enricher]")
        crm = run_crm_enricher(ctx.customer_email, classification)
        ctx.account_tier = crm.get("account_tier")
        ctx.sla_tier = crm.get("sla_tier")
        ctx.account_manager = crm.get("account_manager")
        print(json.dumps(crm, indent=2))

        gate_enrichment(ctx)
        print("Gate 2 passed")

        print("\n[Drafter]")
        ctx.draft_response = run_drafter(
            ctx.raw_ticket,
            {"product_area": ctx.product_area, "severity": ctx.severity, "intent": ctx.intent},
            {"account_tier": ctx.account_tier, "sla_tier": ctx.sla_tier, "account_manager": ctx.account_manager},
        )
        print(ctx.draft_response)

        gate_draft(ctx)
        print("Gate 3 passed")

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

    except PipelineGateError as e:
        print(f"\n[PIPELINE BLOCKED] {e}")


if __name__ == "__main__":
    main()
