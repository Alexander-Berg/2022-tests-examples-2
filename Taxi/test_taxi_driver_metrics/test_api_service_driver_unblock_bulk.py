import datetime
from operator import itemgetter

import pytest

from taxi_driver_metrics.common.models import DriverInfo

HANDLER_PATH = 'v1/service/driver/unblock_bulk'
CHECK_HANDLER_PATH = 'v1/service/driver/unblock_bulk/check'


UDID_1 = '5b05621ee6c22ea2654849c9'
UDID_2 = '5b05621ee6c22ea2654849c0'
UDID_NOT_BLOCKED = '5b05621ee6c22ea2654849c1'
UDID_3 = '5b05621ee6c22ea2654849c2'
UDID_NOT_VALID = 'not_valid'
TIMESTAMP = datetime.datetime(2016, 5, 8, 10, 0, 0, 0)
EVENT_NEW_URL = '/driver-metrics-storage/v2/event/new'


@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.config(DRIVER_METRICS_MAX_COUNT_UDIDS_FOR_BULK_API=3)
@pytest.mark.filldb(unique_drivers='common')
async def test_unblock_drivers_by_udids(
        web_context,
        web_app_client,
        fake_event_provider,
        mockserver,
        dms_mockserver,
):
    @mockserver.json_handler(EVENT_NEW_URL)
    async def event_new(*args, **kwargs):
        return {}

    app = web_context

    driver_1 = await DriverInfo.make(
        app, UDID_1, fake_event_provider([]), TIMESTAMP,
    )
    driver_2 = await DriverInfo.make(
        app, UDID_2, fake_event_provider([]), TIMESTAMP,
    )
    driver_3 = await DriverInfo.make(
        app, UDID_NOT_BLOCKED, fake_event_provider([]), TIMESTAMP,
    )
    assert driver_1.blocking_state
    assert driver_2.blocking_state
    assert not driver_3.blocking_state
    assert driver_1.current_blocking
    assert driver_2.current_blocking
    assert not driver_3.current_blocking

    udids = [UDID_1, UDID_2, UDID_NOT_BLOCKED]

    response = await web_app_client.post(
        HANDLER_PATH, json={'unique_driver_ids': udids},
    )
    assert event_new.times_called
    content = await response.json()

    driver_1 = await DriverInfo.make(
        app, UDID_1, fake_event_provider([]), TIMESTAMP,
    )
    driver_2 = await DriverInfo.make(
        app, UDID_2, fake_event_provider([]), TIMESTAMP,
    )
    assert content['num_unblocked'] == 2
    assert not driver_1.blocking_state
    assert not driver_2.blocking_state
    assert not driver_1.current_blocking
    assert not driver_2.current_blocking

    udids = [UDID_1, UDID_2, UDID_NOT_VALID]

    response = await web_app_client.post(
        HANDLER_PATH, json={'unique_driver_ids': udids},
    )

    assert response.status == 400

    udids = [UDID_1, UDID_2]

    response = await web_app_client.post(
        HANDLER_PATH, json={'unique_driver_ids': udids},
    )
    content = await response.json()
    assert content['num_unblocked'] == 0

    udids = [UDID_1, UDID_2, UDID_NOT_BLOCKED, UDID_3]
    response = await web_app_client.post(
        HANDLER_PATH, json={'unique_driver_ids': udids},
    )
    assert response.status == 400


@pytest.mark.now(TIMESTAMP.isoformat())
@pytest.mark.filldb(unique_drivers='common')
async def test_unblock_drivers_by_udids_with_exception(
        taxi_driver_metrics, mockserver,
):
    @mockserver.json_handler(EVENT_NEW_URL)
    async def event_new(*args, **kwargs):
        return mockserver.make_response('error', status=500)

    udids = [UDID_1, UDID_2, UDID_NOT_BLOCKED]

    response = await taxi_driver_metrics.post(
        HANDLER_PATH, json={'unique_driver_ids': udids},
    )
    assert event_new.times_called

    assert response.status == 200
    response_json = await response.json()
    errors = sorted(response_json['errors'], key=itemgetter('udid'))
    assert errors == [
        {'error': '', 'udid': '5b05621ee6c22ea2654849c0'},
        {'error': '', 'udid': '5b05621ee6c22ea2654849c9'},
    ]


async def test_unblock_drivers_check(web_app_client):
    udids = [UDID_1, UDID_2, UDID_NOT_BLOCKED]

    response = await web_app_client.post(
        CHECK_HANDLER_PATH, json={'unique_driver_ids': udids},
    )

    assert response.status == 200
    response_json = await response.json()

    assert response_json == {
        'data': {
            'unique_driver_ids': [
                '5b05621ee6c22ea2654849c9',
                '5b05621ee6c22ea2654849c0',
                '5b05621ee6c22ea2654849c1',
            ],
        },
    }

    udids = [UDID_1, '123.,.,.,\\]]}[p[p-==+']

    response = await web_app_client.post(
        CHECK_HANDLER_PATH, json={'unique_driver_ids': udids},
    )
    assert response.status == 400
