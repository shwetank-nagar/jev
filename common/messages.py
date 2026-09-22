"""Helpers for passing small JSON payloads inside A2A Message objects.

Every agent in this demo speaks the same convention: a Message carries a
single TextPart whose text is a JSON-encoded object. This keeps the request/
response shape uniform across agents built with different internal libraries.
"""
import json
import uuid

from a2a.server.agent_execution import RequestContext
from a2a.types.a2a_pb2 import Message, Part, Role


def agent_reply(payload: dict) -> Message:
    """Build an agent -> caller reply message carrying a JSON payload."""
    return Message(
        message_id=str(uuid.uuid4()),
        role=Role.ROLE_AGENT,
        parts=[Part(text=json.dumps(payload))],
    )


def user_request(payload: dict) -> Message:
    """Build a caller -> agent request message carrying a JSON payload."""
    return Message(
        message_id=str(uuid.uuid4()),
        role=Role.ROLE_USER,
        parts=[Part(text=json.dumps(payload))],
    )


def read_request_payload(context: RequestContext) -> dict:
    """Parse the JSON payload out of the incoming request context."""
    return json.loads(context.get_user_input())


def read_message_payload(message: Message) -> dict:
    """Parse the JSON payload out of a Message (e.g. a StreamResponse.message)."""
    text = "".join(part.text for part in message.parts)
    return json.loads(text)
