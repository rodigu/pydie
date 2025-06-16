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
