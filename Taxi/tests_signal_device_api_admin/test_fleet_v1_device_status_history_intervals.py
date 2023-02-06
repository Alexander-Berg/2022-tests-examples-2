import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/device/status-history/intervals'

CONFIG_MOCK_1 = {
    'pg_statuses_limit': 1500,
    'intervals_limit': 20,
    'supposed_statuses_interval_minutes': 1,
    'big_gap_length_minutes': 5,
    'default_request_period_hours': 168,
    'is_obsolete_response': False,
    'driver_statuses_interval_hours': 24,
}

EXPECTED_RESPONSE_1 = {
    'intervals': [
        {
            'status': 'turned_off',
            'start_at': '2021-03-03T21:10:00+00:00',
            'end_at': '2021-03-04T17:49:00+00:00',
        },
        {
            'status': 'closed',
            'start_at': '2021-03-04T17:49:00+00:00',
            'end_at': '2021-03-04T17:52:00+00:00',
        },
        {
            'status': 'offline',
            'start_at': '2021-03-04T17:52:00+00:00',
            'end_at': '2021-03-04T18:00:00+00:00',
        },
    ],
    'cursor': utils.get_encoded_dev_stathist_cursor(
        '2021-03-03T21:10:00+0000',
    ),
}

EXPECTED_RESPONSE_2 = {
    'intervals': [
        {
            'status': 'faced_away',
            'start_at': '2021-03-03T21:00:00+00:00',
            'end_at': '2021-03-03T21:06:00+00:00',
        },
        {
            'status': 'turned_on',
            'start_at': '2021-03-03T21:06:00+00:00',
            'end_at': '2021-03-03T21:10:00+00:00',
        },
    ],
}


def _check_statuses_sequence(statuses, expected_statuses):
    assert len(statuses) == len(expected_statuses)
    for status, expected in zip(statuses, expected_statuses):
        assert status['status'] == expected, statuses


@pytest.mark.pgsql('signal_device_api_meta_db', files=['statuses.sql'])
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_STATUS_HISTORY_SETTINGS_V4=CONFIG_MOCK_1,
)
@pytest.mark.parametrize(
    'device_id, body, expected_code, expected_statuses',
    [
        ('d1', {}, 200, ['offline', 'turned_on']),
        ('d2', {}, 200, ['turned_off', 'turned_on', 'offline', 'turned_on']),
        (
            'd1',
            {
                'period': {
                    'from': '2021-01-02T00:00:00+03:00',
                    'to': '2021-01-02T21:00:00+03:00',
                },
            },
            200,
            ['offline', 'turned_on', 'offline', 'turned_on'],
        ),
        (
            'd2',
            {
                'period': {
                    'from': '2021-03-04T00:00:00+03:00',
                    'to': '2021-03-04T21:00:00+03:00',
                },
            },
            200,
            ['faced_away', 'turned_on', 'turned_off', 'closed', 'offline'],
        ),
        (
            'd2',
            {
                'period': {
                    'from': '2020-11-04T00:00:00+03:00',
                    'to': '2020-11-04T21:00:00+03:00',
                },
            },
            200,
            ['offline'],
        ),
        (
            'd2',
            {
                'period': {
                    'from': '2020-11-04T00:00:00+03:00',
                    'to': '2020-11-04T21:00:00+03:00',
                },
                'cursor': utils.get_encoded_dev_stathist_cursor(
                    '2020-11-03T21:00:00+0000',
                ),
            },
            400,
            None,
        ),
        (
            'd2',
            {
                'period': {
                    'from': '2020-11-04T00:00:00+03:00',
                    'to': '2019-11-04T21:00:00+03:00',
                },
                'cursor': utils.get_encoded_dev_stathist_cursor(
                    '2020-11-03T21:00:00+0000',
                ),
            },
            400,
            None,
        ),
    ],
)
async def test_status_history_intervals(
        taxi_signal_device_api_admin,
        device_id,
        body,
        expected_code,
        expected_statuses,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(),
                    'specifications': ['signalq'],
                },
            ],
        }

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        params={'device_id': device_id},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
        json=body,
    )
    assert response.status_code == expected_code, response.text
    if expected_code == 200:
        _check_statuses_sequence(
            response.json()['intervals'], expected_statuses,
        )


@pytest.mark.pgsql('signal_device_api_meta_db', files=['statuses.sql'])
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_STATUS_HISTORY_SETTINGS_V4=CONFIG_MOCK_1,
)
async def test_status_history_states_with_timestamps(
        taxi_signal_device_api_admin, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(),
                    'specifications': ['signalq'],
                },
            ],
        }

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        params={'device_id': 'd2'},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
        json={
            'period': {
                'from': '2021-03-04T00:00:00+03:00',
                'to': '2021-03-04T22:00:00+03:00',
            },
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'intervals': [
            {  # статус начался до промежутка
                'status': 'faced_away',
                'start_at': '2021-03-03T21:00:00+00:00',
                'end_at': '2021-03-03T21:06:00+00:00',
            },
            {  # статус сменился на корректный
                'status': 'turned_on',
                'start_at': '2021-03-03T21:06:00+00:00',
                'end_at': '2021-03-03T21:10:00+00:00',
            },
            {  # камеру выключили
                'status': 'turned_off',
                'start_at': '2021-03-03T21:10:00+00:00',
                'end_at': '2021-03-04T17:49:00+00:00',
            },
            {  # камеру включили, через минуту пришёл первый статус "закрыта"
                'status': 'closed',
                'start_at': '2021-03-04T17:49:00+00:00',
                'end_at': '2021-03-04T17:52:00+00:00',
            },
            {  # камера перестала слать статусы -> оффлайн
                'status': 'offline',
                'start_at': '2021-03-04T17:52:00+00:00',
                'end_at': '2021-03-04T18:10:00+00:00',
            },
            {  # в какой-то момент камера выключилась, хотя статусы не пришли
                'status': 'turned_off',
                'start_at': '2021-03-04T18:10:00+00:00',
                'end_at': '2021-03-04T18:20:00+00:00',
            },
            {  # камера включилась
                'status': 'turned_on',
                'start_at': '2021-03-04T18:20:00+00:00',
                'end_at': '2021-03-04T18:21:00+00:00',
            },
            {  # но статусы не прислала, поэтому почти сразу стала оффлайн
                'status': 'offline',
                'start_at': '2021-03-04T18:21:00+00:00',
                'end_at': '2021-03-04T18:30:00+00:00',
            },
            {  # точнее, прислала нормальный статус два раза, но нескоро
                'status': 'turned_on',
                'start_at': '2021-03-04T18:30:00+00:00',
                'end_at': '2021-03-04T18:37:00+00:00',
            },
            {  # потом выключилась
                'status': 'turned_off',
                'start_at': '2021-03-04T18:37:00+00:00',
                'end_at': '2021-03-04T18:45:00+00:00',
            },
            {  # потом прислала статус, не присылая события включения
                'status': 'faced_away',
                'start_at': '2021-03-04T18:45:00+00:00',
                'end_at': '2021-03-04T18:46:00+00:00',
            },
            {  # и ушла в оффлайн
                'status': 'offline',
                'start_at': '2021-03-04T18:46:00+00:00',
                'end_at': '2021-03-04T19:00:00+00:00',
            },
        ],
    }


@pytest.mark.pgsql('signal_device_api_meta_db', files=['statuses.sql'])
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_STATUS_HISTORY_SETTINGS_V4={
        **CONFIG_MOCK_1,
        'intervals_limit': 3,
    },
)
async def test_status_history_states_with_cursor(
        taxi_signal_device_api_admin, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(),
                    'specifications': ['signalq'],
                },
            ],
        }

    body = {
        'period': {
            'from': '2021-03-04T00:00:00+03:00',
            'to': '2021-03-04T21:00:00+03:00',
        },
    }
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        params={'device_id': 'd2'},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
        json=body,
    )
    assert response.status_code == 200, response.text
    response_json = response.json()
    assert response_json == EXPECTED_RESPONSE_1
    body['cursor'] = response_json.pop('cursor')
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        params={'device_id': 'd2'},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
        json=body,
    )
    assert response.status_code == 200, response.text
    assert response.json() == EXPECTED_RESPONSE_2


# этот тест и is_obsolete_response можно удалить,
# когда фронт поддержит новый ответ
@pytest.mark.pgsql('signal_device_api_meta_db', files=['statuses.sql'])
async def test_status_history_states_obsolete(
        taxi_signal_device_api_admin, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(),
                    'specifications': ['signalq'],
                },
            ],
        }

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        params={'device_id': 'd2'},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
        json={
            'period': {
                'from': '2021-03-04T00:00:00+03:00',
                'to': '2021-03-04T22:00:00+03:00',
            },
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'intervals': [
            {  # статус начался до промежутка
                'status': 'bad_camera_pose',
                'start_at': '2021-03-03T21:00:00+00:00',
                'end_at': '2021-03-03T21:06:00+00:00',
            },
            {  # статус сменился на корректный
                'status': 'online',
                'start_at': '2021-03-03T21:06:00+00:00',
                'end_at': '2021-03-03T21:10:00+00:00',
            },
            {  # камеру выключили
                'status': 'offline',
                'start_at': '2021-03-03T21:10:00+00:00',
                'end_at': '2021-03-04T17:49:00+00:00',
            },
            {  # камеру включили, через минуту пришёл первый статус "закрыта"
                'status': 'camera_closed',
                'start_at': '2021-03-04T17:49:00+00:00',
                'end_at': '2021-03-04T17:52:00+00:00',
            },
            {  # камера перестала слать статусы -> оффлайн
                'status': 'offline',
                'start_at': '2021-03-04T17:52:00+00:00',
                'end_at': '2021-03-04T18:10:00+00:00',
            },
            {  # в какой-то момент камера выключилась, хотя статусы не пришли
                'status': 'offline',
                'start_at': '2021-03-04T18:10:00+00:00',
                'end_at': '2021-03-04T18:20:00+00:00',
            },
            {  # камера включилась
                'status': 'online',
                'start_at': '2021-03-04T18:20:00+00:00',
                'end_at': '2021-03-04T18:21:00+00:00',
            },
            {  # но статусы не прислала, поэтому почти сразу стала оффлайн
                'status': 'offline',
                'start_at': '2021-03-04T18:21:00+00:00',
                'end_at': '2021-03-04T18:30:00+00:00',
            },
            {  # точнее, прислала нормальный статус два раза, но нескоро
                'status': 'online',
                'start_at': '2021-03-04T18:30:00+00:00',
                'end_at': '2021-03-04T18:37:00+00:00',
            },
            {  # потом выключилась
                'status': 'offline',
                'start_at': '2021-03-04T18:37:00+00:00',
                'end_at': '2021-03-04T18:45:00+00:00',
            },
            {  # потом прислала статус, не присылая события включения
                'status': 'bad_camera_pose',
                'start_at': '2021-03-04T18:45:00+00:00',
                'end_at': '2021-03-04T18:46:00+00:00',
            },
            {  # и ушла в оффлайн
                'status': 'offline',
                'start_at': '2021-03-04T18:46:00+00:00',
                'end_at': '2021-03-04T19:00:00+00:00',
            },
        ],
    }


async def test_demo_status_history_intervals(
        taxi_signal_device_api_admin, mockserver,
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
        params={'device_id': 'd1'},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no such park'},
        json={},
    )
    assert response.status_code == 200, response.text
    response_json = response.json()
    assert response_json['intervals'][0]['status'] == 'offline'
    assert response_json['intervals'][-1]['status'] == 'online'
