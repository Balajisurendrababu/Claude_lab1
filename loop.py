import json
import time
import anthropic
from dotenv import load_dotenv
from tools import classify_ticket

load_dotenv()

TICKET = """From: sarah.johnson@techcorp.com
Subject: Cannot access SSO login — entire team locked out

Our team of 40 has been unable to log in via SSO since 09:00 this morning.
We have a client demo in 3 hours. This is completely blocking us."""

tools = [
    {
        "name": "classify_ticket",
        "description": (
            "Classify a support ticket and return values for the requested fields. "
            "Call this tool one or more times until all three required fields have "
            "confirmed values: product_area, severity, and intent."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticket_text": {
                    "type": "string",
                    "description": "The raw support ticket text to classify.",
                },
                "fields_needed": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "List of field names to classify. "
                        "Valid values: \"product_area\", \"severity\", \"intent\"."
                    ),
                },
            },
            "required": ["ticket_text", "fields_needed"],
        },
    }
]

client = anthropic.Anthropic()

messages = [
    {
        "role": "user",
        "content": (
            "Classify the following support ticket. You must determine all three fields: "
            "product_area, severity, and intent. Use the classify_ticket tool as many times "
            "as needed until you have confirmed values for all three fields. "
            "Do not stop until all three are confirmed.\n\n"
            f"{TICKET}"
        ),
    }
]

iteration = 0
while True:
    iteration += 1
    for attempt in range(5):
        try:
            response = client.messages.create(
                model="claude-opus-4-8",
                max_tokens=1024,
                tools=tools,
                messages=messages,
            )
            break
        except anthropic.OverloadedError:
            wait = 2 ** attempt
            print(f"  [overloaded] retrying in {wait}s...")
            time.sleep(wait)
    else:
        raise RuntimeError("API overloaded after 5 retries — try again later.")
    print(f"\n--- Iteration {iteration} | stop_reason: {response.stop_reason} ---")

    # Append assistant response FIRST before any branching
    messages.append({"role": "assistant", "content": response.content})

    if response.stop_reason == "end_turn":
        final_text = next(
            (block.text for block in response.content if block.type == "text"),
            "(no text response)",
        )
        print(f"\nFinal answer:\n{final_text}")
        break

    if response.stop_reason == "tool_use":
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  Calling {block.name}({json.dumps(block.input)})")
                result = classify_ticket(**block.input)
                print(f"  Result: {result}")
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    }
                )
        messages.append({"role": "user", "content": tool_results})
