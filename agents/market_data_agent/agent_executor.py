"""Framework-free AgentExecutor: talks directly to the a2a-sdk primitives, no
agent/workflow library in between.
"""
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue

from common.market_data import get_market_data, is_known_ticker, list_known_tickers
from common.messages import agent_reply, read_request_payload


class MarketDataAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        request = read_request_payload(context)
        ticker = str(request.get("ticker", "")).upper()

        if not ticker or not is_known_ticker(ticker):
            await event_queue.enqueue_event(
                agent_reply(
                    {
                        "error": f"unknown ticker: {ticker!r}",
                        "known_tickers": list_known_tickers(),
                    }
                )
            )
            return

        data = get_market_data(ticker)
        await event_queue.enqueue_event(agent_reply(data))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass
