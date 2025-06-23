import interfaces.rest as rest


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


def dependency_adaptor(
    parametrizable_values: dict[
        rest.Path,
        dict[rest.PathParameterName, list[rest.ParametrizableValue]],
    ],
    dependent_requests: dict[rest.Path, rest.FetcherConfiguration],
) -> list[rest.FetcherConfiguration]: ...


def fetcher(
    connection: rest.FetcherConfiguration, engine: rest.EngineConfiguration
) -> rest.ConverterConfiguration:
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

    return response.json()
