import yaml
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import sys
import yfinance as yf

load_dotenv()

# load skill instructions
ANALYSIS_SKILL = (Path(__file__).parent.parent / "skills" / "stock-analysis" / "SKILL.md").read_text()

# load subagent config
CONFIG_PATH = Path(__file__).parent.parent / "subagents.yaml"
CONFIG = yaml.safe_load(CONFIG_PATH.read_text())
MODEL = CONFIG["subagents"]["analyst"]["model"]

# add sandbox to path
sys.path.append(str(Path(__file__).parent.parent))
from sandbox.executor import execute_code

# initialise LLM (text analysis only — no tools needed)
llm = ChatOpenAI(model=MODEL)

# pre-written chart functions injected into every sandbox run.
_BOILERPLATE = """\
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

plt.style.use('dark_background')

df = pd.read_csv('/data/stock_data.csv', index_col=0, parse_dates=True)
df.index = pd.to_datetime(df.index, utc=True).tz_convert(None)
df.columns = [col.strip() for col in df.columns]
print("Loaded stock data:", df.shape)


def plot_price_ma(df, ticker):
    df1y = pd.read_csv('/data/stock_data_1y.csv', index_col=0, parse_dates=True)
    df1y.index = pd.to_datetime(df1y.index, utc=True).tz_convert(None)
    df1y.columns = [col.strip() for col in df1y.columns]
    ma50 = df1y['Close'].rolling(50).mean()
    ma200 = df1y['Close'].rolling(200).mean()
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.plot(df1y.index, df1y['Close'], color='#00ff88', linewidth=1.5, label='Price')
    ax.plot(df1y.index, ma50, color='#ffaa00', linewidth=1, label='50 MA')
    ax.plot(df1y.index, ma200, color='#ff4444', linewidth=1, label='200 MA')
    ax.set_title(f'{ticker} Price + Moving Averages', fontsize=14)
    ax.set_xlabel('Date')
    ax.set_ylabel('Price ($)')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()
    plt.tight_layout()
    path = f'/output/{ticker}_price_ma.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_rsi(df, ticker, period=14):
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.plot(df.index, rsi, color='#aa88ff', linewidth=1.5, label=f'RSI ({period})')
    ax.axhline(70, color='#ff4444', linestyle='--', linewidth=1, label='Overbought (70)')
    ax.axhline(30, color='#00ff88', linestyle='--', linewidth=1, label='Oversold (30)')
    ax.fill_between(df.index, rsi, 70, where=(rsi >= 70), alpha=0.3, color='#ff4444')
    ax.fill_between(df.index, rsi, 30, where=(rsi <= 30), alpha=0.3, color='#00ff88')
    ax.set_ylim(0, 100)
    ax.set_title(f'{ticker} RSI ({period})', fontsize=14)
    ax.set_xlabel('Date')
    ax.set_ylabel('RSI')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()
    plt.tight_layout()
    path = f'/output/{ticker}_rsi.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_macd(df, ticker, fast=12, slow=26, signal=9):
    ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    colors = ['#00ff88' if v >= 0 else '#ff4444' for v in histogram]
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.plot(df.index, macd, color='#00aaff', linewidth=1.5, label='MACD')
    ax.plot(df.index, signal_line, color='#ffaa00', linewidth=1, label='Signal')
    ax.bar(df.index, histogram, color=colors, alpha=0.6, label='Histogram', width=1)
    ax.axhline(0, color='white', linewidth=0.5)
    ax.set_title(f'{ticker} MACD ({fast},{slow},{signal})', fontsize=14)
    ax.set_xlabel('Date')
    ax.set_ylabel('MACD')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()
    plt.tight_layout()
    path = f'/output/{ticker}_macd.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_volume(df, ticker):
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.bar(df.index, df['Volume'], color='#4488ff', alpha=0.7, width=1)
    ax.set_title(f'{ticker} Trading Volume', fontsize=14)
    ax.set_xlabel('Date')
    ax.set_ylabel('Volume')
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()
    plt.tight_layout()
    path = f'/output/{ticker}_volume.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


def plot_benchmark(df, ticker):
    sp500_path = '/data/sp500_data.csv'
    if not os.path.exists(sp500_path):
        print("S&P 500 data not available, skipping benchmark chart")
        return
    sp500_df = pd.read_csv(sp500_path, index_col=0, parse_dates=True)
    sp500_df.index = pd.to_datetime(sp500_df.index, utc=True).tz_convert(None)
    sp500_df.columns = [col.strip() for col in sp500_df.columns]
    stock_norm = df['Close'] / df['Close'].iloc[0] * 100
    sp500_norm = sp500_df['Close'] / sp500_df['Close'].iloc[0] * 100
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.plot(df.index, stock_norm, color='#00ff88', linewidth=1.5, label=ticker)
    ax.plot(sp500_df.index, sp500_norm, color='#ff4444', linewidth=1.5, label='S&P 500')
    ax.axhline(100, color='white', linestyle='--', linewidth=0.5)
    ax.set_title(f'{ticker} vs S&P 500 (6 Month Normalized)', fontsize=14)
    ax.set_xlabel('Date')
    ax.set_ylabel('Normalized Price (Base = 100)')
    ax.legend()
    ax.grid(alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()
    plt.tight_layout()
    path = f'/output/{ticker}_benchmark.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {path}")


"""

def _compute_indicators(csv_data: str, csv_1y_data: str, sp500_return: float) -> str:
    """Compute technical indicators from CSV and return as formatted string for LLM."""
    import io
    import pandas as pd

    # 6-month data — RSI, MACD, stock return (unchanged)
    df = pd.read_csv(io.StringIO(csv_data), index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index, utc=True).tz_convert(None)
    df.columns = [c.strip() for c in df.columns]
    close = df['Close']

    delta  = close.diff()
    gain   = delta.clip(lower=0).rolling(14).mean()
    loss   = (-delta.clip(upper=0)).rolling(14).mean()
    rsi    = (100 - 100 / (1 + gain / loss)).iloc[-1]

    ema12      = close.ewm(span=12, adjust=False).mean()
    ema26      = close.ewm(span=26, adjust=False).mean()
    macd_line  = (ema12 - ema26).iloc[-1]
    signal     = (ema12 - ema26).ewm(span=9, adjust=False).mean().iloc[-1]

    stock_return = ((close.iloc[-1] - close.iloc[0]) / close.iloc[0]) * 100

    # 1-year data — MA50 and MA200 only
    df1y = pd.read_csv(io.StringIO(csv_1y_data), index_col=0, parse_dates=True)
    df1y.index = pd.to_datetime(df1y.index, utc=True).tz_convert(None)
    df1y.columns = [c.strip() for c in df1y.columns]
    ma50  = df1y['Close'].rolling(50).mean().iloc[-1]
    ma200 = df1y['Close'].rolling(200).mean().iloc[-1]
    trend        = "Uptrend" if close.iloc[-1] > ma200 else "Downtrend"
    ma_signal    = "Golden Cross (bullish)" if ma50 > ma200 else "Death Cross (bearish)"
    macd_signal  = "Bullish (MACD above signal)" if macd_line > signal else "Bearish (MACD below signal)"
    vs_benchmark = f"{'Outperforming' if stock_return > sp500_return else 'Underperforming'} by {abs(stock_return - sp500_return):.2f}%"

    return f"""
50 Day MA:      ${ma50:.2f}
200 Day MA:     ${ma200:.2f}
Trend:          {trend} (price {'above' if close.iloc[-1] > ma200 else 'below'} 200 MA)
MA Signal:      {ma_signal}
RSI (14):       {rsi:.1f} ({'Overbought' if rsi > 70 else 'Oversold' if rsi < 30 else 'Neutral'})
MACD Line:      {macd_line:.4f}
Signal Line:    {signal:.4f}
MACD Signal:    {macd_signal}
6 Month Return: {stock_return:.2f}%
S&P 500 Return: {sp500_return:.2f}%
vs Benchmark:   {vs_benchmark}
"""


# chart calls injected after the boilerplate — always generate all 5
_CHART_CALLS = """\
plot_price_ma(df, "{ticker}")
plot_rsi(df, "{ticker}")
plot_macd(df, "{ticker}")
plot_volume(df, "{ticker}")
plot_benchmark(df, "{ticker}")
"""


def run(research_data: dict, ticker: str) -> dict:
    """Run the analyst agent on research data for a given ticker."""

    csv_data = research_data.get("csv", "") if isinstance(research_data, dict) else ""
    csv_1y_data = research_data.get("csv_1y", "") if isinstance(research_data, dict) else ""
    summary = research_data.get("summary", "") if isinstance(research_data, dict) else str(research_data)

    # step 1 — pre-fetch S&P 500 for benchmark chart
    print("  → Fetching S&P 500 benchmark data...")
    sp500_history = yf.Ticker("^GSPC").history(period="6mo")
    sp500_csv_data = sp500_history.to_csv()
    sp500_return = ((sp500_history['Close'].iloc[-1] - sp500_history['Close'].iloc[0])
                    / sp500_history['Close'].iloc[0]) * 100

    # step 2 — generate all charts directly (no LLM involvement)
    print("  → Generating charts...")
    chart_code = _BOILERPLATE + _CHART_CALLS.format(ticker=ticker)
    result = execute_code(chart_code, csv_data=csv_data, sp500_csv_data=sp500_csv_data, csv_1y_data=csv_1y_data)
    charts = result["charts"] if result["success"] else []
    if not result["success"]:
        print(f"  → Chart error: {result['error']}")
    else:
        print(f"  → Charts generated: {len(charts)}")

    # step 3 — LLM writes text analysis only
    print("  → Running text analysis...")
    indicators = _compute_indicators(csv_data, csv_1y_data, sp500_return)
    response = llm.invoke([
        SystemMessage(f"""
        You are a stock analyst. Write a technical analysis of the stock.

        {ANALYSIS_SKILL}

        Charts have already been generated separately.
        """),
        HumanMessage(f"""
        Analyse {ticker} based on the following data:

        ## Research Summary
        {summary}

        ## Calculated Technical Indicators
        {indicators}
        """)
    ])

    return {
        "analysis": response.content,
        "charts": charts
    }
