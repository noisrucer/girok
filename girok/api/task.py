from typing import List, Optional
from urllib.parse import urljoin

import requests
from requests import HTTPError

from girok.api.category import get_category_id_by_path
from girok.api.entity import APIResponse
from girok.config.auth_handler import AuthHandler
from girok.constants import BASE_URL


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
    access_token = AuthHandler.get_access_token()

    # Resolve target category id
    category_id = None
    if category_path:
        resp = get_category_id_by_path(category_path.split("/"))
        if not resp.is_success:
            return resp
        category_id = resp.body["categoryId"]

    request_body = {
        "categoryId": category_id,
        "name": name,
        "eventDate": {"startDate": start_date, "startTime": start_time, "endDate": end_date, "endTime": end_time},
        "repetition": {"repetitionType": repetition_type, "repetitionEndDate": repetition_end_date},
        "tags": tags,
        "priority": priority,
        "memo": memo,
    }

    resp = requests.post(
        url=urljoin(BASE_URL, "events"), headers={"Authorization": "Bearer " + access_token}, json=request_body
    )

    try:
        resp.raise_for_status()
        return APIResponse(is_success=True, body=resp.json())
    except HTTPError:
        try:
            error_body = resp.json()
            error_message = error_body["message"]
        except:
            error_message = "Failed to create a new task"

        return APIResponse(is_success=False, error_message=error_message)


def get_all_tasks(
    start_date: Optional[str] = "2000-01-01",
    end_date: Optional[str] = "2050-01-01",
    category_id: Optional[int] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
):
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "categoryId": category_id,
        "priority": priority,
        "tags": tags,
    }

    access_token = AuthHandler.get_access_token()
    resp = requests.get(
        url=urljoin(BASE_URL, "events"), headers={"Authorization": "Bearer " + access_token}, params=params
    )

    try:
        resp.raise_for_status()
        return APIResponse(is_success=True, body=resp.json())
    except HTTPError:
        try:
            error_body = resp.json()
            error_message = error_body["message"]
        except:
            error_message = "Failed to retrieve tasks"

        return APIResponse(is_success=False, error_message=error_message)


def remove_event(event_id: int):
    access_token = AuthHandler.get_access_token()
    resp = requests.delete(
        url=urljoin(BASE_URL, f"events/{event_id}"), headers={"Authorization": "Bearer " + access_token}
    )

    try:
        resp.raise_for_status()
        return APIResponse(is_success=True)
    except HTTPError:
        try:
            error_body = resp.json()
            error_message = error_body["message"]
        except:
            error_message = "Failed to retrieve tasks"

        return APIResponse(is_success=False, error_message=error_message)
