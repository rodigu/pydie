from typing import TypedDict, Protocol
from pandas import DataFrame

type SQLTableName = str


class EngineConfiguration(TypedDict):
    """# Engine configuration specs

    Configuration specifications used through the data integration process.
    """


type FetcherID = str


class FetcherConfiguration(TypedDict):
    """# Configuration specs for data fetching functions"""

    target_table: SQLTableName


type ConverterID = str


class ConverterConfiguration(TypedDict):
    """# Configuration specs for data conversion functions"""

    destination_table: str
    data: dict | DataFrame


type IntegratorID = str


class IntegratorConfiguration(TypedDict):
    """# Configuration specs for the SQL DB integrator"""

    db_connection_string: str


class Converter(Protocol):
    def __call__(
        self,
        data: dict[FetcherID, ConverterConfiguration],
        engine: EngineConfiguration,
    ) -> list[IntegratorConfiguration]: ...


class Fetcher(Protocol):
    def __call__(
        self, connection: FetcherConfiguration, engine: EngineConfiguration
    ) -> ConverterConfiguration: ...
