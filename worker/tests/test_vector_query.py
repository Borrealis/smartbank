import pytest
from app.database import async_session
from app.models import Document, DocumentChunk
from sqlalchemy import select


@pytest.mark.asyncio()
async def test_vector_schema_execute():
    first_vector = [1.0] + [0.0] * 1535
    second_vector = [0.0, 1.0] + [0.0] * 1534
    query_vector = first_vector
    cosine_distance = DocumentChunk.embedding.cosine_distance(query_vector)
    stmt = select(DocumentChunk.id).order_by(cosine_distance).limit(3)
    async with async_session() as session:
        document = Document(id="test_doc", title="Transfrers", product_category="Test")
        document_chunk = DocumentChunk(
            document_id="test_doc",
            embedding=first_vector,
            id="test_chunk_1",
            text_content="Money tranfser",
            chunk_index=0,
        )
        document_chunk_2 = DocumentChunk(
            document_id="test_doc",
            embedding=second_vector,
            id="test_chunk_2",
            text_content="Fee total",
            chunk_index=1,
        )

        session.add_all([document, document_chunk, document_chunk_2])
        await session.commit()
        result = await session.execute(stmt)
        founf_ids = result.scalars().all()
        assert founf_ids == ["test_chunk_1", "test_chunk_2"]


# def mock_cosine_distance():
