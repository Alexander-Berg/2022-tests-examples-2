# pylint: disable=invalid-attribute-name
import dmp_suite.greenplum as gp
from dmp_suite.greenplum.view import View
from test_dmp_suite.greenplum import utils
from dmp_suite.table import abstracttable

from taxi_etl.layer.greenplum.rep.amr.common.table import (
    AggTariffZoneCurTariffClassMskFields, AggTariffZoneCurTariffClassLclFields
)

SQL_TEMPLATE = '''
SELECT currency_code, lcl_scale_dttm, operational_tariff_class_code, scale_name, tariff_geo_zone_code, another_field, some_field FROM {table_daily}
UNION ALL
SELECT currency_code, lcl_scale_dttm, operational_tariff_class_code, scale_name, tariff_geo_zone_code, another_field, some_field FROM {table_weekly}
UNION ALL
SELECT currency_code, lcl_scale_dttm, operational_tariff_class_code, scale_name, tariff_geo_zone_code, another_field, some_field FROM {table_monthly}
'''


@abstracttable
class Fields(gp.GPTable):
    """Аггрегирует до уровня тарифной зоны"""
    some_field = gp.Int(comment='some_field comment')
    another_field = gp.Int(comment='another_field comment')


class TableLclDaily(AggTariffZoneCurTariffClassLclFields, Fields):
    """Аггрегирует до уровня тарифной зоны и операционного класса тарифа. Временные скейлы для агрегации определяются по местному времени. Дневной скейл"""
    __distributed_by__ = gp.Distribution('tariff_geo_zone_code', 'lcl_scale_dttm', 'operational_tariff_class_code')
    __partition_scale__ = gp.YearPartitionScale('lcl_scale_dttm', start='2015-12-01')
    __layout__ = utils.TestLayout('table_lcl_daily')


class TableMskMonthly(AggTariffZoneCurTariffClassMskFields, Fields):
    """Аггрегирует до уровня тарифной зоны и операционного класса тарифа. Временные скейлы для агрегации определяются по московскому времени. Месячный скейл"""
    __distributed_by__ = gp.Distribution('tariff_geo_zone_code', 'msk_scale_dttm', 'operational_tariff_class_code')
    __partition_scale__ = gp.YearPartitionScale('msk_scale_dttm', start='2015-12-01')
    __layout__ = utils.TestLayout('table_lmsk_monthly')


class ViewLcl(View, AggTariffZoneCurTariffClassLclFields, Fields):
    """Аггрегирует до уровня тарифной зоны и операционного класса тарифа. Временные скейлы для агрегации определяются по местному времени"""
    __layout__ = utils.TestLayout('view_lcl')
    __query__ = SQL_TEMPLATE
