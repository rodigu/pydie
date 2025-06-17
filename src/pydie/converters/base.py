from dataclasses import dataclass
from pandas import DataFrame
from typing import Protocol


@dataclass
class ReceiverConverterInterface:
    table: str
    key: str
    data: DataFrame | dict


class Converter(Protocol):
    def __call__(self, data: ReceiverConverterInterface):
        pass
