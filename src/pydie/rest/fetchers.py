import interfaces as rest


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


def fetcher_to_fetcher_adaptor(
    converter_configuration: rest.ConverterConfiguration,
) -> list[rest.FetcherConfiguration]: ...


def get_data_at_address(data: dict, address: rest.ResponsePropertyKey):
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

    connection["request_function_parameters"]["headers"].update(
        engine["default_headers"]
    )

    response = connection["request_function"](
        url=url, **connection["request_function_parameters"]
    )

    if response.status_code != 200:
        raise BaseException(response, response.reason)

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
        "destination_table": connection["destination_table"],
        "data": response_data,
        "dependent_requests": dependencies,
    }
