"""AgentExecutor that wraps the Jinja2-based report writer."""
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue

from common.messages import agent_reply, read_request_payload

from .report_template import write_report


class ReportWriterAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        request = read_request_payload(context)
        market_data = request.get("market_data")
        risk_data = request.get("risk_data")

        if not market_data or not risk_data:
            await event_queue.enqueue_event(
                agent_reply({"error": "both market_data and risk_data are required"})
            )
            return

        report_text = write_report(market_data, risk_data)
        await event_queue.enqueue_event(agent_reply({"report": report_text}))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass
