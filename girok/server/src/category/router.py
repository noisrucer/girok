from typing import List
from collections import defaultdict
from sqlalchemy.orm import Session

from girok.server.src.database import get_db
import girok.server.src.category.schemas as schemas
import girok.server.src.category.service as service
import girok.server.src.category.exceptions as exceptions
import girok.server.src.category.constants as category_constants


def get_all_categories():
    db = next(get_db())
    resp = defaultdict(dict)
    cats = service.get_subcategories_by_parent_id(db, pid=None)
    for cat in cats:
        resp[cat.name]["subcategories"] = service.build_category_tree(db, cat.task_category_id)
        resp[cat.name]["color"] = cat.color
        
    resp['No Category'] = {
        "color": "grey",
        "subcategories": {}
    }
    
    return resp


def create_category(category: schemas.CategoryCreateIn):
    db = next(get_db())
    ''' Example
    category = {
        names: ['HKU', 'COMP3230', 'Assignment']
        color: yellow
    }
    '''
    names = category['names']
    color = category['color']
    if color and color not in category_constants.CATEGORY_COLORS:
        return {"success": False, "detail": exceptions.CategoryColorNotExistException(color).detail}
    
    try:
        pid_of_second_last_cat, cumul_path = service.get_last_cat_id(db, names[:-1])
    except Exception as e:
        return {"success": False, "detail": e.detail}
    
    # If given, check if the subdirectory color is equal to the parent's color,
    if color is None:
        if pid_of_second_last_cat is not None:
            color = service.get_category_color_by_id(db, pid_of_second_last_cat) # set to parent's color
        else:
            # Select non-overlapping colors
            existing_colors = set(service.get_all_category_colors(db).values())
            for c in category_constants.CATEGORY_COLORS: # Assign color (lower index higher priority)
                if c in existing_colors: 
                    continue
                color = c
                break
            if color is None: # If no available non-overlapping color, assign the default color
                color = category_constants.DEFAULT_CATEGORY_COLOR
    else:
        if pid_of_second_last_cat is not None:
            parent_color = service.get_category_color_by_id(db, pid_of_second_last_cat) 
            if color != parent_color:
                return {"success": False, "detail": exceptions.CategoryColorException(names[-1], color, '/'.join(names[:-1]), parent_color).detail}
            
    
    new_cat_name = names[-1]
    dup_cat_id = service.get_category_id_by_name_and_parent_id(db, new_cat_name, pid_of_second_last_cat)
    if dup_cat_id:
        return {"success": False, "detail": exceptions.CategoryAlreadyExistsException(cumul_path, new_cat_name).detail}
    
    new_cat_data = {
        "name": new_cat_name,
        "super_task_category_id": pid_of_second_last_cat,
        "color": color
    }
    new_cat = service.create_category(db, new_cat_data)
    return {"success": True, "data": new_cat}


def delete_category(category: schemas.CategoryDeleteIn):
    db = next(get_db())
    cats = category['cats']
    try:
        cat_id, _ = service.get_last_cat_id(db, cats)
    except Exception as e:
        return {"success": False, "detail": e.detail}
    
    service.delete_category(db, cat_id)
    return {"success": True}
    
        
def rename_category(category: schemas.CategoryRenameIn):
    db = next(get_db())
    cats, new_name, = category['cats'], category['new_name']
    
    # Get cat_id of the original category
    try:
        cat_id, _ = service.get_last_cat_id(db, cats)
    except Exception as e:
        return {"success": False, "detail": e.detail}
    
    # Check if new_cats exists (ex. cats[:-1] + /new_cat)
    new_cats = cats[:-1] + [new_name]
    if service.check_exist_category(db, new_cats):
        return {"success": False, "detail": exceptions.CategoryAlreadyExistsException('/'.join(new_cats[:-1]), new_name)}
    service.rename_category(db, cat_id, new_name)
    return {"success": True}
    

def move_category(category: schemas.CategoryMoveIn):
    """
    cats: ['HKU', 'COMP3230']
    new_parent_cats: ['Dev', 'Git']
    
    Then, we want to move the entire HKU/COMP3230 category into under Dev/Git category.
    """
    db = next(get_db())
    cats, new_parent_cats = category['cats'], category['new_parent_cats']
    if not cats:
        return {"success": False, "detail": exceptions.CannotMoveRootDirectoryException().detail}
    
    new_cat = new_parent_cats + [cats[-1]]
    
    if service.check_exist_category(db, new_parent_cats + [cats[-1]]):
        raise exceptions.CategoryAlreadyExistsException('/'.join(new_parent_cats), cats[-1])
        
    try:
        cat_id, _ = service.get_last_cat_id(db, cats)
        new_pid, _ = service.get_last_cat_id(db, new_parent_cats)
    except Exception as e:
        return {"success": False, "detail": e.detail}
    if cat_id == new_pid:
        return {"success": False, "detail": exceptions.CannotMoveToSameLocation().detail}
    
    service.move_category(db, cat_id, new_pid)
    return {"success": True}
    
    
def get_last_cat_id(cat_data: schemas.LastCategoryIdIn):
    db = next(get_db())
    try:
        cat_id, _ = service.get_last_cat_id(db, cat_data['cats'])
        return {"success": True, "cat_id": cat_id}
    except Exception as e:
        return {"success": False, "detail": e.detail}


def get_category_color(cat_id: int):
    db = next(get_db())
    try:
        color = service.get_category_color_by_id(db, cat_id)
        return {"success": True, "color": color}
    except Exception as e:
        return {"success": False, "detail": e.detail}


def get_category_colors_dict():
    db = next(get_db())
    try:
        colors = service.get_all_category_colors(db)
        colors['No Category'] = "grey"
        return {"success": True, "colors": colors}
    except Exception as e:
        return {"success": False, "detail": e.detail}