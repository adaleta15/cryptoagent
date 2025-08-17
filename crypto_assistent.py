import os
import requests
from dotenv import load_dotenv

# OPTIONAL: support for Streamlit Cloud secrets
try:
    import streamlit as st
    _STREAMLIT = True
except Exception:
    _STREAMLIT = False

from openai import OpenAI

# Load env vars (for local dev)
load_dotenv()

# Read OpenAI key: first from Streamlit secrets, for env var
if _STREAMLIT and "OPENAI_API_KEY" in st.secrets:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
else:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY not set. Add Streamlit Secrets or .env file."
    )

#  OpenAI client inicialization
client = OpenAI(api_key=OPENAI_API_KEY)

# --- Coin helpers ---
ALIASES = {
    "btc": "bitcoin",
    "xbt": "bitcoin",
    "eth": "ethereum",
    "sol": "solana",
    "doge": "dogecoin",
    "ada": "cardano",
}

def normalize_coin(name: str) -> str:
    c = name.strip().lower()
    return ALIASES.get(c, c)

def get_price(coin="bitcoin"):
    coin = normalize_coin(coin)
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin, "vs_currencies": "usd"}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        price = data.get(coin, {}).get("usd")
        if price is None:
            return f"Sorry, I couldn't find the price for '{coin}'. Try another coin id (e.g., 'bitcoin', 'ethereum', 'solana')."
        return f"The current price of {coin.capitalize()} is ${price}."
    except requests.RequestException as e:
        return f"Network error fetching price: {e}"

# --- Intent classification using the new OpenAI SDK ---
def classify_intent(user_input: str) -> str:
    prompt = f"""You are a crypto assistant. Classify the intent of the user's question.
User input: "{user_input}"

Your response must be one of exactly:
- "get_price:<coin_name>"
- "define_term"
- "unknown"

Examples:
"What’s the price of bitcoin?" -> "get_price:bitcoin"
"Define DeFi" -> "define_term"
"Tell me a joke" -> "unknown"

Now respond:
"""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return resp.choices[0].message.content.strip()

def respond(user_input: str) -> str:
    intent = classify_intent(user_input)

    if intent.startswith("get_price:"):
        coin = intent.split(":", 1)[1]
        return get_price(coin)
    elif intent == "define_term":
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_input}],
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    else:
        return "Sorry, I can only help with crypto prices and definitions right now."

if __name__ == "__main__":
    print("🧠 Crypto Assistant | Type 'exit' to quit\n")
    while True:
        query = input("Ask me something about crypto: ")
        if query.lower() in ["exit", "quit"]:
            break
        print("🤖", respond(query))
