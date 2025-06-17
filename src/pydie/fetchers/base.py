from typing import Protocol
from datetime import datetime
from dataclasses import dataclass


@dataclass
class EntryWithDatetime:
    id: str | int
    dt: datetime


@dataclass
class LastIntegrationMeta:
    dt_inclusion: EntryWithDatetime
    dt_update: EntryWithDatetime


class DataFetchFunction:
    def __call__(self, connection_auth: dict, last_integration: LastIntegrationMeta):
        raise NotImplementedError()


class BaseFetcher:
    """# BaseFetcher class

    Fetchers connect to a data source (SQL, REST, etc)
    and fetch their data to be sent to a Converter,
    which turns it into a SQL-ready data format.
    """

    source_connection_settings: dict
