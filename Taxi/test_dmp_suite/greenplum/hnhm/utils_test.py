# coding: utf-8
from argparse import Namespace

import mock
import uuid
import pytest

from connection import greenplum as gp

from dmp_suite import datetime_utils as dtu
from dmp_suite.greenplum import String, Datetime, Int, BigInt, MonthPartitionScale, GPMeta
from dmp_suite.greenplum.hnhm import HnhmEntity, HnhmLink, HnhmLinkElement, HnhmLinkDeprecated, HnhmLinkPartition
from dmp_suite.greenplum.hnhm.utils import HnhmCte, ActualEntityCte, ActualLinkCte, HistoryEntityCte, HistoryLinkCte
from dmp_suite.greenplum.hnhm.exceptions import LinkWithoutHistoryInHistoryLinkCte
from dmp_suite.table import ChangeType, DdsLayout
from dmp_suite.task.args import use_arg

from .utils_expected_sql import *

SERVICE_ETL = 'taxi_etl'


# С помощью этой функции, для каждой сущности мы зададим уникальную таблицу
def get_uniq_layout():
    return DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)


# В тестах нам понадобятся имена таблиц, но для того, чтобы тесты могли бежать параллельно,
# к именам таблиц автоматически добавляется рандомный код.
# Поэтому получать имена табличек нужно внутри теста, с помощью этой функции:
def table_name(t):
    return GPMeta(t).table_name


class Entity1(HnhmEntity):
    __layout__ = get_uniq_layout()
    entity_id = Int()
    value = String(change_type=ChangeType.UPDATE)
    dt = Datetime(change_type=ChangeType.UPDATE)
    attr_new = String(change_type=ChangeType.NEW)

    __keys__ = [entity_id]


class Entity2(HnhmEntity):
    __layout__ = get_uniq_layout()
    entity2_id = Int()
    nr = String(change_type=ChangeType.UPDATE)
    attr1 = Datetime(change_type=ChangeType.UPDATE)
    attr2 = Datetime(change_type=ChangeType.NEW)
    attr3 = String(change_type=ChangeType.NEW)
    attr4 = BigInt()

    __keys__ = [entity2_id]


class Entity3(HnhmEntity):
    __layout__ = get_uniq_layout()
    entity3_id = Int()
    nr = String(change_type=ChangeType.UPDATE)
    attr1 = Datetime(change_type=ChangeType.UPDATE)
    attr2 = Datetime(change_type=ChangeType.NEW)
    attr3 = String(change_type=ChangeType.NEW)
    attr4 = BigInt()

    attr5 = Int(group='g1')
    attr6 = String(group='g1')

    attr7 = Int(change_type=ChangeType.UPDATE, group='g2')
    attr8 = String(change_type=ChangeType.UPDATE, group='g2')

    __keys__ = [entity3_id]


class Link1(HnhmLink):
    __layout__ = get_uniq_layout()

    e1 = HnhmLinkElement(entity=Entity1)
    e2 = HnhmLinkElement(entity=Entity2)

    __keys__ = [e1, e2]


class Link1Deprecated(HnhmLinkDeprecated):
    __layout__ = get_uniq_layout()

    e1 = HnhmLinkElement(entity=Entity1)
    e2 = HnhmLinkElement(entity=Entity2)

    __keys__ = [e1, e2]


class Link2(HnhmLink):
    __layout__ = get_uniq_layout()

    e1 = HnhmLinkElement(entity=Entity1)
    e2 = HnhmLinkElement(entity=Entity2)
    e2_2 = HnhmLinkElement(entity=Entity2)

    __keys__ = [e1]


class Entity4(HnhmEntity):
    __layout__ = get_uniq_layout()
    __partition_scale__ = MonthPartitionScale('utc_start_dttm')

    entity4_id = Int()
    utc_start_dttm = Datetime()

    nr = String(change_type=ChangeType.UPDATE)
    attr1 = Datetime(change_type=ChangeType.UPDATE)
    attr2 = Datetime(change_type=ChangeType.NEW)
    attr3 = String(change_type=ChangeType.NEW)
    attr4 = BigInt()

    __keys__ = [entity4_id]


class Link2Partition(HnhmLink):
    __layout__ = get_uniq_layout()

    e4 = HnhmLinkElement(entity=Entity4)
    e2 = HnhmLinkElement(entity=Entity2)
    e2_2 = HnhmLinkElement(entity=Entity2)
    zz = HnhmLinkPartition(partition_position=1, link_element=e4)

    __keys__ = [e4]


class Link3LeftBound(HnhmLink):
    __layout__ = get_uniq_layout()
    hub_left_bound = True

    e1 = HnhmLinkElement(entity=Entity1)
    e2 = HnhmLinkElement(entity=Entity2)
    e2_2 = HnhmLinkElement(entity=Entity2)

    __keys__ = [e1]


class Link3LeftBoundPartition(HnhmLink):
    __layout__ = get_uniq_layout()
    hub_left_bound = True

    e4 = HnhmLinkElement(entity=Entity4)
    e2 = HnhmLinkElement(entity=Entity2)
    e2_2 = HnhmLinkElement(entity=Entity2)
    zz = HnhmLinkPartition(partition_position=1, link_element=e4)

    __keys__ = [e4]


class Link3LeftBoundDiffPartition(HnhmLink):
    __layout__ = get_uniq_layout()
    hub_left_bound = True

    e4 = HnhmLinkElement(entity=Entity4)
    e2 = HnhmLinkElement(entity=Entity4)
    e2_2 = HnhmLinkElement(entity=Entity2)
    zz = HnhmLinkPartition(partition_position=1, link_element=e2)

    __keys__ = [e4]


def test_project():
    entity_id = Int(name='entity_id')
    value = String(name='value', change_type=ChangeType.UPDATE)
    dt = Datetime(name='dt', change_type=ChangeType.UPDATE)

    actual = HnhmCte._internal_project(entity_id, value, a=dt)
    expect = {'entity_id': entity_id, 'value': value, 'a': dt}

    assert actual == expect

    with pytest.raises(ValueError):
        HnhmCte._internal_project(entity_id, entity_id=value)

    with pytest.raises(ValueError):
        HnhmCte._internal_project(entity_id, entity_id=Entity1)

    with pytest.raises(ValueError):
        HnhmCte._internal_project(entity_id, Entity1)


def _normalize_sql(sql):
    return ' '.join(sql.replace('\n', ' ').split())


def assert_sql(actual, expected):
    # Если сравнивать actual == expected, то PyCharm показывает
    # правильный diff. Стоит поменять их местами, и в PyCharm
    # на панели Expected будет то, что здесь - actual.
    assert _normalize_sql(actual) == _normalize_sql(expected)


@pytest.mark.slow('gp')
def test_cte():
    with mock.patch('dmp_suite.greenplum.meta.get_dev_prefix_by_key', return_value=''):
        with gp.connection.cursor() as cur:
            a = ActualEntityCte(Entity1)

            expected_sql = EXCEPTED_SQL_ACTUAL_ALL.format(ent=table_name(Entity1))
            actual_sql = a.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            a = a.project(Entity1.value, Entity1.dt, abc=Entity1.attr_new)
            expected_sql = EXCEPTED_SQL_ACTUAL_PROJECT.format(ent=table_name(Entity1))
            actual_sql = a.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            h = HistoryEntityCte(Entity2)
            expected_sql = EXCEPTED_SQL_HISTORY_ALL.format(ent=table_name(Entity2))
            actual_sql = h.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            h = h.project(Entity2.attr1, Entity2.attr2, Entity2.attr3, z=Entity2.nr)
            expected_sql = EXCEPTED_SQL_HISTORY_PROJECT.format(ent=table_name(Entity2))
            actual_sql = h.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            # actual link
            link = ActualLinkCte(Link1)
            expected_sql = EXPECTED_SQL_LINK1_ACTUAL.format(link=table_name(Link1), ent1=table_name(Entity1), ent2=table_name(Entity2))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            link = link.project(Link1.e1, zzz=Link1.e2)
            expected_sql = EXPECTED_SQL_LINK1_ACTUAL_PROJECT.format(link=table_name(Link1), ent1=table_name(Entity1), ent2=table_name(Entity2))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            link = link.project(Link1.e1)
            expected_sql = EXPECTED_SQL_LINK1_ACTUAL_PROJECT2.format(link=table_name(Link1), ent1=table_name(Entity1), ent2=table_name(Entity2))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            link = ActualLinkCte(Link2)
            expected_sql = EXPECTED_SQL_LINK2_ACTUAL.format(link=table_name(Link2), ent1=table_name(Entity1), ent2=table_name(Entity2))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            link = link.project(Link2.e1, ddd=Link2.e2_2)
            expected_sql = EXPECTED_SQL_LINK2_ACTUAL_PROJECT.format(link=table_name(Link2), ent1=table_name(Entity1), ent2=table_name(Entity2))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            link = link.project(Link2.e1)
            expected_sql = EXPECTED_SQL_LINK2_ACTUAL_PROJECT2.format(link=table_name(Link2), ent1=table_name(Entity1), ent2=table_name(Entity2))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            # history link
            link = HistoryLinkCte(Link2)
            expected_sql = EXPECTED_SQL_LINK2_HISTORY.format(link=table_name(Link2), ent1=table_name(Entity1), ent2=table_name(Entity2))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            link = link.project(Link2.e1, ddd=Link2.e2_2)
            expected_sql = EXPECTED_SQL_LINK2_HISTORY_PROJECT.format(link=table_name(Link2), ent1=table_name(Entity1), ent2=table_name(Entity2))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            link = link.project(Link2.e1)
            expected_sql = EXPECTED_SQL_LINK2_HISTORY_PROJECT2.format(link=table_name(Link2), ent1=table_name(Entity1), ent2=table_name(Entity2))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            with pytest.raises(LinkWithoutHistoryInHistoryLinkCte):
                HistoryLinkCte(Link1Deprecated)

            link = ActualLinkCte(Link1Deprecated)
            expected_sql = EXPECTED_SQL_LINK1_ACTUAL_DEP.format(link=table_name(Link1Deprecated), ent1=table_name(Entity1), ent2=table_name(Entity2))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            link = link.project(Link1Deprecated.e1, zzz=Link1Deprecated.e2)
            expected_sql = EXPECTED_SQL_LINK1_ACTUAL_PROJECT_DEP.format(link=table_name(Link1Deprecated), ent1=table_name(Entity1), ent2=table_name(Entity2))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            link = link.project(Link1Deprecated.e1)
            expected_sql = EXPECTED_SQL_LINK1_ACTUAL_PROJECT2_DEP.format(link=table_name(Link1Deprecated), ent1=table_name(Entity1), ent2=table_name(Entity2))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            a = ActualEntityCte(Entity3)
            expected_sql = EXPECTED_SQL_ACTUAL_ALL_WITH_GROUP.format(ent=table_name(Entity3))
            actual_sql = a.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            a = a.project(Entity3.attr1, Entity3.attr7, Entity3.attr5)
            expected_sql = EXPECTED_SQL_ACTUAL_PROJECT_WITH_GROUP.format(ent=table_name(Entity3))
            actual_sql = a.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            a = ActualEntityCte(Entity3)
            a = a.project(Entity3.attr1, Entity3.attr8, Entity3.attr6)
            expected_sql = EXPECTED_SQL_ACTUAL_PROJECT_WITH_GROUP2.format(ent=table_name(Entity3))
            actual_sql = a.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            h = HistoryEntityCte(Entity3)
            expected_sql = EXPECTED_SQL_HISTORY_ALL_WITH_GROUP.format(ent=table_name(Entity3))
            actual_sql = h.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            h = h.project(Entity3.attr1, Entity3.attr7, Entity3.attr5)
            expected_sql = EXPECTED_SQL_HISTORY_PROJECT_WITH_GROUP.format(ent=table_name(Entity3))
            actual_sql = h.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            h = HistoryEntityCte(Entity3)
            h = h.project(Entity3.attr1, Entity3.attr8, Entity3.attr6)
            expected_sql = EXPECTED_SQL_HISTORY_PROJECT_WITH_GROUP2.format(ent=table_name(Entity3))
            actual_sql = h.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            h = HistoryEntityCte(Entity3)
            h = h.project(Entity3.attr1, Entity3.attr8)
            expected_sql = EXPECTED_SQL_HISTORY_PROJECT_WITHOUT_HIST.format(ent=table_name(Entity3))
            actual_sql = h.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            h = HistoryEntityCte(Entity4)
            expected_sql = EXCEPTED_SQL_HISTORY_ALL_PARTITION.format(ent=table_name(Entity4))
            actual_sql = h.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            h = HistoryEntityCte(Entity4)
            h = h.project(Entity4.attr1, Entity4.attr4)
            expected_sql = EXCEPTED_SQL_HISTORY_PROJECT_PARTITION.format(ent=table_name(Entity4))
            actual_sql = h.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            h = HistoryEntityCte(Entity4)
            h = h.project(Entity4.attr1, Entity4.attr4, Entity4.utc_start_dttm)
            expected_sql = EXCEPTED_SQL_HISTORY_PROJECT_PARTITION_2.format(ent=table_name(Entity4))
            actual_sql = h.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            a = ActualEntityCte(Entity4)
            expected_sql = EXCEPTED_SQL_ACTUAL_ALL_PARTITION.format(ent=table_name(Entity4))
            actual_sql = a.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            a = ActualEntityCte(Entity4)
            a = a.project(Entity4.attr1, Entity4.attr4)
            expected_sql = EXCEPTED_SQL_ACTUAL_PROJECT_PARTITION.format(ent=table_name(Entity4))
            actual_sql = a.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            a = ActualEntityCte(Entity4)
            a = a.project(Entity4.attr1, Entity4.attr4, Entity4.utc_start_dttm)
            expected_sql = EXCEPTED_SQL_ACTUAL_PROJECT_PARTITION_2.format(ent=table_name(Entity4))
            actual_sql = a.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            period = dtu.period('2020-01-15', dtu.get_end_of_day('2020-01-17'))

            h = HistoryEntityCte(Entity4).filter(partition_period=period)
            expected_sql = EXCEPTED_SQL_HISTORY_ALL_PARTITION_FILTER.format(ent=table_name(Entity4))
            actual_sql = h.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            h = HistoryEntityCte(Entity4)
            h = h.project(Entity4.attr1, Entity4.attr4, Entity4.utc_start_dttm).filter(partition_period=period)
            expected_sql = EXCEPTED_SQL_HISTORY_PROJECT_PARTITION_2_FILTER.format(ent=table_name(Entity4))
            actual_sql = h.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            a = ActualEntityCte(Entity4).filter(period)
            a = a.project(Entity4.attr1, Entity4.attr4)
            expected_sql = EXCEPTED_SQL_ACTUAL_PROJECT_PARTITION_FILTER.format(ent=table_name(Entity4))
            actual_sql = a.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            a = ActualEntityCte(Entity4)
            a = a.project(Entity4.attr1, Entity4.attr4, Entity4.utc_start_dttm).filter(partition_period=period)
            expected_sql = EXCEPTED_SQL_ACTUAL_PROJECT_PARTITION_2_FILTER.format(ent=table_name(Entity4))
            actual_sql = a.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            link = ActualLinkCte(Link2Partition)
            expected_sql = EXPECTED_SQL_LINK_PARTITIONED.format(link=table_name(Link2Partition), ent2=table_name(Entity2), ent4=table_name(Entity4))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            link = link.project(Link2Partition.e2, zz1=Link2Partition.zz)
            expected_sql = EXPECTED_SQL_LINK_PARTITIONED_PROJECT.format(link=table_name(Link2Partition), ent2=table_name(Entity2), ent4=table_name(Entity4))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            link = link.filter(partition_period=dtu.period('2020-01-15', dtu.get_end_of_day('2020-01-17')))
            expected_sql = EXPECTED_SQL_LINK_PARTITIONED_PROJECT_FILTER.format(link=table_name(Link2Partition), ent2=table_name(Entity2), ent4=table_name(Entity4))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            link = HistoryLinkCte(Link2Partition)
            expected_sql = EXPECTED_SQL_LINK_PARTITIONED_HIST.format(link=table_name(Link2Partition), ent2=table_name(Entity2), ent4=table_name(Entity4))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            link = link.project(Link2Partition.e2, zz1=Link2Partition.zz)
            expected_sql = EXPECTED_SQL_LINK_PARTITIONED_HIST_PROJECT.format(link=table_name(Link2Partition), ent2=table_name(Entity2), ent4=table_name(Entity4))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            link = link.filter(partition_period=dtu.period('2020-01-15', dtu.get_end_of_day('2020-01-17')))
            expected_sql = EXPECTED_SQL_LINK_PARTITIONED_HIST_PROJECT_FILTER.format(link=table_name(Link2Partition), ent2=table_name(Entity2), ent4=table_name(Entity4))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            link = link.filter(partition_period=dtu.period('2020-01-15', dtu.get_end_of_day('2020-01-17')), partition_key='zz')
            expected_sql = EXPECTED_SQL_LINK_PARTITIONED_HIST_PROJECT_FILTER.format(link=table_name(Link2Partition), ent2=table_name(Entity2), ent4=table_name(Entity4))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            link = HistoryLinkCte(Link3LeftBound)
            expected_sql = EXPECTED_SQL_LINK3_HISTORY_LEFT_BOUND.format(link=table_name(Link3LeftBound), ent1=table_name(Entity1), ent2=table_name(Entity2))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            link = link.project(Link3LeftBound.e1, zz1=Link3LeftBound.e2)
            expected_sql = EXPECTED_SQL_LINK3_HISTORY_LEFT_BOUND_PROJECT.format(link=table_name(Link3LeftBound), ent1=table_name(Entity1), ent2=table_name(Entity2))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            link = HistoryLinkCte(Link3LeftBoundPartition).filter(partition_period=dtu.period('2020-01-15', dtu.get_end_of_day('2020-01-17')))
            expected_sql = EXPECTED_SQL_LINK3_HISTORY_LEFT_BOUND_PARTITION.format(link=table_name(Link3LeftBoundPartition), ent4=table_name(Entity4), ent2=table_name(Entity2))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            link = HistoryLinkCte(Link3LeftBoundDiffPartition).filter(partition_period=dtu.period('2020-01-15', dtu.get_end_of_day('2020-01-17')))
            expected_sql = EXPECTED_SQL_LINK3_HISTORY_LEFT_BOUND_PARTITION_KEY_OTHER_PARTITION.format(link=table_name(Link3LeftBoundDiffPartition), ent4=table_name(Entity4), ent2=table_name(Entity2))
            actual_sql = link.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)


@pytest.mark.slow('gp')
def test_cte_with_args():
    with mock.patch('dmp_suite.greenplum.meta.get_dev_prefix_by_key', return_value=''):
        with gp.connection.cursor() as cur:
            period = dtu.period('2020-01-15', dtu.get_end_of_day('2020-01-17'))
            args = Namespace()
            args.period = period

            h = HistoryEntityCte(Entity4).filter(partition_period=use_arg('period'))
            h = h.get_value(args, None)
            expected_sql = EXCEPTED_SQL_HISTORY_ALL_PARTITION_FILTER.format(ent=table_name(Entity4))
            actual_sql = h.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            h = HistoryEntityCte(Entity4)
            h = h.project(
                Entity4.attr1, Entity4.attr4, Entity4.utc_start_dttm
            ).filter(
                partition_period=use_arg('period')
            )
            h = h.get_value(args, None)
            expected_sql = EXCEPTED_SQL_HISTORY_PROJECT_PARTITION_2_FILTER.format(ent=table_name(Entity4))
            actual_sql = h.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            a = ActualEntityCte(Entity4).filter(use_arg('period'))
            a = a.project(Entity4.attr1, Entity4.attr4)
            a = a.get_value(args, None)
            expected_sql = EXCEPTED_SQL_ACTUAL_PROJECT_PARTITION_FILTER.format(ent=table_name(Entity4))
            actual_sql = a.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)

            a = ActualEntityCte(Entity4)
            a = a.project(
                Entity4.attr1, Entity4.attr4, Entity4.utc_start_dttm
            ).filter(
                partition_period=use_arg('period')
            )
            a = a.get_value(args, None)
            expected_sql = EXCEPTED_SQL_ACTUAL_PROJECT_PARTITION_2_FILTER.format(ent=table_name(Entity4))
            actual_sql = a.sql_desc.as_string(cur)
            assert_sql(actual_sql, expected_sql)
