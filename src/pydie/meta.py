from dataclasses import dataclass
from integrator.base import LastIntegrationMeta, BaseIntegrator


@dataclass
class SQLTargetMeta:
    table: str
    last_datetime: LastIntegrationMeta


class IntegrationMeta:
    """
    # Integration Metadata class
    """

    def __init__(self, integrator: BaseIntegrator, sql_target: SQLTargetMeta):
        self.integrator = integrator
        self.target = sql_target
