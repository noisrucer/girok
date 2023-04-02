from typing import Union, List
import datetime
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

import girok.server.src.task.models as models
import girok.server.src.task.exceptions as exceptions
import girok.server.src.category.service as category_service
import girok.server.src.utils as general_utils



def create_task(db: Session, task_data):
    new_task = models.Task(**task_data)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return general_utils.sql_obj_to_dict(new_task)


def get_single_task(db: Session, task_id: int):
    task = db.query(models.Task).\
        filter(
            and_(
                models.Task.task_id == task_id
            )
        ).first()
    
    if not task:
        raise exceptions.TaskNotFoundException(task_id=task_id)
    
    task = general_utils.sql_obj_to_dict(task)
    return task


def get_tasks_by_category(
    db: Session,
    cat_ids: List[int],
    start_date: datetime,
    end_date: datetime,
    tag: str,
    priority: Union[int, None] = None,
    no_priority: bool = False,
):
    tasks = defaultdict(dict)
    for cat_id in cat_ids:
        cat_name = category_service.get_category_name_by_id(db, cat_id)
        cat_tasks = get_direct_tasks_of_category(
            db=db,
            cat_id=cat_id,
            start_date=start_date,
            end_date=end_date,
            priority=priority,
            no_priority=no_priority,
            tag=tag
        )
        if cat_id is not None:
            sub_cat_ids = category_service.get_subcategory_ids_by_parent_id(db, cat_id)
        else:
            sub_cat_ids = []
        tasks[cat_name]["tasks"] = cat_tasks
        tasks[cat_name]["sub_categories"] = get_tasks_by_category(
            db=db,
            cat_ids=sub_cat_ids,
            start_date=start_date,
            end_date=end_date,
            priority=priority,
            no_priority=no_priority,
            tag=tag
        )
    
    return tasks
     

def get_tasks_as_list(
    db: Session,
    cat_ids: Union[List[int], None],
    start_date: datetime,
    end_date: datetime,
    tag: str,
    priority: Union[int, None] = None,
    no_priority: bool = False
):
    if not cat_ids:
        return []
    tasks = []
    for cat_id in cat_ids:
        cat_tasks = get_direct_tasks_of_category(
            db=db,
            cat_id=cat_id,
            start_date=start_date,
            end_date=end_date,
            tag=tag,
            priority=priority,
            no_priority=no_priority
        )
        tasks += cat_tasks
        if cat_id is not None:
            sub_cat_ids = category_service.get_subcategory_ids_by_parent_id(db, cat_id)
        else:
            sub_cat_ids = []
        tasks += get_tasks_as_list(
            db=db,
            cat_ids=sub_cat_ids,
            start_date=start_date,
            end_date=end_date,
            tag=tag,
            priority=priority,
            no_priority=no_priority
        )
    
    return tasks
    

def get_tags(db: Session):
    tags = db.query(models.Task.tag).\
        filter(
            and_(
                models.Task.tag != None
            )    
        ).all()
    tags = {tag[0] for tag in tags} # unique tags
    return list(tags)


def get_direct_tasks_of_category(
    db: Session,
    cat_id: int,
    start_date: datetime,
    end_date: datetime,
    tag: str,
    priority: Union[int, None] = None,
    no_priority: bool = False
    ):
    cat_color = None
    if cat_id:
        root_id = category_service.get_root_category_id(db, cat_id)
        cat_color = category_service.get_category_color_by_id(db, root_id)
        
    tasks_query = db.query(models.Task).\
        filter(
            and_(
                models.Task.task_category_id == cat_id,
                func.date(models.Task.deadline) >= start_date,
                func.date(models.Task.deadline) <= end_date
            )
        )
        
    if no_priority:
        tasks_query = tasks_query.filter(models.Task.priority == None)
    else:
        if priority:
            tasks_query = tasks_query.filter(models.Task.priority == priority)
    
    if tag:
        tasks_query = tasks_query.filter(models.Task.tag == tag)
    
    tasks = tasks_query.order_by(models.Task.deadline.asc()).order_by(models.Task.priority.desc()).all()
    tasks_obj_list = general_utils.sql_obj_list_to_dict_list(tasks)
    for task_obj in tasks_obj_list:
        task_obj.update({
            "task_category_full_path": category_service.get_category_full_path_by_id(db, task_obj['task_category_id']),
        })
        
        if cat_color:
            task_obj.update({"color": cat_color})

    return tasks_obj_list
    
    
def delete_task(db: Session, task_id: int):
    task = db.query(models.Task).\
        filter(
            and_(
                models.Task.task_id == task_id
            )
        ).first()
    if not task:
        raise exceptions.TaskNotFoundException(task_id=task_id)
        
    db.delete(task)
    db.commit()
    return task


def change_task_tag(db: Session, task_id: int, new_tag_name: str):
    task = db.query(models.Task).\
        filter(
            and_(
                models.Task.task_id == task_id
            )
        ).first()
        
    if not task:
        raise exceptions.TaskNotFoundException(task_id=task_id)

    setattr(task, "tag", new_tag_name)
    db.commit()
    return general_utils.sql_obj_to_dict(task)
    


def change_task_priority(db: Session, task_id: int, new_priority: int):
    task = db.query(models.Task).\
        filter(
            and_(
                models.Task.task_id == task_id
            )
        ).first()
        
    if not task:
        raise exceptions.TaskNotFoundException(task_id=task_id)

    setattr(task, "priority", new_priority)
    db.commit()
    return general_utils.sql_obj_to_dict(task)

    
def change_task_date(db: Session, task_id: int, new_date: str):
    task = db.query(models.Task).\
        filter(
            and_(
                models.Task.task_id == task_id
            )
        ).first()
        
    if not task:
        raise exceptions.TaskNotFoundException(task_id=task_id)

    setattr(task, "deadline", new_date)
    db.commit()
    return general_utils.sql_obj_to_dict(task)


def change_task_name(db: Session, task_id: int, new_name: str):
    task = db.query(models.Task).\
        filter(
            and_(
                models.Task.task_id == task_id
            )
        ).first()
        
    if not task:
        raise exceptions.TaskNotFoundException(task_id=task_id)

    setattr(task, "name", new_name)
    db.commit()
    return general_utils.sql_obj_to_dict(task)
