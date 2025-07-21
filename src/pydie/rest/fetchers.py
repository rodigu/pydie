import pydie.rest.interfaces as rest
from requests import Response
from pydie.utils import get_nested_value, parse_path_parameters, inject_parameter_values


def fetcher(
    configuration: rest.FetcherConfiguration,
    engine_configuration: rest.EngineConfiguration,
) -> rest.ConverterConfiguration:
    request_function = rest.REQUEST_FUNCTIONS[configuration["request_function_name"]]
    response: Response = request_function(
        url=configuration["id"], **configuration["request_function_parameters"]
    )
    if response.status_code != 200:
        raise BaseException(
            f"Failed request to [{configuration['id']}] (status {response.status_code}).\n"
            + f"Details: {response.reason}."
        )
    data = response.json()
    dependent_requests = extract_parametrizable_properties_into_dependent_requests(
        data=data,
        parametrizable_properties=configuration["response_parametrizable_properties"],
    )

    return {
        "dependent_requests_parameters": dependent_requests,
        "target_table": configuration["target_table"],
    }


def extract_parametrizable_properties_into_dependent_requests(
    data: dict, parametrizable_properties: rest.ParametrizablePropertyMapping
) -> rest.DependentRequestMapping:
    dependent_requests: rest.DependentRequestMapping = dict()
    for parameter_key, property in parametrizable_properties.items():
        fetcher_id = property["fetcher_id"]
        if fetcher_id not in dependent_requests:
            dependent_requests[fetcher_id] = {"id": fetcher_id, "parameters": dict()}
        data_at_address = get_data_at_address(data=data, address=property["address"])
        dependent_requests[fetcher_id]["parameters"].update(
            {
                property["parameter_key"]: data_at_address
                if isinstance(data_at_address, list)
                else [data_at_address]
            }
        )
        dependent_fetcher_id = inject_parameter_values(path=fetcher_id)
        property["fetcher_id"]
        property["parameter_key"]
    # TODO, set target table to raw (unparametrized) FetcherID


def path_maker(
    base_url: str,
    path: str,
    path_parameters: dict[rest.PathParameterName, rest.ParametrizableValue] = None,
) -> str:
    """# REST API endpoint path maker

    :param str base_url: API base URL
    :param str path: API path
    :param list[ParametrizableResponseProperty] path_parameters: ID replacements, defaults to None
    :return str: full API enpoint URL
    """
    formatted_path = path
    if path_parameters is not None:
        for parameter_name, parameter_value in path_parameters.items():
            formatted_path = formatted_path.replace(
                "{" + parameter_name + "}", parameter_value
            )
    return f"{base_url}{formatted_path}"


def dependency_injector(
    response_properties: rest.ResponsePropertiesToParametrize,
    dependent_requests: dict[rest.Path, rest.FetcherConfiguration],
    response_data: rest.ResponseData,
) -> dict[rest.Path, rest.FetcherConfiguration]:
    """Extracts `response_properties` from `response_data` and injects them into `dependent_requests`.

    :param rest.ResponsePropertiesToParametrize response_properties: properties in `response_data` to be parametrized into dependent requests
    :param dict[rest.Path, rest.FetcherConfiguration] dependent_requests: requests that depend on values from `response_data`
    :param rest.ResponseData response_data: response data from parent request
    :return dict[rest.Path, rest.FetcherConfiguration]:
    """
    for path, property in response_properties.items():
        data: list[dict] = get_data_at_address(
            data=response_data, address=property["parametrizable_proterty_address"]
        )
        key = property["parametrizable_key"]
        parameter_name = property["path_parameter_name"]

        if "target_table" not in dependent_requests[path]:
            dependent_requests[path]["target_table"] = path
        if dependent_requests[path]["parametrizable_values"] is None:
            dependent_requests[path]["parametrizable_values"] = dict()
        dependent_requests[path]["parametrizable_values"].update(
            {parameter_name: [v[key] for v in data]}
        )
    return dependent_requests


def dependency_extractor(
    converter_configuration: rest.ConverterConfiguration,
) -> list[rest.FetcherConfiguration]:
    """Splits dependent requests in converter configuration into separate fetcher configurations

    :param rest.ConverterConfiguration converter_configuration: converter configuration output from a fetcher
    :return list[rest.FetcherConfiguration]:
    """


def get_data_at_address(data: dict | list, address: rest.ResponsePropertyKey):
    if address is None or type(data) is list:
        return data
    index = 0
    result = data
    while index < len(address):
        result = result[address[index]]
        index += 1
    return result


def fetcher(
    connection: rest.FetcherConfiguration, engine: rest.EngineConfiguration
) -> rest.ConverterConfiguration:
    """Fetches from a REST API using the given configurations.

    :param rest.FetcherConfiguration connection: particular API path endpiont to connect to
    :param rest.EngineConfiguration engine: general REST API configurations
    :raises BaseException: on `status_code!=200`
    :return rest.ConverterConfiguration: specifications to be fed into a converter
    """
    url = path_maker(
        base_url=engine["base_url"],
        path=connection["path"],
        path_parameters=connection.get("parametrizable_values"),
    )

    connection.get("request_function_parameters", {}).get("headers", {}).update(
        engine["default_headers"]
    )

    response = connection["request_function"](
        url=url, **connection.get("request_function_parameters", {})
    )

    if response.status_code != 200:
        raise BaseException(url, response, response.reason)

    response_data = response.json()

    if "top_level_data_address" in connection:
        response_data = get_data_at_address(
            data=response_data, address=connection["top_level_data_address"]
        )

    dependencies = dependency_injector(
        response_data=response_data,
        response_properties=connection["response_properties_to_parametrize"],
        dependent_requests=connection["dependent_requests"],
    )

    return {
        "target_table": connection["target_table"],
        "data": response_data,
        "dependent_requests": dependencies,
    }


def dependent_fetcher(
    connection: rest.FetcherConfiguration, engine: rest.EngineConfiguration
) -> rest.ConverterConfiguration: ...
