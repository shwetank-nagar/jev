"""AgentExecutor for jev: the orchestrator/host agent.

On each incoming request, jev acts as an A2A client to three remote agents
in sequence - market-data, risk-analysis, report-writer, each built with a
different library - and returns the synthesized report as its own reply.
"""
import re

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue

from common.messages import agent_reply
from common.registry import url_for

from .remote_agent_connection import RemoteAgentConnection

_TICKER_RE = re.compile(r"[A-Za-z]{1,5}")


class JevExecutor(AgentExecutor):
    def __init__(self) -> None:
        self._market_data = RemoteAgentConnection(
            "market-data-agent", url_for("market_data")
        )
        self._risk_analysis = RemoteAgentConnection(
            "risk-analysis-agent", url_for("risk_analysis")
        )
        self._report_writer = RemoteAgentConnection(
            "report-writer-agent", url_for("report_writer")
        )

    @staticmethod
    def _extract_ticker(user_text: str) -> str | None:
        match = _TICKER_RE.search(user_text.strip())
        return match.group(0).upper() if match else None

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        ticker = self._extract_ticker(context.get_user_input())

        if not ticker:
            await event_queue.enqueue_event(
                agent_reply({"error": "please provide a ticker symbol, e.g. 'AAPL'"})
            )
            return

        market_data = await self._market_data.call({"ticker": ticker})
        if "error" in market_data:
            await event_queue.enqueue_event(agent_reply(market_data))
            return

        risk_data = await self._risk_analysis.call(
            {"price_history": market_data["price_history"]}
        )
        if "error" in risk_data:
            await event_queue.enqueue_event(agent_reply(risk_data))
            return

        report = await self._report_writer.call(
            {"market_data": market_data, "risk_data": risk_data}
        )
        await event_queue.enqueue_event(agent_reply(report))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass
