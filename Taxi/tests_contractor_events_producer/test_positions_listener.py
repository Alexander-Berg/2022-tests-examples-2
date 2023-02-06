import datetime as dt
from typing import List

# pylint: disable=import-error
from geobus_tools import geobus
import pytest

from testsuite.utils import callinfo

from tests_contractor_events_producer import db_tools
from tests_contractor_events_producer import geo_hierarchies


MOSCOW_POSITION = [37.5, 55.5]
SPB_POSITION = [30.5, 59.5]
UNKNOWN_POSITION = [0.0, 0.0]

BR_MOSCOW_HASH = -5773412326495586962
BR_MOSCOW_GH = ['moscow', 'br_moscow', 'br_russia', 'br_root']

BR_SPB_HASH = -3212398904552146072
BR_SPB_GH = ['spb', 'br_spb', 'br_russia', 'br_root']

BR_UNKNOWN_HASH = 0
BR_UNKNOWN_GH: List[str] = []

POSITION_TS = 1577836800
POSITION_DT = dt.datetime(2020, 1, 1, 0, 0, tzinfo=dt.timezone.utc)


async def redis_publish(redis_store, channel, message, callback):
    for _ in range(5):
        redis_store.publish(channel, message)

        try:
            await callback.wait_call(1)

            return
        except callinfo.CallQueueTimeoutError:
            pass


@pytest.mark.geoareas(filename='geoareas_moscow_spb.json')
@pytest.mark.tariffs(filename='tariffs_moscow_spb.json')
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        {
            'name': 'br_russia',
            'name_en': 'Russia',
            'name_ru': 'Россия',
            'node_type': 'root',
            'parent_name': 'br_root',
            'region_id': '225',
        },
        {
            'name': 'br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'root',
            'parent_name': 'br_russia',
            'tariff_zones': ['moscow'],
        },
        {
            'name': 'br_spb',
            'name_en': 'St. Petersburg',
            'name_ru': 'Cанкт-Петербург',
            'node_type': 'root',
            'parent_name': 'br_russia',
            'tariff_zones': ['spb'],
            'region_id': '2',
        },
    ],
)
@pytest.mark.parametrize(
    'drivers, expected_gh_db, expected_gh_outbox_db',
    (
        pytest.param(
            [
                {
                    'driver_id': f'dbid{idx}_uuid{idx}',
                    'position': MOSCOW_POSITION if idx % 2 else SPB_POSITION,
                    'direction': 0,
                    'timestamp': POSITION_TS,
                    'speed': 20,
                    'accuracy': 0,
                }
                for idx in range(10)
            ],
            [
                geo_hierarchies.GeoHierarchyDb(
                    f'dbid{idx}',
                    f'uuid{idx}',
                    BR_MOSCOW_HASH if idx % 2 else BR_SPB_HASH,
                    POSITION_DT,
                )
                for idx in range(10)
            ],
            [
                geo_hierarchies.GeoHierarchyOutboxDb(
                    f'dbid{idx}',
                    f'uuid{idx}',
                    BR_MOSCOW_GH if idx % 2 else BR_SPB_GH,
                    POSITION_DT,
                )
                for idx in range(10)
            ],
            marks=[
                pytest.mark.config(
                    CONTRACTOR_EVENTS_PRODUCER_POSITIONS_LISTENER_SETTINGS={
                        'enabled': True,
                        'accumulation_queue_limit': 1,
                    },
                ),
            ],
            id='everyone',
        ),
        pytest.param(
            [
                {
                    'driver_id': f'dbid{idx}_uuid{idx}',
                    'position': MOSCOW_POSITION if idx % 2 else SPB_POSITION,
                    'direction': 0,
                    'timestamp': POSITION_TS,
                    'speed': 20,
                    'accuracy': 0,
                }
                for idx in range(10)
            ],
            [
                geo_hierarchies.GeoHierarchyDb(
                    f'dbid{idx}',
                    f'uuid{idx}',
                    BR_MOSCOW_HASH if idx % 2 else BR_SPB_HASH,
                    POSITION_DT,
                )
                for idx in range(4)
            ],
            [
                geo_hierarchies.GeoHierarchyOutboxDb(
                    f'dbid{idx}',
                    f'uuid{idx}',
                    BR_MOSCOW_GH if idx % 2 else BR_SPB_GH,
                    POSITION_DT,
                )
                for idx in range(4)
            ],
            marks=[
                pytest.mark.config(
                    CONTRACTOR_EVENTS_PRODUCER_POSITIONS_LISTENER_SETTINGS={
                        'enabled': True,
                        'count_to_process': 4,
                        'accumulation_queue_limit': 1,
                    },
                ),
            ],
            id='first four',
        ),
        pytest.param(
            [
                {
                    'driver_id': f'dbid{idx}_uuid{idx}',
                    'position': (
                        MOSCOW_POSITION if idx % 2 else UNKNOWN_POSITION
                    ),
                    'direction': 0,
                    'timestamp': POSITION_TS,
                    'speed': 20,
                    'accuracy': 0,
                }
                for idx in range(2)
            ],
            [
                geo_hierarchies.GeoHierarchyDb(
                    f'dbid{idx}',
                    f'uuid{idx}',
                    BR_MOSCOW_HASH if idx % 2 else BR_UNKNOWN_HASH,
                    POSITION_DT,
                )
                for idx in range(2)
            ],
            [
                geo_hierarchies.GeoHierarchyOutboxDb(
                    f'dbid{idx}',
                    f'uuid{idx}',
                    BR_MOSCOW_GH if idx % 2 else BR_UNKNOWN_GH,
                    POSITION_DT,
                )
                for idx in range(2)
            ],
            marks=[
                pytest.mark.config(
                    CONTRACTOR_EVENTS_PRODUCER_POSITIONS_LISTENER_SETTINGS={
                        'enabled': True,
                        'accumulation_queue_limit': 1,
                    },
                ),
            ],
            id='unknown geo hierarchy',
        ),
    ),
)
async def test_geo_hierarchy_storage(
        pgsql,
        redis_store,
        testpoint,
        taxi_contractor_events_producer,
        now,
        tariffs,
        geoareas,
        drivers,
        expected_gh_db,
        expected_gh_outbox_db,
):
    @testpoint('positions-listener::process_payload_begin')
    def process_payload_begin_tp(_):
        pass

    @testpoint('positions-listener::process_payload_end')
    def process_payload_end_tp(_):
        pass

    @testpoint('positions-listener::push_accumulated_data')
    def push_accumulated_data_tp(_):
        pass

    @testpoint('positions-listener::accumulate_contractors_iteration')
    def accumulate_contractors_tp(_):
        pass

    @testpoint('positions-listener::process_contractors_iteration')
    def process_contractors_tp(_):
        pass

    await taxi_contractor_events_producer.enable_testpoints()

    message = geobus.serialize_positions_v2(drivers, now)

    await redis_publish(
        redis_store,
        'channel:yagr:position',
        message,
        process_payload_begin_tp,
    )

    await process_payload_end_tp.wait_call()
    await accumulate_contractors_tp.wait_call()
    await push_accumulated_data_tp.wait_call()
    await process_contractors_tp.wait_call()

    assert db_tools.get_geo_hierarchies(pgsql) == expected_gh_db
    assert (
        db_tools.get_geo_hierarchies_in_outbox(pgsql) == expected_gh_outbox_db
    )
