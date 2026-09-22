"""Bridges plain REST calls from the browser to real A2A agents.

This is the only place in the demo where the browser's request turns into
an actual A2A JSON-RPC call - everything above this module talks plain
JSON/REST, everything below it (jev, jev-parallel, the sub-agents) talks A2A.
"""
import json
import time
import uuid

from a2a.client import create_client
from a2a.types.a2a_pb2 import Message, Part, Role, SendMessageRequest


async def ask_agent(url: str, text: str) -> tuple[dict, float]:
    """Send `text` to the agent at `url`, return (parsed JSON reply, elapsed_ms)."""
    client = await create_client(url)
    try:
        request = SendMessageRequest(
            message=Message(
                message_id=str(uuid.uuid4()),
                role=Role.ROLE_USER,
                parts=[Part(text=text)],
            )
        )
        start = time.perf_counter()
        result: dict | None = None
        async for response in client.send_message(request):
            if response.HasField("message"):
                reply_text = "".join(p.text for p in response.message.parts)
                result = json.loads(reply_text)
        elapsed_ms = (time.perf_counter() - start) * 1000
        if result is None:
            raise RuntimeError(f"agent at {url!r} returned no message response")
        return result, elapsed_ms
    finally:
        await client.close()
