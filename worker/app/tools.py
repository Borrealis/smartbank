from app.database import async_session, get_embedding
from app.models import Client, Document, DocumentChunk
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from sqlalchemy import select


class ClientTariffInput(BaseModel):
    client_id: str = Field(..., description="Uniq client identifier")


class ComplianceSearchInput(BaseModel):
    search_query: str = Field(..., description="User search query to database")
    product_category: str | None = None


@tool(args_schema=ClientTariffInput, description="Search and get tariff info in docs")
async def get_client_tariff_info(client_id: str) -> dict:
    async with async_session() as session:
        stmt = select(Client).where(Client.id == client_id)
        result = await session.execute(stmt)
        client = result.scalar_one_or_none()

    if client is None:
        return {"error": "Client not found", "client_id": client_id}
    return {"tariff": client.tariff_plan, "status": client.status}


@tool(args_schema=ComplianceSearchInput, description="Search limitation and restriction in docs ")
async def search_compliance_knowledge(
    search_query: str, product_category: str | None = None
) -> dict:
    query_vector = get_embedding(search_query)
    async with async_session() as session:
        stmt = (
            select(DocumentChunk, Document.title)
            .join(Document, DocumentChunk.document_id == Document.id)
            .order_by(DocumentChunk.embedding.cosine_distance(query_vector))
            .limit(3)
        )
        if product_category is not None:
            stmt = stmt.where(Document.product_category == product_category)
        result = await session.execute(stmt)
        chunks_rows = result.all()

        if not chunks_rows:
            return {"result": []}

        parts = []
        for chunk, title in chunks_rows:
            parts.append({"source": title, "text": chunk.text_content})

        return {"result": parts}

    # filter_info = f" with category filter: '{product_category}'" if product_category else ""
    # return f"Found documents for query: '{search_query}'{filter_info}"
