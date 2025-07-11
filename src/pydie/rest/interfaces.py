import pydie.interfaces as interfaces
from typing import Optional, TypedDict, Protocol
from requests import Response

# API path string (e.g. "/api/users/{userID}/items")
type Path = str
# API path parameter string (e.g. "userID")
type PathParameterName = str
# API response data key
type ResponsePropertyKey = list[str | int]
type ResponsePropertyValue = str
# Object key from a list of consistent objects.
# The values for this key are used as parameters for an API Path string
type ParametrizableKey = str
type ParametrizableValue = ResponsePropertyValue


class RequestParameters(TypedDict): ...


class RequestJSON(TypedDict): ...


class RequestFunctionParameters(TypedDict):
    headers: dict
    parameters: Optional[RequestParameters]
    json: Optional[RequestJSON]


class ResponseData(TypedDict): ...


class RequestFunction(Protocol):
    """Simplifind `requests` library function type
    (get, put, post, delete).
    """

    def __call__(
        self,
        url: str,
        headers: dict,
        parameters: Optional[dict] = None,
        json: Optional[dict] = None,
    ) -> Response: ...


class ParametrizableResponseProperty(TypedDict):
    """
    # Parametrizable property key

    Properties in a response that serve as parameters to other requests.

    ## Path parameter name

    The identifier for the parameter in a path.
    E.g. `userID` in `/api/users/{userID}`

    ## Parametrizable property address

    Adress with to the property containing the parametrizable property.
    The address it a `ResponsePropertyKey`, which is a list of dictionary keys
    which allow access to a response property, even when they are layered.

    The value of said property should be a list of consistent objects.

    ## Parametrizable key

    Key that can be turned into another request's parameter.

    ## Example

    For the path `/api/users/all`, a sample response is:

    ```json
    {"data": {"users": [{"id": 1}, {"id": 2}]}, "requestDate": "date", "responseTime": 10}
    ```

    The property `response['data']['users']` has parametrizable keys (`id`) in the objects in its list.

    A `ParametrizableResponseProperty` would look like:

    ```py
    sample: ParametrizableResponseProperty = {
        'parametrizable_key': 'id',
        'parametrizable_proterty_address': ['data','users'],
        'path_parameter_name': 'userID'
    }
    ```
    """

    path_parameter_name: PathParameterName
    parametrizable_proterty_address: ResponsePropertyKey
    parametrizable_key: ParametrizableKey


type ResponsePropertiesToParametrize = dict[Path, ParametrizableResponseProperty]


class FetcherConfiguration(interfaces.FetcherConfiguration):
    """
    ## top_level_data_address

    When response data is not found at the top level of the response (e.g. it comes with metadata on the request),
    `top_level_data_address` contains the address for the actual response data.
    """

    path: Path
    request_function_parameters: RequestFunctionParameters
    request_function: RequestFunction
    response_properties_to_parametrize: Optional[ResponsePropertiesToParametrize]
    parametrizable_values: Optional[dict[PathParameterName, ParametrizableValue]]
    dependent_requests: Optional[dict[Path, "FetcherConfiguration"]]
    destination_table: interfaces.SQLTableName
    top_level_data_address: Optional[ResponsePropertyKey]


class ConverterConfiguration(interfaces.ConverterConfiguration):
    dependent_requests: Optional[dict[Path, FetcherConfiguration]]
    data: ResponseData


class SubTable(TypedDict):
    path: Path
    subtable_address: ResponsePropertyKey
    destination_table: interfaces.SQLTableName
    id_property: ResponsePropertyKey


class EngineConfiguration(interfaces.EngineConfiguration):
    base_url: str
    default_headers: dict
    sub_tables: dict[Path, dict[ResponsePropertyKey]]
