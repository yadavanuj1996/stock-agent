# Stock Analysis Skill

## Goal
Analyse stock data provided by the researcher and generate
technical indicators, insights and a clear recommendation.

## Steps
1. Calculate 50 day and 200 day moving averages from historical data
2. Calculate RSI (14 day) to determine momentum
3. Calculate MACD (12, 26, 9) to determine trend direction
4. Calculate Bollinger Bands (20 day, 2 std dev) to determine volatility
5. Identify if stock is in uptrend or downtrend
6. Compare stock performance against S&P 500 over same period
7. Combine technical indicators with fundamentals for final recommendation

## Technical Indicator Rules
- RSI > 70 = Overbought (potential sell signal)
- RSI < 30 = Oversold (potential buy signal)
- Price above 200 MA = Long term uptrend
- Price below 200 MA = Long term downtrend
- 50 MA crosses above 200 MA = Golden Cross (bullish signal)
- 50 MA crosses below 200 MA = Death Cross (bearish signal)
- MACD above signal line = Bullish momentum
- MACD below signal line = Bearish momentum

## Recommendation Rules
- BUY = Strong fundamentals + bullish technical signals + outperforming S&P 500
- HOLD = Mixed signals or in line with S&P 500 performance
- SELL = Weak fundamentals + bearish technical signals + underperforming S&P 500

## Output Format

### Technical Indicators
- 50 Day MA
- 200 Day MA
- RSI (14)
- MACD
- Bollinger Bands
- Trend Direction

### Benchmark Comparison
- Stock 6 month return vs S&P 500 6 month return

### Recommendation
- BUY / HOLD / SELL
- Confidence Level (High / Medium / Low)
- Key Reasons (3-5 bullet points)

### Risk Factors
- List 3-5 key risks to the recommendation

### Disclaimer
Always include: "This is not financial advice. Always do your own
research before making investment decisions."