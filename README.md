# Claude Ticket Classifier — Agentic Pipeline Lab

A step-by-step lab building a support-ticket classification pipeline using the Anthropic Python SDK. Covers single-agent tool use, multi-subagent orchestration, shared context, and programmatic pipeline gates.

---

## Project Structure

| File | Purpose |
|---|---|
| `tools.py` | `classify_ticket()` tool with simulated random classification values |
| `loop.py` | Manual agentic loop — single Claude agent with tool use (Exercise 1) |
| `subagents.py` | Four Haiku subagent functions: Classifier, CRM Enricher, Drafter, Validator |
| `coordinator.py` | Simple sequential pipeline calling all four subagents |
| `context.py` | `TicketContext` dataclass — shared state object for the pipeline |
| `gates.py` | `PipelineGateError` and three gate functions blocking premature stage execution |
| `coordinator_v2.py` | Pipeline refactored to use `TicketContext` |
| `coordinator_v3.py` | Pipeline with programmatic gates between every stage |
| `coordinator_v3_sabotage.py` | Gate-failure demo — deliberately triggers Gate 1 |

---

## Setup

**1. Create and activate a virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
```

**2. Install dependencies**
```bash
pip install anthropic python-dotenv
```

**3. Add your API key**

Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Running the Exercises

**Exercise 1 — Single agent with tool use**
```bash
python loop.py
```
Runs a `while True` agentic loop. Claude calls `classify_ticket` via tool use until all three fields (`product_area`, `severity`, `intent`) are confirmed, then stops.

**Exercise 2 — Multi-subagent pipeline**
```bash
python coordinator.py
```
Calls Classifier → CRM Enricher → Drafter → Validator in sequence, printing each subagent's output.

**Exercise 3 — Shared context object**
```bash
python coordinator_v2.py
```
Same pipeline but all state flows through a single `TicketContext` dataclass. Prints the fully populated context at the end.

**Exercise 4 — Programmatic gates**
```bash
# Full clean run (all gates pass)
python coordinator_v3.py

# Gate failure demo (Gate 1 fires, pipeline stops immediately)
python coordinator_v3_sabotage.py
```

---

## Architecture

### Exercise 1 — Agentic Loop
```
User prompt
    │
    ▼
┌─────────────────────────────┐
│  while True                 │
│  Claude (claude-opus-4-8)   │
│    ├── tool_use → classify_ticket() → tool_result
│    └── end_turn → print final answer, break
└─────────────────────────────┘
```

### Exercise 2–4 — Multi-Subagent Pipeline
```
TicketContext (ticket_id, raw_ticket, customer_email)
       │
       ▼
[Classifier]        claude-haiku-4-5  →  product_area, severity, intent
       │
  Gate 1 ──✗──► PipelineGateError (stops pipeline)
       │
       ▼
[CRM Enricher]      claude-haiku-4-5  →  account_tier, sla_tier, account_manager
       │
  Gate 2 ──✗──► PipelineGateError
       │
       ▼
[Drafter]           claude-haiku-4-5  →  draft_response
       │
  Gate 3 ──✗──► PipelineGateError
       │
       ▼
[Validator]         claude-haiku-4-5  →  validation_result (APPROVED / issues)
```

---

## Models Used

| Role | Model |
|---|---|
| Agentic loop (Exercise 1) | `claude-opus-4-8` |
| All subagents (Exercise 2–4) | `claude-haiku-4-5-20251001` |

---

## Key Concepts Demonstrated

- **Tool use / function calling** — registering tools with JSON Schema and handling `tool_use` stop reason
- **Manual agentic loop** — `while True` with `stop_reason` branching; appending assistant response before tool results
- **Explicit context passing** — each subagent receives only the fields it needs, not the full context object
- **Dataclass as pipeline state** — `TicketContext` enforces required fields at construction time vs. silent dict failures
- **Programmatic gates** — hard stops enforced by Python, not prompt instructions the model can ignore
