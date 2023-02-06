# pylint: disable=import-only-modules

import json

import pytest

from .utils import select_named


def get_task_name():
    return 'events-uploader'


def build_default_whitelist():
    return {
        '__default__': [],
        'home': ['offer_created', 'offer_expired', 'violation', 'stop'],
        'poi': ['offer_created', 'offer_expired', 'violation', 'stop'],
    }


@pytest.mark.uservice_oneshot
@pytest.mark.config(
    REPOSITION_API_EVENTS_UPLOADER_CONFIG={
        'enabled': False,
        'events_ttl_s': 300,
        'processing_items_limit': 200,
        'mode_types_whitelist': build_default_whitelist(),
    },
)
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'reposition_events.sql'],
)
@pytest.mark.now('2019-09-01T13:00:05')
async def test_disabled(taxi_reposition_api, mockserver):
    @mockserver.json_handler('/driver-metrics-storage/v1/event/new/bulk')
    def mock(request):
        events = json.loads(request.get_data())['events']
        response = [
            {'idempotency_token': f'whatever_{idx}'}
            for idx in range(len(events))
        ]

        return mockserver.make_response(
            json.dumps({'events': response}), status=200,
        )

    assert (
        await taxi_reposition_api.post(
            '/service/cron', {'task_name': get_task_name()},
        )
    ).status_code == 200

    assert mock.times_called == 0


@pytest.mark.uservice_oneshot
@pytest.mark.now('2019-09-01T13:00:05')
@pytest.mark.config(
    REPOSITION_API_EVENTS_UPLOADER_CONFIG={
        'enabled': True,
        'events_ttl_s': 300,
        'processing_items_limit': 200,
        'mode_types_whitelist': build_default_whitelist(),
    },
)
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'reposition_events.sql'],
)
async def test_upload(
        taxi_reposition_api, taxi_reposition_api_monitor, pgsql, mockserver,
):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def ud_mock(request):
        response = {
            'uniques': [
                {
                    'park_driver_profile_id': 'dbid777_uuid3',
                    'data': {'unique_driver_id': 'udid3'},
                },
            ],
        }

        return mockserver.make_response(json.dumps(response), status=200)

    @mockserver.json_handler('/driver-metrics-storage/v1/event/new/bulk')
    def dms_mock(request):
        events = json.loads(request.get_data())['events']
        response = []

        for event in events:
            assert 'descriptor' in event
            if event['descriptor']['tags'][0] == 'valid_tag':
                assert event['unique_driver_id'] == 'udid3'

                response.append({'idempotency_token': 'ok_whatever'})
            else:
                response.append(
                    {
                        'idempotency_token': 'err_whatever',
                        'error': {
                            'code': 'BAD_REQUEST',
                            'message': 'Bad Request',
                        },
                    },
                )

        return mockserver.make_response(
            json.dumps({'events': response}), status=200,
        )

    query = (
        'SELECT event_id '
        'FROM state.uploading_reposition_events '
        'WHERE uploaded = FALSE'
    )

    rows = select_named(query, pgsql['reposition'])

    assert len(rows) == 3
    assert rows[0]['event_id'] == 1001  # expected to be uploaded
    assert rows[1]['event_id'] == 1002  # expected to be skipped
    assert rows[2]['event_id'] == 1003  # expected to be discarded

    assert (
        await taxi_reposition_api.post(
            '/service/cron', {'task_name': get_task_name()},
        )
    ).status_code == 200

    await ud_mock.wait_call()
    await dms_mock.wait_call()

    rows = select_named(query, pgsql['reposition'])

    assert len(rows) == 2
    assert rows[0]['event_id'] == 1002  # skipped
    assert rows[1]['event_id'] == 1003  # discarded

    metrics = await taxi_reposition_api_monitor.get_metric('events-uploader')
    del metrics['latency_s']

    assert metrics == {
        'ok_total': 2,
        'ok_processed': 1,
        'warn_unknown_udid': 0,
        'error_processed': 1,
    }


@pytest.mark.uservice_oneshot
@pytest.mark.now('2019-09-01T13:10:00')
@pytest.mark.config(
    REPOSITION_API_EVENTS_UPLOADER_CONFIG={
        'enabled': True,
        'events_ttl_s': 300,
        'processing_items_limit': 200,
        'mode_types_whitelist': build_default_whitelist(),
    },
)
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'reposition_events.sql'],
)
async def test_types_events_ttl(
        taxi_reposition_api, taxi_reposition_api_monitor, pgsql, mockserver,
):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def ud_mock(request):
        response = {
            'uniques': [
                {
                    'park_driver_profile_id': 'dbid777_uuid3',
                    'data': {'unique_driver_id': 'udid3'},
                },
            ],
        }

        return mockserver.make_response(json.dumps(response), status=200)

    @mockserver.json_handler('/driver-metrics-storage/v1/event/new/bulk')
    def dms_mock(request):
        events = json.loads(request.get_data())['events']
        response = [
            {'idempotency_token': f'whatever_{idx}'}
            for idx in range(len(events))
        ]

        return mockserver.make_response(
            json.dumps({'events': response}), status=200,
        )

    query = (
        'SELECT event_id FROM state.uploading_reposition_events '
        'WHERE uploaded = FALSE'
    )

    rows = select_named(query, pgsql['reposition'])

    assert len(rows) == 3
    assert rows[0]['event_id'] == 1001  # expected to be skipped
    assert rows[1]['event_id'] == 1002  # expected to be skipped
    assert rows[2]['event_id'] == 1003  # expected to be uploaded

    assert (
        await taxi_reposition_api.post(
            '/service/cron', {'task_name': get_task_name()},
        )
    ).status_code == 200

    await ud_mock.wait_call()
    await dms_mock.wait_call()

    rows = select_named(query, pgsql['reposition'])

    assert len(rows) == 2
    assert rows[0]['event_id'] == 1001
    assert rows[1]['event_id'] == 1002

    metrics = await taxi_reposition_api_monitor.get_metric('events-uploader')
    del metrics['latency_s']

    assert metrics == {
        'ok_total': 1,
        'ok_processed': 1,
        'warn_unknown_udid': 0,
        'error_processed': 0,
    }


@pytest.mark.uservice_oneshot
@pytest.mark.now('2019-09-01T13:00:07')
@pytest.mark.config(
    REPOSITION_API_EVENTS_UPLOADER_CONFIG={
        'enabled': True,
        'events_ttl_s': 300,
        'processing_items_limit': 200,
        'mode_types_whitelist': {
            '__default__': [],
            'home': ['offer_created', 'offer_expired', 'stop'],
        },
    },
)
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'reposition_events.sql'],
)
async def test_types_whitelist(
        taxi_reposition_api, taxi_reposition_api_monitor, pgsql, mockserver,
):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def ud_mock(request):
        response = {
            'uniques': [
                {
                    'park_driver_profile_id': 'dbid777_uuid3',
                    'data': {'unique_driver_id': 'udid3'},
                },
            ],
        }

        return mockserver.make_response(json.dumps(response), status=200)

    @mockserver.json_handler('/driver-metrics-storage/v1/event/new/bulk')
    def dms_mock(request):
        events = json.loads(request.get_data())['events']
        response = [
            {'idempotency_token': f'whatever_{idx}'}
            for idx in range(len(events))
        ]

        return mockserver.make_response(
            json.dumps({'events': response}), status=200,
        )

    query = (
        'SELECT event_id FROM state.uploading_reposition_events '
        'WHERE uploaded = FALSE'
    )

    rows = select_named(query, pgsql['reposition'])

    assert len(rows) == 3
    assert rows[0]['event_id'] == 1001  # expected to be uploaded
    assert rows[1]['event_id'] == 1002  # expected to be uploaded
    assert rows[2]['event_id'] == 1003  # expected to be uploaded

    assert (
        await taxi_reposition_api.post(
            '/service/cron', {'task_name': get_task_name()},
        )
    ).status_code == 200

    await ud_mock.wait_call()
    await dms_mock.wait_call()

    rows = select_named(query, pgsql['reposition'])

    assert not rows

    metrics = await taxi_reposition_api_monitor.get_metric('events-uploader')
    del metrics['latency_s']

    assert metrics == {
        'ok_total': 3,
        'ok_processed': 3,
        'warn_unknown_udid': 0,
        'error_processed': 0,
    }


@pytest.mark.uservice_oneshot
@pytest.mark.now('2019-09-01T13:00:10')
@pytest.mark.config(
    REPOSITION_API_EVENTS_UPLOADER_CONFIG={
        'enabled': True,
        'events_ttl_s': 300,
        'processing_items_limit': 1,
        'mode_types_whitelist': build_default_whitelist(),
    },
)
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'reposition_events.sql'],
)
async def test_limit(
        taxi_reposition_api, taxi_reposition_api_monitor, pgsql, mockserver,
):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def ud_mock(request):
        response = {
            'uniques': [
                {
                    'park_driver_profile_id': 'dbid777_uuid3',
                    'data': {'unique_driver_id': 'udid3'},
                },
            ],
        }

        return mockserver.make_response(json.dumps(response), status=200)

    @mockserver.json_handler('/driver-metrics-storage/v1/event/new/bulk')
    def dms_mock(request):
        events = json.loads(request.get_data())['events']
        response = [
            {'idempotency_token': f'whatever_{idx}'}
            for idx in range(len(events))
        ]

        return mockserver.make_response(
            json.dumps({'events': response}), status=200,
        )

    query = (
        'SELECT event_id FROM state.uploading_reposition_events '
        'WHERE uploaded = FALSE'
    )

    rows = select_named(query, pgsql['reposition'])

    assert len(rows) == 3
    assert rows[0]['event_id'] == 1001  # expected to be uploaded
    assert rows[1]['event_id'] == 1002  # expected to be skipped
    assert rows[2]['event_id'] == 1003  # expected to be skipped

    assert (
        await taxi_reposition_api.post(
            '/service/cron', {'task_name': get_task_name()},
        )
    ).status_code == 200

    await ud_mock.wait_call()
    await dms_mock.wait_call()

    rows = select_named(query, pgsql['reposition'])

    assert len(rows) == 2
    assert rows[0]['event_id'] == 1002  # skipped
    assert rows[1]['event_id'] == 1003  # skipped

    metrics = await taxi_reposition_api_monitor.get_metric('events-uploader')
    del metrics['latency_s']

    assert metrics == {
        'ok_total': 1,
        'ok_processed': 1,
        'warn_unknown_udid': 0,
        'error_processed': 0,
    }
