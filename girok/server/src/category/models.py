from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP, Boolean, DateTime
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship

from girok.server.src.database import Base
    

class TaskCategory(Base):
    __tablename__ = "task_category"
    task_category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    super_task_category_id = Column(Integer, ForeignKey('task_category.task_category_id'), nullable=True)
    color = Column(String(20), nullable=True)
    children = relationship('TaskCategory', cascade="all,delete")

