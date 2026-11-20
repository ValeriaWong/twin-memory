"""Observer — logs events and observations into the shared datapack.

It never judges, never invents, never writes stories. Every observation
carries a source and a confidence label (observed vs inferred). Durable
facts are captured by saving the turn (Meko extracts facts from saved user
turns automatically); explicit memory_add is only for corrections the
turn-extraction cannot reach.
"""

from __future__ import annotations

AGENT_ID = "observer"


def log_event(client, event: dict) -> dict:
    """Log one observation event. Returns the stored conversation result."""
    text = (
        f"[{event['event_id']}] {event['text']} "
        f"(source: {event['source']}; confidence: {event['confidence']})"
    )
    conv = client.conversation_create(AGENT_ID, title=f"Observation {event['event_id']}")
    conv_id = conv.get("conversation_id", "mock-conv")
    return client.conversation_add_message(
        conv_id, AGENT_ID, input_text=text, output_text="Logged to the datapack."
    )


def add_durable_fact(client, text: str, metadata: dict | None = None) -> dict:
    """Explicit memory_add — corrections only, not the default path."""
    return client.memory_add(text, AGENT_ID, metadata=metadata or {})
