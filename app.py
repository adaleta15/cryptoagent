# app.py
import streamlit as st
from crypto_assistent import respond  # respond has to exist (user_input: str)

st.set_page_config(page_title="Crypto Assistant", page_icon="🧠", layout="centered")

st.title("🧠 Crypto Assistant")
query = st.text_input("Ask me something about crypto")
if query:
    answer = respond(query)
    st.write("🤖", answer)
