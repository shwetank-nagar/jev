"""In-memory registry of A2A agent cards, seeded with the 5 local demo
agents and open to registering any other agent by URL.
"""
import httpx

from a2a.client import A2ACardResolver
from a2a.server.request_handlers.response_helpers import agent_card_to_dict

from common.registry import url_for

# url -> {"label": str, "card": dict | None, "error": str | None}
REGISTRY: dict[str, dict] = {}

_SEED = {
    "jev": "jev (sequential orchestrator)",
    "jev_parallel": "jev-parallel (parallel orchestrator)",
    "single_prompt": "single-prompt-agent (baseline)",
    "market_data": "market-data-agent",
    "risk_analysis": "risk-analysis-agent",
    "report_writer": "report-writer-agent",
}


def seed_registry() -> None:
    for key, label in _SEED.items():
        REGISTRY[url_for(key)] = {"label": label, "card": None, "error": None}


async def fetch_card(url: str) -> dict:
    async with httpx.AsyncClient() as hc:
        resolver = A2ACardResolver(hc, url)
        card = await resolver.get_agent_card()
        return agent_card_to_dict(card)


async def refresh_all() -> None:
    for url, entry in REGISTRY.items():
        try:
            entry["card"] = await fetch_card(url)
            entry["error"] = None
        except Exception as exc:  # noqa: BLE001 - best-effort warmup
            entry["card"] = None
            entry["error"] = str(exc)


def list_agents() -> list[dict]:
    return [
        {"url": url, "label": entry["label"], "card": entry["card"], "error": entry["error"]}
        for url, entry in REGISTRY.items()
    ]


async def register(url: str, label: str | None) -> dict:
    if not url.endswith("/"):
        url = url + "/"
    card = await fetch_card(url)
    REGISTRY[url] = {"label": label or card.get("name", url), "card": card, "error": None}
    return {"url": url, **REGISTRY[url]}


def unregister(url: str) -> bool:
    return REGISTRY.pop(url, None) is not None
