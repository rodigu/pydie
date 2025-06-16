import pandas as pd
from typing import TypedDict
from datetime import datetime


class EntryDatetime(TypedDict):
    id: str | int
    dt: datetime


class LastIntegrationMeta(TypedDict):
    dt_inclusion: EntryDatetime
    dt_update: EntryDatetime
    dt_deletion: EntryDatetime


class DataRetrievalFunction:
    def __call__(
        self, connection_meta: dict, last_integration: LastIntegrationMeta
    ) -> pd.DataFrame:
        """Base function class for data fetchers

        :param dict connection_meta: metadata needed to complete connection, i.e. authentication data
        :param LastIntegrationMeta last_integration: last integration metadata
        :return pd.DataFrame: dataframe with resulting data fetch
        """
        pass


class DataFrameColumn(TypedDict):
    name: str
    type: str


class BaseIntegrator:
    """
    # Base integrator class
    """

    source_config: dict
    dataframe_columns: list[DataFrameColumn]
    data_endpoints: dict[str, DataRetrievalFunction]

    def __init__(
        self,
        source_config: dict,
        dataframe_columns: list[DataFrameColumn],
    ):
        self.source_config = source_config
        self.dataframe_columns = dataframe_columns
        self.data_endpoints = dict()
        self._initialize()

    def _initialize(self):
        """Initialize any particulars of the child class here.

        :raises NotImplementedError:
        """
        raise NotImplementedError("_initialize needs to be implemented by child class.")

    def add_endpoint(self, endpoint_id: str, retrieval_function: DataRetrievalFunction):
        self.data_endpoints.update({endpoint_id: retrieval_function})
