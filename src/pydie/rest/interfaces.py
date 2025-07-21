import pydie.interfaces as interfaces
from typing import Optional, TypedDict, Protocol
from requests import Response, get, put, post, delete


class APIPath:
    type ParameterKey = str
    type ParameterValue = str


class RequestParameters(TypedDict):
    """Base request parameters class.
    Should be instanced into the particular REST API implementation to specify the necessary parameters.
    """


class RequestJSON(TypedDict):
    """Base request JSON payload class."""


class RequestFunctionParameters(TypedDict):
    """Parameters for one of Python's `request` functions (GET, PUT, etc) parameters."""

    headers: dict
    parameters: Optional[RequestParameters]
    json: Optional[RequestJSON]


class ResponseData(TypedDict):
    """Base response data JSON."""


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


REQUEST_FUNCTIONS = {"get": get, "put": put, "post": post, "delete": delete}


class ParametrizableProperty(TypedDict):
    parameter_key: APIPath.ParameterKey
    address: list[int]
    fetcher_id: interfaces.FetcherID


class DependentRequest(TypedDict):
    id: interfaces.FetcherID
    parameters: dict[APIPath.ParameterKey, list[APIPath.ParameterValue]]


type ParametrizablePropertyMapping = dict[APIPath.ParameterKey, ParametrizableProperty]
type DependentRequestMapping = dict[interfaces.FetcherID, DependentRequest]


class FetcherConfiguration(interfaces.FetcherConfiguration):
    """
    The `id` property (`FetcherID` type) should be a valid api endpoint.
    """

    request_function_parameters: RequestFunctionParameters
    request_function_name: str
    response_parametrizable_properties: Optional[ParametrizablePropertyMapping]


class ConverterConfiguration(interfaces.FetcherConfiguration):
    dependent_requests_parameters: Optional[DependentRequestMapping]


class EngineConfiguration(interfaces.EngineConfiguration):
    base_url: str
