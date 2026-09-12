import json

from app.database import async_session, get_embedding
from app.models import Document, DocumentChunk
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from sqlalchemy import select


class ClientTariffInput(BaseModel):
    client_id: str = Field(..., description="Uniq client identifier")


class ComplianceSearchInput(BaseModel):
    search_query: str = Field(..., description="User search query to database")
    product_category: str | None = None


@tool(args_schema=ClientTariffInput, description="Search and get tariff info in docs")
def get_client_tariff_info(client_id: str) -> str:
    mock_db = {
        "client_123": {"tariff": "Premium", "status": "active"},
        "client_S934": {"tariff": "Base", "status": "active"},
        "client_ff94": {"tariff": "Diamond", "status": "blocked"},
    }
    client_data = mock_db.get(client_id, None)
    if not client_data:
        return json.dumps({"error": "Client not found", "client_id": client_id})
    return json.dumps(client_data)


@tool(args_schema=ComplianceSearchInput, description="Search limitation and restriction in docs ")
async def search_compliance_knowledge(
    search_query: str, product_category: str | None = None
) -> str:
    query_vector = get_embedding(search_query)
    async with async_session() as session:
        stmt = (
            select(DocumentChunk, Document.title)
            .join(Document, DocumentChunk.document_id == Document.id)
            .order_by(DocumentChunk.embedding.cosine_distance(query_vector))
            .limit(10)
        )
        if product_category is not None:
            stmt = stmt.where(Document.product_category == product_category)
        result = await session.execute(stmt)
        chunks_rows = result.all()

        if not chunks_rows:
            return json.dumps({"result": []})

        parts = []
        for chunk, title in chunks_rows:
            parts.append({"source": title, "text": chunk.text_content})

        return json.dumps({"result": parts}, ensure_ascii=False)

    # filter_info = f" with category filter: '{product_category}'" if product_category else ""
    # return f"Found documents for query: '{search_query}'{filter_info}"
