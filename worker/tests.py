import asyncio

from app.database import async_session
from app.llm import get_embedding
from app.models import DocumentChunk
from sqlalchemy import select


async def main():
    query_vector = await get_embedding(
        "когда я могу перевести деньги если я пополнил их на свой счет сегодня"
    )

    async with async_session() as session:
        distance = DocumentChunk.embedding.cosine_distance(query_vector)
        stmt = (
            select(DocumentChunk.chunk_index, distance.label("dist"))
            .where(DocumentChunk.document_id == "doc_tariff")
            .order_by(distance)
        )
        result = await session.execute(stmt)
        rows = result.all()

        for idx, dist in rows:
            marker = " <-- ЭТОТ" if idx == 44 else ""
            print(f"chunk_index={idx}, distance={dist:.4f}{marker}")


asyncio.run(main())
