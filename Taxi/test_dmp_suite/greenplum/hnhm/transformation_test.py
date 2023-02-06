# coding: utf-8
import pytest
import logging

from dataclasses import dataclass
from typing import Type, Union
from psycopg2.sql import SQL, Identifier, Literal

from dmp_suite import datetime_utils as dtu
from dmp_suite.exceptions import DWHError
from dmp_suite.greenplum import Int, Boolean, String, Datetime, GPField
from dmp_suite.greenplum.hnhm import SourceSystem, HnhmEntity, HnhmLink, HnhmLinkElement, GPStgTable
from dmp_suite.greenplum.hnhm.exceptions import (
    DeleteFlgShouldBeBool, DeleteFlgWithNotLink, KeyMappingNull, TimeZoneException,
    ExcludedFieldInGroupException, LinkedFieldsExcludedException,
)
from dmp_suite.greenplum.hnhm.transformation import (
    Mapping, _make_md5_key, _check_attributes_for_null, _get_partition_params, HybridLoadGenerator
)
from dmp_suite.table import DdsLayout, StgLayout
from connection import greenplum as gp
from test_dmp_suite.qb2_test import data_for_check

SERVICE_ETL = 'taxi_etl'

logger = logging.getLogger(__name__)


class Entity1(HnhmEntity):
    __layout__ = DdsLayout('e_ent1', group='demand', prefix_key=SERVICE_ETL)

    id_1 = Int()

    __keys__ = [id_1]


class Entity2(HnhmEntity):
    __layout__ = DdsLayout('e_ent2', group='demand', prefix_key=SERVICE_ETL)

    id_1 = Int()

    __keys__ = [id_1]


class Link(HnhmLink):
    __layout__ = DdsLayout('link', group='demand', prefix_key=SERVICE_ETL)

    e1 = HnhmLinkElement(entity=Entity1)
    e2 = HnhmLinkElement(entity=Entity2)

    __keys__ = [e1]


class StgTable(GPStgTable):
    __layout__ = StgLayout('t_stg_1', source='oktell', prefix_key=SERVICE_ETL)

    id = Int()
    delete_flg = Boolean()
    text = String()
    business_dt = Datetime()


class StgTableGroupExclude(GPStgTable):
    __layout__ = StgLayout('t_stg_1', source='oktell', prefix_key=SERVICE_ETL)

    ent_id = Int()
    attr1 = Int()
    attr2 = String()
    attr3 = Datetime()
    ent_id_2 = Int()
    ent_id_3 = Int()


class EntityGroupExclude(HnhmEntity):
    __layout__ = DdsLayout('ent111', group='demand', prefix_key=SERVICE_ETL)

    ent_id = Int()
    attr1 = Int(group='g1')
    attr2 = String(group='g1')
    attr3 = Datetime(group='g1')

    __keys__ = [ent_id]


class LinkExclude(HnhmLink):
    __layout__ = DdsLayout('link', group='demand', prefix_key=SERVICE_ETL)

    e1 = HnhmLinkElement(entity=EntityGroupExclude)
    e2 = HnhmLinkElement(entity=EntityGroupExclude)
    e3 = HnhmLinkElement(entity=EntityGroupExclude)

    __keys__ = [e1]


@pytest.mark.slow('gp')
def test_make_md5_key():
    params = [{'expected': 'md5(nullif(\'\'||case when "a1" is null then \'\' else cast("a1" as varchar)||\'.._..\' end,\'\')) :: uuid as "z"',
               'key_mapping': [Mapping(source=Int(name='a1'), target=Int(name='a2'))],
               'alias': 'z',
               'table_alias': None},
              {'expected': 'md5(nullif(\'\'||case when "a1" is null then \'\' else cast("a1" as varchar)||\'.._..\' end||case when "a3" is null then \'\' else cast("a3" as varchar)||\'.._..\' end,\'\')) :: uuid as "z"',
               'key_mapping': [Mapping(source=Int(name='a1'), target=Int(name='a2')), Mapping(source=Int(name='a3'), target=Int(name='a4')) ],
               'alias': 'z',
               'table_alias': None},
              {'expected': 'md5(nullif(\'\'||case when \'dd\'\'dd\' is null then \'\' else cast(\'dd\'\'dd\' as varchar)||\'.._..\' end||case when "a3" is null then \'\' else cast("a3" as varchar)||\'.._..\' end,\'\')) :: uuid as "z"',
               'key_mapping': [Mapping(source='dd\'dd', target=Int(name='a2')), Mapping(source=Int(name='a3'), target=Int(name='a4')), ],
               'alias': 'z',
               'table_alias': None},
              {'expected': 'md5(nullif(\'\'||case when "alias"."a1" is null then \'\' else cast("alias"."a1" as varchar)||\'.._..\' end,\'\')) :: uuid as "z"',
               'key_mapping': [Mapping(source=Int(name='a1'), target=Int(name='a2'))],
               'alias': 'z',
               'table_alias': 'alias'},
              {'expected': 'md5(nullif(\'\'||case when "alias"."a1" is null then \'\' else cast("alias"."a1" as varchar)||\'.._..\' end||case when "alias"."a3" is null then \'\' else cast("alias"."a3" as varchar)||\'.._..\' end,\'\')) :: uuid as "z"',
               'key_mapping': [Mapping(source=Int(name='a1'), target=Int(name='a2')), Mapping(source=Int(name='a3'), target=Int(name='a4')) ],
               'alias': 'z',
               'table_alias': 'alias'},
              {'expected': 'md5(nullif(\'\'||case when \'dd\'\'dd\' is null then \'\' else cast(\'dd\'\'dd\' as varchar)||\'.._..\' end||case when "alias"."a3" is null then \'\' else cast("alias"."a3" as varchar)||\'.._..\' end,\'\')) :: uuid as "z"',
               'key_mapping': [Mapping(source='dd\'dd', target=Int(name='a2')), Mapping(source=Int(name='a3'), target=Int(name='a4')), ],
               'alias': 'z',
               'table_alias': 'alias'},
              ]

    with gp.connection.cursor() as cur:
        for step in params:
            actual = _make_md5_key(step['key_mapping'], step['alias'], step['table_alias']).as_string(cur)
            assert step['expected'] == actual


@dataclass
class GpCol:
    name: str
    _value: Union[str, int] = None

    @property
    def casting(self):
        return f'::{self.gp_type.data_type}'

    @property
    def val(self):
        return self._value

    @property
    def gp_type(self) -> Type[GPField]:
        return self._gp_type_by_value(self._value)

    def _gp_type_by_value(self, val: Union[str, int]) -> Type[GPField]:
        assn = (
            (lambda v: isinstance(v, str), String),
            (lambda v: isinstance(v, int), Int),
            (lambda v: v is None, String),
        )
        for func, gp_type in assn:
            if func(val):
                return gp_type
        raise ValueError(f'{val}({type(val)}) failed to convert to GP column')


@pytest.mark.parametrize(
    "given_fields, expected_surrogate_key",
    data_for_check
)
@pytest.mark.slow('gp')
def test_md5_key(given_fields, expected_surrogate_key):
    columns = [GpCol(k, v) for k, v in given_fields.items()]

    def get_sql_for_data(_columns):
        """
        на основании входных данных сформируем запрос, который возвращает эти данные в GP
        пример: "SELECT 123::int as a1, NULL::int as a2"
        """
        sql_data = (SQL('{val}{cast} as {name}').format(
            val=Literal(c.val), cast=SQL(c.casting), name=Identifier(c.name)) for c in _columns)
        sql_data = SQL(', ').join(sql_data)
        sql_data = SQL('SELECT {}').format(sql_data)
        return sql_data

    mapping = [Mapping(source=c.gp_type(name=c.name), target=String(name='not_used')) for c in columns]

    with gp.connection.cursor() as cur:
        md5_sql = _make_md5_key(mapping, alias='z')
        data_sql = get_sql_for_data(columns)
        query = SQL('SELECT {md5_sql} FROM ({data_sql}) t1').format(md5_sql=md5_sql, data_sql=data_sql)
        logger.info(query.as_string(cur))
        cur.execute(query)
        result = cur.fetchone()[0]
        assert expected_surrogate_key == result


@pytest.mark.slow('gp')
def test_check_attributes_for_null():
    params = [{'expected': '(True  AND "a1" IS NOT NULL)',
               'key_mapping': [Mapping(source=Int(name='a1'), target=Int(name='a2'))],
               'table_alias': None},
              {'expected': '(True  AND "a1" IS NOT NULL AND "a3" IS NOT NULL)',
               'key_mapping': [Mapping(source=Int(name='a1'), target=Int(name='a2')), Mapping(source=Int(name='a3'), target=Int(name='a4')) ],
               'table_alias': None},
              {'expected': '(True  AND \'dd\'\'dd\' IS NOT NULL AND "a3" IS NOT NULL)',
               'key_mapping': [Mapping(source='dd\'dd', target=Int(name='a2')), Mapping(source=Int(name='a3'), target=Int(name='a4')), ],
               'table_alias': None},
              {'expected': '(True  AND "alias"."a1" IS NOT NULL)',
               'key_mapping': [Mapping(source=Int(name='a1'), target=Int(name='a2'))],
               'table_alias': 'alias'},
              {'expected': '(True  AND "alias"."a1" IS NOT NULL AND "alias"."a3" IS NOT NULL)',
               'key_mapping': [Mapping(source=Int(name='a1'), target=Int(name='a2')), Mapping(source=Int(name='a3'), target=Int(name='a4')) ],
               'table_alias': 'alias'},
              {'expected': '(True  AND \'dd\'\'dd\' IS NOT NULL AND "alias"."a3" IS NOT NULL)',
               'key_mapping': [Mapping(source='dd\'dd', target=Int(name='a2')), Mapping(source=Int(name='a3'), target=Int(name='a4')), ],
               'table_alias': 'alias'},
              ]

    with gp.connection.cursor() as cur:
        for step in params:
            actual = _check_attributes_for_null(step['key_mapping'], step['table_alias']).as_string(cur)
            assert step['expected'] == actual


@pytest.mark.slow('gp')
def test_get_partition_params():
    params = [{'expected': {'partition_list_plus_base': ', base."a2"', 'stage_partition_list': ', "a1" as "a2"', 'partition_list': ', "a2"'},
               'key_mapping': [
                   {'mapping': Mapping(source=Int(name='a1'), target=Int(name='a2')), 'scale': None}
               ]},
              {'expected': {'partition_list_plus_base': ', base."a2", base."a4"', 'stage_partition_list': ', "a1" as "a2", "a3" as "a4"', 'partition_list': ', "a2", "a4"'},
               'key_mapping': [
                   {'mapping': Mapping(source=Int(name='a1'), target=Int(name='a2')), 'scale': None},
                   {'mapping': Mapping(source=Int(name='a3'), target=Int(name='a4')), 'scale': None}
               ]},
              {'expected': {'partition_list_plus_base': ', base."a2", base."a4"', 'stage_partition_list': ', \'dd\'\'dd\' as "a2", "a3" as "a4"', 'partition_list': ', "a2", "a4"'},
               'key_mapping': [
                   {'mapping': Mapping(source='dd\'dd', target=Int(name='a2')), 'scale': None},
                   {'mapping': Mapping(source=Int(name='a3'), target=Int(name='a4')), 'scale': None},
               ]},
              ]

    with gp.connection.cursor() as cur:
        for step in params:
            actual = _get_partition_params(step['key_mapping'])
            res = dict()
            for key in actual.keys():
                if key in step['expected']:
                    res[key] = actual[key].as_string(cur)
            assert step['expected'] == res


def test_wrong_transformations():
    with pytest.raises(LinkedFieldsExcludedException):
        HybridLoadGenerator(
            source=StgTableGroupExclude,
            business_date_field=StgTableGroupExclude.attr3,
            source_system=SourceSystem.oktell,
            exclude_nulls=[StgTableGroupExclude.ent_id_2]
        ).target(EntityGroupExclude, alias='e1').mappings({
            EntityGroupExclude.ent_id: StgTableGroupExclude.ent_id,
        }).target(EntityGroupExclude, alias='e2').mappings({
            EntityGroupExclude.ent_id: StgTableGroupExclude.ent_id_2,
        }).target(EntityGroupExclude, alias='e3').mappings({
            EntityGroupExclude.ent_id: StgTableGroupExclude.ent_id_3,
        }).target(LinkExclude).mappings({
            LinkExclude.e1: 'e1',
            LinkExclude.e2: 'e2',
            LinkExclude.e3: 'e3',
        })._resolve_mappings()


    with pytest.raises(ExcludedFieldInGroupException):
        HybridLoadGenerator(
            source=StgTableGroupExclude,
            business_date_field=StgTableGroupExclude.attr3,
            source_system=SourceSystem.oktell,
            exclude_nulls=[StgTableGroupExclude.attr2]
        ).target(EntityGroupExclude).mappings({
            EntityGroupExclude.ent_id: StgTableGroupExclude.ent_id,
            EntityGroupExclude.attr1: StgTableGroupExclude.attr1,
            EntityGroupExclude.attr2: StgTableGroupExclude.attr2,
            EntityGroupExclude.attr3: StgTableGroupExclude.attr3,
        })._resolve_mappings()

    with pytest.raises(DeleteFlgWithNotLink):
        HybridLoadGenerator(
            source=StgTable,
            business_date_field=StgTable.business_dt,
            source_system=SourceSystem.oktell,
            set_ctl=False
        ).target(Entity1, field_with_deleted_flg=StgTable.text).mappings({
            Entity1.id_1: StgTable.id
        })

    with pytest.raises(DeleteFlgShouldBeBool):
        HybridLoadGenerator(
            source=StgTable,
            business_date_field=StgTable.business_dt,
            source_system=SourceSystem.oktell,
            set_ctl=False
        ).target(Entity1).mappings({
            Entity1.id_1: StgTable.id
        }).target(Entity2).mappings({
            Entity2.id_1: StgTable.id
        }).target(Link, field_with_deleted_flg=StgTable.text)

    with pytest.raises(KeyMappingNull):
        HybridLoadGenerator(
            source=StgTable,
            business_date_field=StgTable.business_dt,
            source_system=SourceSystem.oktell,
            set_ctl=False
        ).target(Entity1).mappings({
            Entity1.id_1: None})



@pytest.mark.parametrize('business_dt_field, tz', [
    (None, 'UTC'),
    (StgTable.business_dt, 'wrong tz'),
    (StgTable.business_dt, 'MSK'),
])
def test_wrong_tz(business_dt_field, tz):
    with pytest.raises(TimeZoneException):
        HybridLoadGenerator(
            source=StgTable,
            business_date_field=business_dt_field,
            business_date_tz=tz,
            source_system=SourceSystem.oktell,
            set_ctl=False
        )

    with pytest.raises(TimeZoneException):
        HybridLoadGenerator(
            source=StgTable,
            business_date_field=StgTable.business_dt,
            source_system=SourceSystem.oktell,
            set_ctl=False
        ).target(
            Entity1,
            field_with_created_dt=business_dt_field,
            field_with_created_dt_tz=tz,
        ).mappings({
            Entity1.id_1: StgTable.id
        })
