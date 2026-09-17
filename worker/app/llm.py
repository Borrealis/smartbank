from langchain_google_genai import ChatGoogleGenerativeAI
from openai import AsyncOpenAI, RateLimitError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from .config import settings

chat_llm_client = AsyncOpenAI(
    api_key=settings.gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=settings.gemini_api_key)


@retry(
    retry=retry_if_exception_type(RateLimitError),
    wait=wait_fixed(35),
    stop=stop_after_attempt(3),
    reraise=True,
)
async def get_embedding(text: str) -> list[float]:
    response = await chat_llm_client.embeddings.create(
        model="gemini-embedding-001",
        input=text,
        dimensions=1536,
    )
    if not response.data or not response.data[0].embedding:
        raise ValueError("Failed to reatreat the embeddind vector from a model ")
    return response.data[0].embedding
