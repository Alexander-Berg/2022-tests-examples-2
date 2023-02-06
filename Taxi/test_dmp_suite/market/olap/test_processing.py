# pylint: disable=C9002
import pytest
import dataclasses

from dmp_suite import datetime_utils as dtu
from dmp_suite.yt.table import ShortMonthPartitionScale, Date

from dmp_suite.market.olap.processing import FabrikenProcessing, OLAPOps
from dmp_suite.market.olap.attributes import (
    ClickhouseAttributes, ClickhouseAttribute,
)


@dataclasses.dataclass
class Args:
    period: dtu.Period = None
    send_olap_event: bool = False


def get_olap_event(table_path, partition):
    return {
        'name': 'olap',
        'param': {
            'cluster_name': 'hahn',
            'table_path': table_path,
            'partition': partition,
        },
    }


def get_publish_event(entity_name, folder_path):
    return {
        'name': 'publish',
        'param': {
            'cluster_name': 'hahn',
            'name': entity_name,
            'path': folder_path,
        }
    }


class DummyOLAPOps(OLAPOps):

    def __init__(self):
        self.events = []
        self.olap_attrs = {}

    def get_olap_event(self, *args, **kwargs):
        return get_olap_event(*args, **kwargs)

    def get_publish_event(self, *args, **kwargs):
        return get_publish_event(*args, **kwargs)

    def set_olap_attrs(self, target_table, olap_schema):
        self.olap_attrs[target_table] = olap_schema

    def send_events(self, events):
        self.events = events


@pytest.fixture
def make_fabriken_table(unit_test_settings):
    def make_table(cls):
        with unit_test_settings():
            from dmp_suite.market.olap.table import ETLFabrikenTable
            class Table(cls, ETLFabrikenTable):
                __layout__ = ETLFabrikenTable.fabriken_layout('test')
        return Table
    return make_table


class Table:
    pass


class PartitionedTable:
    __partition_scale__ = ShortMonthPartitionScale('partition_dt')
    partition_dt = Date()


@pytest.mark.parametrize('args, table, expected_events', [
    pytest.param(
        Args(),
        Table,
        [
            get_publish_event(
                'test',
                '//home/market/production/mstat/analyst/regular/cubes_vertica/test',
            )
        ],
        id='snapshot-wo-olap-event',
    ),
    pytest.param(
        Args(send_olap_event=True),
        Table,
        [
            get_publish_event(
                'test',
                '//home/market/production/mstat/analyst/regular/cubes_vertica/test',
            ),
            get_olap_event(
                '//home/market/production/mstat/analyst/regular/cubes_vertica/test',
                None,
            ),
        ],
        id='snapshot-w-olap-event',
    ),
    pytest.param(
        Args(period=dtu.Period(start='2022-05-01', end='2022-06-30')),
        PartitionedTable,
        [
            get_publish_event(
                'test',
                '//home/market/production/mstat/analyst/regular/cubes_vertica/test',
            ),
        ],
        id='partition-wo-olap-event',
    ),
    pytest.param(
        Args(
            send_olap_event=True,
            period=dtu.Period(start='2022-05-01', end='2022-06-30'),
        ),
        PartitionedTable,
        [
            get_publish_event(
                'test',
                '//home/market/production/mstat/analyst/regular/cubes_vertica/test',
            ),
            get_olap_event(
                '//home/market/production/mstat/analyst/regular/cubes_vertica/test/2022-05',
                '2022-05',
            ),
            get_olap_event(
                '//home/market/production/mstat/analyst/regular/cubes_vertica/test/2022-06',
                '2022-06',
            ),
        ],
        id='partition-w-olap-event',
    ),
])
def test_events(make_fabriken_table, table, args, expected_events):
    ops = DummyOLAPOps()
    for _ in FabrikenProcessing(make_fabriken_table(table), '', ops)(args):
        pass

    assert ops.events == expected_events


class PartitionedTableChPartitionAttr:
    __partition_scale__ = ShortMonthPartitionScale('partition_dt')

    partition_dt = Date()
    ch_partition_dt = Date()

    __clickhouse_attributes__ = ClickhouseAttributes(
        ClickhouseAttribute(ch_partition_dt, partition_key=True),
    )


class TableChNullableAttr:
    nullable_dt = Date()
    __clickhouse_attributes__ = ClickhouseAttributes(
        ClickhouseAttribute(nullable_dt, nullable=True),
    )


default_attr = {
    'attributes': [],
    'name': 'etl_updated',
    'ru_name': '*системное поле, utc-время последнего обновления строки*'
}
partition_attr = {
    'attributes': [],
    'name': 'partition_dt',
    'ru_name': ''
}
ch_partition_attr = {
    'attributes': [],
    'name': 'ch_partition_dt',
    'ru_name': ''
}
nullable_attr = {
    'attributes': ['Nullable'],
    'name': 'nullable_dt',
    'ru_name': ''
}


@pytest.mark.parametrize('args, table, expected_attrs', [
    pytest.param(
        Args(),
        Table,
        {'//home/market/production/mstat/analyst/regular/cubes_vertica/test': {'ru_schema': [default_attr], 'partitioning_fields': []}},
        id='snapshot',
    ),
    pytest.param(
        Args(period=dtu.Period(start='2022-05-01', end='2022-06-30')),
        PartitionedTable,
        {
            '//home/market/production/mstat/analyst/regular/cubes_vertica/test/2022-05': {
                'ru_schema': [default_attr, partition_attr],
                'partitioning_fields': [partition_attr['name']]
            },
            '//home/market/production/mstat/analyst/regular/cubes_vertica/test/2022-06': {
                'ru_schema': [default_attr, partition_attr],
                'partitioning_fields': [partition_attr['name']]
            },
        },
        id='partitioned',
    ),
    pytest.param(
        Args(period=dtu.Period(start='2022-05-01', end='2022-06-30')),
        PartitionedTableChPartitionAttr,
        {
            '//home/market/production/mstat/analyst/regular/cubes_vertica/test/2022-05': {
                'ru_schema': [ch_partition_attr, default_attr, partition_attr],
                'partitioning_fields': [ch_partition_attr['name']]
            },
            '//home/market/production/mstat/analyst/regular/cubes_vertica/test/2022-06': {
                'ru_schema': [ch_partition_attr, default_attr, partition_attr],
                'partitioning_fields': [ch_partition_attr['name']]
            },
        },
        id='partitioned-with-ch-attributes',
    ),
    pytest.param(
        Args(),
        TableChNullableAttr,
        {
            '//home/market/production/mstat/analyst/regular/cubes_vertica/test': {
                'ru_schema': [default_attr, nullable_attr],
                'partitioning_fields': []
            },
        },
        id='ch-nullable-attributes',
    ),
])
def test_olap_attr(make_fabriken_table, table, args, expected_attrs):
    ops = DummyOLAPOps()
    for _ in FabrikenProcessing(make_fabriken_table(table), '', ops)(args):
        pass

    assert len(expected_attrs) == len(ops.olap_attrs), 'Кол-во таблиц с атрибутами не совпадает'
    for expected_table, table_attrs in expected_attrs.items():
        assert expected_table in ops.olap_attrs, 'Не хватает таблицы'
        for expected_attr_key, expected_attr_value in table_attrs.items():
            assert expected_attr_key in ops.olap_attrs[expected_table], 'Не хватает атрибута в таблице'
            assert ops.olap_attrs[expected_table][expected_attr_key] == expected_attr_value, 'Значение атрибута не совпадает'
