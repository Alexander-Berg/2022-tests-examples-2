import datetime as dt
import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

_NOW = dt.datetime(2022, 5, 1, 13, 57, 8, tzinfo=dt.timezone.utc)

_DRIVER_LOGIN_TIMESTAMP = '2022-02-24T12:35:20.510109+03:00'
_CONTRACTOR_GEOHIERARCHIES_TIMESTAMP = '2022-02-24T11:23:07.58+00:00'

_TEST_PARK_ID = 'test_park_id'
_TEST_PROFILE_ID = 'test_profile_id'
_TEST_UDID = 'test_udid'


def make_set_event_type_node(event_type: str):
    return {
        'name': 'set-stq-event-type',
        'operation_variant': {
            'operation_name': 'set_string_value',
            'type': 'mapper',
            'arguments': {'value': event_type, 'dst_key': 'stq_event_type'},
        },
    }


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'pipeline_operations_config, pipeline_sink_config, expected_stq_kwargs',
    [
        pytest.param(
            [make_set_event_type_node('login')],
            {
                'sink_name': 'contractor_profile_events_sink',
                'arguments': {
                    'event_type_field_name': 'stq_event_type',
                    'dbid_field_name': 'park_id',
                    'uuid_field_name': 'profile_id',
                },
            },
            {
                'created_at': _NOW.isoformat(),
                'profile_event': {
                    'dbid': _TEST_PARK_ID,
                    'event_type': 'login',
                    'uuid': _TEST_PROFILE_ID,
                },
            },
            id='no tariff zone',
        ),
        pytest.param(
            [make_set_event_type_node('tariff_zone')],
            {
                'sink_name': 'contractor_profile_events_sink',
                'arguments': {
                    'event_type_field_name': 'stq_event_type',
                    'dbid_field_name': 'park_id',
                    'uuid_field_name': 'profile_id',
                    'tariff_zone_field_name': 'nothing',
                },
            },
            None,
            id='no tariff zone, but event type tariff_zone',
        ),
        pytest.param(
            [make_set_event_type_node('login')],
            {
                'sink_name': 'contractor_profile_events_sink',
                'arguments': {
                    'event_type_field_name': 'stq_event_type',
                    'dbid_field_name': 'park_id',
                    'uuid_field_name': 'profile_id',
                    'tariff_zone_field_name': 'topic',
                },
            },
            {
                'created_at': _NOW.isoformat(),
                'profile_event': {
                    'dbid': _TEST_PARK_ID,
                    'event_type': 'login',
                    'uuid': _TEST_PROFILE_ID,
                    'tariff_zone': 'priority',
                },
            },
            id='tariff zone set',
        ),
        pytest.param(
            [
                make_set_event_type_node('login'),
                {
                    'name': 'extract-tariff-zone',
                    'operation_variant': {
                        'operation_name': 'set_key_flat',
                        'type': 'mapper',
                        'arguments': {
                            'recursive_keys': ['geo_hierarchy', '0'],
                            'flat_key': 'extracted_tariff_zone',
                        },
                    },
                },
            ],
            {
                'sink_name': 'contractor_profile_events_sink',
                'arguments': {
                    'event_type_field_name': 'stq_event_type',
                    'dbid_field_name': 'park_id',
                    'uuid_field_name': 'profile_id',
                    'tariff_zone_field_name': 'extracted_tariff_zone',
                },
            },
            {
                'created_at': _NOW.isoformat(),
                'profile_event': {
                    'dbid': _TEST_PARK_ID,
                    'event_type': 'login',
                    'uuid': _TEST_PROFILE_ID,
                    'tariff_zone': 'first',
                },
            },
            id='tariff zone extract',
        ),
        pytest.param(
            [make_set_event_type_node('login')],
            {
                'sink_name': 'contractor_profile_events_sink',
                'arguments': {
                    'event_type_field_name': 'stq_event_type',
                    'dbid_field_name': 'park_id',
                    'uuid_field_name': 'profile_id',
                    'timestamp_field_name': 'wrong',
                },
            },
            {
                'created_at': _NOW.isoformat(),
                'profile_event': {
                    'dbid': _TEST_PARK_ID,
                    'event_type': 'login',
                    'uuid': _TEST_PROFILE_ID,
                },
            },
            id='wrong timestamp field',
        ),
        pytest.param(
            [make_set_event_type_node('logout')],
            {
                'sink_name': 'contractor_profile_events_sink',
                'arguments': {
                    'event_type_field_name': 'stq_event_type',
                    'dbid_field_name': 'park_id',
                    'uuid_field_name': 'profile_id',
                    'timestamp_field_name': 'timestamp_from_driver_login',
                },
            },
            {
                'created_at': '2022-02-24T09:35:20.510109+00:00',
                'profile_event': {
                    'dbid': _TEST_PARK_ID,
                    'event_type': 'logout',
                    'uuid': _TEST_PROFILE_ID,
                },
            },
            id='timestamp from driver login',
        ),
        pytest.param(
            [make_set_event_type_node('tags')],
            {
                'sink_name': 'contractor_profile_events_sink',
                'arguments': {
                    'event_type_field_name': 'stq_event_type',
                    'dbid_field_name': 'park_id',
                    'uuid_field_name': 'profile_id',
                    'timestamp_field_name': (
                        'timestamp_from_contractor_events_producer'
                    ),
                },
            },
            {
                'created_at': '2022-02-24T11:23:07.58+00:00',
                'profile_event': {
                    'dbid': _TEST_PARK_ID,
                    'event_type': 'tags',
                    'uuid': _TEST_PROFILE_ID,
                },
            },
            id='timestamp from contractor events producer',
        ),
        pytest.param(
            [make_set_event_type_node('bad')],
            {
                'sink_name': 'contractor_profile_events_sink',
                'arguments': {
                    'event_type_field_name': 'stq_event_type',
                    'dbid_field_name': 'park_id',
                    'uuid_field_name': 'profile_id',
                    'timestamp_field_name': (
                        'timestamp_from_contractor_events_producer'
                    ),
                },
            },
            None,
            id='skip on wrong event_type',
        ),
        pytest.param(
            [],
            {
                'sink_name': 'contractor_profile_events_sink',
                'arguments': {
                    'event_type_field_name': 'stq_event_type',
                    'dbid_field_name': 'park_id',
                    'uuid_field_name': 'profile_id',
                    'timestamp_field_name': (
                        'timestamp_from_contractor_events_producer'
                    ),
                },
            },
            None,
            id='skip on empty event_type',
        ),
        pytest.param(
            [make_set_event_type_node('rating')],
            {
                'sink_name': 'unique_drivers_events_sink',
                'arguments': {
                    'change_type_field_name': 'stq_event_type',
                    'unique_driver_id_field_name': 'unique_driver_id',
                    'timestamp_field_name': (
                        'timestamp_from_contractor_events_producer'
                    ),
                },
            },
            {
                'created_at': '2022-02-24T11:23:07.58+00:00',
                'unique_driver_event': {
                    'unique_driver_id': _TEST_UDID,
                    'change_type': 'rating',
                },
            },
            id='rating correct event with udid sink',
        ),
        pytest.param(
            [make_set_event_type_node('complete_scores')],
            {
                'sink_name': 'unique_drivers_events_sink',
                'arguments': {
                    'change_type_field_name': 'stq_event_type',
                    'unique_driver_id_field_name': 'unique_driver_id',
                    'timestamp_field_name': (
                        'timestamp_from_contractor_events_producer'
                    ),
                },
            },
            {
                'created_at': '2022-02-24T11:23:07.58+00:00',
                'unique_driver_event': {
                    'unique_driver_id': _TEST_UDID,
                    'change_type': 'complete_scores',
                },
            },
            id='complete_scores correct event with udid sink',
        ),
        pytest.param(
            [make_set_event_type_node('bad')],
            {
                'sink_name': 'unique_drivers_events_sink',
                'arguments': {
                    'change_type_field_name': 'stq_event_type',
                    'unique_driver_id_field_name': 'unique_driver_id',
                    'timestamp_field_name': (
                        'timestamp_from_contractor_events_producer'
                    ),
                },
            },
            None,
            id='incorrect udid sink event',
        ),
    ],
)
async def test_eventus_sinks(
        taxi_driver_priority,
        testpoint,
        stq,
        taxi_eventus_orchestrator_mock,
        pipeline_operations_config: List[Dict[str, Any]],
        pipeline_sink_config: Dict[str, Any],
        expected_stq_kwargs: Optional[Dict[str, Any]],
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    pipeline_config = [
        {
            'name': 'tags-events',
            'description': '',
            'st_ticket': '',
            'source': {'name': 'tags-events'},
            'root': {
                'operations': pipeline_operations_config,
                'output': pipeline_sink_config,
            },
        },
    ]

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_driver_priority, pipeline_config,
    )

    event = {
        'topic': 'priority',
        'park_id': _TEST_PARK_ID,
        'profile_id': _TEST_PROFILE_ID,
        'unique_driver_id': _TEST_UDID,
        'geo_hierarchy': ['first', 'second'],
        'timestamp_from_driver_login': _DRIVER_LOGIN_TIMESTAMP,
        'timestamp_from_contractor_events_producer': (
            _CONTRACTOR_GEOHIERARCHIES_TIMESTAMP
        ),
    }

    response = await taxi_driver_priority.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'tags-events',
                'data': json.dumps(event),
                'topic': 'smth',
                'cookie': 'cookie_for_adjust_sink_0',
            },
        ),
    )
    assert response.status_code == 200

    assert (await commit.wait_call())['data'] == 'cookie_for_adjust_sink_0'

    if expected_stq_kwargs:
        assert stq.recalculate_contractor_priorities.times_called == 1
        call_args = stq.recalculate_contractor_priorities.next_call()

        if 'log_extra' in call_args['kwargs']:
            del call_args['kwargs']['log_extra']

        assert call_args['queue'] == 'recalculate_contractor_priorities'

        assert call_args['kwargs'] == expected_stq_kwargs
    else:
        assert stq.recalculate_contractor_priorities.times_called == 0


@pytest.mark.parametrize(
    'base_sink_config, stq_event_type, error_injector_name',
    [
        pytest.param(
            {
                'sink_name': 'contractor_profile_events_sink',
                'arguments': {
                    'event_type_field_name': 'stq_event_type',
                    'dbid_field_name': 'park_id',
                    'uuid_field_name': 'profile_id',
                },
            },
            'tags',
            'profiles_injector',
            id='profiles sink',
        ),
        pytest.param(
            {
                'sink_name': 'unique_drivers_events_sink',
                'arguments': {
                    'change_type_field_name': 'stq_event_type',
                    'unique_driver_id_field_name': 'unique_driver_id',
                    'timestamp_field_name': (
                        'timestamp_from_contractor_events_producer'
                    ),
                },
            },
            'rating',
            'udids_injector',
            id='udid sink',
        ),
    ],
)
async def test_eventus_not_commit_on_error(
        taxi_driver_priority,
        testpoint,
        stq,
        taxi_eventus_orchestrator_mock,
        base_sink_config: Dict[str, Any],
        stq_event_type: str,
        error_injector_name: str,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('ContractorProfileEventsSink::ErrorInjector')
    def profiles_error_testpoint(data):
        return {'inject_failure': True}

    @testpoint('UniqueDriverEventsSink::ErrorInjector')
    def udids_error_testpoint(data):
        return {'inject_failure': True}

    attempts_count = 10

    pipeline_sink_config = base_sink_config
    pipeline_sink_config['error_handling_policy'] = {
        'retry_policy': {
            'attempts': attempts_count,
            'min_delay_ms': 1,
            'max_delay_ms': 10,
            'delay_factor': 2,
        },
        'erroneous_statistics_level': 'error',
    }

    operation = {
        'name': 'set-stq-event-type',
        'operation_variant': {
            'operation_name': 'delay_mapper',
            'type': 'mapper',
            'arguments': {'delay_interval_ms': 1},
        },
    }

    pipeline_config = [
        {
            'name': 'tags-events',
            'description': '',
            'st_ticket': '',
            'source': {'name': 'tags-events'},
            'root': {
                'operations': [operation],
                'output': pipeline_sink_config,
            },
        },
    ]

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_driver_priority, pipeline_config,
    )

    event = {
        'topic': 'priority',
        'park_id': _TEST_PARK_ID,
        'profile_id': _TEST_PROFILE_ID,
        'unique_driver_id': _TEST_UDID,
        'stq_event_type': stq_event_type,
        'timestamp_from_contractor_events_producer': (
            _CONTRACTOR_GEOHIERARCHIES_TIMESTAMP
        ),
    }

    response = await taxi_driver_priority.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'tags-events',
                'data': json.dumps(event),
                'topic': 'smth',
                'cookie': 'cookie_for_adjust_sink_0',
            },
        ),
    )
    assert response.status_code == 200

    expected_attempts_count = attempts_count

    if error_injector_name == 'profiles_injector':
        error_injector = profiles_error_testpoint
    elif error_injector_name == 'udids_injector':
        error_injector = udids_error_testpoint
    else:
        assert False, 'bad error injector'
    for _ in range(expected_attempts_count):
        await error_injector.wait_call()
        assert not commit.has_calls

    assert (
        stq.recalculate_contractor_priorities.times_called
        == expected_attempts_count
    )

    await commit.wait_call()
