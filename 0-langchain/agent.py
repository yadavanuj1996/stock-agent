from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
import yfinance as yf

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

@tool
def get_stock_price(ticker: str) -> str:
    """Get the current stock price and basic info for a given ticker symbol."""
    stock = yf.Ticker(ticker)
    info = stock.info
    return f"""
    Company: {info.get('longName')}
    Current Price: ${info.get('currentPrice')}
    52 Week High: ${info.get('fiftyTwoWeekHigh')}
    52 Week Low: ${info.get('fiftyTwoWeekLow')}
    Market Cap: ${info.get('marketCap')}
    """

@tool
def get_stock_news(ticker: str) -> str:
    """Get the latest news headlines for a given stock ticker symbol."""
    stock = yf.Ticker(ticker)
    news = stock.news[:5]  # get latest 5 news items
    
    result = ""
    for item in news:
        result += f"- {item['content']['title']}\n"
    
    return result


tools = [get_stock_price, get_stock_news]
llm_with_tools = llm.bind_tools(tools)

# memory — this list persists across multiple questions
conversation_history = [
    SystemMessage("You are a stock market research assistant. Help users analyse stocks and make informed decisions.")
]

def chat(user_input: str):
    # add user message to history
    conversation_history.append(HumanMessage(user_input))
    
    # first LLM call
    response = llm_with_tools.invoke(conversation_history)
    conversation_history.append(response)
    
    # handle tool calls
    if response.tool_calls:
        for tool_call in response.tool_calls:
            if tool_call["name"] == "get_stock_price":
                tool_result = get_stock_price.invoke(tool_call["args"])
            elif tool_call["name"] == "get_stock_news":
                tool_result = get_stock_news.invoke(tool_call["args"])
            
            conversation_history.append({
                "role": "tool",
                "content": tool_result,
                "tool_call_id": tool_call["id"]
            })
        
        # second LLM call with tool results
        response = llm_with_tools.invoke(conversation_history)
        conversation_history.append(response)
    
    return response.content
# multi-turn conversation loop
print("Stock Research Assistant (type 'quit' to exit)")
print("-" * 50)

while True:
    user_input = input("\nYou: ")
    if user_input.lower() == "quit":
        break
    
    response = chat(user_input)
    print(f"\nAssistant: {response}")