from pydie.integrator.base import (
    BaseIntegrator,
    DataRetrievalFunction,
    LastIntegrationMeta,
)
from pydie.integrator.open_api_config import OpenAPISpecification, OpenAPIConnectionMeta
import pandas as pd
from requests import get, put, post, delete, Response


class RequestFunction(DataRetrievalFunction):
    def __call__(
        self,
        connection_meta: OpenAPIConnectionMeta,
        last_integration: LastIntegrationMeta,
    ) -> pd.DataFrame:
        raise NotImplementedError("RequestFunction.__call__ not implemented.")


class GenericGET:
    """
    # Generic GET request
    """

    def __call__(self, url: str, headers=dict(), parameters=None) -> Response:
        if "User-Agent" not in headers:
            headers.update(
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0"
                }
            )
        return get(url=url, headers=headers, params=parameters)


class GenericMOD:
    def __call__(
        self, func: callable, url: str, headers=dict(), json: dict | list = None
    ) -> Response:
        if "User-Agent" not in headers:
            headers.update(
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:138.0) Gecko/20100101 Firefox/138.0"
                }
            )
        return func(url=url, headers=headers, json=json)


class GenericPUT(GenericMOD):
    """
    # Generic PUT request
    """

    def __call__(self, url: str, headers=dict(), json: dict | list = None) -> Response:
        super().__call__(put, url, headers, json)


class GenericDELETE(GenericMOD):
    """
    # Generic DELETE request
    """

    def __call__(self, url: str, headers=dict(), json: dict | list = None) -> Response:
        super().__call__(delete, url, headers, json)


class GenericPOST(GenericMOD):
    """
    # Generic POST request
    """

    def __call__(self, url: str, headers=dict(), json: dict | list = None) -> Response:
        super().__call__(post, url, headers, json)


class OpenAPI(BaseIntegrator):
    """
    # Integrator for REST APIs with the OpenAPI specs implementation
    """

    source_config: OpenAPISpecification
    data_endpoints: dict[str, RequestFunction]

    def _initialize(self):
        pass
