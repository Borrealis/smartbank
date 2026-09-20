import pytest
from app.database import async_session
from app.models import Document, DocumentChunk
from app.tools import search_compliance_knowledge

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_search_compliance_knowledge_query_search(monkeypatch: pytest.MonkeyPatch):
    first_vector = [1.0] + [0.0] * 1535
    second_vector = [0.0, 1.0] + [0.0] * 1534
    async with async_session() as session:
        document = Document(
            id="test_compliance_doc",
            title="Методические рекомендации ЦБ",
            product_category="Compliance",
        )
        document_2 = Document(
            id="test_tariff_doc", title="currency money transfers", product_category="Tariff"
        )

        document_chunk = DocumentChunk(
            document_id="test_compliance_doc",
            embedding=first_vector,
            id="test_chunk_1",
            text_content="Money tranfser",
            chunk_index=0,
        )
        document_chunk_2 = DocumentChunk(
            document_id="test_tariff_doc",
            embedding=second_vector,
            id="test_chunk_2",
            text_content="Fee total",
            chunk_index=1,
        )

        session.add_all([document, document_2, document_chunk, document_chunk_2])
        await session.commit()

    async def fake_embedding(text: str) -> list[float]:
        return [1.0] + [0.0] * 1535

    monkeypatch.setattr("app.tools.get_embedding", fake_embedding)

    result = await search_compliance_knowledge.ainvoke(
        {
            "product_category": "Compliance",
            "search_query": "Какие огранчиения дейтсвуют при переводе денег ",
        }
    )

    assert result["result"]
    assert all(chunk["source"] == "Методические рекомендации ЦБ" for chunk in result["result"])
