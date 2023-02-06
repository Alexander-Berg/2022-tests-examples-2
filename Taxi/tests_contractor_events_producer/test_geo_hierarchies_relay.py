import datetime as dt
import json
from typing import List

import pytest

from tests_contractor_events_producer import db_tools
from tests_contractor_events_producer import geo_hierarchies


def to_geo_hierarchy_db(json_str: str):
    geo_hierarchy_json = json.loads(json_str)

    return geo_hierarchies.GeoHierarchyOutboxDb(
        geo_hierarchy_json['park_id'],
        geo_hierarchy_json['driver_id'],
        geo_hierarchy_json['geo_hierarchy'],
        dt.datetime.fromisoformat(geo_hierarchy_json['updated_at']),
    )


@pytest.mark.pgsql(
    'contractor_events_producer',
    queries=[
        db_tools.insert_geo_hierarchies_history(
            [
                geo_hierarchies.GeoHierarchyOutboxDb(
                    'dbid1',
                    'uuid1',
                    ['br_moscow', 'br_russia', 'br_root'],
                    dt.datetime.fromisoformat('2020-11-14T23:59:59+00:00'),
                ),
                geo_hierarchies.GeoHierarchyOutboxDb(
                    'dbid2',
                    'uuid2',
                    ['br_spb', 'br_russia', 'br_root'],
                    dt.datetime.fromisoformat('2020-11-16T22:59:59+03:00'),
                ),
                geo_hierarchies.GeoHierarchyOutboxDb(
                    'dbid3',
                    'uuid3',
                    ['br_baku', 'br_azerbaijan', 'br_root'],
                    dt.datetime.fromisoformat('2020-11-13T22:59:59+03:00'),
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'expected_left, expected_to_be_sent',
    (
        pytest.param(
            0,
            [
                geo_hierarchies.GeoHierarchyOutboxDb(
                    'dbid1',
                    'uuid1',
                    ['br_moscow', 'br_russia', 'br_root'],
                    dt.datetime.fromisoformat('2020-11-14T23:59:59+00:00'),
                ),
                geo_hierarchies.GeoHierarchyOutboxDb(
                    'dbid2',
                    'uuid2',
                    ['br_spb', 'br_russia', 'br_root'],
                    dt.datetime.fromisoformat('2020-11-16T22:59:59+03:00'),
                ),
                geo_hierarchies.GeoHierarchyOutboxDb(
                    'dbid3',
                    'uuid3',
                    ['br_baku', 'br_azerbaijan', 'br_root'],
                    dt.datetime.fromisoformat('2020-11-13T22:59:59+03:00'),
                ),
            ],
            id='send geo hierarchies with default limit',
        ),
        pytest.param(
            1,
            [
                geo_hierarchies.GeoHierarchyOutboxDb(
                    'dbid1',
                    'uuid1',
                    ['br_moscow', 'br_russia', 'br_root'],
                    dt.datetime.fromisoformat('2020-11-14T23:59:59+00:00'),
                ),
                geo_hierarchies.GeoHierarchyOutboxDb(
                    'dbid2',
                    'uuid2',
                    ['br_spb', 'br_russia', 'br_root'],
                    dt.datetime.fromisoformat('2020-11-16T22:59:59+03:00'),
                ),
            ],
            marks=[
                pytest.mark.config(
                    CONTRACTOR_EVENTS_PRODUCER_GEO_HIERARCHIES_RELAY={
                        'polling_delay_ms': 1000,
                        'chunk_size': 2,
                        'remove_from_db_attempts': 3,
                        'remove_from_db_retry_ms': 100,
                    },
                ),
            ],
            id='send geo hierarchies with limit 2',
        ),
    ),
)
async def test_relay(
        pgsql,
        testpoint,
        taxi_contractor_events_producer,
        expected_left: int,
        expected_to_be_sent: List[geo_hierarchies.GeoHierarchyOutboxDb],
):
    @testpoint('geo-hierarchies-relay::iteration')
    def relay_tp(_):
        pass

    @testpoint('logbroker_publish')
    def logbroker_tp(data):
        pass

    async with taxi_contractor_events_producer.spawn_task(
            'workers/geo-hierarchies-relay',
    ):
        await relay_tp.wait_call()

    assert logbroker_tp.times_called == len(expected_to_be_sent)

    for elem in expected_to_be_sent:
        message = logbroker_tp.next_call()['data']

        assert message['name'] == 'contractor-geo-hierarchies'
        assert to_geo_hierarchy_db(message['data']) == elem

    actually_left = len(db_tools.get_geo_hierarchies_in_outbox(pgsql))

    assert actually_left == expected_left


async def test_not_send_already_sended(
        pgsql, mockserver, testpoint, taxi_contractor_events_producer,
):
    fill_outbox_query = db_tools.insert_geo_hierarchies_history(
        [
            geo_hierarchies.GeoHierarchyOutboxDb(
                'dbid1',
                'uuid1',
                ['br_moscow', 'br_russia', 'br_root'],
                dt.datetime.fromisoformat('2020-11-14T23:59:59+00:00'),
            ),
            geo_hierarchies.GeoHierarchyOutboxDb(
                'dbid2',
                'uuid2',
                ['br_spb', 'br_russia', 'br_root'],
                dt.datetime.fromisoformat('2020-11-16T22:59:59+03:00'),
            ),
        ],
    )

    pgsql['contractor_events_producer'].cursor().execute(fill_outbox_query)

    inject_error = True

    @testpoint('geo-hierarchies-relay::error-injector')
    def relay_error_testpoint(data):
        nonlocal inject_error
        return {'inject_failure': inject_error}

    @testpoint('geo-hierarchies-relay::iteration')
    def relay_testpoint(arg):
        pass

    @testpoint('logbroker_publish')
    def logbroker_commit(data):
        pass

    with pytest.raises(taxi_contractor_events_producer.TestsuiteTaskFailed):
        async with taxi_contractor_events_producer.spawn_task(
                'workers/geo-hierarchies-relay',
        ):
            await relay_error_testpoint.wait_call()

    assert logbroker_commit.times_called == 2

    actual_left_events_count = len(
        db_tools.get_geo_hierarchies_in_outbox(pgsql),
    )
    # events not deleted in db because of injected error
    assert actual_left_events_count == 2

    inject_error = False

    async with taxi_contractor_events_producer.spawn_task(
            'workers/geo-hierarchies-relay',
    ):
        await relay_testpoint.wait_call()

    # no new lb calls
    assert logbroker_commit.times_called == 2

    actual_left_events_count = len(
        db_tools.get_geo_hierarchies_in_outbox(pgsql),
    )

    assert actual_left_events_count == 0
