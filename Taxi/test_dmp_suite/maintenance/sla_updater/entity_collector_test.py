import mock
from lazy_object_proxy import Proxy

from dmp_suite import yt, greenplum as gp
from dmp_suite.ctl import CTL_LAST_SYNC_DATE
from dmp_suite.ctl.extensions.domain.greenplum import GP_DOMAIN
from dmp_suite.ctl.extensions.domain.yt import YT_DOMAIN
from dmp_suite.maintenance.sla_updater.entity_collector import collect_entities


def lazy_import():
    from . import hnhm_tables
    return hnhm_tables


tables = Proxy(lazy_import)


def test_collect_entities():
    with mock.patch(
        'dmp_suite.maintenance.sla_updater.entity_collector.find_tables',
        return_value=[tables.TestGPTable, tables.TestYTTable]
    ):
        sla_entities = list(collect_entities(pymodule='test_dmp_suite'))

    assert len(sla_entities) == 1 + 2
    assert all(sla_entity.domain in (GP_DOMAIN, YT_DOMAIN) for sla_entity in sla_entities)

    for sla_entity in sla_entities:
        if sla_entity.domain == GP_DOMAIN:
            meta = gp.GPMeta(tables.TestGPTable)
            assert sla_entity.entity_name == meta.table_full_name
        else:
            meta = yt.YTMeta(tables.TestYTTable)
            assert sla_entity.entity_name == meta.target_path_wo_partition.rstrip('/')
        assert sla_entity.warn_sec == 1
        assert sla_entity.crit_sec == 2


def test_collect_entities_hnhm_entity():
    hnhm_tables = [
        tables.TestHnhmEntityTableTop,
        tables.TestHnhmEntityTableBottom,
        tables.TestHnhmEntityTableAlias,
    ]

    for table in hnhm_tables:
        with mock.patch(
            'dmp_suite.maintenance.sla_updater.entity_collector.find_tables',
            return_value=[table]
        ):
            sla_entities = list(collect_entities(pymodule='test_dmp_suite'))

        assert len(sla_entities) == 2 * 3
        assert all(sla_entity.domain == GP_DOMAIN for sla_entity in sla_entities)
        for sla_entity in sla_entities:
            if sla_entity.param_code == 'last_sync_date':
                assert sla_entity.warn_sec == 12
                assert sla_entity.crit_sec == 21
            elif sla_entity.param_code == 'last_load_date':
                assert sla_entity.warn_sec == 123
                assert sla_entity.crit_sec == 321
            else:
                assert False


def test_collect_entities_hnhm_link():
    with mock.patch(
        'dmp_suite.maintenance.sla_updater.entity_collector.find_tables',
        return_value=[tables.TestHnhmLink]
    ):
        sla_entities = list(collect_entities(pymodule='test_dmp_suite'))

    assert len(sla_entities) == 1
    sla_entity = sla_entities[0]
    expected_table_full_name = gp.GPMeta(tables.TestHnhmLink).table_full_name

    assert sla_entity.entity_name == expected_table_full_name
    assert sla_entity.domain == GP_DOMAIN
    assert sla_entity.param_code == CTL_LAST_SYNC_DATE.name
    assert sla_entity.warn_sec == 1
    assert sla_entity.crit_sec == 2


def test_collect_entities_with_hnhm_partitioned():
    with mock.patch(
        'dmp_suite.maintenance.sla_updater.entity_collector.find_tables',
        return_value=[tables.TestHnhmEntityWithPartitionKey]
    ):
        sla_entities = list(collect_entities(pymodule='test_dmp_suite'))

    # Поле "c" не может попасть, поэтому ровно 2 поля
    assert len(sla_entities) == 2
