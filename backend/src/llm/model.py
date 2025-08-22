from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel
import os


def get_model():

    client = AsyncOpenAI(
        base_url=os.getenv("OPENAI_API_ENDPOINT"),
        api_key=os.getenv("OPENAI_API_KEY")
    )

    model = OpenAIChatCompletionsModel(
        model="gpt-4.1",
        openai_client=client
    )

    return model