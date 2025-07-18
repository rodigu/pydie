from typing import TypedDict, Protocol, Optional
from polars import DataFrame


type SQLTableName = str


type FetcherID = str
type SourceID = str


class FetcherConfiguration(TypedDict):
    id: FetcherID
    source_id: SourceID
    target_table: SQLTableName


type ConverterID = str


class ConverterConfiguration(TypedDict):
    id: ConverterID
    target_table: SQLTableName
    data: dict | DataFrame


class EngineConfiguration(TypedDict):
    """# Engine configuration specs

    Configuration specifications used through the data integration process.
    """


class Fetcher(Protocol):
    def __call__(
        self,
        configuration: FetcherConfiguration,
        engine_configuration: EngineConfiguration,
    ) -> ConverterConfiguration: ...


class FetcherFetcherAdaptor(Protocol):
    def __call__(
        self,
        configuration: FetcherConfiguration,
        engine_configuration: EngineConfiguration,
    ) -> dict[FetcherID, FetcherConfiguration]: ...


class Integrator(Protocol):
    def __call__(
        self,
        engine_configuration: EngineConfiguration,
    ): ...
