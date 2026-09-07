"""
Single-page Streamlit frontend. Run with: streamlit run app.py

Keeps almost no logic of its own on purpose - it just loads the data,
displays the chat, and hands each user message to llm/client.py.
"""

from google.genai import types

import pandas as pd
import streamlit as st
from llm.client import chat


st.set_page_config(page_title="Time Series Insight Bot", layout="centered")
st.title("📊 Time Series Insight Bot")
st.caption(
    "Ask questions about the sales data - trend, seasonality, anomalies, changepoints."
)

VALUE_COL = "sales"


@st.cache_data
def load_data():
    df = pd.read_csv("data/sales.csv", parse_dates=["date"])
    return df


df = load_data()


with st.expander("📈 Raw data preview"):
    st.line_chart(df.set_index("date")[VALUE_COL])
    st.dataframe(df.tail(10))


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Render existing conversation
for msg in st.session_state.messages:

    # Gemini uses "user" and "model"
    if msg.role == "user":
        text = "".join(
            part.text
            for part in (msg.parts or [])
            if part.text is not None
        )

        if text:
            st.chat_message("user").write(text)

    elif msg.role == "model":
        text = "".join(
            part.text
            for part in (msg.parts or [])
            if part.text is not None
        )

        if text:
            st.chat_message("assistant").write(text)


# Chat input
user_input = st.chat_input(
    "e.g. 'What's the overall trend?' or 'Any spikes I should know about?'"
)


if user_input:

    # Display user's message immediately
    st.chat_message("user").write(user_input)

    # Add user's actual input to Gemini history
    st.session_state.messages.append(
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=user_input)
            ],
        )
    )

    # Send conversation to Gemini
    with st.spinner("Thinking..."):
        st.session_state.messages = chat(
            st.session_state.messages,
            df,
            VALUE_COL,
        )

    # Display latest model response
    last = st.session_state.messages[-1]

    final_text = "".join(
        part.text
        for part in (last.parts or [])
        if part.text is not None
    )

    if final_text:
        st.chat_message("assistant").write(final_text)