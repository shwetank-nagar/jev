"""AgentExecutor that wraps a LangGraph state graph for risk analysis.

Accepts either a `price_history` directly, or a `ticker` (in which case it
generates its own price history via the same shared mock generator that
market-data-agent uses). The ticker path lets this agent be called
independently of market-data-agent's response - e.g. by an orchestrator that
fans both calls out concurrently instead of chaining them.
"""
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue

from common.market_data import get_market_data, is_known_ticker, list_known_tickers
from common.messages import agent_reply, read_request_payload

from .risk_graph import analyze_risk


class RiskAnalysisAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        request = read_request_payload(context)
        price_history = request.get("price_history")

        if not price_history:
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
            price_history = get_market_data(ticker)["price_history"]

        if len(price_history) < 2:
            await event_queue.enqueue_event(
                agent_reply(
                    {"error": "price_history must contain at least 2 data points"}
                )
            )
            return

        result = await analyze_risk(price_history)
        await event_queue.enqueue_event(agent_reply(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass
