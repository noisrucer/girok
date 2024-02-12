from urllib.parse import urljoin

import requests
from requests import HTTPError

from girok.api.entity import APIResponse
from girok.constants import BASE_URL


def verify_access_token(access_token: str) -> bool:
    resp = requests.get(
        url=urljoin(BASE_URL, "tags"),
        headers={"Authorization": "Bearer " + access_token}
    )
    return resp.status_code == 200


def send_verification_code(email: str) -> APIResponse:
    resp = requests.post(url=urljoin(BASE_URL, "auth/verification-code"), json={"email": email})

    try:
        resp.raise_for_status()
        return APIResponse(is_success=True)
    except HTTPError as e:
        print(e)
        error_body = resp.json()
        error_message = error_body["message"]
        return APIResponse(is_success=False, error_message=error_message)


def verify_verification_code(email: str, verification_code: str) -> APIResponse:
    resp = requests.post(
        url=urljoin(BASE_URL, "auth/verification-code/check"),
        json={"email": email, "verificationCode": verification_code},
    )

    try:
        resp.raise_for_status()
        return APIResponse(is_success=True)
    except HTTPError as e:
        error_body = resp.json()
        error_message = error_body["message"]
        return APIResponse(is_success=False, error_message=error_message)


def register(email: str, verification_code: str, password: str) -> APIResponse:
    resp = requests.post(
        url=urljoin(BASE_URL, "sign-up"),
        json={
            "email": email,
            "verificationCode": verification_code,
            "password": password,
        },
    )

    try:
        resp.raise_for_status()
        return APIResponse(is_success=True)
    except HTTPError as e:
        try:
            error_body = resp.json()
            error_message = error_body["message"]
        except:
            error_message = "Registration failed"

        return APIResponse(is_success=False, error_message=error_message)


def login(email: str, password: str) -> APIResponse:
    resp = requests.post(url=urljoin(BASE_URL, "login"), json={"email": email, "password": password})

    try:
        resp.raise_for_status()
        return APIResponse(is_success=True, body=resp.json())
    except HTTPError as e:
        try:
            error_body = resp.json()
            error_message = error_body["message"]
        except:
            error_message = "Login failed"

        return APIResponse(is_success=False, error_message=error_message)
