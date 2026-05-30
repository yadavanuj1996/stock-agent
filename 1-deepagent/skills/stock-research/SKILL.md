# Stock Research Skill

## Goal
Fetch comprehensive and accurate stock data for a given ticker symbol.

## Steps
1. Fetch current price, 52 week high/low, market cap, P/E ratio
2. Fetch last 6 months of historical OHLCV (Open, High, Low, Close, Volume) data
3. Fetch key fundamentals (revenue, profit margin, EPS, dividend yield)
4. Fetch latest 5 news headlines with dates
5. Return all data in a structured format for the analyst to use

## Rules
- Always validate the ticker symbol before fetching data
- If a ticker is invalid, return a clear error message
- Always include the data timestamp so user knows how fresh the data is
- Never fabricate or estimate data — only return what yfinance provides
- If a data point is unavailable, explicitly say "Data unavailable" 

## Output Format
Return data in this exact structure:

### Price Info
- Current Price
- 52 Week High / Low
- Market Cap
- P/E Ratio
- EPS
- Dividend Yield

### Historical Data
- Last 6 months OHLCV as a table

### Fundamentals
- Revenue (TTM)
- Profit Margin
- Return on Equity
- Debt to Equity

### Recent News
- Headline 1 (date)
- Headline 2 (date)
- Headline 3 (date)
- Headline 4 (date)
- Headline 5 (date)
