import pytest

from tests_signal_device_api_admin import dashboard_chart_utils
from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/dashboard/chart'

MOSCOW_TZ_OFFSET = 3 * 3600
UTC_TZ_OFFSET = 0

RESPONSE1 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-04-10T00:00:00+03:00',
    chart_period_to='2020-04-17T00:00:00+03:00',
    chart_elems=[],
    timezone='Europe/Moscow',
)

RESPONSE2 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-04-27T00:00:00+03:00',
    chart_period_to='2020-05-01T00:00:00+03:00',
    chart_elems=[
        {
            'date': '2020-04-27T00:00:00+03:00',
            'critical': 0,
            'non_critical': 3,
        },
    ],
    timezone='Europe/Moscow',
)

RESPONSE3 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-04-28T00:00:00+03:00',
    chart_period_to='2020-05-01T00:00:00+03:00',
    chart_elems=[],
    timezone='Europe/Moscow',
    is_cursor_after_needed=True,
)

RESPONSE4 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-04-27T03:00:00+03:00',
    chart_period_to='2020-05-01T03:00:00+03:00',
    chart_elems=[
        {
            'date': '2020-04-27T00:00:00+00:00',
            'critical': 0,
            'non_critical': 2,
        },
    ],
    timezone='UTC',
)

RESPONSE5 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-04-01T00:00:00+03:00',
    chart_period_to='2020-05-01T00:00:00+03:00',
    chart_elems=[
        {
            'date': '2020-04-01T00:00:00+03:00',
            'critical': 2,
            'non_critical': 0,
        },
        {
            'date': '2020-04-27T00:00:00+03:00',
            'critical': 0,
            'non_critical': 3,
        },
    ],
    timezone='Europe/Moscow',
)

RESPONSE6 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-03-31T00:00:00+03:00',
    chart_period_to='2020-04-01T00:00:00+03:00',
    chart_elems=[],
    timezone='Europe/Moscow',
)

RESPONSE7 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-03-31T00:00:00+00:00',
    chart_period_to='2020-04-01T00:00:00+00:00',
    chart_elems=[
        {
            'date': '2020-03-31T00:00:00+00:00',
            'critical': 1,
            'non_critical': 0,
        },
    ],
    timezone='UTC',
)

RESPONSE8 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-02-01T00:00:00+00:00',
    chart_period_to='2020-03-01T00:00:00+00:00',
    chart_elems=[
        {
            'date': '2020-02-02T00:00:00+00:00',
            'critical': 1,
            'non_critical': 1,
        },
        {
            'date': '2020-02-03T00:00:00+00:00',
            'critical': 0,
            'non_critical': 1,
        },
    ],
    timezone='UTC',
    is_cursor_after_needed=True,
)

RESPONSE9 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-02-01T00:00:00+03:00',
    chart_period_to='2020-03-01T00:00:00+03:00',
    chart_elems=[
        {
            'date': '2020-02-03T00:00:00+03:00',
            'critical': 1,
            'non_critical': 2,
        },
    ],
    timezone='Europe/Moscow',
    is_cursor_after_needed=True,
)

RESPONSE10 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-01-01T00:00:00+03:00',
    chart_period_to='2020-02-01T00:00:00+03:00',
    chart_elems=[],
    timezone='Europe/Moscow',
    is_cursor_after_needed=True,
)

RESPONSE11 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-04-28T00:00:00+03:00',
    chart_period_to='2020-05-28T00:00:00+03:00',
    chart_elems=[],
    timezone='Europe/Moscow',
)

RESPONSE_P2_1 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-02-27T00:00:00+03:00',
    chart_period_to='2020-03-01T00:00:00+03:00',
    chart_elems=[
        {
            'date': '2020-02-27T00:00:00+03:00',
            'critical': 1,
            'non_critical': 0,
        },
    ],
    timezone='Europe/Moscow',
)

RESPONSE_P2_2 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-02-03T00:00:00+03:00',
    chart_period_to='2020-02-20T00:00:00+03:00',
    chart_elems=[],
    timezone='Europe/Moscow',
)


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=[
        {
            'event_type': 'sleep',
            'is_critical': False,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'distraction',
            'is_critical': True,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'driver_lost',
            'is_critical': False,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
    ],
)
@pytest.mark.parametrize(
    'park_id, period_from, period_to, tz_offset, expected_response',
    [
        pytest.param(
            'p1',
            '2020-04-10T00:00:00+03:00',
            '2020-04-17T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            RESPONSE1,
            id='No events in current range, without month splitting',
        ),
        (
            'p1',
            '2020-04-27T00:00:00+03:00',
            '2020-05-01T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            RESPONSE2,
        ),
        (
            'p1',
            '2020-04-27T00:00:00+03:00',
            '2020-04-30T21:00:00+00:00',
            MOSCOW_TZ_OFFSET,
            RESPONSE2,
        ),
        pytest.param(
            'p1',
            '2020-04-28T00:00:00+03:00',
            '2020-05-30T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            RESPONSE3,
            id='No events, but returning cursor_after',
        ),
        pytest.param(
            'p1',
            '2020-04-27T00:00:00+00:00',
            '2020-05-01T00:00:00+00:00',
            UTC_TZ_OFFSET,
            RESPONSE4,
            id='1 event is not included because of tz',
        ),
        (
            'p1',
            '2020-04-01T00:00:00+03:00',
            '2020-05-01T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            RESPONSE5,
        ),
        pytest.param(
            'p1',
            '2020-03-31T00:00:00+03:00',
            '2020-04-01T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            RESPONSE6,
            id='Checking March for moving event in 2 months in +03',
        ),
        pytest.param(
            'p1',
            '2020-03-31T00:00:00+00:00',
            '2020-04-01T00:00:00+00:00',
            UTC_TZ_OFFSET,
            RESPONSE7,
            id='Checking March for moving event in 2 months in +00',
        ),
        (
            'p1',
            '2020-02-01T00:00:00+00:00',
            '2020-03-15T00:00:00+00:00',
            UTC_TZ_OFFSET,
            RESPONSE8,
        ),
        (
            'p1',
            '2020-02-01T00:00:00+03:00',
            '2020-03-15T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            RESPONSE9,
        ),
        (
            'p1',
            '2020-01-01T00:00:00+03:00',
            '2020-06-15T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            RESPONSE10,
        ),
        pytest.param(
            'p1',
            '2020-04-28T00:00:00+03:00',
            '2020-05-28T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            RESPONSE11,
            id='No events, and not returning cursor_after',
        ),
        (
            'p2',
            '2020-02-27T00:00:00+03:00',
            '2020-03-01T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            RESPONSE_P2_1,
        ),
        (
            'p2',
            '2020-02-03T00:00:00+03:00',
            '2020-02-20T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            RESPONSE_P2_2,
        ),
    ],
)
async def test_v1_dashboard_chart_without_anything(
        taxi_signal_device_api_admin,
        park_id,
        period_from,
        period_to,
        tz_offset,
        expected_response,
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

    body = {
        'period': {'from': period_from, 'to': period_to},
        'tz_offset': tz_offset,
    }

    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': park_id}
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )
    assert response.status_code == 200, response.text
    dashboard_chart_utils.check_dashboard_chart_responses(
        response.json(), expected_response,
    )


RESPONSE_WITH_WEBLIST1 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-01-01T00:00:00+03:00',
    chart_period_to='2020-02-01T00:00:00+03:00',
    chart_elems=[
        {
            'date': '2020-01-01T00:00:00+03:00',
            'critical': 1,
            'non_critical': 0,
        },
    ],
    timezone='Europe/Moscow',
)

RESPONSE_WITH_WEBLIST2 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-03-01T00:00:00+03:00',
    chart_period_to='2020-04-01T00:00:00+03:00',
    chart_elems=[
        {
            'date': '2020-03-30T00:00:00+03:00',
            'critical': 0,
            'non_critical': 1,
        },
    ],
    timezone='Europe/Moscow',
)

RESPONSE_WITH_CRITICAL_TYPES1 = (
    dashboard_chart_utils.get_dashboard_chart_response(
        chart_period_from='2020-03-01T00:00:00+03:00',
        chart_period_to='2020-04-01T00:00:00+03:00',
        chart_elems=[
            {
                'date': '2020-03-30T00:00:00+03:00',
                'critical': 2,
                'non_critical': 0,
            },
        ],
        timezone='Europe/Moscow',
    )
)

RESPONSE_WITH_CRITICAL_TYPES2 = (
    dashboard_chart_utils.get_dashboard_chart_response(
        chart_period_from='2020-03-01T00:00:00+03:00',
        chart_period_to='2020-04-01T00:00:00+03:00',
        chart_elems=[
            {
                'date': '2020-03-30T00:00:00+03:00',
                'critical': 0,
                'non_critical': 2,
            },
        ],
        timezone='Europe/Moscow',
    )
)

RESPONSE_WITH_BOTH_CONFIGS = (
    dashboard_chart_utils.get_dashboard_chart_response(
        chart_period_from='2020-04-01T00:00:00+03:00',
        chart_period_to='2020-05-01T00:00:00+03:00',
        chart_elems=[
            {
                'date': '2020-04-27T00:00:00+03:00',
                'critical': 2,
                'non_critical': 2,
            },
        ],
        timezone='Europe/Moscow',
        is_cursor_after_needed=True,
    )
)

BIG_WHITELIST_CONFIG = pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=[
        {
            'event_type': 'seatbelt',
            'is_critical': True,
            'is_violation': False,
            'fixation_config_path': 'seatbelt.events.seatbelt.enabled',
        },
        {
            'event_type': 'distraction',
            'is_critical': True,
            'is_violation': False,
            'fixation_config_path': 'distraction.events.distraction.enabled',
        },
        {
            'event_type': 'bad_camera_pose',
            'is_critical': False,
            'is_violation': False,
            'fixation_config_path': 'general.events.bad_camera_pose.enabled',
        },
        {
            'event_type': 'fart',
            'is_critical': False,
            'is_violation': True,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'sleep',
            'is_critical': False,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'driver_lost',
            'is_critical': False,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
    ],
)


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'park_id, period_from, period_to, tz_offset, whitelist, critical_types, '
    'expected_response',
    [
        pytest.param(
            'p1',
            '2020-01-01T00:00:00+03:00',
            '2020-02-01T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            ['seatbelt'],
            None,
            RESPONSE_WITH_WEBLIST1,
            marks=BIG_WHITELIST_CONFIG,
        ),
        (
            'p1',
            '2020-03-01T00:00:00+03:00',
            '2020-04-01T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            ['sleep'],
            None,
            RESPONSE_WITH_WEBLIST2,
        ),
        (
            'p1',
            '2020-03-01T00:00:00+03:00',
            '2020-04-01T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            None,
            ['distraction', 'sleep'],
            RESPONSE_WITH_CRITICAL_TYPES1,
        ),
        (
            'p1',
            '2020-03-01T00:00:00+03:00',
            '2020-04-01T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            None,
            ['driver_lost'],
            RESPONSE_WITH_CRITICAL_TYPES2,
        ),
        pytest.param(
            'p1',
            '2020-04-01T00:00:00+03:00',
            '2020-05-12T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            ['sleep', 'fart', 'driver_lost'],
            ['sleep'],
            RESPONSE_WITH_BOTH_CONFIGS,
            marks=BIG_WHITELIST_CONFIG,
        ),
    ],
)
async def test_v1_dashboard_chart_with_whitelist_and_critical_types(
        taxi_signal_device_api_admin,
        pgsql,
        park_id,
        period_from,
        period_to,
        tz_offset,
        whitelist,
        critical_types,
        expected_response,
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

    body = {
        'period': {'from': period_from, 'to': period_to},
        'tz_offset': tz_offset,
    }
    if whitelist is not None:
        body['whitelist'] = whitelist
    if critical_types is not None:
        utils.add_park_critical_types_in_db(
            pgsql, park_id=park_id, critical_types=critical_types,
        )

    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': park_id}
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )
    assert response.status_code == 200, response.text
    dashboard_chart_utils.check_dashboard_chart_responses(
        response.json(), expected_response,
    )


RESPONSE_CURSOR_AFTER1 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-04-01T00:00:00+03:00',
    chart_period_to='2020-05-01T00:00:00+03:00',
    chart_elems=[
        {
            'date': '2020-04-01T00:00:00+03:00',
            'critical': 2,
            'non_critical': 0,
        },
        {
            'date': '2020-04-27T00:00:00+03:00',
            'critical': 0,
            'non_critical': 3,
        },
    ],
    timezone='Europe/Moscow',
    is_cursor_before_needed=True,
    is_cursor_after_needed=True,
)

RESPONSE_CURSOR_AFTER2 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-04-01T00:00:00+03:00',
    chart_period_to='2020-04-27T00:00:00+03:00',
    chart_elems=[
        {
            'date': '2020-04-01T00:00:00+03:00',
            'critical': 2,
            'non_critical': 0,
        },
        {
            'date': '2020-04-27T00:00:00+03:00',
            'critical': 0,
            'non_critical': 3,
        },
    ],
    timezone='Europe/Moscow',
    is_cursor_before_needed=True,
)

RESPONSE_CURSOR_AFTER3 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-04-01T00:00:00+03:00',
    chart_period_to='2020-04-02T00:00:00+03:00',
    chart_elems=[
        {
            'date': '2020-04-01T00:00:00+03:00',
            'critical': 2,
            'non_critical': 0,
        },
    ],
    timezone='Europe/Moscow',
    is_cursor_before_needed=True,
)

RESPONSE_CURSOR_BEFORE1 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-04-01T00:00:00+03:00',
    chart_period_to='2020-05-01T00:00:00+03:00',
    chart_elems=[
        {
            'date': '2020-04-01T00:00:00+03:00',
            'critical': 2,
            'non_critical': 0,
        },
        {
            'date': '2020-04-27T00:00:00+03:00',
            'critical': 0,
            'non_critical': 3,
        },
    ],
    timezone='Europe/Moscow',
    is_cursor_before_needed=True,
    is_cursor_after_needed=True,
)

RESPONSE_CURSOR_BEFORE2 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-04-01T00:00:00+03:00',
    chart_period_to='2020-05-01T00:00:00+03:00',
    chart_elems=[
        {
            'date': '2020-04-01T00:00:00+03:00',
            'critical': 2,
            'non_critical': 0,
        },
        {
            'date': '2020-04-27T00:00:00+03:00',
            'critical': 0,
            'non_critical': 3,
        },
    ],
    timezone='Europe/Moscow',
    is_cursor_after_needed=True,
)

RESPONSE_CURSOR_BEFORE3 = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2020-04-27T00:00:00+03:00',
    chart_period_to='2020-05-01T00:00:00+03:00',
    chart_elems=[
        {
            'date': '2020-04-27T00:00:00+03:00',
            'critical': 0,
            'non_critical': 3,
        },
    ],
    timezone='Europe/Moscow',
    is_cursor_after_needed=True,
)


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'park_id, period_from, period_to, tz_offset, cursor_before, cursor_after, '
    'expected_code, expected_response',
    [
        (
            'p1',
            '2020-01-01T00:00:00+03:00',
            '2020-04-01T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            utils.get_encoded_chart_cursor('2020-02-01T00:00:00+03:00'),
            utils.get_encoded_chart_cursor('2020-03-01T00:00:00+03:00'),
            400,
            None,
        ),
        (
            'p1',
            '2020-03-01T00:00:00+00:00',
            '2020-05-01T00:00:00+00:00',
            UTC_TZ_OFFSET,
            utils.get_encoded_chart_cursor('2020-04-01T00:00:00+03:00'),
            None,
            400,
            None,
        ),
        (
            'p1',
            '2020-03-01T00:00:00+03:00',
            '2020-05-01T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            utils.get_encoded_chart_cursor('2020-04-02T00:00:00+03:00'),
            None,
            400,
            None,
        ),
        (
            'p1',
            '2020-03-01T00:00:00+03:00',
            '2020-05-01T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            utils.get_encoded_chart_cursor('2020-03-01T00:00:00+03:00'),
            None,
            400,
            None,
        ),
        (
            'p1',
            '2020-03-01T00:00:00+03:00',
            '2020-05-01T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            utils.get_encoded_chart_cursor('2020-05-01T00:00:00+03:00'),
            None,
            400,
            None,
        ),
        (
            'p1',
            '2020-03-01T00:00:00+03:00',
            '2020-05-01T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            None,
            utils.get_encoded_chart_cursor('2020-05-01T00:00:00+03:00'),
            400,
            None,
        ),
        (
            'p1',
            '2020-03-15T00:00:00+03:00',
            '2020-05-12T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            None,
            utils.get_encoded_chart_cursor('2020-04-01T00:00:00+03:00'),
            200,
            RESPONSE_CURSOR_AFTER1,
        ),
        (
            'p1',
            '2020-03-01T00:00:00+03:00',
            '2020-04-27T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            None,
            utils.get_encoded_chart_cursor('2020-04-01T00:00:00+03:00'),
            200,
            RESPONSE_CURSOR_AFTER2,
        ),
        (
            'p1',
            '2020-03-01T00:00:00+03:00',
            '2020-04-02T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            None,
            utils.get_encoded_chart_cursor('2020-04-01T00:00:00+03:00'),
            200,
            RESPONSE_CURSOR_AFTER3,
        ),
        (
            'p1',
            '2020-03-01T00:00:00+03:00',
            '2020-05-12T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            utils.get_encoded_chart_cursor('2020-05-01T00:00:00+03:00'),
            None,
            200,
            RESPONSE_CURSOR_BEFORE1,
        ),
        (
            'p1',
            '2020-04-01T00:00:00+03:00',
            '2020-05-12T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            utils.get_encoded_chart_cursor('2020-05-01T00:00:00+03:00'),
            None,
            200,
            RESPONSE_CURSOR_BEFORE2,
        ),
        (
            'p1',
            '2020-04-27T00:00:00+03:00',
            '2020-05-12T00:00:00+03:00',
            MOSCOW_TZ_OFFSET,
            utils.get_encoded_chart_cursor('2020-05-01T00:00:00+03:00'),
            None,
            200,
            RESPONSE_CURSOR_BEFORE3,
        ),
    ],
)
async def test_v1_dashboard_chart_with_cursor(
        taxi_signal_device_api_admin,
        park_id,
        period_from,
        period_to,
        tz_offset,
        cursor_before,
        cursor_after,
        expected_code,
        expected_response,
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

    body = {
        'period': {'from': period_from, 'to': period_to},
        'tz_offset': tz_offset,
    }
    if cursor_before is not None:
        body['cursor_before'] = cursor_before
    if cursor_after is not None:
        body['cursor_after'] = cursor_after

    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': park_id}
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )
    assert response.status_code == expected_code, response.text
    if expected_code == 200:
        dashboard_chart_utils.check_dashboard_chart_responses(
            response.json(), expected_response,
        )


DEMO_CHART = [
    {'date': '2021-11-24T00:00:00+03:00', 'critical': 1, 'non_critical': 0},
    {'date': '2021-11-25T00:00:00+03:00', 'critical': 0, 'non_critical': 1},
    {'date': '2021-11-26T00:00:00+03:00', 'critical': 0, 'non_critical': 1},
    {'date': '2021-11-27T00:00:00+03:00', 'critical': 0, 'non_critical': 1},
    {'date': '2021-11-28T00:00:00+03:00', 'critical': 1, 'non_critical': 0},
    {'date': '2021-11-29T00:00:00+03:00', 'critical': 0, 'non_critical': 1},
    {'date': '2021-11-30T00:00:00+03:00', 'critical': 0, 'non_critical': 1},
]

DEMO_RESPONSE = dashboard_chart_utils.get_dashboard_chart_response(
    chart_period_from='2021-11-24T00:00:00+03:00',
    chart_period_to='2021-12-01T00:00:00+03:00',
    chart_elems=DEMO_CHART,
    timezone='Europe/Moscow',
)

DEMO_RESPONSE_CURSOR_BEFORE = (
    dashboard_chart_utils.get_dashboard_chart_response(
        chart_period_from='2021-11-24T00:00:00+03:00',
        chart_period_to='2021-12-01T00:00:00+03:00',
        chart_elems=DEMO_CHART,
        timezone='Europe/Moscow',
        is_cursor_after_needed=True,
    )
)

DEMO_RESPONSE_CURSOR_AFTER = (
    dashboard_chart_utils.get_dashboard_chart_response(
        chart_period_from='2021-12-01T00:00:00+03:00',
        chart_period_to='2021-12-03T00:00:00+03:00',
        chart_elems=[
            {
                'date': '2021-12-01T00:00:00+03:00',
                'critical': 1,
                'non_critical': 0,
            },
            {
                'date': '2021-12-02T00:00:00+03:00',
                'critical': 0,
                'non_critical': 1,
            },
        ],
        timezone='Europe/Moscow',
        is_cursor_before_needed=True,
    )
)


@pytest.mark.now('2021-12-31T16:00:00+03:00')
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_DEMO_SETTINGS_V2={
        'timings': {
            'working_day_start': 8,
            'working_day_end': 20,
            'working_days_amount': 7,
        },
        'comments': ['Комментарий 1', 'Комментарий 2', 'Комментарий 3'],
        'media': {'__default__': {}},
        'devices': web_common.DEMO_DEVICES,
        'events': web_common.DEMO_EVENTS,
        'vehicles': web_common.DEMO_VEHICLES,
        'groups': web_common.DEMO_GROUPS,
        'drivers': web_common.DEMO_DRIVERS,
    },
    SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=web_common.get_demo_whitelist(  # noqa: E501 line too long
        ['brosil signalq', 'tired'],
    ),
)
@pytest.mark.parametrize(
    'period_from, period_to, tz_offset, cursor_before, '
    'cursor_after, expected_response',
    [
        pytest.param(
            '2021-11-24T00:00:00+03:00',
            '2021-11-30T23:59:59+03:00',
            MOSCOW_TZ_OFFSET,
            None,
            None,
            DEMO_RESPONSE,
            id='demo no cursor',
        ),
        pytest.param(
            '2021-11-24T00:00:00+03:00',
            '2021-12-30T23:59:59+03:00',
            MOSCOW_TZ_OFFSET,
            utils.get_encoded_chart_cursor('2021-12-01T00:00:00+03:00'),
            None,
            DEMO_RESPONSE_CURSOR_BEFORE,
            id='demo cursor after',
        ),
        pytest.param(
            '2021-11-01T00:00:00+03:00',
            '2021-12-02T23:59:59+03:00',
            MOSCOW_TZ_OFFSET,
            None,
            utils.get_encoded_chart_cursor('2021-12-01T00:00:00+03:00'),
            DEMO_RESPONSE_CURSOR_AFTER,
            id='demo cursor before',
        ),
    ],
)
async def test_demo_chart(
        taxi_signal_device_api_admin,
        period_from,
        period_to,
        tz_offset,
        cursor_before,
        cursor_after,
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

    body = {
        'period': {'from': period_from, 'to': period_to},
        'tz_offset': tz_offset,
    }
    if cursor_before is not None:
        body['cursor_before'] = cursor_before
    if cursor_after is not None:
        body['cursor_after'] = cursor_after

    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': 'no such park'}
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )
    assert response.status_code == 200, response.text
    dashboard_chart_utils.check_dashboard_chart_responses(
        response.json(), expected_response,
    )
