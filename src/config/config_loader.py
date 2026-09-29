import json

def load_config(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as file:
        config = json.load(file)

    return config
