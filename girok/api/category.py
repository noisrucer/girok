"""
Category API for local SQLite storage.
Handles CRUD operations for hierarchical categories.
"""
from typing import Optional

from girok.api.entity import APIResponse
from girok.config.auth_handler import AuthHandler
from girok.database.db import get_db, init_database


def get_all_categories() -> APIResponse:
    """Get all categories for the current user in hierarchical structure."""
    user_id = AuthHandler.get_user_id()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get all categories for user
        cursor.execute("""
            SELECT id, parent_id, name, color 
            FROM categories 
            WHERE user_id = ?
            ORDER BY name
        """, (user_id,))
        
        rows = cursor.fetchall()
        categories = [dict(row) for row in rows]
        
        # Build hierarchical structure
        root_categories = _build_category_tree(categories)
        
        return APIResponse(is_success=True, body={"rootCategories": root_categories})


def _build_category_tree(categories: list) -> list:
    """Convert flat list of categories to hierarchical tree."""
    # Create lookup by id
    by_id = {cat["id"]: {**cat, "children": []} for cat in categories}
    
    roots = []
    for cat in categories:
        cat_with_children = by_id[cat["id"]]
        parent_id = cat["parent_id"]
        
        if parent_id is None:
            roots.append(cat_with_children)
        elif parent_id in by_id:
            by_id[parent_id]["children"].append(cat_with_children)
    
    return roots


def create_category(category_path: str, color: str) -> APIResponse:
    """Create a new category at the given path."""
    user_id = AuthHandler.get_user_id()
    
    category_path_list = category_path.split("/")
    new_category_name = category_path_list[-1]
    
    # Resolve parent category's id
    parent_category_id_resp = get_category_id_by_path(category_path_list[:-1])
    if not parent_category_id_resp.is_success:
        return APIResponse(is_success=False, error_message=parent_category_id_resp.error_message)
    
    parent_category_id = parent_category_id_resp.body["categoryId"]
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check for duplicate
        if parent_category_id is None:
            cursor.execute("""
                SELECT id FROM categories 
                WHERE user_id = ? AND parent_id IS NULL AND name = ?
            """, (user_id, new_category_name))
        else:
            cursor.execute("""
                SELECT id FROM categories 
                WHERE user_id = ? AND parent_id = ? AND name = ?
            """, (user_id, parent_category_id, new_category_name))
        
        if cursor.fetchone():
            parent_path = "/".join(category_path_list[:-1]) + "/" if category_path_list[:-1] else "/"
            return APIResponse(
                is_success=False, 
                error_message=f"Duplicate Category: '{parent_path}' already has '{new_category_name}'"
            )
        
        try:
            cursor.execute("""
                INSERT INTO categories (user_id, parent_id, name, color)
                VALUES (?, ?, ?, ?)
            """, (user_id, parent_category_id, new_category_name, color))
            
            new_id = cursor.lastrowid
            return APIResponse(is_success=True, body={"id": new_id})
        except Exception as e:
            return APIResponse(is_success=False, error_message=f"Failed to create category: {str(e)}")


def remove_category(category_path: str) -> APIResponse:
    """Remove a category and all its subcategories and tasks."""
    user_id = AuthHandler.get_user_id()
    
    category_path_list = category_path.split("/")
    category_id_resp = get_category_id_by_path(category_path_list)
    if not category_id_resp.is_success:
        return APIResponse(is_success=False, error_message=category_id_resp.error_message)
    
    category_id = category_id_resp.body["categoryId"]
    
    if category_id is None:
        return APIResponse(is_success=False, error_message="Category not found")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        try:
            # Get all descendant category IDs (including self)
            descendant_ids = _get_category_descendants(cursor, category_id)
            descendant_ids.append(category_id)
            
            # Delete all events belonging to these categories
            placeholders = ",".join("?" * len(descendant_ids))
            cursor.execute(f"""
                DELETE FROM events 
                WHERE category_id IN ({placeholders}) AND user_id = ?
            """, (*descendant_ids, user_id))
            
            # Now delete the category (CASCADE will handle child categories)
            cursor.execute("""
                DELETE FROM categories 
                WHERE id = ? AND user_id = ?
            """, (category_id, user_id))
            
            if cursor.rowcount == 0:
                return APIResponse(is_success=False, error_message="Category not found")
            
            return APIResponse(is_success=True)
        except Exception as e:
            return APIResponse(is_success=False, error_message=f"Failed to remove category: {str(e)}")


def _get_category_descendants(cursor, category_id: int) -> list:
    """Recursively get all descendant category IDs."""
    cursor.execute("SELECT id FROM categories WHERE parent_id = ?", (category_id,))
    children = [row["id"] for row in cursor.fetchall()]
    
    descendants = []
    for child_id in children:
        descendants.append(child_id)
        descendants.extend(_get_category_descendants(cursor, child_id))
    
    return descendants


def update_category(category_path: str, new_name: Optional[str] = None, new_color: Optional[str] = None) -> APIResponse:
    """Update category name and/or color."""
    user_id = AuthHandler.get_user_id()
    
    category_path_list = category_path.split("/")
    category_id_resp = get_category_id_by_path(category_path_list)
    if not category_id_resp.is_success:
        return category_id_resp
    
    category_id = category_id_resp.body["categoryId"]
    
    if category_id is None:
        return APIResponse(is_success=False, error_message="Category not found")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if new_name:
            updates.append("name = ?")
            params.append(new_name)
        if new_color:
            updates.append("color = ?")
            params.append(new_color)
        
        if not updates:
            return APIResponse(is_success=True)
        
        params.extend([category_id, user_id])
        
        try:
            cursor.execute(f"""
                UPDATE categories 
                SET {", ".join(updates)}
                WHERE id = ? AND user_id = ?
            """, params)
            
            return APIResponse(is_success=True)
        except Exception as e:
            return APIResponse(is_success=False, error_message=f"Failed to update category: {str(e)}")


def move_category(path: str, new_parent_path: str) -> APIResponse:
    """Move a category to a new parent."""
    user_id = AuthHandler.get_user_id()
    
    path_list = path.split("/")
    new_parent_path_list = new_parent_path.split("/") if new_parent_path else []
    
    # Get the category id
    resp = get_category_id_by_path(path_list)
    if not resp.is_success:
        return resp
    category_id = resp.body["categoryId"]
    
    if category_id is None:
        return APIResponse(is_success=False, error_message="Category not found")
    
    # Get target parent's id
    resp = get_category_id_by_path(new_parent_path_list)
    if not resp.is_success:
        return resp
    new_parent_category_id = resp.body["categoryId"]
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE categories 
                SET parent_id = ?
                WHERE id = ? AND user_id = ?
            """, (new_parent_category_id, category_id, user_id))
            
            return APIResponse(is_success=True)
        except Exception as e:
            return APIResponse(is_success=False, error_message=f"Failed to move category: {str(e)}")


def get_category_id_by_path(path_list: list[str]) -> APIResponse:
    """Get category ID by traversing the path."""
    if len(path_list) == 0 or (len(path_list) == 1 and path_list[0] == ""):
        return APIResponse(is_success=True, body={"categoryId": None})
    
    user_id = AuthHandler.get_user_id()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        current_parent_id = None
        
        for name in path_list:
            if current_parent_id is None:
                cursor.execute("""
                    SELECT id FROM categories 
                    WHERE user_id = ? AND parent_id IS NULL AND name = ?
                """, (user_id, name))
            else:
                cursor.execute("""
                    SELECT id FROM categories 
                    WHERE user_id = ? AND parent_id = ? AND name = ?
                """, (user_id, current_parent_id, name))
            
            row = cursor.fetchone()
            if row is None:
                return APIResponse(
                    is_success=False, 
                    error_message=f"Category '{'/'.join(path_list)}' not found"
                )
            
            current_parent_id = row["id"]
        
        return APIResponse(is_success=True, body={"categoryId": current_parent_id})
