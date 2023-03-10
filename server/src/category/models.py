from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP, Boolean, DateTime
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship

from server.src.database import Base
    

class TaskCategory(Base):
    __tablename__ = "task_category"
    task_category_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    name = Column(String(50), nullable=False)
    super_task_category_id = Column(Integer, ForeignKey('task_category.task_category_id', ondelete="CASCADE"), nullable=True)
    color = Column(String(20), nullable=True)
    Supercat = relationship('TaskCategory', remote_side=[super_task_category_id], passive_deletes=True)
    task = relationship("Task", cascade="all,delete", backref="task_category")