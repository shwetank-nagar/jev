"""Jinja2-based report writer.

Renders a narrative investment note from combined market-data + risk-analysis
results, plus a simple rule-based recommendation. This is the third distinct
library used across the sample agents (framework-free, LangGraph, Jinja2).
"""
from jinja2 import Template

_TEMPLATE = Template(
    "Investment Research Note - {{ ticker }} (as of {{ as_of }})\n"
    "{{ '=' * 60 }}\n"
    "Current price: ${{ '%.2f'|format(current_price) }} "
    "({{ '%+.2f'|format(day_change_pct) }}% today)\n"
    "30-day volatility: {{ volatility_pct }}%  |  Max drawdown: {{ max_drawdown_pct }}%\n"
    "Risk rating: {{ risk_rating }} ({{ risk_score }}/100)"
    "{% if risk_source == 'typesafe-jev' %}"
    " [via TypeSafe Jev, confidence {{ risk_confidence }}]"
    "{% elif risk_source == 'typesafe-jev-via-vercel-gateway' %}"
    " [via TypeSafe Jev (Vercel AI Gateway), confidence {{ risk_confidence }}]"
    "{% endif %}\n"
    "\n"
    "Recommendation: {{ recommendation }}\n"
)


def _recommend(day_change_pct: float, risk_score: int) -> str:
    if risk_score >= 70:
        return "High risk - proceed with caution and consider a small position size."
    if risk_score < 35 and day_change_pct > 0:
        return "Favorable entry point - low risk with positive short-term momentum."
    if risk_score < 35:
        return "Low risk overall, but no strong momentum signal today - hold and monitor."
    return "Moderate risk - suitable for a balanced position, monitor volatility."


def write_report(market_data: dict, risk_data: dict) -> str:
    recommendation = _recommend(market_data["day_change_pct"], risk_data["risk_score"])
    return _TEMPLATE.render(
        ticker=market_data["ticker"],
        as_of=market_data["as_of"],
        current_price=market_data["current_price"],
        day_change_pct=market_data["day_change_pct"],
        volatility_pct=risk_data["volatility_pct"],
        max_drawdown_pct=risk_data["max_drawdown_pct"],
        risk_score=risk_data["risk_score"],
        risk_rating=risk_data["risk_rating"],
        risk_source=risk_data.get("risk_source"),
        risk_confidence=risk_data.get("risk_confidence"),
        recommendation=recommendation,
    )
