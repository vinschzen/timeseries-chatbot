"""
Turns analysis/registry.py into OpenAI tool-calling schemas.

Because this reads the registry dynamically, adding a new analysis
module automatically gives the LLM a new tool to call - no schema to
hand-write.
"""
from analysis.registry import ANALYSES
from google.genai import types

def build_tool_schemas():
    return [
        types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name="trend",
                    description="Analyze the trend in the dataset.",
                    parameters_json_schema={
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                )
            ]
        )
    ]


def run_tool(name: str, df, value_col: str) -> dict:
    """Executes the analysis function registered under `name`."""
    if name not in ANALYSES:
        return {"error": f"unknown tool '{name}'"}
    return ANALYSES[name]["func"](df, value_col)
