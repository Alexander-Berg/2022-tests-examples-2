# coding: utf-8
from dmp_suite.greenplum import etl_table, GPTable, Datetime, String
from dmp_suite.greenplum.table import LayeredLayout


class EtlTable(etl_table.GPEtlTable):
    __layout__ = LayeredLayout(name='test', layer='test')


class TableWithEtlProcessedDttm(GPTable):
    __layout__ = LayeredLayout(name='test', layer='test')

    dttm = Datetime(name=etl_table.ETL_PROCESSED_DTTM_FIELD)


class TableWithoutEtlProcessedDttm(GPTable):
    __layout__ = LayeredLayout(name='test', layer='test')

    dttm = String(name=etl_table.ETL_PROCESSED_DTTM_FIELD)


class NotEtlTable(GPTable):
    __layout__ = LayeredLayout(name='test', layer='test')


def test_is_etl_table():
    assert etl_table.is_etl_table(EtlTable)
    assert etl_table.is_etl_table(TableWithEtlProcessedDttm)
    assert not etl_table.is_etl_table(NotEtlTable)
    assert not etl_table.is_etl_table(TableWithoutEtlProcessedDttm)
