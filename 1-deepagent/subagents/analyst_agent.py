import json
import uvicorn
import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.routes.fastapi_routes import add_a2a_routes_to_fastapi
from a2a.server.routes.rest_routes import create_rest_routes
from a2a.server.routes.agent_card_routes import create_agent_card_routes
from a2a.types import AgentCard, AgentSkill, AgentCapabilities, AgentInterface, Message, Part, Role

from subagents.analyst import run as analyst_run


class AnalystAgentExecutor(AgentExecutor):

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        payload = json.loads(context.get_user_input())
        research_data = payload["research_data"]
        ticker = payload["ticker"]

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(
                pool, analyst_run, research_data, ticker
            )

        await event_queue.enqueue_event(
            Message(
                role=Role.ROLE_AGENT,
                task_id=context.task_id,
                context_id=context.context_id,
                parts=[Part(text=json.dumps(result))],
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("cancel not supported")


skill = AgentSkill(
    id="analyse_stock",
    name="Analyse Stock",
    description="Runs technical analysis, computes indicators and generates charts for a given ticker",
    tags=["stock", "analysis", "charts", "technical"],
    examples=["Analyse AAPL", "Analyse NVDA"],
)

agent_card = AgentCard(
    name="Analyst Agent",
    description="Performs technical analysis and generates charts for a given stock",
    version="1.0.0",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[skill],
    supported_interfaces=[
        AgentInterface(
            protocol_binding="HTTP+JSON",
            url="http://localhost:8002/",
            protocol_version="1.0",
        )
    ],
)


def serve():
    handler = DefaultRequestHandler(
        agent_executor=AnalystAgentExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )
    app = FastAPI()
    add_a2a_routes_to_fastapi(
        app,
        agent_card_routes=create_agent_card_routes(agent_card),
        rest_routes=create_rest_routes(handler),
    )
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="warning")


if __name__ == "__main__":
    serve()
