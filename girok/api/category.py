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
    resp = requests.post(
        url=urljoin(BASE_URL, "categories/path"),
        headers={"Authorization": "Bearer " + access_token},
        json={"path": category_path.split("/"), "color": color}
    )

    try:
        resp.raise_for_status()
        return APIResponse(is_success=True, body=resp.json())
    except HTTPError:
        try:
            error_body = resp.json()
            print(error_body)
            error_message = error_body["message"]
        except:
            error_message = "Failed to create a new category"
        
        return APIResponse(is_success=False, error_message=error_message)
    
