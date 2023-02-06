from dmp_suite.greenplum import GPTable, GPEtlTable

from taxi_etl.layer.greenplum.rep.demand.agg_tariff_zone_demand_session_metric.common.table import Fields as DSFields
from taxi_etl.layer.greenplum.rep.finance.agg_tariff_zone_metric.common.table import Fields as FinanceFields
from taxi_etl.layer.greenplum.rep.finance.agg_tariff_zone_candidate_metric.common.table import Fields as CandidateFields
from taxi_etl.layer.greenplum.rep.finance.agg_tariff_zone_dlos_metric.common.table import Fields as DlosFields
from taxi_etl.layer.greenplum.rep.finance.agg_tariff_zone_sh_metric.common.table import Fields as SHFields
from taxi_etl.layer.greenplum.rep.finance.agg_tariff_zone_subsidy_metric.common.table import Fields as SubsidyFields

from taxi_etl.layer.greenplum.rep.amr.dm_geo_node_plan.common.table import Fields as PlanFields
from taxi_etl.layer.greenplum.rep.amr.dm_geo_node_fact.common.table import Fields as FactFields
from taxi_etl.layer.greenplum.rep.amr.dm_geo_node_forecast.common.table import Fields as ForecastFields

from taxi_etl.layer.greenplum.rep.amr.agg_executor_unique_metric.common.table import FieldsExecutorUniqueMetric
from taxi_etl.layer.greenplum.rep.amr.dm_geo_node_unique.common.table import Fields as UniqueFields


FIELDS = [
    DSFields,
    FinanceFields,
    CandidateFields,
    DlosFields,
    SHFields,
    SubsidyFields,
    PlanFields,
    FactFields,
    ForecastFields,
    FieldsExecutorUniqueMetric,
    UniqueFields,
]


def test_unique_names_in_fields():
    fields = [fld.name for cls in FIELDS for fld in cls.fields()]
    deduplicated = list(set(fields))
    assert len(fields) == len(deduplicated), 'error: field names collision in table classes'


def test_inheritance_of_fields():
    for cls in FIELDS:
        assert issubclass(cls, GPTable), f'error: {cls} should be subclass of GPTable'
        assert not issubclass(cls, GPEtlTable), f'error: {cls} should NOT be subclass of GPEtlTable'
