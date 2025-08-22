from fastapi import FastAPI

# Apply httpx patches before importing anything that uses httpx
from src.agent_.httpx_patch import apply_patches
apply_patches()

from src.agent_.data_analysis import run

app = FastAPI()


@app.post("/chat")
async def chat_endpoint(question: str):

    response = await run(question)
    return response.final_output