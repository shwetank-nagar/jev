"""AgentExecutor for the single-prompt baseline.

Given a ticker, does the entire pipeline in one shot (one LLM completion, or
a simulated equivalent) instead of delegating to specialized agents the way
jev does. This is the "just a prompt doing the same thing" comparison point.
"""
import re

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue

from common.market_data import get_market_data, is_known_ticker, list_known_tickers
from common.messages import agent_reply

from .llm_backend import run_single_prompt

_TICKER_RE = re.compile(r"[A-Za-z]{1,5}")


class SinglePromptAgentExecutor(AgentExecutor):
    @staticmethod
    def _extract_ticker(user_text: str) -> str | None:
        match = _TICKER_RE.search(user_text.strip())
        return match.group(0).upper() if match else None

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        ticker = self._extract_ticker(context.get_user_input())

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

        market_data = get_market_data(ticker)
        report, used_real_llm = await run_single_prompt(market_data)
        await event_queue.enqueue_event(
            agent_reply({"report": report, "used_real_llm": used_real_llm})
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass
