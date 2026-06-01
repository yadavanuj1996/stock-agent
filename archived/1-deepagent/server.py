from mcp.server.fastmcp import FastMCP
import yfinance as yf

mcp = FastMCP("Stock Research Server", host="0.0.0.0", port=8050)


@mcp.tool()
def get_stock_price(ticker: str) -> str:
    """Get current stock price and basic info for a given ticker symbol."""
    info = yf.Ticker(ticker).info
    return f"""
Company: {info.get('longName')}
Current Price: ${info.get('currentPrice')}
52 Week High: ${info.get('fiftyTwoWeekHigh')}
52 Week Low: ${info.get('fiftyTwoWeekLow')}
Market Cap: ${info.get('marketCap')}
P/E Ratio: {info.get('trailingPE')}
EPS: {info.get('trailingEps')}
Dividend Yield: {info.get('dividendYield')}
"""


@mcp.tool()
def get_stock_history(ticker: str) -> str:
    """Get last 6 months of historical OHLCV data for a given ticker symbol."""
    return yf.Ticker(ticker).history(period="6mo").to_string()


@mcp.tool()
def get_stock_news(ticker: str) -> str:
    """Get latest 5 news headlines for a given ticker symbol."""
    news = yf.Ticker(ticker).news[:5]
    return "".join(f"- {item['content']['title']}\n" for item in news)


@mcp.tool()
def get_stock_fundamentals(ticker: str) -> str:
    """Get key fundamental data for a given ticker symbol."""
    info = yf.Ticker(ticker).info
    return f"""
Revenue (TTM): ${info.get('totalRevenue')}
Profit Margin: {info.get('profitMargins')}
Return on Equity: {info.get('returnOnEquity')}
Debt to Equity: {info.get('debtToEquity')}
Free Cash Flow: ${info.get('freeCashflow')}
"""


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
