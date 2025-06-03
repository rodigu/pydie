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
        if property_value == "NULL":
            return SQLItem(property_value, f"VARCHAR({max_length})")
        return SQLItem(f"N'{property_value}'", f"VARCHAR({max_length})")
    if pattern is not None and "date" in format:
        if property_value == "NULL":
            return SQLItem(property_value, "DATETIME")
        return SQLItem(datetime.strptime(property_value, pattern), "DATETIME")
    if format == "date-time":
        if property_value == "NULL":
            return SQLItem(property_value, "DATETIME")
        return SQLItem(parser.parse(property_value), "DATETIME")
    if type == "string":
        if property_value == "NULL":
            return SQLItem(property_value, "VARCHAR(MAX)")
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


def parse_response_into_sql(schema: dict, response: dict) -> dict[str, SQLItem]:
    """Parses API response into `SQLItem` instances

    :param dict schema: API response schema for given property
    :param str property_name: name of the property to be parsed (must be in `schema`)
    :param dict response: API response dictionary
    :return dict[str, SQLItem]:


    >>> r = {
    ...     "codigo": 20384029,
    ...     "localizador": "LB20384029",
    ...     "data_hora": "03/01/2024 15:10:00",
    ...     "status": "A",
    ...     "idorigem": "1010",
    ...     "cod_local_venda": 624,
    ...     "ponto_venda": "https://qa.limber.net.br/",
    ...     "local_venda": "AGÊNCIA DEMONSTRAÇÃO",
    ...     "nome_titular": "NOME DO TITULAR",
    ...     "email_titular": "emailtitular@email.com",
    ...     "fone_titular": "+55 46999990000",
    ...     "doc_titular": "12345678910",
    ...     "nascimento_titular": "10/11/2003",
    ...     "codigo_promocional": None,
    ...     "total_liquido": 0.1,
    ...     "idioma": "PT",
    ...     "data_hora_inc": "2024-01-03T18:07:32.344Z",
    ...     "pedido_de_cancelamento": False,
    ...     "ip_comprador": "111.111.111.11",
    ...     "tag_nao_enviada": None,
    ...     "quantidade": 1,
    ...     "importante": False,
    ...     "tick_nome": None,
    ...     "tick_terminal": None,
    ...     "tick_term_descricao": None,
    ...     "formas_pag_desc": "Cartão",
    ...     "nome_adquirente": "NOME ADQUIRENTE",
    ...     "data": "03/01/2024",
    ...     "hora": "15:10:00",
    ...     "data_hora_utilizacao": None,
    ...     "status_desc": "Aprovada",
    ... }
    >>> s = {
    ...     "codigo": {"type": "number", "description": "Código único da venda em questão", "format": "int32"},
    ...     "status": {"type": "string", "description": "Status"},
    ...     "localizador": {
    ...         "type": "string",
    ...         "description": "Código único da venda com prefixo",
    ...     },
    ...     "data_hora": {
    ...         "type": "string",
    ...         "description": "Data e hora do registro da venda formatada",
    ...     },
    ...     "idorigem": {
    ...         "type": "string",
    ...         "description": "Código da venda no estabelecimento de origem",
    ...     },
    ...     "cod_local_venda": {
    ...         "type": "number",
    ...         "description": "Código do estabelecimento que realizou a venda",
    ...     },
    ...     "ponto_venda": {
    ...         "type": "string",
    ...         "description": "URL do e-commerce que realizou a venda",
    ...     },
    ...     "local_venda": {
    ...         "type": "string",
    ...         "description": "Nome do estabelecimento que realizou a venda",
    ...     },
    ...     "nome_titular": {"type": "string", "description": "Nome do titular da venda"},
    ...     "email_titular": {"type": "string", "description": "E-mail do titular da venda"},
    ...     "fone_titular": {"type": "string", "description": "Telefone do titular da venda"},
    ...     "doc_titular": {"type": "string", "description": "Documento do titular da venda"},
    ...     "nascimento_titular": {
    ...         "type": "string",
    ...         "description": "Data de nascimento do titular da venda formatada",
    ...     },
    ...     "codigo_promocional": {
    ...         "type": "string",
    ...         "description": "Código promocional que foi aplicado para a venda",
    ...     },
    ...     "total_liquido": {"type": "number", "description": "Valor total da venda"},
    ...     "idioma": {"type": "string", "description": 'Idioma da venda ("PT", "EN", "ES")'},
    ...     "data_hora_inc": {
    ...         "type": "string",
    ...         "format": "date-time",
    ...         "description": "Data e hora do registro da venda UTC",
    ...     },
    ...     "data_hora_utilizacao": {
    ...         "type": "string",
    ...         "format": "date-time",
    ...         "description": "Data e hora da utilizacao UTC",
    ...     },
    ...     "pedido_de_cancelamento": {
    ...         "type": "boolean",
    ...         "description": "Se a venda tem algum item com pedido de cancelamento",
    ...     },
    ...     "ip_comprador": {"type": "string", "description": "IP do dispositivo do comprador"},
    ...     "tag_nao_enviada": {
    ...         "type": "string",
    ...         "description": 'Parâmetro indica se o pagamento foi enviado para o TagManager, quando é "null" o pagamento foi enviado. Se for "true", significa que o pagamento ainda não foi enviado para o TagManager',
    ...     },
    ...     "quantidade": {"type": "number", "description": "Quantidade de itens da venda"},
    ...     "importante": {"type": "boolean", "description": "Quantidade de itens da venda"},
    ...     "tick_nome": {
    ...         "type": "string",
    ...         "description": "Nome do cadastro do Tick Ingressos",
    ...     },
    ...     "tick_terminal": {
    ...         "type": "string",
    ...         "description": "Identificador do dispositivo que roda o aplicativo do Tick Ingressos e realizou a venda",
    ...     },
    ...     "tick_term_descricao": {
    ...         "type": "string",
    ...         "description": "Descrição do dispositivo que roda o aplicativo do Tick Ingressos e realizou a venda",
    ...     },
    ...     "formas_pag_desc": {
    ...         "type": "array",
    ...         "description": "Forma(s) de pagamento utilizados na venda",
    ...         "items": {"type": "string"},
    ...     },
    ...     "nome_adquirente": {
    ...         "type": "string",
    ...         "description": "Nome da adquirente de pagamento",
    ...     },
    ...     "data": {"type": "string", "description": "Data da venda formatada - DD/MM/YYYY"},
    ...     "hora": {"type": "string", "description": "Hora da venda formatada - HH:mm:ss"},
    ...     "atrativo_data_nasc": {
    ...         "type": "string",
    ...         "description": "Data de nascimento do visitante (PRIMEIRO ITEM DA VENDA)",
    ...     },
    ...     "data_hora_canc": {
    ...         "type": "string",
    ...         "description": "Data/Hora de cancelamento (PRIMEIRO ITEM DA VENDA)",
    ...     },
    ...     "status_desc": {
    ...         "type": "string",
    ...         "description": "Descrição referente ao status da venda",
    ...     },
    ... }
    >>> parse_response_into_sql(s, r)
    {'codigo': SQLItem(value=20384029, type='INT'), 'localizador': SQLItem(value="N'LB20384029'", type='VARCHAR(MAX)'), 'data_hora': SQLItem(value="N'03/01/2024 15:10:00'", type='VARCHAR(MAX)'), 'status': SQLItem(value="N'A'", type='VARCHAR(MAX)'), 'idorigem': SQLItem(value="N'1010'", type='VARCHAR(MAX)'), 'cod_local_venda': SQLItem(value=624.0, type='FLOAT'), 'ponto_venda': SQLItem(value="N'https://qa.limber.net.br/'", type='VARCHAR(MAX)'), 'local_venda': SQLItem(value="N'AGÊNCIA DEMONSTRAÇÃO'", type='VARCHAR(MAX)'), 'nome_titular': SQLItem(value="N'NOME DO TITULAR'", type='VARCHAR(MAX)'), 'email_titular': SQLItem(value="N'emailtitular@email.com'", type='VARCHAR(MAX)'), 'fone_titular': SQLItem(value="N'+55 46999990000'", type='VARCHAR(MAX)'), 'doc_titular': SQLItem(value="N'12345678910'", type='VARCHAR(MAX)'), 'nascimento_titular': SQLItem(value="N'10/11/2003'", type='VARCHAR(MAX)'), 'codigo_promocional': SQLItem(value='NULL', type='VARCHAR(MAX)'), 'total_liquido': SQLItem(value=0.1, type='FLOAT'), 'idioma': SQLItem(value="N'PT'", type='VARCHAR(MAX)'), 'data_hora_inc': SQLItem(value=datetime.datetime(2024, 1, 3, 18, 7, 32, 344000, tzinfo=tzutc()), type='DATETIME'), 'pedido_de_cancelamento': SQLItem(value=0, type='BIT'), 'ip_comprador': SQLItem(value="N'111.111.111.11'", type='VARCHAR(MAX)'), 'tag_nao_enviada': SQLItem(value='NULL', type='VARCHAR(MAX)'), 'quantidade': SQLItem(value=1.0, type='FLOAT'), 'importante': SQLItem(value=0, type='BIT'), 'tick_nome': SQLItem(value='NULL', type='VARCHAR(MAX)'), 'tick_terminal': SQLItem(value='NULL', type='VARCHAR(MAX)'), 'tick_term_descricao': SQLItem(value='NULL', type='VARCHAR(MAX)'), 'formas_pag_desc': SQLItem(value='Cartão', type='VARCHAR(MAX)'), 'nome_adquirente': SQLItem(value="N'NOME ADQUIRENTE'", type='VARCHAR(MAX)'), 'data': SQLItem(value="N'03/01/2024'", type='VARCHAR(MAX)'), 'hora': SQLItem(value="N'15:10:00'", type='VARCHAR(MAX)'), 'data_hora_utilizacao': SQLItem(value='NULL', type='DATETIME'), 'status_desc': SQLItem(value="N'Aprovada'", type='VARCHAR(MAX)')}
    """
    return {prop: get_sql(schema, prop, value) for prop, value in response.items()}
