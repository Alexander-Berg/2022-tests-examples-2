import pytest

from tests_subventions_activity_producer import common
from tests_subventions_activity_producer import pg_helpers
from tests_subventions_activity_producer import redis_helpers


@pytest.mark.parametrize(
    'init_pg_doc, init_redis_doc',
    [('pg_init_raw_events_grouped.json', 'redis_init.json')],
)
@pytest.mark.now('2020-01-01T01:30:00+00:00')
@common.suspend_all_periodic_tasks
async def test_write_activity_events_for_verification(
        taxi_subventions_activity_producer,
        testpoint,
        load_json,
        taxi_config,
        pgsql,
        redis_store,
        init_pg_doc,
        init_redis_doc,
):
    pg_helpers.init_raw_driver_events_grouped(load_json, pgsql, [init_pg_doc])
    redis_helpers.prepare_storage(redis_store, load_json(init_redis_doc))

    additional_settings = {
        'destinations': [
            'activity_events_unsent',
            'incomplete_events',
            'events_verification',
        ],
    }

    await common.run_activity_producer_once(
        taxi_subventions_activity_producer,
        taxi_config,
        enable_redis=True,
        enable_postgres=True,
        **additional_settings,
    )

    expected_doc = {
        'end': '2020-01-01T00:01:00+00:00',
        'clid': 'clid1',
        'dbid': 'dbid1',
        'udid': 'udid1',
        'uuid': 'uuid1',
        'start': '2020-01-01T00:00:00+00:00',
        'rule_types': ['geo_booking'],
        'activities': [
            {
                'end': '2020-01-01T00:00:24+00:00',
                'tags': ['fixer'],
                'start': '2020-01-01T00:00:15+00:00',
                'status': 'free',
                'geoareas': ['zone1'],
                'activity_points': 88.0,
                'available_tariff_classes': ['econom', 'business'],
                'profile_payment_type_restrictions': 'none',
            },
        ],
    }

    events = pg_helpers.get_verification_events(pgsql, pg_helpers.SHARDS[0])
    assert len(events) == 1
    for event in events:
        assert event['event_id'] == 'udid1_2020-01-01T00:00'
        assert expected_doc == event['event_from_pg']
        assert expected_doc == event['event_from_redis']


@pytest.mark.parametrize(
    'should_work',
    [
        pytest.param(
            True,
            marks=[pytest.mark.now('2020-01-01T00:02:00+00:00')],
            id='time_to_work',
        ),
        pytest.param(
            False,
            marks=[pytest.mark.now('2020-01-01T00:01:59+00:00')],
            id='early_to_work',
        ),
    ],
)
@common.suspend_all_periodic_tasks
async def test_events_verificator(
        taxi_subventions_activity_producer,
        testpoint,
        load_json,
        taxi_config,
        pgsql,
        redis_store,
        should_work,
):
    pg_helpers.init_activity_events_verification(
        load_json,
        pgsql,
        ['pg_init_activity_events_verification.json'] * len(pg_helpers.SHARDS),
    )

    verification_result = {}

    @testpoint('events-verification-result')
    def _on_result(request):
        nonlocal verification_result
        verification_result = request
        return {}

    await common.run_events_verificator_once(
        taxi_subventions_activity_producer, taxi_config,
    )

    events = pg_helpers.get_verification_events(pgsql, pg_helpers.SHARDS[0])

    if should_work:
        assert events == []
    else:
        assert len(events) == len(pg_helpers.SHARDS)

    assert _on_result.times_called == len(pg_helpers.SHARDS)
    assert verification_result['count_matched'] == 1 * int(should_work)
    assert verification_result['count_mismatched'] == 2 * int(should_work)
