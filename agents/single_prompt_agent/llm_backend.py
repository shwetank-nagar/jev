"""Runs the single-prompt baseline: one completion asked to reason about
market data, assess risk, AND write the narrative report - all in one shot -
instead of jev's pipeline of fast, specialized, non-LLM agents. This is the
baseline jev/jev-parallel are compared against on the Compare tab.

Uses a real Anthropic completion (the fast Haiku model, so the comparison is
charitable to the baseline) if ANTHROPIC_API_KEY is set; otherwise simulates
a representative single-large-completion latency and produces an equivalent
report from the same underlying data, clearly labeled as simulated so the UI
never misrepresents it as a real model call.
"""
import asyncio
import os
import random

MODEL = "claude-haiku-4-5-20251001"

_PROMPT_TEMPLATE = """You are a financial analyst. Given this raw market data for {ticker}, \
in a single response: (1) assess volatility and drawdown risk on a 0-100 scale, \
(2) rate the risk as Low/Medium/High, and (3) write a short investment research \
note with a recommendation - all in one shot, the way a single unstructured \
prompt would, rather than as separate specialized steps.

Market data:
current_price: {current_price}
day_change_pct: {day_change_pct}
price_history: {price_history}
as_of: {as_of}

Respond with just the research note as plain text, no preamble."""


async def _call_anthropic(market_data: dict) -> str:
    from anthropic import AsyncAnthropic  # optional dependency, imported lazily

    client = AsyncAnthropic()
    prompt = _PROMPT_TEMPLATE.format(**market_data)
    response = await client.messages.create(
        model=MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(
        block.text for block in response.content if block.type == "text"
    ).strip()


def _simulate(market_data: dict) -> str:
    # Mirrors jev's own computation so the CONTENT is comparable - only the
    # single-prompt agent's TIMING is meant to differ. A monolithic call
    # reasoning through the whole task at once is slower than jev's
    # decomposed pipeline of fast specialized steps; this isn't a claim
    # about report quality.
    from agents.risk_analysis_agent.risk_graph import analyze_risk
    from agents.report_writer_agent.report_template import write_report

    risk_data = analyze_risk(market_data["price_history"])
    report = write_report(market_data, risk_data)
    return report + "\n\n(simulated single-prompt output - no ANTHROPIC_API_KEY set)"


async def run_single_prompt(market_data: dict) -> tuple[str, bool]:
    """Returns (report_text, used_real_llm)."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            report = await _call_anthropic(market_data)
            return report, True
        except Exception:
            pass  # fall through to the simulated path on any error

    await asyncio.sleep(random.uniform(2.0, 4.0))
    return _simulate(market_data), False
