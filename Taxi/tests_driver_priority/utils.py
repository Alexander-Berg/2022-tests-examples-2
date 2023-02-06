import datetime as dt
from typing import Any
from typing import Dict
from typing import Optional

import psycopg2

from tests_driver_priority import constants

TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'


def _convert_timestamps(data):
    for key in ['starts_at', 'stops_at']:
        if key in data:
            data[key] = parse_datetime(data[key])


def _check_response_diff(
        response: Dict[str, Any], expected_diff: Optional[Dict[str, Any]],
):
    if expected_diff is None:
        assert 'diff' not in response
    else:
        assert response['diff']['new'] == expected_diff['new']
        assert response['diff']['current'] == expected_diff['current']


def parse_datetime(raw_datetime: str) -> dt.datetime:
    return dt.datetime.strptime(raw_datetime, TIME_FORMAT)


def validate_check_response(
        response: Dict[str, Any],
        request_body: Dict[str, Any],
        expected_diff: Optional[Dict[str, Any]] = None,
):
    # convert all(!) timestamps to datetime before comparison
    if 'version' in request_body:
        _convert_timestamps(request_body['version'])
        _convert_timestamps(response['data']['version'])
        if expected_diff is not None:
            _convert_timestamps(response['diff']['new'])
            _convert_timestamps(response['diff']['current'])

    priority_name = (
        request_body.get('priority_name') or request_body['priority']['name']
    )
    expected_change_doc_id = f'priority_{priority_name}_draft'
    assert response['data'] == request_body
    assert response['change_doc_id'] == expected_change_doc_id

    _check_response_diff(response, expected_diff)


def validate_check_version_response(
        response: Dict[str, Any],
        request: Dict[str, Any],
        preset_name: Optional[str],
        expected_diff: Optional[Dict[str, Any]] = None,
):
    # convert all(!) timestamps to datetime before comparison
    if 'version' in request:
        _convert_timestamps(request['version'])
        _convert_timestamps(response['data']['version'])
        if expected_diff is not None:
            _convert_timestamps(response['diff']['new'])
            _convert_timestamps(response['diff']['current'])
            if 'version' in response['diff']['new']:
                _convert_timestamps(response['diff']['new']['version'])
            if 'version' in response['diff']['current']:
                _convert_timestamps(response['diff']['current']['version'])

    priority_name = request['priority_name']
    change_doc_id = (
        f'priority_{priority_name}_preset_{preset_name}_draft'
        if preset_name is not None
        else f'priority_{priority_name}_draft'
    )
    assert response['data'] == request
    assert response['change_doc_id'] == change_doc_id
    _check_response_diff(response, expected_diff)


def polling_response(stable_priority, temporary_priority, possible_priority):
    return {
        'priority': {
            'stable': stable_priority,
            'temporary': temporary_priority,
            'possible': possible_priority,
        },
    }


def summary_values(stable_priority, temporary_priority, possible_priority):
    return {
        'stable': stable_priority,
        'temporary': temporary_priority,
        'possible': possible_priority,
    }


def fleet_status(screen_item):
    if (
            'left_tip' in screen_item
            and 'animated' in screen_item['left_tip']
            and screen_item['left_tip']['animated']
    ):
        return 'temporary'

    if (
            'left_tip' in screen_item
            and 'background_color' in screen_item['left_tip']
            and screen_item['left_tip']['background_color'] == '#C4C2BE'
    ):
        return 'achievable'

    return 'stable'


def make_fleet_item(screen_item):
    item = {
        'title': screen_item['title'],
        'value': int(screen_item['detail']),
        'status': fleet_status(screen_item),
    }
    if 'subtitle' in screen_item:
        item['subtitle'] = screen_item['subtitle']
    return item


def _ensure_polling_header(header):
    parts = header.split(', ')
    parts.sort()
    assert parts == [
        'background=1200s',
        'full=600s',
        'idle=1800s',
        'powersaving=1200s',
    ]


async def ensure_polling_and_screen(
        taxi_driver_priority,
        headers: Dict[str, str],
        params: Dict[str, Any],
        expected_code: int,
        expected_screen_response,
        expected_polling_response,
        expected_value_response,
        call_value_handler: Optional[bool] = True,
):
    response = await taxi_driver_priority.get(
        constants.POLLING_URL, params=params, headers=headers,
    )
    assert response.status_code == expected_code
    if expected_polling_response:
        assert response.json() == expected_polling_response
        if response.status_code == 200:
            _ensure_polling_header(response.headers['X-Polling-Power-Policy'])

    response = await taxi_driver_priority.get(
        constants.SCREEN_URL, params=params, headers=headers,
    )
    assert response.status_code == expected_code
    if expected_screen_response:
        ans = response.json()
        assert ans == expected_screen_response
        if response.status_code == 200:
            _ensure_polling_header(response.headers['X-Polling-Power-Policy'])

    if 'Accept-Language' in headers:
        headers.pop('Accept-Language')
    if not call_value_handler:
        return
    response = await taxi_driver_priority.get(
        constants.VALUE_URL, params=params, headers=headers,
    )
    assert response.status_code == expected_code
    if expected_value_response:
        assert response.json() == expected_value_response


async def ensure_fleet(
        driver_trackstory_mock,
        driver_profiles_mocks,
        taxi_driver_priority,
        lat,
        lon,
        park_id,
        uuid,
        expected_fleet_reponse,
):
    fleet_headers = {
        'X-Ya-User-Ticket': 'user_ticket',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-Login': 'login',
        'X-Yandex-UID': '123',
        'X-Park-ID': park_id,
        'Accept-Language': constants.DEFAULT_ACCEPT_LANGUAGE,
    }

    driver_trackstory_mock.set_positions(f'{park_id}_{uuid}', lat, lon)
    driver_profiles_mocks.set_taximeter_info(
        profile=f'{park_id}_{uuid}',
        platform='Taximeter',
        version='9.20',
        version_type='1234',
    )

    response = await taxi_driver_priority.get(
        constants.FLEET_URL, headers=fleet_headers, params={'driver_id': uuid},
    )
    assert response.status_code == 200
    assert response.json() == expected_fleet_reponse


def add_local_tz(timestamp: dt.datetime) -> dt.datetime:
    return (timestamp + dt.timedelta(hours=3)).replace(
        tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180),
    )
