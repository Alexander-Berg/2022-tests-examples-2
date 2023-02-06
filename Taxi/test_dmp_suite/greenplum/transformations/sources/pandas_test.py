import pandas as pd
import pytest

from connection import greenplum as gp
from dmp_suite.greenplum import Int, String, etl_table
from dmp_suite.greenplum.transformations import Transformation
from dmp_suite.greenplum.transformations.sources import SqlSource
from dmp_suite.greenplum.transformations.sources.pandas import PandasSource, _DataFrameSource
from test_dmp_suite.greenplum.utils import GreenplumTestTable, external_gp_layout


class ResultTable(GreenplumTestTable):
    __layout__ = external_gp_layout()
    foo = Int()
    bar = String()


class EtlResultTable(ResultTable, etl_table.GPEtlTable):
    pass


class DummyTransformation(Transformation):
    def run(self):
        pass


def ensure_etl_table_format(data, table):
    if etl_table.is_etl_table(table):
        for row in data:
            row[etl_table.ETL_PROCESSED_DTTM_FIELD] = None
    return data


@pytest.mark.slow('gp')
@pytest.mark.parametrize('table', [ResultTable, EtlResultTable])
def test_snapshot(table):
    sql = '''create temp table result_table on commit drop as
    select 1 as id, 'aaa' as value, '2019-01-01'::date as dt'''

    def transform(df):
        return df.rename(columns={'id': 'foo', 'value': 'bar'})

    source = PandasSource(
        sources={'df': SqlSource.from_string(sql)},
        transform=transform,
    )

    expected = ensure_etl_table_format([dict(foo=1, bar='aaa')], table)

    transformation = DummyTransformation(source=source, target=table)

    source.prepare(transformation=transformation)

    with source.source_table(transformation=transformation) as src:
        sql = 'SELECT * FROM {}'
        actual = [dict(row) for row in gp.connection.query(sql.format(src))]
        assert expected == actual


@pytest.mark.slow('gp')
@pytest.mark.parametrize('table', [ResultTable, EtlResultTable])
def test_wrong_column(table):
    sql = '''create temp table result_table on commit drop as
    select 1 as id, 'aaa' as value, '2019-01-01'::date as dt'''

    def transform(df):
        return df.rename(columns={'id': 'foo', 'value': 'baq'})

    with pytest.raises(KeyError):
        source = SqlSource.from_string(sql)
        source = PandasSource(sources={'df': source},
                              transform=transform)

        transformation = DummyTransformation(source=source, target=table)

        source.prepare(transformation=transformation)

        with source.source_table(transformation=transformation):
            # raises `KeyError` on __enter__ call
            pass


@pytest.mark.slow('gp')
@pytest.mark.parametrize('table', [ResultTable, EtlResultTable])
def test_data_frame_source(table):
    _df = pd.DataFrame([{'foo': 1, 'bar': 'aaa'}])

    def transform(df):
        return df

    source = PandasSource(sources={'df': _DataFrameSource(_df)},
                          transform=transform)

    transformation = DummyTransformation(source=source, target=table)
    source.prepare(transformation=transformation)

    with source.source_table(transformation=transformation):
        pass
