from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP, Boolean, DateTime
from typing import Union, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import girok.server.src.task.enums as task_enums

class TaskCreateIn(BaseModel):
    task_category_id: Union[int, None] = None
    name: str
    deadline: str
    priority: int = Field(default=None, ge=1, le=5)
    color: Union[str, None] = None
    everyday: Union[bool, None] = False
    tag: Union[str, None] = None
    is_time: bool = False
    all_day: Union[bool, None] = False
    weekly_repeat: int = Field(default=None, gt=0, le=6)


class TaskCreateOut(BaseModel):
    task_id: int
    
    class Config:
        orm_mode = True
        

class Task(BaseModel):
    task_id: int
    user_id: int
    task_category_id: Union[int, None]
    category_path: Union[str, None]
    name: str
    color: str
    deadline: str
    all_day: Union[bool, None]
    is_time: bool
    priority: Union[int, None]
    everyday: Union[bool, None]
    created_at: datetime
    
    class Config:
        orm_mode = True
        

class TaskGetIn(BaseModel):
    category: Union[List[str], None] = Field(
        default_factory=None,
        title="Category",
        description="Full category path of a category. Ex. ['HKU', 'COMP3230'].",
    ),
    start_date: Union[str, None] = Field(
        default_factory="2000-01-01 00:00:00",
        title="Start date",
        description="Start date. Ex. '2023-01-23 12:00:00'",
        regex="^[0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{2}:[0-9]{2}:[0-9]{2}$"
    ),
    end_date: Union[str, None] = Field(
        default_factory=(datetime.now() + timedelta(days=365*10)).strftime("%Y-%m-%d 00:00:00"),
        title="End date",
        description="End date. Ex. '2023-03-23 12:00:00'",
        regex="^[0-9]{4}-[0-9]{1,2}-[0-9]{1,2} [0-9]{2}:[0-9]{2}:[0-9]{2}$"
    ),
    priority: Union[int, None] = Field(
        default_factory=None,
        title="Priority",
        ge=1,
        le=5
    ),
    no_priority: bool = False,
    tag: Union[str, None] = Field(
        default_factory=None,
        title="Tag"
    ),
    view: Union[task_enums.TaskView, None]= Field(
        default_factory=None,
        title="View method for tasks"  
    )

class GetSingleTaskOut(BaseModel):
    name: str
    
        
class TaskOut(BaseModel):
    tasks: Dict[str, dict]
    
    
class Tag(BaseModel):
    tag_id: int
    task_id: int
    name: int
    
class TagOut(BaseModel):
    tags: List[str]
    

class ChangeTaskTagIn(BaseModel):
    new_tag_name: str


class ChangeTaskPriorityIn(BaseModel):
    new_priority: int = Field(ge=1, le=5)


class ChangeTaskDateIn(BaseModel):
    new_date: str = Field(default=..., regex="^([0-9]){4}-([0-9]){1,2}-([0-9]){1,2} [0-9]{2}:[0-9]{2}:[0-9]{2}$")


class ChangeTaskNameIn(BaseModel):
    new_name: str