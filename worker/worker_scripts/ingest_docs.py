import argparse
import asyncio
from pathlib import Path
from uuid import uuid4

from app.database import async_session
from app.llm import get_embedding
from app.models import Document, DocumentChunk
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from sqlalchemy import delete

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]
markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)


async def ingest_file(file_path: Path, doc_id: str, title: str, category: str):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    md_header_splits = markdown_splitter.split_text(content)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    final_splits = text_splitter.split_documents(md_header_splits)
    async with async_session() as session:
        await session.execute(delete(DocumentChunk).where(DocumentChunk.document_id == doc_id))
        await session.execute(delete(Document).where(Document.id == doc_id))

        doc = Document(id=doc_id, title=title, product_category=category, source_url=str(file_path))
        session.add(doc)

        for idx, chunk in enumerate(final_splits):
            get_vector = await get_embedding(chunk.page_content)
            chunk_record = DocumentChunk(
                id=str(uuid4()),
                document_id=doc_id,
                text_content=chunk.page_content,
                embedding=get_vector,
                chunk_index=idx,
            )
            session.add(chunk_record)
        await session.commit()


async def main(documenct: str | None = None):
    docs_dir = Path("docs")
    compliance_path = docs_dir / "compliance.md"
    tariff_path = docs_dir / "tariff.md"

    if documenct in (None, "compliance") and compliance_path.exists():
        await ingest_file(
            compliance_path, "doc_compliance", "Методические рекомендации ЦБ", "Compliance"
        )
    if documenct in (None, "tariff") and tariff_path.exists():
        await ingest_file(tariff_path, "doc_tariff", "Условия банковского обслуживания", "Tariff")


def cli() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--document",
        choices=["compliance", "tariff"],
        default=None,
    )
    args = parser.parse_args()
    asyncio.run(main(args.document))


if __name__ == "__main__":
    cli()
