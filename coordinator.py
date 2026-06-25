import json
from subagents import run_classifier, run_crm_enricher, run_drafter, run_validator

TICKET = """From: [REDACTED_EMAIL_ADDRESS_2]
Subject: Cannot access SSO login — entire team locked out

Our team of 40 has been unable to log in via SSO since 09:00 this morning.
We have a client demo in 3 hours. This is completely blocking us."""

CUSTOMER_EMAIL = "[REDACTED_EMAIL_ADDRESS_2]"


def main():
    print("=" * 60)

    print("\n[Classifier]")
    classification = run_classifier(TICKET)
    print(json.dumps(classification, indent=2))

    print("\n[CRM Enricher]")
    crm = run_crm_enricher(CUSTOMER_EMAIL, classification)
    print(json.dumps(crm, indent=2))

    print("\n[Drafter]")
    draft = run_drafter(TICKET, classification, crm)
    print(draft)

    print("\n[Validator]")
    verdict = run_validator(draft, classification, crm)
    print(verdict)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
