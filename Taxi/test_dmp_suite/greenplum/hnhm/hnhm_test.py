import hashlib
import json
import os
import re
import uuid
from datetime import datetime

import pytest

from connection import greenplum as gp
from connection.ctl import get_ctl
from dmp_suite import datetime_utils as dtu
from dmp_suite.ctl import CTL_LAST_SYNC_DATE
from dmp_suite.greenplum import (Boolean, Datetime, Distribution, GPMeta, Int, String, YearPartitionScale,
                                 connection as connection_classes)
from dmp_suite.greenplum.hnhm import (GPStgTable, HnhmEntity, HnhmLink, HnhmLinkDeprecated, HnhmLinkElement,
                                      HnhmLinkPartition, SourceSystem)
from dmp_suite.greenplum.hnhm.transformation import HybridLoadGenerator, _NoKey
from dmp_suite.greenplum.hnhm.utils import drop_dds_entity
from dmp_suite.greenplum.hnhm.exceptions import ExcludedFieldInGroupException, LinkedFieldsExcludedException
from dmp_suite.string_utils import to_unicode
from dmp_suite.table import ChangeType, DdsLayout, StgLayout

SERVICE_ETL = 'taxi'


class StgTable(GPStgTable):
    __layout__ = StgLayout('t_' + str(uuid.uuid4().hex)[0:10], source='oktell', prefix_key=SERVICE_ETL)
    __distributed_by__ = Distribution('id')

    id = Int()
    value = String()
    dt = Datetime()


class StgTablePartition(GPStgTable):
    __layout__ = StgLayout('t_' + str(uuid.uuid4().hex)[0:10], source='oktell', prefix_key=SERVICE_ETL)
    __distributed_by__ = Distribution('id')

    id = Int()
    value = String()
    dt = Datetime()
    pdt = Datetime()


class StgTableLink(GPStgTable):
    __layout__ = StgLayout('t_' + str(uuid.uuid4().hex)[0:10], source='oktell', prefix_key=SERVICE_ETL)
    __distributed_by__ = Distribution('id')

    id = Int()
    dt = Datetime()
    e1 = Int()
    e2 = Int()
    e3 = Int()


class StgTableLinkPartition(GPStgTable):
    __layout__ = StgLayout('t_' + str(uuid.uuid4().hex)[0:10], source='oktell', prefix_key=SERVICE_ETL)
    __distributed_by__ = Distribution('id')

    id = Int()
    dt = Datetime()
    e1 = Int()
    e2 = Int()
    e3 = Int()
    pdt = Datetime()


class StgTableLinkDeleted(GPStgTable):
    __layout__ = StgLayout('t_' + str(uuid.uuid4().hex)[0:10], source='oktell', prefix_key=SERVICE_ETL)
    __distributed_by__ = Distribution('id')

    id = Int()
    dt = Datetime()
    e1 = Int()
    e2 = Int()
    e3 = Int()
    deleted_flg = Boolean()


class Entity1(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)
    eid = Int()
    evalue = String(change_type=ChangeType.UPDATE)
    edt = Datetime(change_type=ChangeType.UPDATE)

    __keys__ = [eid]


class Entity1l(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    eid = Int()
    evalue = String(change_type=ChangeType.UPDATE)
    edt = Datetime(change_type=ChangeType.UPDATE)

    __keys__ = [eid]


class Entity1lPartition(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    __partition_scale__ = YearPartitionScale('edt', start='2018-01-01')

    eid = Int()
    evalue = String(change_type=ChangeType.UPDATE)
    edt = Datetime()

    __keys__ = [eid]


class Entity1Partition(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    __partition_scale__ = YearPartitionScale('pdt', start='2018-01-01')

    eid = Int()
    pdt = Datetime()
    evalue = String(change_type=ChangeType.UPDATE)
    edt = Datetime(change_type=ChangeType.UPDATE)

    __keys__ = [eid]


class Entity2(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    eid = Int()
    evalue = String(change_type=ChangeType.IGNORE)
    edt = Datetime(change_type=ChangeType.IGNORE)

    __keys__ = [eid]


class Entity2l(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    eid = Int()
    evalue = String(change_type=ChangeType.IGNORE)
    edt = Datetime(change_type=ChangeType.IGNORE)

    __keys__ = [eid]


class Entity2Partition(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)
    __partition_scale__ = YearPartitionScale('pdt', start='2018-01-01')

    eid = Int()
    pdt = Datetime()
    evalue = String(change_type=ChangeType.IGNORE)
    edt = Datetime(change_type=ChangeType.IGNORE)

    __keys__ = [eid]


class Entity3(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    eid = Int()
    evalue = String(change_type=ChangeType.NEW)
    edt = Datetime(change_type=ChangeType.UPDATE)

    __keys__ = [eid]


class Entity3l(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    eid = Int()
    evalue = String(change_type=ChangeType.NEW)
    edt = Datetime(change_type=ChangeType.UPDATE)

    __keys__ = [eid]


class Entity3Partition(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)
    __partition_scale__ = YearPartitionScale('pdt', start='2018-01-01')

    eid = Int()
    pdt = Datetime()
    evalue = String(change_type=ChangeType.NEW)
    edt = Datetime(change_type=ChangeType.UPDATE)

    __keys__ = [eid]


class LinkStaticD(HnhmLinkDeprecated):
    __layout__ = DdsLayout('l_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    e1 = HnhmLinkElement(entity=Entity1l)
    e2 = HnhmLinkElement(entity=Entity2l)
    e3 = HnhmLinkElement(entity=Entity3l)

    __keys__ = [e1, e2, e3]


class LinkStatic(HnhmLink):
    __layout__ = DdsLayout('l_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    e1 = HnhmLinkElement(entity=Entity1l)
    e2 = HnhmLinkElement(entity=Entity2l)
    e3 = HnhmLinkElement(entity=Entity3l)

    __keys__ = [e1, e2, e3]


class LinkHistD(HnhmLinkDeprecated):
    __layout__ = DdsLayout('l_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    e1 = HnhmLinkElement(entity=Entity1l)
    e2 = HnhmLinkElement(entity=Entity2l)
    e3 = HnhmLinkElement(entity=Entity3l)

    __keys__ = [e1, e2]


class LinkHist(HnhmLink):
    __layout__ = DdsLayout('l_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    e1 = HnhmLinkElement(entity=Entity1l)
    e2 = HnhmLinkElement(entity=Entity2l)
    e3 = HnhmLinkElement(entity=Entity3l)

    __keys__ = [e1, e2]


class LinkHistExclude(HnhmLink):
    __layout__ = DdsLayout('l_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    e1 = HnhmLinkElement(entity=Entity1l)
    e2 = HnhmLinkElement(entity=Entity2l)
    e3 = HnhmLinkElement(entity=Entity3l)

    __keys__ = [e1, e2]


class LinkHistPartition(HnhmLink):
    __layout__ = DdsLayout('l_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    e1 = HnhmLinkElement(entity=Entity1lPartition)
    e2 = HnhmLinkElement(entity=Entity2l)
    e3 = HnhmLinkElement(entity=Entity3l)
    zzz = HnhmLinkPartition(partition_position=1, link_element=e1)

    __keys__ = [e1, e2]


class EntityGroup1(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    ent_id = Int()
    attr1 = Int(change_type=ChangeType.UPDATE, group='g1')
    attr2 = String(change_type=ChangeType.UPDATE, group='g1')
    attr3 = Datetime(change_type=ChangeType.UPDATE, group='g1')

    __keys__ = [ent_id]


class Entity1Exclude(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    ent_id = Int()
    attr1 = Int(change_type=ChangeType.UPDATE)
    attr2 = String(change_type=ChangeType.NEW)

    __keys__ = [ent_id]


class EntityGroup2(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    ent_id = Int()
    attr1 = Int(change_type=ChangeType.NEW, group='g1')
    attr2 = String(change_type=ChangeType.NEW, group='g1')
    attr3 = Datetime(change_type=ChangeType.NEW, group='g1')

    __keys__ = [ent_id]


class StgTableGroup1(GPStgTable):
    __layout__ = StgLayout('t_' + str(uuid.uuid4().hex)[0:10], source='oktell', prefix_key=SERVICE_ETL)
    __distributed_by__ = Distribution('ent_id')

    ent_id = Int()
    attr1 = Int()
    attr2 = String()
    attr3 = Datetime()


class EntityCheckDelete(HnhmEntity):
    """
    проверяет корректность удаления. если приходит null в атрибуте то и исторический и статический атрибуты
    должны обнулиться
    """
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    ent_id = Int()
    attr1 = String(change_type=ChangeType.UPDATE)
    attr2 = String(change_type=ChangeType.NEW)

    __keys__ = [ent_id]


class EntityCheckIgnoreWithTwoEtlDt(HnhmEntity):
    """
    проверяет корректность удаления. если приходит null в атрибуте то и исторический и статический атрибуты
    должны обнулиться
    """
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    ent_id = Int()
    attr1 = String(change_type=ChangeType.IGNORE)
    attr2 = String(change_type=ChangeType.UPDATE)

    __keys__ = [ent_id]


class StgCheckDelete(GPStgTable):
    __layout__ = StgLayout('t_' + str(uuid.uuid4().hex)[0:10], source='oktell', prefix_key=SERVICE_ETL)
    __distributed_by__ = Distribution('ent_id')

    ent_id = Int()
    attr1 = String()
    attr2 = String()
    bdt = Datetime()


class StgCreatedField(GPStgTable):
    __layout__ = StgLayout('t_' + str(uuid.uuid4().hex)[0:10], source='oktell', prefix_key=SERVICE_ETL)
    __distributed_by__ = Distribution('id')

    id = Int()
    value = String()
    business_dt = Datetime()
    created_dt = Datetime()


class EntityCreated(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    entity_id = Int()
    val = String(change_type=ChangeType.UPDATE)

    __keys__ = [entity_id]


class EntityExtended(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    entity_id = Int()
    val = String(hub_left_bound=True)

    __keys__ = [entity_id]


class EntitySetupExtKey(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    entity_id = Int()
    val = String()

    __keys__ = [entity_id]


class EntityExtKey(EntitySetupExtKey):
    entity_id = Int()
    entity_ext_id = Int()
    val = String()

    __keys__ = [entity_id, entity_ext_id]


def get_md5(val):
    v = hashlib.md5(str(val)).hexdigest()

    return '{}-{}-{}-{}-{}'.format(v[:8], v[8:12], v[12:16], v[16:20], v[20:])


def get_actual(cls):
    with gp.connection.transaction():
        actual = [dict(row) for row in gp.connection.select_all(cls)]
    for r in actual:
        del r['_utc_etl_processed_dttm']
    actual = sorted(actual, key=lambda d: str(d['id']) + str(d['utc_valid_from_dttm']))
    return actual


def get_actual_link(cls):
    with gp.connection.transaction():
        actual = [dict(row) for row in gp.connection.select_all(cls)]
    for d in actual:
        del d['_utc_etl_processed_dttm']
    actual = sorted(actual, key=lambda z: str(z['utc_valid_from_dttm']))
    return actual


def sort_target(data):
    return sorted(data, key=lambda d: str(d['id']) + str(d['utc_valid_from_dttm']))


def sort_target_link(data):
    return sorted(data, key=lambda d: str(d['utc_valid_from_dttm']))


def run_test_attr_without_partitioning(source, entity):
    loader = HybridLoadGenerator(
        source=source,
        business_date_field=source.dt,
        source_system=oktell,
        set_ctl=False

    ).target(entity).mappings({
        entity.eid: source.id,
        entity.evalue: source.value,
        entity.edt: source.dt
    })

    loader.run('1900-01-01')


def run_group1(source, entity):
    loader = HybridLoadGenerator(
        source=source,
        business_date_field=source.attr3,
        source_system=oktell,
        set_ctl=False

    ).target(entity).mappings({
        entity.ent_id: source.ent_id,
        entity.attr1: source.attr1,
        entity.attr2: source.attr2,
        entity.attr3: source.attr3,
    })

    loader.run('1900-01-01')


def run_test_attr_with_partitioning(source, entity):
    loader = HybridLoadGenerator(
        source=source,
        business_date_field=source.dt,
        source_system=oktell,
        set_ctl=False

    ).target(entity).mappings({
        entity.eid: source.id,
        entity.evalue: source.value,
        entity.edt: source.dt,
        entity.pdt: source.pdt
    })

    loader.run('1900-01-01')


def run_test_link(source, link, e1, e2, e3):
    loader = HybridLoadGenerator(
        source=source,
        business_date_field=source.dt,
        source_system=oktell,
        set_ctl=False

    ).target(e1).mappings({
        e1.eid: source.e1
    }).target(e2).mappings({
        e2.eid: source.e2
    }).target(e3).mappings({
        e3.eid: source.e3
    }).target(
        link
    )

    loader.run('1900-01-01')


def run_test_link_partition(source, link, e1, e2, e3):
    loader = HybridLoadGenerator(
        source=source,
        business_date_field=source.dt,
        source_system=oktell,
        set_ctl=False

    ).target(e1).mappings({
        e1.eid: source.e1,
        e1.edt: source.pdt,
    }).target(e2).mappings({
        e2.eid: source.e2
    }).target(e3).mappings({
        e3.eid: source.e3
    }).target(
        link
    )

    loader.run('1900-01-01')


def run_test_link_deleted(source, link, e1, e2, e3):
    loader = HybridLoadGenerator(
        source=source,
        business_date_field=source.dt,
        source_system=oktell,
        set_ctl=False

    ).target(e1).mappings({
        e1.eid: source.e1
    }).target(e2).mappings({
        e2.eid: source.e2
    }).target(e3).mappings({
        e3.eid: source.e3
    }).target(
        link, field_with_deleted_flg=source.deleted_flg
    )

    loader.run('1900-01-01')


def run_check_delete(source, entity):
    loader = HybridLoadGenerator(
        source=source,
        business_date_field=source.bdt,
        source_system=oktell,
        set_ctl=False

    ).target(entity).mappings({
        entity.ent_id: source.ent_id,
        entity.attr1: source.attr1,
        entity.attr2: source.attr2,
    })

    loader.run('1900-01-01')


def run_test_check_created_at(source, entity):
    loader = HybridLoadGenerator(
        source=source,
        business_date_field=source.business_dt,
        source_system=oktell,
        set_ctl=False

    ).target(entity, field_with_created_dt=source.created_dt).mappings({
        entity.entity_id: source.id,
        entity.val: source.value,
    })

    loader.run('1900-01-01')


def run_test_check_created_at_tz(source, entity):
    loader = HybridLoadGenerator(
        source=source,
        business_date_field=source.business_dt,
        source_system=oktell,
        set_ctl=False
    ).target(
        entity,
        field_with_created_dt=source.created_dt,
        field_with_created_dt_tz=dtu.MSK,
    ).mappings({
        entity.entity_id: source.id,
        entity.val: source.value
    })

    loader.run('1900-01-01')


def run_test_nulls_in_link(source, link, e1, e2, e3):
    loader = HybridLoadGenerator(
        source=source,
        business_date_field=source.dt,
        source_system=oktell,
        set_ctl=False

    ).target(e1).mappings({
        e1.eid: source.e1
    }).target(e2).mappings({
        e2.eid: source.e2
    }).target(e3).mappings({
        e3.eid: source.e3
    }).target(
        link
    ).mappings({
        link.e1: e1,
        link.e2: e2,
        link.e3: e3
    })

    loader.run('1900-01-01')


def run_test_key_extension(source, entity):
    loader = HybridLoadGenerator(
        source=source,
        business_date_field=source.dt,
        source_system=oktell,
        set_ctl=False

    ).target(entity).mappings({
        entity.entity_id: source.id,
        entity.entity_ext_id: _NoKey,
        entity.val: source.value,
    })

    loader.run('1900-01-01')


def load_source_data_key_extension(context_data):
    with gp.connection.transaction():
        gp.connection.create_table(StgTable)
        gp.connection.truncate(StgTable)
        gp.connection.insert(StgTable, context_data['initial_source'])


def load_source_data_nulls_in_link(context_data):
    with gp.connection.transaction():
        gp.connection.create_table(StgTable)
        gp.connection.truncate(StgTable)
        gp.connection.insert(StgTable, context_data['initial_source'])


def load_entity_data_key_extension(context_data):
    loader = HybridLoadGenerator(
        source=StgTable,
        business_date_field=StgTable.dt,
        source_system=oktell,
        set_ctl=False,
    ).target(EntitySetupExtKey).mappings({
        EntitySetupExtKey.entity_id: StgTable.id,
        EntitySetupExtKey.val: StgTable.value,
    })

    loader.run('1900-01-01')


def run_test_check_business_date_tz(source, entity):
    loader = HybridLoadGenerator(
        source=source,
        business_date_field=source.dt,
        business_date_tz=dtu.MSK,
        source_system=oktell,
        set_ctl=False
    ).target(entity).mappings({
        entity.eid: source.id,
        entity.evalue: source.value,
        entity.edt: source.dt,
    })

    loader.run('1900-01-01')


def run_test_group_exclude(source, entity):
    loader = HybridLoadGenerator(
        source=source,
        business_date_field=source.attr3,
        source_system=oktell,
        exclude_nulls=[source.attr2, source.attr1]
    ).target(entity).mappings({
        entity.ent_id: source.ent_id,
        entity.attr1: source.attr1,
        entity.attr2: source.attr2,
    })

    loader.run('1900-01-01')


def run_test_link_exclude(source, entity, e1, e2, e3):
    loader = HybridLoadGenerator(
        source=source,
        business_date_field=source.dt,
        source_system=oktell,
        set_ctl=False,
        exclude_nulls=[source.e3]
    ).target(e1).mappings({
        e1.eid: source.e1
    }).target(e2).mappings({
        e2.eid: source.e2
    }).target(e3).mappings({
        e3.eid: source.e3
    }).target(
        entity
    ).mappings({
        entity.e1: e1,
        entity.e2: e2,
        entity.e3: e3
    })

    loader.run('1900-01-01')


oktell = SourceSystem.oktell.value

params1 = [
    {'entity': LinkHistExclude,
     'e1': Entity1l,
     'e2': Entity2l,
     'e3': Entity3l,
     'source': StgTableLink,
     'proc': run_test_link_exclude,
     'data': 'exclude_link_exception.json',
    },
    {'entity': Entity1Exclude,
     'source': StgTableGroup1,
     'proc': run_test_group_exclude,
     'data': 'exclude_group_exception.json',
    },
    {'entity': LinkHist,
     'source': StgTableLink,
     'e1': Entity1l,
     'e2': Entity2l,
     'e3': Entity3l,
     'proc': run_test_nulls_in_link,
     'data': 'nulls_in_link.json',
     },
    {'entity': EntityExtKey,
     'source': StgTable,
     'proc': run_test_key_extension,
     'data': 'key_extension.json',
     'setup': [load_source_data_key_extension, load_entity_data_key_extension]
     },
    {'entity': Entity1,
     'source': StgTable,
     'proc': run_test_attr_without_partitioning,
     'data': 'attr_update.json'
     },
    {'entity': Entity2,
     'source': StgTable,
     'proc': run_test_attr_without_partitioning,
     'data': 'attr_ignore.json'
     },
    {'entity': Entity3,
     'source': StgTable,
     'proc': run_test_attr_without_partitioning,
     'data': 'attr_new.json'
     },
    {'entity': LinkStaticD,
     'e1': Entity1l,
     'e2': Entity2l,
     'e3': Entity3l,
     'source': StgTableLink,
     'proc': run_test_link,
     'data': 'link_deprecated.json'
     },
    {'entity': LinkHistD,
     'e1': Entity1l,
     'e2': Entity2l,
     'e3': Entity3l,
     'source': StgTableLink,
     'proc': run_test_link,
     'data': 'link_hist.json'
     },
    {'entity': Entity1Partition,
     'source': StgTablePartition,
     'proc': run_test_attr_with_partitioning,
     'data': 'attr_update_partition.json'
     },
    {'entity': Entity2Partition,
     'source': StgTablePartition,
     'proc': run_test_attr_with_partitioning,
     'data': 'attr_ignore_partition.json'
     },
    {'entity': Entity3Partition,
     'source': StgTablePartition,
     'proc': run_test_attr_with_partitioning,
     'data': 'attr_new_partition.json'
     },
    {'entity': EntityGroup1,
     'source': StgTableGroup1,
     'proc': run_group1,
     'data': 'group1.json'
     },
    {'entity': EntityGroup2,
     'source': StgTableGroup1,
     'proc': run_group1,
     'data': 'group2.json'
     },
    {'entity': EntityCheckDelete,
     'source': StgCheckDelete,
     'proc': run_check_delete,
     'data': 'check_delete_attribute.json'
     },
    {'entity': EntityCheckDelete,
     'source': StgCheckDelete,
     'proc': run_check_delete,
     'data': 'check_microsecond.json'
     },
    {'entity': EntityCheckDelete,
     'source': StgCheckDelete,
     'proc': run_check_delete,
     'data': 'check_microsecond_same_etl_dttm.json'
     },
    {'entity': EntityCheckIgnoreWithTwoEtlDt,
     'source': StgCheckDelete,
     'proc': run_check_delete,
     'data': 'check_ignore_with_two_etldt.json'
     },
    {'entity': LinkStaticD,
     'e1': Entity1l,
     'e2': Entity2l,
     'e3': Entity3l,
     'source': StgTableLinkDeleted,
     'proc': run_test_link_deleted,
     'data': 'link_deleted_deprecated.json'
     },
    {'entity': LinkHistD,
     'e1': Entity1l,
     'e2': Entity2l,
     'e3': Entity3l,
     'source': StgTableLinkDeleted,
     'proc': run_test_link_deleted,
     'data': 'link_deleted_hist.json'
     },
    {'entity': LinkHist,
     'e1': Entity1l,
     'e2': Entity2l,
     'e3': Entity3l,
     'source': StgTableLinkDeleted,
     'proc': run_test_link_deleted,
     'data': 'link_deleted_hist.json'
     },
    {'entity': LinkHist,
     'e1': Entity1l,
     'e2': Entity2l,
     'e3': Entity3l,
     'source': StgTableLink,
     'proc': run_test_link,
     'data': 'link_hist.json'
     },
    {'entity': LinkStatic,
     'e1': Entity1l,
     'e2': Entity2l,
     'e3': Entity3l,
     'source': StgTableLinkDeleted,
     'proc': run_test_link_deleted,
     'data': 'link_deleted.json'
     },
    {'entity': LinkStatic,
     'e1': Entity1l,
     'e2': Entity2l,
     'e3': Entity3l,
     'source': StgTableLink,
     'proc': run_test_link,
     'data': 'link.json'
     },
    {'entity': LinkHistPartition,
     'e1': Entity1lPartition,
     'e2': Entity2l,
     'e3': Entity3l,
     'source': StgTableLinkPartition,
     'proc': run_test_link_partition,
     'data': 'link_hist_partition.json'
     },
    {'entity': Entity3,
     'source': StgTable,
     'proc': run_test_attr_without_partitioning,
     'data': 'attr_new_null.json'
     },
    {'entity': EntityCreated,
     'source': StgCreatedField,
     'proc': run_test_check_created_at,
     'data': 'created_field.json'
     },
    {'entity': EntityCreated,
     'source': StgCreatedField,
     'proc': run_test_check_created_at_tz,
     'data': 'created_field_tz.json'
     },
    {'entity': EntityExtended,
     'source': StgCreatedField,
     'proc': run_test_check_created_at,
     'data': 'attr_created_and_extend.json'
     },
    {'entity': EntityExtended,
     'source': StgCreatedField,
     'proc': run_test_check_created_at_tz,
     'data': 'attr_created_and_extend_tz.json'
     },
    {'entity': LinkStatic,
     'e1': Entity1l,
     'e2': Entity2l,
     'e3': Entity3l,
     'source': StgTableLinkDeleted,
     'proc': run_test_link_deleted,
     'data': 'link_deleted_compress.json'
     },
    {'entity': Entity1,
     'source': StgTable,
     'proc': run_test_check_business_date_tz,
     'data': 'check_business_date_tz.json'
     },
]


def datetime_parser(dct):
    for k, v in dct.items():
        if isinstance(v, str):
            v = to_unicode(v)
            if re.search(r"\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d.\d\d\d\d\d\d", v):
                dct[k] = datetime.strptime(v, u'%Y-%m-%d %H:%M:%S.%f')
            elif re.search(r"\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d", v):
                dct[k] = datetime.strptime(v, u'%Y-%m-%d %H:%M:%S')

    return dct


@pytest.mark.slow('gp')
@pytest.mark.parametrize('params',
    params1,
)
def test_hnhm(params):
    ent = params
    entity = ent['entity']
    source = ent['source']
    setup = ent.get('setup')

    data_path = os.path.join(os.path.dirname(__file__), ent['data'])

    with open(data_path) as f:
        tests = json.load(f, object_hook=datetime_parser)

    try:
        for test in tests:
            if setup:
                for proc in setup:
                    proc(test)


            with gp.connection.transaction():
                gp.connection.create_table(source)
                gp.connection.truncate(source)
                gp.connection.insert(source, test['source'])

            meta = GPMeta(entity)

            # признак, что мы работаем с линком
            if 'e1' in ent:
                # в ctl данные с точностью до сек.
                start_utc = dtu.utcnow().replace(microsecond=0)
                ent['proc'](source, entity, ent['e1'], ent['e2'], ent['e3'])
                end_utc = dtu.utcnow().replace(microsecond=0)
                actual = get_actual_link(meta.table.get_main_class())
                for i in test['hub']:
                    i[GPMeta(ent['e1']).table_name + '_e1__id'] = i.pop('e1')
                    i[GPMeta(ent['e2']).table_name + '_e2__id'] = i.pop('e2')
                    i[GPMeta(ent['e3']).table_name + '_e3__id'] = i.pop('e3')
                target = sort_target_link(test['hub'])
            else:
                start_utc = dtu.utcnow().replace(microsecond=0)
                ent['proc'](source, entity)
                end_utc = dtu.utcnow().replace(microsecond=0)
                actual = get_actual(meta.table.get_main_class())
                target = sort_target(test['hub'])

            assert actual == target
            main_class_ctl = get_ctl().gp.get_param(meta.table.get_main_class(), CTL_LAST_SYNC_DATE)
            assert start_utc <= main_class_ctl <= end_utc

            if 'e1' not in ent:
                for i in meta.table.get_field_classes():
                    field = GPMeta(i).table_name.split('__')[2]
                    if field in test:
                        actual = get_actual(i)
                        target = sort_target(test[GPMeta(i).table_name.split('__')[2]])

                        assert actual == target
                        field_ctl = get_ctl().gp.get_param(i, CTL_LAST_SYNC_DATE)
                        assert start_utc <= field_ctl <= end_utc
    finally:
        with gp.connection.transaction():
            gp.connection.drop_table(source)
            drop_dds_entity(entity, gp.connection)

            if 'e1' in ent:
                drop_dds_entity(ent['e1'], gp.connection)
                drop_dds_entity(ent['e2'], gp.connection)
                drop_dds_entity(ent['e3'], gp.connection)


def run_test_key_extension_split_sql(source, entity, connection_mock, split_sql):
    loader = HybridLoadGenerator(
        source=source,
        business_date_field=source.dt,
        source_system=oktell,
        set_ctl=False,
        split_sql=split_sql,
        connection=connection_mock,
    ).target(entity).mappings({
        entity.entity_id: source.id,
        entity.entity_ext_id: _NoKey,
        entity.val: source.value,
    })

    loader.run('1900-01-01')


class MockEtlConnection(connection_classes.EtlConnection):
    def __init__(self, parent_role=None, **kwargs):
        self._calls = []
        super().__init__(parent_role=parent_role, **kwargs)

    def execute(self, query, *args, with_transaction=True, **kwargs):
        self._calls.append(query)
        super().execute(query, *args, with_transaction=with_transaction, **kwargs)


@pytest.fixture
def mocked_connection():
    def _get_connection():
        return MockEtlConnection(
            **gp.get_default_connection_conf(),
            parent_role=gp.settings('greenplum.parent_role', default=None),
        )

    return _get_connection()


@pytest.fixture
def test_data():
    with open(os.path.join(os.path.dirname(__file__), 'key_extension.json')) as f:
        return json.load(f, object_hook=datetime_parser)[0]


@pytest.mark.slow('gp')
def test_hnhm_split_sql(mocked_connection, test_data):
    entity = EntityExtKey
    source = StgTable

    def _get_calls(split_sql):
        try:
            with mocked_connection.transaction():
                mocked_connection.create_table(StgTable)
                mocked_connection.truncate(StgTable)
                mocked_connection.insert(StgTable, test_data['initial_source'])

            loader = HybridLoadGenerator(
                source=source,
                business_date_field=source.dt,
                source_system=oktell,
                set_ctl=False,
                split_sql=split_sql,
                connection=mocked_connection,
            ).target(entity).mappings({
                entity.entity_id: source.id,
                entity.entity_ext_id: _NoKey,
                entity.val: source.value,
            })

            mocked_connection._calls = []
            loader.run('1900-01-01')
            filtered_calls = [call_ for call_ in mocked_connection._calls if isinstance(call_, str)]
            yield len(mocked_connection._calls), len(filtered_calls)

            with mocked_connection.transaction():
                mocked_connection.create_table(source)
                mocked_connection.truncate(source)
                mocked_connection.insert(source, test_data['source'])

            meta = GPMeta(entity)

            start_utc = dtu.utcnow().replace(microsecond=0)
            run_test_key_extension_split_sql(False, source, entity, mocked_connection, split_sql)
            end_utc = dtu.utcnow().replace(microsecond=0)
            actual = get_actual(meta.table.get_main_class())
            target = sort_target(test_data['hub'])

            assert target == actual
            main_class_ctl = get_ctl().gp.get_param(meta.table.get_main_class(), CTL_LAST_SYNC_DATE)
            assert start_utc <= main_class_ctl <= end_utc

        finally:
            with mocked_connection.transaction():
                mocked_connection.drop_table(source)
                drop_dds_entity(entity, mocked_connection)

    result = [next(_get_calls(True)), next(_get_calls(False))]
    assert result[0][0] > result[1][0]  # More calls with splits
    assert result[0][1] > result[1][1]  # More strings as Query with splits
