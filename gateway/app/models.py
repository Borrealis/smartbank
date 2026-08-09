from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TaskRecord(Base):
    __tablename__ = "tasks"
    task_id = Column(String, primary_key=True)
    query = Column(String)
    status = Column(String)
    result = Column(String, nullable=True)


class Documents(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True)
    title = Column(String)
    product_category = Column(String)
    source_url = Column(String, nullable=True)


class DocumentsChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(String, primary_key=True)
    document_id = Column(String, ForeignKey("documents.id"))
    text_content = Column(Text)
    embedding = Column(Vector(1536))
    chunk_index = Column(Integer)


class Client(Base):
    __tablename__ = "clients"
    id = Column(String, primary_key=True)
    status = Column(String)
    tariff_plan = Column(String)
