"""
Thin wrapper around the Gemini API that runs the function-calling loop:
send message -> if the model wants a tool, run it -> send the result
back -> repeat until the model answers in plain text.

This is the only file that talks to the API. Swap models/providers here
without touching app.py or the analysis layer.

Auth: reads the GEMINI_API_KEY environment variable automatically.
"""
from google import genai
from google.genai import types, errors
from llm.tools import build_tool_schemas, run_tool

import time

MODEL = "gemini-3.8-flash"

SYSTEM_PROMPT = """You are a business analyst chatbot. You have tools that run
statistical analysis over a time series dataset (trend, seasonality, anomaly
detection, changepoint detection). You do NOT do arithmetic yourself -
always call a tool to get numbers, then reason about what they mean for
the business in plain, direct language. Point out plausible causes when
metadata (like a promo_flag column) lines up with what you found. If you
are speculating rather than reading it from the data, say so."""

import os
from dotenv import load_dotenv

load_dotenv()

def chat(messages: list[types.Content], df, value_col: str) -> list[types.Content]:
    """
    Takes the running message history as a list of google.genai
    types.Content objects and returns the updated history with the
    model's replies and tool responses appended.
    """
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    client = genai.Client(api_key=api_key)

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=build_tool_schemas(),
    )

    while True:

        # -----------------------------------------
        # Generate response with graceful retry
        # -----------------------------------------
        response = None

        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=MODEL,
                    contents=messages,
                    config=config,
                )

                # Successful request
                break

            except errors.ServerError as e:
                if attempt < 2:
                    wait_time = 2 ** attempt

                    print(
                        f"Gemini temporarily unavailable ({e}). "
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)
                else:
                    raise

        # -----------------------------------------
        # Process Gemini response
        # -----------------------------------------

        candidate = response.candidates[0]
        model_content = candidate.content

        # Append Gemini's response to conversation history
        messages.append(model_content)

        # Check whether Gemini requested any function calls
        function_calls = [
            part.function_call
            for part in model_content.parts
            if part.function_call is not None
        ]

        if not function_calls:
            # No tool calls = final model response
            break

        # -----------------------------------------
        # Execute requested tools
        # -----------------------------------------

        response_parts = []

        for fc in function_calls:
            result = run_tool(
                fc.name,
                df,
                value_col,
            )

            response_parts.append(
                types.Part.from_function_response(
                    name=fc.name,
                    response={
                        "result": result
                    },
                )
            )

        # Feed tool results back to Gemini
        messages.append(
            types.Content(
                role="user",
                parts=response_parts,
            )
        )

    return messages