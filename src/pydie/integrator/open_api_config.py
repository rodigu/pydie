from typing import TypedDict, NotRequired


class OpenAPIConnectionMeta(TypedDict):
    token: str


class Described(TypedDict):
    description: NotRequired[str]


class Info(TypedDict, Described):
    title: str
    version: str


class Server(TypedDict, Described):
    url: str
    version: str


class Operation(TypedDict, Described):
    tags: list[str]
    summary: str


class Path(TypedDict, Described):
    summary: NotRequired[str]
    get: NotRequired[Operation]
    post: NotRequired[Operation]
    put: NotRequired[Operation]
    patch: NotRequired[Operation]
    delete: NotRequired[Operation]
    head: NotRequired[Operation]
    options: NotRequired[Operation]
    trace: NotRequired[Operation]


class Tag(TypedDict, Described):
    name: str


class SecurityScheme(TypedDict):
    type: str
    scheme: str


class Components(TypedDict):
    securitySchemes: dict[str, SecurityScheme]


class OpenAPISpecification(TypedDict):
    """
    # OpenAPI source specification
    """

    openapi: str
    info: Info
    servers: list[Server]
    components: Components
    tags: list[Tag]
    paths: dict[str, Path]


class IntegrationMetaProperties(TypedDict):
    dt_inclusion: str
    dt_update: str
    id: str


class EndpointMeta(TypedDict):
    """
    # Data integration metadata

    ## Subtables

    The `sub_tables` property specifies any response properties that should become subtables

    ## Omissions

    Any property named on `omit` won't be included in the integration.
    All subtables also won't be included.
    """

    request_function: str
    target_table: str
    omit: list[str]
    sub_tables: dict[str, "EndpointMeta"]
    integration_properties: IntegrationMetaProperties


class OpenAPIIntegrationMeta(TypedDict):
    endpoints: list[EndpointMeta]
