import pandas as pd
from dateutil import parser
from datetime import datetime
from dataclasses import dataclass


@dataclass
class SQLItem:
    value: str
    type: str


def get_sql(schema: dict, property_name: str, property_value: str) -> SQLItem:
    """Converts `property_value` into valid SQL, with a SQL type equivalent to the property type (taken from the schema).

        :param dict schema: valid OpenAPI 3.0 schema for /paths/`[PATH]`/get/responses/200/content/"application/json"/schema/properties/`[PROPRERTY]`
        where `[PATH]` is a valid API path and `[PROPERTY]` is the name of the property name that references `property_value`
        :param str path: OpenAPI API path in `schema` where `property_name` may be found
        :param str property_value: value of the API response property
        :raises Exception: on unhandled API types (`object`, `array`, `null`, `files`)
        :return SQLItem:

    ## Tests
    >>> schema = {
    ...         "data_hora_inc": {
    ...             "type": "string",
    ...             "format": "date-time",
    ...             "description": "Data e hora do registro da venda UTC",
    ...         },
    ...         "total_liquido": {
    ...             "type": "number",
    ...             "description": "Valor total da venda",
    ...             "format": "money",
    ...         },
    ...         "codigo_promocional": {
    ...             "type": "string",
    ...             "description": "Código promocional que foi aplicado para a venda",
    ...             "maxLength": 30,
    ...         },
    ...         "nascimento_titular": {
    ...             "type": "string",
    ...             "description": "Data de nascimento do titular da venda formatada",
    ...             "format": "date",
    ...             "pattern": "%d/%m/%Y",
    ...         },
    ...         "cod_local_venda": {
    ...             "type": "number",
    ...             "description": "Código do estabelecimento que realizou a venda",
    ...             "format": "int32",
    ...         },
    ...         "unhandled_property": {
    ...             "type": "object"
    ...         },
    ...         "another_unhandled_property": {
    ...             "type": "array",
    ...             "items": {
    ...                 "type": "object",
    ...                 "items": {
    ...                     "sample": {
    ...                         "type": "string"
    ...                     }
    ...                 }
    ...             }
    ...         },
    ...         "array_property": {
    ...             "type": "array",
    ...             "items": {
    ...                 "type": "string"
    ...             }
    ...         }
    ...     }
    >>> get_sql(schema, "data_hora_inc", '2024-01-03T18:07:32.344Z')
    SQLItem(value=datetime.datetime(2024, 1, 3, 18, 7, 32, 344000, tzinfo=tzutc()), type='DATETIME')
    >>> get_sql(schema, "total_liquido", 0.1)
    SQLItem(value=0.1, type='money')
    >>> get_sql(schema, "nascimento_titular", "10/11/2003")
    SQLItem(value=datetime.datetime(2003, 11, 10, 0, 0), type='DATETIME')
    >>> get_sql(schema, "codigo_promocional", None)
    SQLItem(value='NULL', type='VARCHAR(30)')
    >>> get_sql(schema, "cod_local_venda", 624)
    SQLItem(value=624, type='INT')
    >>> get_sql(schema, "array_property", ['a','b'])
    SQLItem(value="['a', 'b']", type='VARCHAR(MAX)')

    ### Failing
    >>> get_sql(schema, "inexistent_property", 0)
    Traceback (most recent call last):
    ...
    Exception: inexistent_property not in provided schema
    >>> get_sql(schema, "unhandled_property", 0)
    Traceback (most recent call last):
    ...
    Exception: SQL parsing cannot handle type [object] with format [None]: {'property_name': 'unhandled_property', 'property_value': 0}
    >>> get_sql(schema, "another_unhandled_property", 0)
    Traceback (most recent call last):
    ...
    Exception: SQL parsing cannot handle type [array] with format [None]: {'property_name': 'another_unhandled_property', 'property_value': 0}
    """
    if property_name not in schema:
        raise Exception(f"{property_name} not in provided schema")
    property_schema = schema[property_name]

    type: str = property_schema.get("type")

    format: str = property_schema.get("format")
    pattern: str = property_schema.get("pattern")
    max_length: int = property_schema.get("maxLength")

    if property_value is None:
        property_value = "NULL"

    if type == "array" and property_schema["items"]["type"] in {"number", "string"}:
        return SQLItem(str(property_value), "VARCHAR(MAX)")
    if type == "string" and max_length is not None:
        return SQLItem(property_value, f"VARCHAR({max_length})")
    if pattern is not None and "date" in format:
        return SQLItem(datetime.strptime(property_value, pattern), "DATETIME")
    if format == "date-time":
        return SQLItem(parser.parse(property_value), "DATETIME")
    if type == "string":
        return SQLItem(f"N'{property_value}'", "VARCHAR(MAX)")
    if type == "boolean":
        return SQLItem(int(property_value), "BIT")
    if type == "number" and format == "int32":
        return SQLItem(int(property_value), "INT")
    if type == "number" and format == "int64":
        return SQLItem(int(property_value), "BIGINT")
    if type == "number" and format is None:
        return SQLItem(float(property_value), "FLOAT")
    if type == "number":
        return SQLItem(property_value, format)

    raise Exception(
        f"SQL parsing cannot handle type [{type}] with format [{format}]: {dict(property_name=property_name, property_value=property_value)}"
    )


def parse_response_into_sql(
    schema: dict, path: str, property_name: str, response: dict
):
    return {
        prop: get_sql(schema, path, property_name, value)
        for prop, value in response.items()
    }
