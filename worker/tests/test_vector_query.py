from app.models import DocumentChunk
from sqlalchemy import select
from sqlalchemy.dialects import postgresql


def test_schema_tool():
    query_vector = [1.0] + [0.0] * 1535
    cosine_distance = DocumentChunk.embedding.cosine_distance(query_vector)
    stmt = select(DocumentChunk.id).order_by(cosine_distance).limit(3)
    compiled_query = stmt.compile(dialect=postgresql.dialect())
    assert "<=>" in str(compiled_query)


# def mock_cosine_distance():
