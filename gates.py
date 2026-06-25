from context import TicketContext


class PipelineGateError(Exception):
    pass


def gate_classification(ctx: TicketContext) -> None:
    if ctx.classification_complete():
        return
    missing = [
        field for field, value in [
            ("product_area", ctx.product_area),
            ("severity", ctx.severity),
            ("intent", ctx.intent),
        ]
        if value is None
    ]
    raise PipelineGateError(
        f"[{ctx.ticket_id}] Classification gate failed — missing fields: {missing}. "
        "Rerun the Classifier before proceeding."
    )


def gate_enrichment(ctx: TicketContext) -> None:
    if ctx.enrichment_complete():
        return
    missing = [
        field for field, value in [
            ("account_tier", ctx.account_tier),
            ("sla_tier", ctx.sla_tier),
        ]
        if value is None
    ]
    raise PipelineGateError(
        f"[{ctx.ticket_id}] Enrichment gate failed — missing fields: {missing}. "
        "Rerun the CRM Enricher before proceeding."
    )


def gate_draft(ctx: TicketContext) -> None:
    if ctx.draft_complete():
        return
    raise PipelineGateError(
        f"[{ctx.ticket_id}] Draft gate failed — draft_response is None. "
        "Rerun the Drafter before proceeding."
    )
