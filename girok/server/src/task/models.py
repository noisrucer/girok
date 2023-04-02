from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP, Boolean, DateTime
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship

from girok.server.src.database import Base


class Task(Base):
    __tablename__ = "task"
    
    task_id = Column(Integer, primary_key=True, autoincrement=True)
    task_category_id = Column(Integer, ForeignKey('task_category.task_category_id', ondelete="CASCADE"), nullable=True)
    name = Column(String(300), nullable=False)
    deadline = Column(DateTime, nullable=False)
    everyday = Column(Boolean, nullable=True)
    weekly_repeat = Column(Integer, nullable=True)
    is_time = Column(Boolean, nullable=False)
    all_day = Column(Boolean, nullable=True)
    priority = Column(Integer, nullable=True)
    color = Column(String(20), nullable=True)
    tag = Column(String(20), nullable=True)
    # created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
