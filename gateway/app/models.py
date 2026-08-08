from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TaskRecord(Base):
    __tablename__ = "tasks"
    task_id = Column(String, primary_key=True)
    query = Column(String)
    status = Column(String)
