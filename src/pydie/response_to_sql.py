import pandas as pd
from dateutil import parser
from datetime import datetime
from dataclasses import dataclass


@dataclass
class SQLItem:
    value: str
    type: str


def get_path_response(schema: dict, path: str) -> dict:
    return schema["paths"][path]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]["properties"]


def get_sql(schema: dict, path: str, property_name: str, property_value: str):
    property_schema = get_path_response(schema, path)[property_name]

    type: str = property_schema.get("type")

    format: str = property_schema.get("format")
    pattern: str = property_schema.get("pattern")
    max_length: int = property_schema.get("maxLength")

    if max_length is not None:
        return SQLItem(property_value, f"VARCHAR({max_length})")
    if pattern is not None and "date" in format:
        return SQLItem(datetime.strptime(property_value, pattern), "DATETIME")
    if format == "date-time":
        return SQLItem(parser.parse(property_value), "DATETIME")
    if type == "string":
        return SQLItem(f"N'{property_value}'", "VARCHAR(MAX)")
    if type == "boolean":
        return SQLItem(int(property_value), "BIT")
    raise Exception(f"SQL parsing cannot handle {type}: {path} > {property_value}")


def parse_response_into_sql(
    schema: dict, path: str, property_name: str, response: dict
):
    return {
        prop: get_sql(schema, path, property_name, value)
        for prop, value in response.items()
    }
