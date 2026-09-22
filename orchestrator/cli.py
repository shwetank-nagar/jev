"""Interactive terminal client for jev - the way a person reaches the
orchestrator agent. This is itself a plain A2A client, calling jev over the
same protocol jev uses to call its own sub-agents.
"""
import asyncio
import uuid

from a2a.client import create_client
from a2a.types.a2a_pb2 import Message, Part, Role, SendMessageRequest

from common.messages import read_message_payload
from common.registry import url_for


async def ask_jev(client, text: str) -> dict:
    request = SendMessageRequest(
        message=Message(
            message_id=str(uuid.uuid4()),
            role=Role.ROLE_USER,
            parts=[Part(text=text)],
        )
    )
    async for response in client.send_message(request):
        if response.HasField("message"):
            return read_message_payload(response.message)
    raise RuntimeError("jev returned no message response")


async def main() -> None:
    jev_url = url_for("jev")
    print(f"Connecting to jev at {jev_url} ...")
    client = await create_client(jev_url)
    print("Connected. Type a ticker symbol (e.g. AAPL) or 'quit' to exit.\n")

    try:
        while True:
            try:
                ticker = input("jev> ").strip()
            except EOFError:
                break
            if not ticker or ticker.lower() in {"quit", "exit"}:
                break

            result = await ask_jev(client, ticker)
            if "report" in result:
                print("\n" + result["report"])
            elif "error" in result:
                print(f"\n[jev] error: {result['error']}")
                if "known_tickers" in result:
                    print(f"[jev] known tickers: {', '.join(result['known_tickers'])}")
            else:
                print(f"\n[jev] unexpected response: {result}")
            print()
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
