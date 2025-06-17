from pydie.integrator.base import (
    BaseIntegrator,
    DataRetrievalFunction,
    LastIntegrationMeta,
)
from pydie.integrator.open_api_config import (
    OpenAPISpecification,
    OpenAPIConnectionMeta,
    OpenAPIIntegrationMeta,
)
import pandas as pd
from requests import get, put, post, delete, Response


class RequestFunction(DataRetrievalFunction):
    def __call__(
        self,
        connection_meta: OpenAPIConnectionMeta,
        last_integration: LastIntegrationMeta,
    ) -> dict[str, pd.DataFrame]:
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

    ## OpenAPI specification

    The dictionary property `source_config` expects an OpenAPI specs dictionary extracted from a YAML or a JSON.

    The OpenAPI specs should have been edited using the following extension to the 3.0 specification.

    ## OpenAPI 3.0 Extension

    The following extensions to the OpenAPI specification exist to support the data integration into a SQL database.

    ### Numbers

    The `format` hint should have a SQL-valid type.

    ### Strings

    Strings without a `maxLength` will be converted into `VARCHAR(MAX)`.

    ### Datetime strings

    Datetimes that do not follow the suggested OAPI 3.0 [RFC 3339, section 5.6](https://datatracker.ietf.org/doc/html/rfc3339#section-5.6)
    date formatting, should have a `pattern` property specified with [Python's date format codes](https://docs.python.org/3/library/datetime.html#format-codes).

    ### Objects and sub-tables

    Objects will be converted to sub-tables.
    """

    source_config: OpenAPISpecification
    integration_meta: OpenAPIIntegrationMeta
    data_endpoints: dict[str, RequestFunction]

    def _initialize(self):
        pass
