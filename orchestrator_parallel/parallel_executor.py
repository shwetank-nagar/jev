"""AgentExecutor for jev-parallel.

Fans market-data and risk-analysis out concurrently - both driven directly
off the ticker, so risk-analysis no longer waits on market-data's response -
then calls report-writer. This is the parallel counterpart to jev's
sequential chain, used to produce a real, measurable timing comparison
rather than a simulated one.
"""
import asyncio
import re

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue

from common.messages import agent_reply
from common.registry import url_for
from orchestrator.remote_agent_connection import RemoteAgentConnection

_TICKER_RE = re.compile(r"[A-Za-z]{1,5}")


class ParallelJevExecutor(AgentExecutor):
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

        market_data, risk_data = await asyncio.gather(
            self._market_data.call({"ticker": ticker}),
            self._risk_analysis.call({"ticker": ticker}),
        )

        if "error" in market_data:
            await event_queue.enqueue_event(agent_reply(market_data))
            return
        if "error" in risk_data:
            await event_queue.enqueue_event(agent_reply(risk_data))
            return

        report = await self._report_writer.call(
            {"market_data": market_data, "risk_data": risk_data}
        )
        await event_queue.enqueue_event(agent_reply(report))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass
