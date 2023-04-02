from typing import Union, List, Dict
from pydantic import BaseModel
    

class CategoryIn(BaseModel):
    user_email: str

class CategoryOut(BaseModel):
    resp: Dict[str, dict]
    
class CategoryCreateIn(BaseModel):
    color: Union[str, None]
    names: List[str]
    

class CategoryCreateOut(BaseModel):
    task_category_id: int
    class Config:
        orm_mode = True
        
        
class CategoryDeleteIn(BaseModel):
    cats: List[str]
    

class CategoryRenameIn(BaseModel):
    cats: List[str]
    new_name: str
    
class CategoryMoveIn(BaseModel):
    cats: List[str]
    new_parent_cats: List[str]
    
class LastCategoryIdIn(BaseModel):
    cats: List[str]
    
    