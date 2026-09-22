"""Optional real classification via TypeSafe AI's Jev model.

TypeSafe's Jev (https://typesafe.ai) is a "System One Model" API for typed,
structured decisions - not a free-text chat model. It answers named
questions about a piece of "state" using three primitives: Choice
(pick a named alternative), Score (rate against an ordered rubric), and
Noul (yes/no). That maps naturally onto "classify this stock's risk" in a
way a narrative-writing model doesn't, so it's used here for exactly that
judgment call - not for the volatility/drawdown arithmetic, which stays
plain LangGraph nodes, and not for report prose, which stays Jinja2.

Requires a TYPESAFE_API_KEY (see console.typesafe.ai); this module is only
imported when that's set, so `typesafe-sdk` need not be installed otherwise.
"""

# Ordered safest -> riskiest; ScoreAnswer.score is the probability-weighted
# rubric index (e.g. 1.7), so it's normalized to 0-100 below.
_RUBRIC = [
    "Very low risk",
    "Low risk",
    "Moderate risk",
    "High risk",
    "Very high risk",
]


async def classify_with_jev(volatility_pct: float, max_drawdown_pct: float) -> dict:
    """Returns {risk_score, risk_rating, risk_source, risk_confidence}."""
    from typesafe_sdk import AsyncTypeSafeClient, Choice, Score

    async with AsyncTypeSafeClient() as client:
        result = await client.system_one(
            state={
                "volatility_pct_30d": volatility_pct,
                "max_drawdown_pct_30d": max_drawdown_pct,
            },
            questions={
                "risk_rating": Choice(
                    instructions=(
                        "Given this stock's 30-day price volatility (%) and max "
                        "drawdown (%), classify its overall investment risk."
                    ),
                    criteria={
                        "Low": "Low volatility and a shallow drawdown; a conservative holding.",
                        "Medium": "Moderate volatility and drawdown; a balanced risk position.",
                        "High": "High volatility and/or a steep drawdown; a speculative position.",
                    },
                ),
                "risk_score": Score(
                    instructions=(
                        "Rate the overall investment risk using this rubric, "
                        "from safest to riskiest."
                    ),
                    criteria=_RUBRIC,
                ),
            },
        )

    choice_answer = result.choices["risk_rating"]
    score_answer = result.scores["risk_score"]
    risk_score_0_100 = round(score_answer.score / (len(_RUBRIC) - 1) * 100)

    return {
        "risk_score": max(0, min(100, risk_score_0_100)),
        "risk_rating": choice_answer.choice,
        "risk_source": "typesafe-jev",
        "risk_confidence": round(choice_answer.confidence, 2),
    }
