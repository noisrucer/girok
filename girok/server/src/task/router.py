from typing import List, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from girok.server.src.database import get_db
import girok.server.src.task.schemas as schemas
import girok.server.src.utils as general_utils
import girok.server.src.task.service as service
import girok.server.src.category.service as category_service
import girok.server.src.task.exceptions as exceptions
import girok.server.src.task.enums as task_enums

# @router.post(
#     "/",
#     status_code=status.HTTP_201_CREATED,
#     response_model=schemas.TaskCreateOut
# )
def create_task(task: schemas.TaskCreateIn):
    db = next(get_db())
    task['deadline'] = datetime.strptime(task['deadline'], '%Y-%m-%d %H:%M:%S')
    try:
        new_task = service.create_task(db, task)
        return {"success": True, "new_task": new_task}
    except Exception as e:
        return {"success": False, "detail": e.detail}
    

# @router.get(
#     "/",
#     status_code=status.HTTP_200_OK
#     # response_model=schemas.TaskOut
# )
def get_tasks(data: schemas.TaskGetIn):
    print("data", data)
    category = data['category']
    start_date = data['start_date']
    end_date = data['end_date']
    priority = data['priority']
    no_priority = data['no_priority']
    tag = data['tag']
    view = data['view']
    
    db = next(get_db())
    try:
        # Check start_date <= end_date
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
        if start_date > end_date:
            raise exceptions.InvalidDateWindowException(start_date, end_date)
        
        if category is None: # ALL tasks regardless of category
            cat_ids = category_service.get_subcategory_ids_by_parent_id(db, None) # top most categories
            cat_ids += [None]
        elif category == ['']: # Only "None category" category 
            cat_ids = [None]
        else: # Specified category
            cat_id, _ = category_service.get_last_cat_id(db, category)
            cat_ids = [cat_id]

        if view == task_enums.TaskView.category:
            tasks = service.get_tasks_by_category(
                db=db,
                cat_ids=cat_ids,
                start_date=start_date,
                end_date=end_date,
                priority=priority,
                no_priority=no_priority,
                tag=tag
            )
        elif view == task_enums.TaskView.list:
            tasks = service.get_tasks_as_list(
                db=db,
                cat_ids=cat_ids,
                start_date=start_date,
                end_date=end_date,
                priority=priority,
                no_priority=no_priority,
                tag=tag
            )
        else:
            raise Exception("Invalid task view!")
        return {"success": True, "tasks": tasks}
    except Exception as e:
        print(e)
        return {"success": False, "detail": e.detail}
    
    
# @router.delete(
#     "/{task_id}",
#     status_code=status.HTTP_204_NO_CONTENT
# )
async def delete_task(
    task_id: int
):
    db = next(get_db())
    try:
        service.delete_task(db, task_id)
        return {"success": True}
    except Exception as e:
        return {"success": False, "detail": e.detail}
    
    
# @router.patch(
#     '/{task_id}/tag',
#     status_code=status.HTTP_200_OK,
# )
async def change_task_tag(
    task_id: int,
    tag: schemas.ChangeTaskTagIn
):
    db = next(get_db())
    try:
        new_tag_name = tag['new_tag_name']
        updated_task = service.change_task_tag(db, task_id, new_tag_name)
        return {"success": True, "updated_task": updated_task}
    except Exception as e:
        return {"success": False, "detail": e.detail}


# @router.patch(
#     '/{task_id}/priority',
#     status_code=status.HTTP_200_OK,
# )
async def change_task_priority(
    task_id: int,
    priority: schemas.ChangeTaskPriorityIn
):
    db = next(get_db())
    try:
        new_priority = priority['new_priority']
        updated_task = service.change_task_priority(db, task_id, new_priority)
        return {"success": True, "updated_task": updated_task}
    except Exception as e:
        return {"success": False, "detail": e.detail}


# @router.patch(
#     '/{task_id}/date',
#     status_code=status.HTTP_200_OK
# )
async def change_task_date(
    task_id: int,
    data: schemas.ChangeTaskDateIn
):
    db = next(get_db())
    try:
        new_date = data['new_date']
        updated_task = service.change_task_date(db, task_id, new_date)
        return {"success": True, "updated_task": updated_task}
    except Exception as e:
        return {"success": False, "detail": e.detail}


# @router.patch(
#     '/{task_id}/name',
#     status_code=status.HTTP_200_OK
# )
async def change_task_name(
    task_id: int,
    data: schemas.ChangeTaskNameIn
):
    db = next(get_db())
    try:
        new_name = data['new_name']
        updated_task = service.change_task_name(db, task_id, new_name)
        return {"success": True, "updated_task": updated_task}
    except Exception as e:
        return {"success": False, "detail": e.detail}


# @router.get(
#     '/tags',
#     status_code=status.HTTP_200_OK,
#     response_model=schemas.TagOut
# )
async def get_tags():
    db = next(get_db())
    try:
        tags = service.get_tags(db)
        return {"success": True, "tags": tags}
    except Exception as e:
        return {"success": False, "detail": e.detail}


# @router.get(
#     "/{task_id}",
#     status_code=status.HTTP_200_OK,
#     response_model=schemas.GetSingleTaskOut
# )
async def get_single_task(task_id: int):
    db = next(get_db())
    try:
        task = service.get_single_task(db, task_id)
        return {"success": True, "task": task}
    except Exception as e:
        return {"success": False, "detail": e.detail}
    
