try:
    from config import load_config
    load_config()
except Exception as e:
    print(f"[warning] Could not load config from Parameter Store: {e}")

import os
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

from subagents.researcher import run as researcher_run

AGENT_HOST = os.getenv("AGENT_HOST", "localhost")


class ResearcherAgentExecutor(AgentExecutor):

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        ticker = context.get_user_input().strip().upper()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            research_data = await loop.run_in_executor(pool, researcher_run, ticker)

        await event_queue.enqueue_event(
            Message(
                role=Role.ROLE_AGENT,
                task_id=context.task_id,
                context_id=context.context_id,
                parts=[Part(text=json.dumps(research_data))],
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("cancel not supported")


skill = AgentSkill(
    id="research_stock",
    name="Research Stock",
    description="Fetches stock price, history, news and fundamentals for a given ticker symbol",
    tags=["stock", "research", "finance"],
    examples=["AAPL", "NVDA", "TSLA"],
)

agent_card = AgentCard(
    name="Researcher Agent",
    description="Fetches comprehensive stock research data for a given ticker",
    version="1.0.0",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[skill],
    supported_interfaces=[
        AgentInterface(
            protocol_binding="HTTP+JSON",
            url=f"http://{AGENT_HOST}:8001/",
            protocol_version="1.0",
        )
    ],
)


def serve():
    handler = DefaultRequestHandler(
        agent_executor=ResearcherAgentExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )
    app = FastAPI()
    add_a2a_routes_to_fastapi(
        app,
        agent_card_routes=create_agent_card_routes(agent_card),
        rest_routes=create_rest_routes(handler),
    )
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="warning")


if __name__ == "__main__":
    serve()
