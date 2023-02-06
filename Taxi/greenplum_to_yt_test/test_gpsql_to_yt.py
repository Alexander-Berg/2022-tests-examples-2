import random
import string
import pytest
from collections import namedtuple
from unittest.mock import patch
from pyspark.sql import functions as f
from connection.yt import get_yt_client
from typing import Type
from dmp_suite import yt
from dmp_suite import greenplum as gp
from dmp_suite.export.greenplum_to_yt.greenplum_to_yt import gp_to_yt_source
from dmp_suite.greenplum.task.transformations import SqlTaskSource
from dmp_suite.task.execution import run_task
from dmp_suite.yt import YTMeta, YTTable
from dmp_suite.yt.task.etl.spark_transform import spark_source
from dmp_suite.yt.task.etl.transform import replace_by_snapshot
from test_dmp_suite.greenplum import utils
from .test_gp_to_yt import _prepare_gp_table


patch_gp_service_env = patch(
    'dmp_suite.greenplum.connection.service',
    namedtuple('FakeService', ['name'])(name='test'),
)


def read_yt_table(table: Type[YTTable]):
    return list(get_yt_client().read_table(YTMeta(table).target_path()))


class GpTestTable(gp.GPTable):
    __layout__ = utils.TestLayout('test_gpsql_to_yt')
    col_int = gp.Int()
    col_data = gp.String()
    col_p1 = gp.Int()
    col_p2 = gp.Int()


def generate_data(n=100):
    return [
        {
            'col_int': i,
            'col_data': ''.join(random.choices(string.ascii_lowercase, k=16)),
            'col_p1': random.randrange(100),
            'col_p2': random.randrange(100),
        }
        for i in range(n)
    ]


class YtSimpleTestTable(yt.NotLayeredYtTable):
    __layout__ = yt.NotLayeredYtLayout('test', 'gpsql_to_yt_simple')
    col_int = yt.Int()
    col_data = yt.String()


@pytest.mark.slow('gp')
@patch_gp_service_env
def test_gpsql_to_yt_simple(monkeypatch):

    data = generate_data()

    # no unique suffixes are needed here
    # todo: fix this in TAXIDWH-9186

    from dmp_suite.greenplum.table import ExternalGPLocation
    monkeypatch.setattr(ExternalGPLocation, 'table_name_pattern', '{table}')

    with _prepare_gp_table(GpTestTable, data):

        source = (
            SqlTaskSource
                .from_string(
                    'CREATE TEMPORARY TABLE result_table ON COMMIT DROP AS '
                    'SELECT col_int, col_data FROM {test_data} '
                    'ORDER BY col_int'
                )
                .add_tables(test_data=GpTestTable)
        )

        task = replace_by_snapshot(
            "test_gpsql_to_yt",
            source=gp_to_yt_source(source),
            target_table=YtSimpleTestTable,
        )

        run_task(task)

        def local_transform(rec):
            return {
                'col_int': rec['col_int'],
                'col_data': rec['col_data'],
            }

        local_data = list(map(local_transform, data))
        yt_data = sorted(read_yt_table(YtSimpleTestTable), key=lambda r: r['col_int'])

        assert local_data == yt_data


class YtChainTestTable(yt.NotLayeredYtTable):
    __layout__ = yt.NotLayeredYtLayout('test', 'gpsql_to_yt_with_chain')
    col_int = yt.Int()
    col_sum = yt.Int()


@pytest.mark.slow('gp')
@patch_gp_service_env
def test_gpsql_to_yt_with_chain(monkeypatch):

    data = generate_data()

    # no unique suffixes are needed here
    # todo: fix this in TAXIDWH-9186

    from dmp_suite.greenplum.table import ExternalGPLocation
    monkeypatch.setattr(ExternalGPLocation, 'table_name_pattern', '{table}')

    with _prepare_gp_table(GpTestTable, data):

        source = (
            SqlTaskSource
                .from_string(
                    'CREATE TEMPORARY TABLE result_table ON COMMIT DROP AS '
                    'SELECT col_int, col_p1, col_p2 FROM {test_data} '
                    'ORDER BY col_int'
                )
                .add_tables(test_data=GpTestTable)
        )

        @spark_source(data=gp_to_yt_source(source))
        def transform(_, data):
            return data.select(
                f.col('col_int'),
                (f.col('col_p1') + f.col('col_p2')).alias('col_sum')
            )

        task = replace_by_snapshot(
            "test_gpsql_to_yt",
            source=transform,
            target_table=YtChainTestTable,
        )

        run_task(task)

        def local_transform(rec):
            return {
                'col_int': rec['col_int'],
                'col_sum': rec['col_p1'] + rec['col_p2'],
            }

        local_data = list(map(local_transform, data))
        yt_data = sorted(read_yt_table(YtChainTestTable), key=lambda r: r['col_int'])

        assert local_data == yt_data
