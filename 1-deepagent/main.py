import yaml
import json
import asyncio
import uuid
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import httpx
from a2a.client import create_client, ClientConfig
from a2a.types import SendMessageRequest, Message, Part, Role

load_dotenv()

AGENTS_MD = (Path(__file__).parent / "AGENTS.md").read_text()
CONFIG = yaml.safe_load((Path(__file__).parent / "subagents.yaml").read_text())
ORCHESTRATOR_MODEL = CONFIG["orchestrator"]["model"]
llm = ChatOpenAI(model=ORCHESTRATOR_MODEL)


def extract_ticker(user_input: str) -> str:
    response = llm.invoke([
        SystemMessage("Extract the stock ticker symbol from the user input. Return ONLY the ticker symbol in uppercase. Nothing else."),
        HumanMessage(user_input)
    ])
    return response.content.strip().upper()


def _build_request(text: str) -> SendMessageRequest:
    return SendMessageRequest(
        message=Message(
            message_id=str(uuid.uuid4()),
            role=Role.ROLE_USER,
            parts=[Part(text=text)],
        )
    )


def _extract_text(chunk) -> str:
    if chunk.HasField("message"):
        return chunk.message.parts[0].text
    if chunk.HasField("task") and chunk.task.history:
        return chunk.task.history[-1].parts[0].text
    return ""


async def _run_async(ticker: str) -> tuple[dict, dict]:
    """Run researcher then analyst in a single event loop."""
    config = ClientConfig(
        supported_protocol_bindings=["HTTP+JSON"],
        httpx_client=httpx.AsyncClient(timeout=300.0),
    )

    print(f"\n[Researcher] Fetching data for {ticker}...")
    researcher = await create_client("http://localhost:8001", client_config=config)
    research_data = None
    async for chunk in researcher.send_message(_build_request(ticker)):
        text = _extract_text(chunk)
        if text:
            research_data = json.loads(text)
            break
    if research_data is None:
        raise RuntimeError("Researcher agent returned no result")
    print(f"[Researcher] Done. Summary length: {len(research_data['summary'])} chars")

    print(f"\n[Analyst] Analysing {ticker}...")
    analyst = await create_client("http://localhost:8002", client_config=config)
    payload = json.dumps({"research_data": research_data, "ticker": ticker})
    analysis_result = None
    async for chunk in analyst.send_message(_build_request(payload)):
        text = _extract_text(chunk)
        if text:
            analysis_result = json.loads(text)
            break
    if analysis_result is None:
        raise RuntimeError("Analyst agent returned no result")
    print("[Analyst] Done.")

    return research_data, analysis_result


def run(user_input: str) -> dict:
    print("\n" + "="*60)
    print(f"USER: {user_input}")
    print("="*60)

    print("\n[Orchestrator] Extracting ticker symbol...")
    ticker = extract_ticker(user_input)
    print(f"[Orchestrator] Ticker identified: {ticker}")

    research_data, analysis_result = asyncio.run(_run_async(ticker))

    print("\n[Orchestrator] Compiling final response...")
    final_response = llm.invoke([
        SystemMessage(f"""
        You are a stock research orchestrator.
        Follow these guidelines:
        {AGENTS_MD}
        """),
        HumanMessage(f"""
        The user asked: {user_input}

        Research data gathered:
        {research_data["summary"]}

        Analysis completed:
        {analysis_result['analysis']}

        Charts already generated: {len(analysis_result['charts'])} charts (price+MA, RSI, MACD, volume, benchmark vs S&P 500)

        Compile a clean, well structured final response for the user.
        Note: Charts have been generated and will be displayed to the user automatically. Do not say charts are pending.
        """)
    ])

    return {
        "response": final_response.content,
        "charts": analysis_result["charts"],
        "ticker": ticker,
    }
