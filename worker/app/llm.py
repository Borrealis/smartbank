from openai import AsyncOpenAI

from .config import settings

llm_client = AsyncOpenAI(
    api_key=settings.gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


async def get_embedding(text: str) -> list[float]:
    response = await llm_client.embeddings.create(
        model="gemini-embedding-001",
        input=text,
        dimensions=1536,
    )
    if not response.data or not response.data[0].embedding:
        raise ValueError("Failed to reatreat the embeddind vector from a model ")
    return response.data[0].embedding
