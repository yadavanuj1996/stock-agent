import yaml
import asyncio
import yfinance as yf
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
from dotenv import load_dotenv

load_dotenv()

SKILL = (Path(__file__).parent.parent / "skills" / "stock-research" / "SKILL.md").read_text()

CONFIG = yaml.safe_load((Path(__file__).parent.parent / "subagents.yaml").read_text())
MODEL = CONFIG["subagents"]["researcher"]["model"]

MCP_URL = "http://localhost:8050/mcp"

llm = ChatOpenAI(model=MODEL)


async def _run_async(ticker: str) -> dict:
    # CSV fetched directly — not through MCP
    stock = yf.Ticker(ticker)
    csv_data = stock.history(period="6mo").to_csv()
    csv_1y_data = stock.history(period="1y").to_csv()

    async with streamablehttp_client(MCP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # discover tools dynamically from MCP server — no hardcoded definitions
            mcp_tools = (await session.list_tools()).tools
            lc_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description or t.name,
                        "parameters": t.inputSchema,
                    },
                }
                for t in mcp_tools
            ]

            llm_with_tools = llm.bind_tools(lc_tools)

            messages = [
                SystemMessage(f"""
                You are a stock research agent.
                Follow these instructions carefully:
                {SKILL}
                """),
                HumanMessage(f"Research the stock with ticker symbol: {ticker}"),
            ]

            response = None
            while True:
                response = await llm_with_tools.ainvoke(messages)
                messages.append(response)
                if not response.tool_calls:
                    break
                for tc in response.tool_calls:
                    result = await session.call_tool(tc["name"], tc["args"])
                    content = result.content[0].text if result.content else ""
                    messages.append({
                        "role": "tool",
                        "content": content,
                        "tool_call_id": tc["id"],
                    })

    return {
        "summary": response.content if response else "",
        "csv": csv_data,
        "csv_1y": csv_1y_data,
        "ticker": ticker,
    }


def run(ticker: str) -> dict:
    return asyncio.run(_run_async(ticker))
