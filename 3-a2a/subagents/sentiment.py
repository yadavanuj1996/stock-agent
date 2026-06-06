import os
import httpx
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(model="gpt-4o-mini")
    return _llm


def fetch_stocktwits(ticker: str) -> list:
    """Fetch 2 pages (60 messages) per stock — safe for 20 stocks in 2 mins."""
    all_messages = []
    max_id = None
    url_base = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
    PAGES = 2

    for page in range(PAGES):
        try:
            url = url_base if max_id is None else f"{url_base}?max={max_id}"
            response = httpx.get(url, timeout=10)
            if response.status_code != 200:
                break
            data = response.json()
            messages = data.get("messages", [])
            if not messages:
                break
            all_messages.extend(messages)
            max_id = messages[-1]["id"]
        except Exception as e:
            print(f"[sentiment] Page {page+1} failed: {e}")
            break

    return all_messages


def parse_messages(messages: list) -> dict:
    """Extract text and sentiment tags from StockTwits messages."""
    bullish = 0
    bearish = 0
    neutral = 0
    texts = []

    for msg in messages:
        text = msg.get("body", "")
        sentiment = msg.get("entities", {}).get("sentiment", {})
        basic = sentiment.get("basic") if sentiment else None

        if basic == "Bullish":
            bullish += 1
        elif basic == "Bearish":
            bearish += 1
        else:
            neutral += 1

        if text:
            texts.append(text)

    return {
        "bullish": bullish,
        "bearish": bearish,
        "neutral": neutral,
        "texts": texts[:60]
    }


def score_sentiment(ticker: str, parsed: dict) -> dict:
    """Use GPT to extract themes and overall sentiment from messages."""
    if not parsed["texts"]:
        return {
            "overall": "Neutral",
            "confidence": "Low",
            "themes": ["No recent StockTwits activity found"],
            "bullish_count": 0,
            "bearish_count": 0,
            "neutral_count": 0,
            "source": "StockTwits"
        }

    messages_text = "\n".join([f"- {t}" for t in parsed["texts"]])
    total = parsed["bullish"] + parsed["bearish"] + parsed["neutral"]

    response = get_llm().invoke([
        SystemMessage("""
        You are a financial sentiment analyst.
        Analyse the social media messages about a stock and extract:
        1. Overall sentiment: Bullish, Bearish, or Neutral
        2. Confidence: High, Medium, or Low
        3. Key themes: 3-5 bullet points summarising what people are saying

        Be objective. Focus on investment-relevant themes only.
        Ignore memes, jokes, and irrelevant content.
        Return response in this exact format:

        OVERALL: <Bullish/Bearish/Neutral>
        CONFIDENCE: <High/Medium/Low>
        THEMES:
        - <theme 1>
        - <theme 2>
        - <theme 3>
        """),
        HumanMessage(f"""
        Stock: {ticker}
        Total messages: {total}
        Bullish tagged: {parsed['bullish']}
        Bearish tagged: {parsed['bearish']}
        Neutral/untagged: {parsed['neutral']}

        Recent messages:
        {messages_text}
        """)
    ])

    # parse GPT response
    content = response.content
    lines = content.strip().split("\n")

    overall = "Neutral"
    confidence = "Low"
    themes = []

    for line in lines:
        if line.startswith("OVERALL:"):
            overall = line.replace("OVERALL:", "").strip()
        elif line.startswith("CONFIDENCE:"):
            confidence = line.replace("CONFIDENCE:", "").strip()
        elif line.startswith("- "):
            themes.append(line[2:].strip())

    return {
        "overall": overall,
        "confidence": confidence,
        "themes": themes,
        "bullish_count": parsed["bullish"],
        "bearish_count": parsed["bearish"],
        "neutral_count": parsed["neutral"],
        "source": "StockTwits"
    }


def run(ticker: str) -> dict:
    """Run sentiment analysis for a given ticker."""
    print(f"  → Fetching StockTwits data for {ticker}...")
    messages = fetch_stocktwits(ticker)
    print(f"  → Got {len(messages)} messages")

    parsed = parse_messages(messages)
    result = score_sentiment(ticker, parsed)

    print(f"  → Sentiment: {result['overall']} ({result['confidence']} confidence)")
    return result


if __name__ == "__main__":
    result = run("AAPL")
    print(result)