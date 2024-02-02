import json
import os


def read_json(path: str) -> dict:
    with open(path) as f:
        data = json.load(f)
        return data


def write_json(path: str, data: dict):
    with open(path, "w") as f:
        json.dump(data, f)


def update_json(path: str, data: dict):
    with open(path) as f:
        org_data = json.load(f)
        org_data.update(**data)
    write_json(path, org_data)
