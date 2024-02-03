from typing import Optional
from urllib.parse import urljoin

import requests
from requests import HTTPError

from girok.api.entity import APIResponse
from girok.config.auth_handler import AuthHandler
from girok.constants import BASE_URL


def get_all_categories() -> APIResponse:
    access_token = AuthHandler.get_access_token()
    resp = requests.get(
        url=urljoin(BASE_URL, "categories"),
        headers={"Authorization": "Bearer " + access_token},
    )

    try:
        resp.raise_for_status()
        return APIResponse(is_success=True, body=resp.json())
    except HTTPError as e:
        try:
            error_body = resp.json()
            error_message = error_body["message"]
        except:
            error_message = "Failed to get categories"

        return APIResponse(is_success=False, error_message=error_message)


def create_category(category_path: str, color: str) -> APIResponse:
    access_token = AuthHandler.get_access_token()

    category_path_list = category_path.split("/")
    new_category_name = category_path_list[-1]

    # Resolve parent category's id
    parent_category_id_resp = get_category_id_by_path(category_path_list[:-1])
    if not parent_category_id_resp.is_success:
        return APIResponse(is_success=False, error_message=parent_category_id_resp.error_message)

    parent_category_id = parent_category_id_resp.body["categoryId"]
    resp = requests.post(
        url=urljoin(BASE_URL, "categories"),
        headers={"Authorization": "Bearer " + access_token},
        json={"parentId": parent_category_id, "name": new_category_name, "color": color},
    )

    try:
        resp.raise_for_status()
        return APIResponse(is_success=True, body=resp.json())
    except HTTPError:
        try:
            error_body = resp.json()
            error_code = error_body["errorCode"]
            error_message = error_body["message"]

            if error_code == "DUPLICATE_CATEGORY":
                parent_category_path_str = (
                    "/" if not category_path_list[:-1] else "/".join(category_path_list[:-1]) + "/"
                )
                error_message = f"Duplicate Category: '{parent_category_path_str}' already has '{new_category_name}'"
        except:
            error_message = "Failed to create a new category"

        return APIResponse(is_success=False, error_message=error_message)


def remove_category(category_path: str) -> APIResponse:
    access_token = AuthHandler.get_access_token()

    category_path_list = category_path.split("/")
    category_id_resp = get_category_id_by_path(category_path_list)
    if not category_id_resp.is_success:
        return APIResponse(is_success=False, error_message=category_id_resp.error_message)

    category_id = category_id_resp.body["categoryId"]
    resp = requests.delete(
        url=urljoin(BASE_URL, f"categories/{category_id}"),
        headers={"Authorization": "Bearer " + access_token},
    )

    try:
        resp.raise_for_status()
        return APIResponse(is_success=True)
    except HTTPError:
        try:
            error_body = resp.json()
            error_message = error_body["message"]
        except:
            error_message = "Failed to remove a category"

        return APIResponse(is_success=False, error_message=error_message)


def update_category(category_path: str, new_name: Optional[str] = None, new_color: Optional[str] = None) -> APIResponse:
    access_token = AuthHandler.get_access_token()

    category_path_list = category_path.split("/")
    category_id_resp = get_category_id_by_path(category_path_list)
    if not category_id_resp.is_success:
        return category_id_resp

    category_id = category_id_resp.body["categoryId"]
    body = {}
    if new_name:
        body["newName"] = new_name
    if new_color:
        body["color"] = new_color

    resp = requests.patch(
        url=urljoin(BASE_URL, f"categories/{category_id}"),
        headers={"Authorization": "Bearer " + access_token},
        json=body,
    )

    try:
        resp.raise_for_status()
        return APIResponse(is_success=True)
    except HTTPError:
        try:
            error_body = resp.json()
            error_message = error_body["message"]
        except:
            error_message = "Failed to rename a category"

        return APIResponse(is_success=False, error_message=error_message)


def move_category(path: str, new_parent_path: str) -> APIResponse:
    # girok mvcat A/B/C D/E
    access_token = AuthHandler.get_access_token()

    path_list = path.split("/")
    new_parent_path_list = new_parent_path.split("/") if new_parent_path else []

    # 1. Get the category id
    resp = get_category_id_by_path(path_list)
    if not resp.is_success:
        return resp
    category_id = resp.body["categoryId"]

    # 2. Get target parent's id
    resp = get_category_id_by_path(new_parent_path_list)
    if not resp.is_success:
        return resp
    new_parent_category_id = resp.body["categoryId"]

    resp = requests.patch(
        url=urljoin(BASE_URL, f"categories/{category_id}/parent"),
        headers={"Authorization": "Bearer " + access_token},
        json={"newParentId": new_parent_category_id},
    )

    try:
        resp.raise_for_status()
        return APIResponse(is_success=True)
    except HTTPError:
        try:
            error_body = resp.json()
            error_message = error_body["message"]
        except:
            error_message = "Failed to move a category"
        return APIResponse(is_success=False, error_message=error_message)


def get_category_id_by_path(path_list: list[str]) -> APIResponse:
    if len(path_list) == 0:
        return APIResponse(is_success=True, body={"categoryId": None})

    access_token = AuthHandler.get_access_token()
    resp = requests.get(
        url=urljoin(BASE_URL, "categories/id-by-path"),
        headers={"Authorization": "Bearer " + access_token},
        params={"path": path_list},
    )

    try:
        resp.raise_for_status()
        return APIResponse(is_success=True, body=resp.json())
    except HTTPError:
        try:
            error_body = resp.json()
            error_message = error_body["message"]
        except:
            error_message = f"Failed to get a category id of '{path_list}'"
        return APIResponse(is_success=False, error_message=error_message)
