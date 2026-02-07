"""
Task/Event API for local SQLite storage.
Handles CRUD operations for tasks, events, and tags.
"""
from typing import List, Optional

from girok.api.category import get_category_id_by_path
from girok.api.entity import APIResponse
from girok.config.auth_handler import AuthHandler
from girok.database.db import get_db


def create_task(
    name: str,
    start_date: str,
    start_time: Optional[str],
    end_date: Optional[str],
    end_time: Optional[str],
    repetition_type: Optional[str],
    repetition_end_date: Optional[str],
    category_path: Optional[str],
    tags: Optional[List[str]],
    priority: Optional[str],
    memo: Optional[str],
) -> APIResponse:
    """Create a new task/event in the database."""
    user_id = AuthHandler.get_user_id()
    
    # Resolve target category id
    category_id = None
    if category_path is not None:
        category_path_list = category_path.split("/")
        if category_path == '':
            category_path_list = []
        resp = get_category_id_by_path(category_path_list)
        if not resp.is_success:
            return resp
        category_id = resp.body["categoryId"]
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO events (
                    user_id, category_id, name, start_date, start_time,
                    end_date, end_time, repetition_type, repetition_end_date,
                    priority, memo
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, category_id, name, start_date, start_time,
                end_date, end_time, repetition_type, repetition_end_date,
                priority, memo
            ))
            
            event_id = cursor.lastrowid
            
            # Insert tags
            if tags:
                for tag in tags:
                    cursor.execute("""
                        INSERT INTO event_tags (event_id, tag)
                        VALUES (?, ?)
                    """, (event_id, tag))
            
            return APIResponse(is_success=True, body={"eventId": event_id})
        except Exception as e:
            return APIResponse(is_success=False, error_message=f"Failed to create task: {str(e)}")


def update_task(
    event_id: int,
    name: str,
    start_date: str,
    start_time: Optional[str],
    end_date: Optional[str],
    end_time: Optional[str],
    repetition_type: Optional[str],
    repetition_end_date: Optional[str],
    category_path: Optional[str],
    tags: Optional[List[str]],
    priority: Optional[str],
    memo: Optional[str],
) -> APIResponse:
    """Update an existing task/event."""
    user_id = AuthHandler.get_user_id()
    
    # Resolve target category id
    category_id = None
    if category_path is not None:
        category_path_list = category_path.split("/")
        if category_path == '':
            category_path_list = []
        resp = get_category_id_by_path(category_path_list)
        if not resp.is_success:
            return resp
        category_id = resp.body["categoryId"]
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE events SET
                    category_id = ?, name = ?, start_date = ?, start_time = ?,
                    end_date = ?, end_time = ?, repetition_type = ?, 
                    repetition_end_date = ?, priority = ?, memo = ?
                WHERE id = ? AND user_id = ?
            """, (
                category_id, name, start_date, start_time,
                end_date, end_time, repetition_type,
                repetition_end_date, priority, memo,
                event_id, user_id
            ))
            
            if cursor.rowcount == 0:
                return APIResponse(is_success=False, error_message="Task not found")
            
            # Update tags - delete old ones and insert new
            cursor.execute("DELETE FROM event_tags WHERE event_id = ?", (event_id,))
            if tags:
                for tag in tags:
                    cursor.execute("""
                        INSERT INTO event_tags (event_id, tag)
                        VALUES (?, ?)
                    """, (event_id, tag))
            
            return APIResponse(is_success=True)
        except Exception as e:
            return APIResponse(is_success=False, error_message=f"Failed to update task: {str(e)}")


def get_single_event(event_id: int) -> APIResponse:
    """Get a single event by ID."""
    user_id = AuthHandler.get_user_id()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT e.*, c.name as category_name, c.color as category_color
            FROM events e
            LEFT JOIN categories c ON e.category_id = c.id
            WHERE e.id = ? AND e.user_id = ?
        """, (event_id, user_id))
        
        row = cursor.fetchone()
        if row is None:
            return APIResponse(is_success=False, error_message="Task not found")
        
        event = dict(row)
        
        # Get tags for this event
        cursor.execute("SELECT tag FROM event_tags WHERE event_id = ?", (event_id,))
        tags = [r["tag"] for r in cursor.fetchall()]
        event["tags"] = tags
        
        # Format response to match expected structure
        result = _format_event_response(event)
        
        return APIResponse(is_success=True, body=result)


def get_all_tasks(
    start_date: Optional[str] = "2000-01-01",
    end_date: Optional[str] = "2050-01-01",
    category_id: Optional[int] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    fetch_children: bool = False
) -> APIResponse:
    """Get all tasks with optional filters."""
    user_id = AuthHandler.get_user_id()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Build query with filters
        query = """
            SELECT e.*, c.name as category_name, c.color as category_color
            FROM events e
            LEFT JOIN categories c ON e.category_id = c.id
            WHERE e.user_id = ?
            AND e.start_date >= ?
            AND e.start_date <= ?
        """
        params = [user_id, start_date, end_date]
        
        if category_id is not None:
            if fetch_children:
                # Get all descendant category IDs
                category_ids = _get_category_descendants(conn, category_id)
                category_ids.append(category_id)
                placeholders = ",".join("?" * len(category_ids))
                query += f" AND e.category_id IN ({placeholders})"
                params.extend(category_ids)
            else:
                query += " AND e.category_id = ?"
                params.append(category_id)
        
        if priority:
            query += " AND e.priority = ?"
            params.append(priority)
        
        query += " ORDER BY e.start_date, e.start_time"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        events = []
        for row in rows:
            event = dict(row)
            
            # Get tags for this event
            cursor.execute("SELECT tag FROM event_tags WHERE event_id = ?", (event["id"],))
            event_tags = [r["tag"] for r in cursor.fetchall()]
            event["tags"] = event_tags
            
            # Filter by tags if specified
            if tags:
                if not any(t in event_tags for t in tags):
                    continue
            
            events.append(_format_event_response(event))
        
        return APIResponse(is_success=True, body={"events": events})


def _get_category_descendants(conn, category_id: int) -> list:
    """Get all descendant category IDs recursively."""
    cursor = conn.cursor()
    
    descendants = []
    cursor.execute("SELECT id FROM categories WHERE parent_id = ?", (category_id,))
    children = [row["id"] for row in cursor.fetchall()]
    
    for child_id in children:
        descendants.append(child_id)
        descendants.extend(_get_category_descendants(conn, child_id))
    
    return descendants


def _format_event_response(event: dict) -> dict:
    """Format event dict to match expected API response structure."""
    return {
        "id": event["id"],
        "name": event["name"],
        "color": event.get("category_color") or "GREY",
        "eventDate": {
            "startDate": event["start_date"],
            "startTime": event["start_time"],
            "endDate": event["end_date"],
            "endTime": event["end_time"],
        },
        "repetition": {
            "repetitionType": event["repetition_type"],
            "repetitionEndDate": event["repetition_end_date"],
        },
        "categoryPath": _get_category_path_list(event.get("category_id")),
        "tags": event.get("tags", []),
        "priority": event["priority"],
        "memo": event["memo"],
    }


def _get_category_path_list(category_id: Optional[int]) -> list:
    """Get the full path of categories from root to the given category."""
    if not category_id:
        return []
    
    path = []
    current_id = category_id
    
    with get_db() as conn:
        cursor = conn.cursor()
        while current_id:
            cursor.execute("SELECT id, name, parent_id FROM categories WHERE id = ?", (current_id,))
            row = cursor.fetchone()
            if not row:
                break
                
            path.insert(0, {"categoryId": row["id"], "categoryName": row["name"]})
            current_id = row["parent_id"]
            
    return path


def remove_event(event_id: int) -> APIResponse:
    """Remove an event by ID."""
    user_id = AuthHandler.get_user_id()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM events 
                WHERE id = ? AND user_id = ?
            """, (event_id, user_id))
            
            if cursor.rowcount == 0:
                return APIResponse(is_success=False, error_message="Task not found")
            
            return APIResponse(is_success=True)
        except Exception as e:
            return APIResponse(is_success=False, error_message=f"Failed to remove task: {str(e)}")


def get_all_tags() -> APIResponse:
    """Get all unique tags for the current user."""
    user_id = AuthHandler.get_user_id()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT et.tag
            FROM event_tags et
            JOIN events e ON et.event_id = e.id
            WHERE e.user_id = ?
            ORDER BY et.tag
        """, (user_id,))
        
        tags = [row["tag"] for row in cursor.fetchall()]
        
        return APIResponse(is_success=True, body={"tags": tags})