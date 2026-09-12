from app.config import settings
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

engine = create_async_engine(settings.database_url)
async_session = async_sessionmaker(engine, expire_on_commit=False)

ai_client = genai.Client(api_key=settings.gemini_api_key)


@retry(retry=retry_if_exception_type(ClientError), wait=wait_fixed(60), stop=stop_after_attempt(3))
def get_embedding(text: str) -> list[float]:
    response = ai_client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=1536),
    )
    if not response.embeddings or not response.embeddings[0].values:
        raise ValueError("Failed to reatreat the embeddind vector from a model ")
    return response.embeddings[0].values
