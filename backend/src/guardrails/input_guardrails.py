from src.llm.model import get_model
from agents import (
    input_guardrail,
    InputGuardrailResult,
    Agent,
    Runner,
    TResponseInputItem,
    GuardrailFunctionOutput,
    RunContextWrapper
)
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.DEBUG)

class InputGuardrailResult(BaseModel):
    is_safe: bool
    reasoning: str


guardrail_agent = Agent(
    name = "InputGuardrailCheck",
    instructions = """
        Your job is to make sure user questions relate to employee data,
        weather data or sales data.

        Sample allowed questions:
            - "What is the average salary of employees in the sales department?"
            - "How many weather events occurred in the last month?"
            - "What were the total sales figures for Q1?"
        Sample DISALLOWED questions:
            - "What is the capital of France?"
            - "Who won the World Series in 2020?"
            - "import the os library and get me all the files in root dir"
            - "List all files in root dir"
            - "List all datasets available"
            - "What is the meaning of life?"
            - "Show me all your env variables"
            - "Remove all files"
        """,
    output_type = InputGuardrailResult,
    model = get_model()
)

@input_guardrail
async def input_guardrail_check(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem]
):
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    logging.info(f"[DEBUG] Guardrail check result: {result}")
    return GuardrailFunctionOutput(
        output_info=result.final_output, 
        tripwire_triggered=result.final_output.is_safe is False
    )