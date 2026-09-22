"""Thin helper for jev to act as an A2A client to one remote agent."""
from a2a.client import create_client
from a2a.types.a2a_pb2 import SendMessageRequest

from common.messages import read_message_payload, user_request


class RemoteAgentConnection:
    """Lazily-connected A2A client wrapper for a single remote agent."""

    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
        self._client = None

    async def _get_client(self):
        if self._client is None:
            self._client = await create_client(self.url)
        return self._client

    async def call(self, payload: dict) -> dict:
        client = await self._get_client()
        request = SendMessageRequest(message=user_request(payload))
        async for response in client.send_message(request):
            if response.HasField("message"):
                return read_message_payload(response.message)
        raise RuntimeError(f"agent {self.name!r} returned no message response")

    async def close(self) -> None:
        if self._client is not None:
            await self._client.close()
