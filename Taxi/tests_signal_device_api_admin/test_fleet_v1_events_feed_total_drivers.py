import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = '/fleet/signal-device-api-admin/v1/events/feed/total/drivers'


@pytest.fixture(name='driver_status')
def _mock_driver_status(mockserver):
    class DriverStatusContext:
        def __init__(self):
            self.v2_status_responses = []
            self.current_idx = 0

        def set_v2_status_responses(self, response, amount_in_response):
            chunks = utils.chunks(response['statuses'], amount_in_response)
            self.v2_status_responses = [
                {'statuses': chunk} for chunk in chunks
            ]

    context = DriverStatusContext()

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _get_driver_statuses(request):
        response = context.v2_status_responses[context.current_idx]
        context.current_idx += 1
        return response

    return context


def make_work_statuses_total(*, online, offline, busy, on_order):
    def make_work_status_total(work_status, amount):
        return {'work_status': work_status, 'amount': amount}

    result = []
    result.append(make_work_status_total('online', online))
    result.append(make_work_status_total('offline', offline))
    result.append(make_work_status_total('busy', busy))
    result.append(make_work_status_total('on_order', on_order))
    return result


DRIVER_STATUS_V2_RESPONSE1 = {
    'statuses': [
        {
            'park_id': 'p1',
            'driver_id': 'd1',
            'status': 'online',
            'updated_ts': 12345,
        },
        {
            'park_id': 'p1',
            'driver_id': 'd2',
            'status': 'busy',
            'updated_ts': 12345,
        },
        {
            'park_id': 'p1',
            'driver_id': 'd3',
            'status': 'busy',
            'orders': [],
            'updated_ts': 12345,
        },
        {
            'park_id': 'p1',
            'driver_id': 'd228',
            'status': 'busy',
            'orders': [{'id': 'some_id', 'status': 'driving'}],
            'updated_ts': 12345,
        },
        {
            'park_id': 'p1',
            'driver_id': 'd2213242148',
            'status': 'offline',
            'updated_ts': 12345,
        },
    ],
}

DRIVER_STATUS_V2_RESPONSE2 = {
    'statuses': [
        {
            'park_id': 'p1',
            'driver_id': 'd1',
            'status': 'online',
            'updated_ts': 12345,
        },
        {
            'park_id': 'p1',
            'driver_id': 'd2',
            'status': 'offline',
            'updated_ts': 12345,
        },
        {
            'park_id': 'p1',
            'driver_id': 'd3',
            'status': 'busy',
            'orders': [{'id': 'some_id', 'status': 'driving'}],
            'updated_ts': 12345,
        },
        {
            'park_id': 'p1',
            'driver_id': 'd4',
            'status': 'busy',
            'orders': [{'id': 'some_id', 'status': 'driving'}],
            'updated_ts': 12345,
        },
    ],
}

V2_STATUSES_AMOUNT_IN_CHUNK = 5


@pytest.mark.now('2020-08-11 15:00:03 +00:00')
@pytest.mark.pgsql('signal_device_api_meta_db', files=['events.sql'])
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_DRIVER_STATUS_SETTINGS=V2_STATUSES_AMOUNT_IN_CHUNK,
)
@pytest.mark.parametrize(
    'park_id, body, driver_status_response, amount_in_v2_statuses_response, '
    'expected_code, expected_response',
    [
        (
            'p1',
            {},
            DRIVER_STATUS_V2_RESPONSE1,
            V2_STATUSES_AMOUNT_IN_CHUNK,
            200,
            {
                'threads_amount': 4,
                'work_statuses_total': make_work_statuses_total(
                    online=1, offline=0, busy=2, on_order=0,
                ),
            },
        ),
        pytest.param(
            'p1',
            {},
            DRIVER_STATUS_V2_RESPONSE1,
            2,
            200,
            {
                'threads_amount': 4,
                'work_statuses_total': make_work_statuses_total(
                    online=1, offline=0, busy=2, on_order=0,
                ),
            },
            marks=pytest.mark.config(
                SIGNAL_DEVICE_API_ADMIN_DRIVER_STATUS_SETTINGS=2,
            ),
        ),
        (
            'p1',
            {},
            DRIVER_STATUS_V2_RESPONSE2,
            V2_STATUSES_AMOUNT_IN_CHUNK,
            200,
            {
                'threads_amount': 4,
                'work_statuses_total': make_work_statuses_total(
                    online=1, offline=1, busy=0, on_order=2,
                ),
            },
        ),
        (
            'p1',
            {'filter': {'event_types': ['distraction', 'driver_lost']}},
            DRIVER_STATUS_V2_RESPONSE2,
            V2_STATUSES_AMOUNT_IN_CHUNK,
            200,
            {
                'threads_amount': 2,
                'work_statuses_total': make_work_statuses_total(
                    online=0, offline=1, busy=0, on_order=1,
                ),
            },
        ),
        (
            'p1',
            {'filter': {'event_types': ['sleep']}},
            DRIVER_STATUS_V2_RESPONSE1,
            V2_STATUSES_AMOUNT_IN_CHUNK,
            200,
            {
                'threads_amount': 2,
                'work_statuses_total': make_work_statuses_total(
                    online=1, offline=0, busy=0, on_order=0,
                ),
            },
        ),
        pytest.param(
            'p1',
            {'filter': {'event_types': ['some_other_event_type']}},
            DRIVER_STATUS_V2_RESPONSE1,
            V2_STATUSES_AMOUNT_IN_CHUNK,
            200,
            {
                'threads_amount': 0,
                'work_statuses_total': make_work_statuses_total(
                    online=0, offline=0, busy=0, on_order=0,
                ),
            },
            marks=pytest.mark.config(
                SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=[
                    {
                        'event_type': 'some_other_event_type',
                        'is_critical': False,
                        'is_violation': False,
                        'fixation_config_path': 'some_path',
                    },
                    {
                        'event_type': 'another_unreal_event_type',
                        'is_critical': False,
                        'is_violation': False,
                        'fixation_config_path': 'some_path',
                    },
                ],
            ),
        ),
        (
            'p1',
            {
                'period': {
                    'from': '2020-02-28T10:00:00+00:00',
                    'to': '2021-04-10T00:00:00+00:00',
                },
            },
            DRIVER_STATUS_V2_RESPONSE1,
            V2_STATUSES_AMOUNT_IN_CHUNK,
            200,
            {
                'threads_amount': 1,
                'work_statuses_total': make_work_statuses_total(
                    online=0, offline=0, busy=0, on_order=0,
                ),
            },
        ),
        (
            'p1',
            {
                'period': {
                    'from': '2021-02-28T10:00:00+00:00',
                    'to': '2020-04-10T00:00:00+00:00',
                },
            },
            DRIVER_STATUS_V2_RESPONSE1,
            V2_STATUSES_AMOUNT_IN_CHUNK,
            400,
            None,
        ),
    ],
)
async def test_ok_total_drivers(
        taxi_signal_device_api_admin,
        park_id,
        body,
        driver_status_response,
        amount_in_v2_statuses_response,
        expected_code,
        expected_response,
        driver_status,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(park_id),
                    'specifications': ['signalq'],
                },
            ],
        }

    driver_status.set_v2_status_responses(
        response=driver_status_response,
        amount_in_response=amount_in_v2_statuses_response,
    )
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json=body,
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': park_id},
    )
    assert response.status_code == expected_code, response.text
    if expected_code != 200:
        return
    response_json = response.json()
    assert (
        response_json['threads_amount'] == expected_response['threads_amount']
    )
    assert (
        sorted(
            response_json['work_statuses_total'],
            key=lambda x: x['work_status'],
        )
        == sorted(
            expected_response['work_statuses_total'],
            key=lambda x: x['work_status'],
        )
    )


@pytest.mark.now('2020-08-11 15:00:03 +00:00')
@pytest.mark.pgsql('signal_device_api_meta_db', files=['events.sql'])
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_DEMO_SETTINGS_V2={
        'timings': {
            'working_day_start': 8,
            'working_day_end': 20,
            'working_days_amount': 7,
        },
        'comments': ['Комментарий 1', 'Комментарий 2', 'Комментарий 3'],
        'media': {'__default__': {}},
        'devices': [],
        'events': web_common.DEMO_EVENTS,
        'vehicles': [],
        'groups': web_common.DEMO_GROUPS,
        'drivers': web_common.DEMO_DRIVERS,
    },
)
@pytest.mark.parametrize(
    'body, expected_code, expected_response',
    [
        ({}, 200, {'threads_amount': 2, 'work_statuses_total': []}),
        (
            {'filter': {'group_id': 'g1'}},
            200,
            {'threads_amount': 0, 'work_statuses_total': []},
        ),
    ],
)
async def test_demo_ok_total_drivers(
        taxi_signal_device_api_admin,
        body,
        expected_code,
        expected_response,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info('no such park'),
                    'specifications': ['taxi'],
                },
            ],
        }

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json=body,
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no such park'},
    )
    assert response.status_code == expected_code, response.text
    if expected_code != 200:
        return
    response_json = response.json()
    assert (
        response_json['threads_amount'] == expected_response['threads_amount']
    )
    assert (
        sorted(
            response_json['work_statuses_total'],
            key=lambda x: x['work_status'],
        )
        == sorted(
            expected_response['work_statuses_total'],
            key=lambda x: x['work_status'],
        )
    )
