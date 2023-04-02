from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import and_

import girok.server.src.category.exceptions as exceptions
import girok.server.src.category.models as models
import girok.server.src.utils as global_utils

def create_category(db: Session, cat_data):
    new_cat = models.TaskCategory(**cat_data)
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return global_utils.sql_obj_to_dict(new_cat)


def delete_category(db: Session, cat_id: int):
    cat = db.query(models.TaskCategory).\
        filter(
            and_(
               models.TaskCategory.task_category_id == cat_id 
            )).first()
    db.delete(cat)
    db.commit()
    return cat


def rename_category(db: Session, cat_id: int, new_name: str):
    cat = db.query(models.TaskCategory).\
        filter(
            and_(
                models.TaskCategory.task_category_id == cat_id
            )
            ).first()
    setattr(cat, "name", new_name)
    db.commit()
    
    
def move_category(db: Session, cat_id: int, new_pid: int):
    cat = db.query(models.TaskCategory).\
        filter(
            and_(
                models.TaskCategory.task_category_id == cat_id
            )
            ).first()
    setattr(cat, "super_task_category_id", new_pid)
    db.commit()


def get_category_id_by_name_and_parent_id(db: Session, name: str, parent_id: int):
    category = db.query(models.TaskCategory.task_category_id).\
        filter(
            and_(
                models.TaskCategory.name == name,
                models.TaskCategory.super_task_category_id == parent_id
            )
        ).first()
    if not category:
        return None
    return category[0]


def get_category_name_by_id(db: Session, cat_id: int):
    if cat_id is None:
        return "No Category"
    
    cat = db.query(models.TaskCategory.name).\
        filter(models.TaskCategory.task_category_id == cat_id).\
        first()
    return cat[0] if cat else None


def get_subcategories_by_parent_id(db: Session, pid: int):
    subcats = db.query(models.TaskCategory).\
        filter(
            and_(
                models.TaskCategory.super_task_category_id == pid)    
            ).all()
    return subcats


def get_subcategory_ids_by_parent_id(db: Session, pid: int):
    sub_cats = get_subcategories_by_parent_id(db, pid)
    sub_cats_id = [sub.task_category_id for sub in sub_cats]
    return sub_cats_id


def build_category_tree(db: Session, cat_id):
    subs = get_subcategories_by_parent_id(db, cat_id)
    if subs is None: # Base case
        return {}
    res = defaultdict(dict)
    for sub in subs:
        res[sub.name]['subcategories'] = build_category_tree(db, sub.task_category_id)
        res[sub.name]['color'] = sub.color
    return res


def is_super_category(db: Session, super: str, sub: str):
    sub_cat = db.query(models.TaskCategory).\
        filter(
            and_(
                models.TaskCategory.name == sub,
                models.TaskCategory.super_category_name == super
            )
        ).first()
    return sub_cat


def get_last_cat_id(db: Session, cats: list):
    '''
    ex) ['HKU', 'COMP3230', 'Assignment'] -> return id of Assignment
    cats: list[str]
    Return
        parent_id (int): closest parent id
        cumul_path (str): cumulative path from first and second to last category, connected by /
    '''
    parent_id = None
    cumul_path = ""
    if not cats:
        return parent_id, cumul_path
    
    for cat_name in cats:
        cat_id = get_category_id_by_name_and_parent_id(db, cat_name, parent_id)
        if not cat_id:
            raise exceptions.SubcategoryNotExistException(cumul_path, cat_name)
        parent_id = cat_id
        cumul_path += cat_name + "/"
    return parent_id, cumul_path


def check_exist_category(db: Session, cats: list):
    parent_id = None
    for cat_name in cats:
        cat_id = get_category_id_by_name_and_parent_id(db, cat_name, parent_id)
        if not cat_id:
            return False
        parent_id = cat_id
    return True
    

def get_category_color_by_id(db: Session, cat_id: int):
    cat = db.query(models.TaskCategory).\
        filter(
                and_(
                    models.TaskCategory.task_category_id == cat_id   
                )
            ).first()
    if not cat:
        return None
    return cat.color


def get_category_full_path_by_id(db: Session, category_id: int):
    if category_id is None:
        return ""
    cat_path = ""
    cat = db.query(models.TaskCategory).\
        filter(
            and_(
                models.TaskCategory.task_category_id == category_id
            )
        ).first()
    cat_name = cat.name
    super_cat_id = cat.super_task_category_id
    if super_cat_id is None: # base case
        return cat_name + "/"
    super_cat_full_path = get_category_full_path_by_id(db, super_cat_id)
    cat_path = super_cat_full_path + cat_name + "/"
    return cat_path


def get_all_category_colors(db: Session):
    colors = db.query(models.TaskCategory.name, models.TaskCategory.color).all()
    colors = {c[0]: c[1] for c in colors}
    return colors

    
def get_root_category_id(db: Session, cat_id: int):
    cat = db.query(models.TaskCategory).\
        filter(
                and_(
                    models.TaskCategory.task_category_id == cat_id   
                )
            ).first()
        
    if not cat:
        raise exceptions.CategoryNotExistException(str(cat_id))
    
    pid = cat.super_task_category_id
    if pid is None:
        return cat_id
    
    return get_root_category_id(db,  pid)


