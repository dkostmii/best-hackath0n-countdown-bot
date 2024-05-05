import json
from typing import Optional


class ReadJSONException(Exception):
    def __init__(self, json_filename: str, additional_info: Optional[str] = None):
        if additional_info:
            super().__init__(f"Error reading JSON file {json_filename}. Additional info: {additional_info}")
        else:
            super().__init__(f"Error reading JSON file {json_filename}")


def read_json(json_filename: str) -> dict:
    try:
        with open(json_filename, mode="r") as f:
            result = json.load(f)

        if not isinstance(result, dict):
            raise ReadJSONException(json_filename=json_filename, additional_info="Expected result to be dict")
        
        return result
    except OSError as e:
        raise ReadJSONException(json_filename=json_filename, additional_info="OSError occurred") from e
