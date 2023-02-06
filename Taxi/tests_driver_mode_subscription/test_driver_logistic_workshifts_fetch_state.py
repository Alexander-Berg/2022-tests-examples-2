import datetime as dt
from typing import Any
from typing import Dict

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scenario
from tests_driver_mode_subscription import scheduled_slots_tools


_PARK_ID = 'park-id-1'
_DRIVER_ID = 'driver-id-1'

_LOGISTIC_WORKSHIFTS = 'logistic_workshifts'
_SLOT_ID_1 = '0d2841a3-b966-4a3b-8be4-7e915d3fb995'
_OFFER_IDENTITY_1 = {'slot_id': _SLOT_ID_1, 'rule_version': 1}
_SLOT_NAME_1 = _SLOT_ID_1.replace('-', '')
_DATE_1 = dt.datetime(2019, 5, 1, 9, 0, tzinfo=dt.timezone.utc)
_QUOTA_ID_1 = '7463f61d-0d9c-4fad-96e4-a06f33dcc9ab'

_LOGISTIC_WORK_MODE_AUTO_NAME = 'logistic_work_mode_auto'

_LOGISTIC_WORK_MODE_AUTO_ID = 'a883a23977484000b870f0cfcc84e1f9'

_LOGISTIC_WORK_MODE_AUTO = mode_rules.Patch(
    rule_name=_LOGISTIC_WORK_MODE_AUTO_NAME,
    features={'logistic_workshifts': {}, 'active_transport': {'type': 'auto'}},
    rule_id=_LOGISTIC_WORK_MODE_AUTO_ID,
)

_POWER_POLICY_CASE_1 = {
    'background': 300,
    'full': 100,
    'idle': 400,
    'powersaving': 200,
}

_POWER_POLICY_CASE_2 = {
    'background': 500,
    'full': 300,
    'idle': 600,
    'powersaving': 400,
}

_POWER_POLICY_DEFAULT = {
    'background': 1200,
    'full': 600,
    'idle': 1800,
    'powersaving': 1200,
}


def _unpack_polling_header(header_content: str):
    result = {}

    parts = header_content.split(', ')
    for part in parts:
        line = part.split('=')
        result[line[0]] = int(line[1][:-1])

    return result


@pytest.mark.config(
    API_OVER_DATA_ENABLE_CACHES=True,
    API_OVER_DATA_ENABLE_SPECIFIC_CACHE={'__default__': {'__default__': True}},
    API_OVER_DATA_OPENING_LAG_MS={'__default__': {'__default__': -1}},
)
@pytest.mark.mode_rules(rules=mode_rules.patched([_LOGISTIC_WORK_MODE_AUTO]))
@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        scheduled_slots_tools.make_insert_reservation_query(
            _SLOT_NAME_1,
            _LOGISTIC_WORKSHIFTS,
            _OFFER_IDENTITY_1,
            _OFFER_IDENTITY_1,
            _DATE_1,
            _DATE_1,
            _QUOTA_ID_1.replace('-', ''),
            1,
            _PARK_ID,
            _DRIVER_ID,
        ),
    ],
)
@pytest.mark.parametrize(
    'lsc_state_response, expected_http_code, expected_response',
    [
        (
            {'is_logistic_workshifts_enabled': False},
            200,
            {'is_logistic_workshifts_enabled': False},
        ),
        (
            {'is_logistic_workshifts_enabled': True},
            200,
            {
                'is_logistic_workshifts_enabled': True,
                'pending_shifts_info': {
                    'captions': {
                        'subtitle': 'Сегодня 1 слот',
                        'title': 'Расписание слотов',
                    },
                    'counter': 1,
                },
            },
        ),
        (
            {
                'is_logistic_workshifts_enabled': True,
                'active_slot': {
                    'identity': {
                        'rule_version': 2,
                        'slot_id': '6c2ec7ec-0df0-4fe0-8aa1-6b01f91a9b6e',
                    },
                    'description': {'captions': {}, 'icon': 'waiting'},
                    'time_range': {
                        'begin': '2033-04-06T08:00:00+00:00',
                        'end': '2033-04-06T20:00:00+00:00',
                    },
                    'allowed_transport_types': [],
                    'activation_state': 'starting',
                    'quota_id': 'a75c75af-2bfb-44bb-969d-b25c63f5b3b7',
                    'actions': [],
                    'free_time_end': '2033-04-06T19:00:00+00:00',
                    'extra_time_end': '2033-04-06T19:05:00+00:00',
                },
            },
            200,
            {
                'is_logistic_workshifts_enabled': True,
                'pending_shifts_info': {
                    'captions': {
                        'subtitle': 'Сегодня 1 слот',
                        'title': 'Расписание слотов',
                    },
                    'counter': 1,
                },
                'active_slot': {
                    'activation_state': 'starting',
                    'pause_warning_title': 'Слот в работе до 23:00',
                    'paused_until': '2033-04-06T19:00:00+00:00',
                    'pause_penalty_deadline': '2033-04-06T19:05:00+00:00',
                },
            },
        ),
    ],
)
async def test_workshift_fetch_state(
        taxi_driver_mode_subscription,
        driver_authorizer,
        mockserver,
        mocked_time,
        mode_rules_data,
        expected_http_code: int,
        lsc_state_response: Dict[str, Any],
        expected_response: Dict[str, Any],
):
    test_profile = driver.Profile(f'{_PARK_ID}_{_DRIVER_ID}')
    scene = scenario.Scene(
        profiles={
            test_profile: driver.Mode(_LOGISTIC_WORK_MODE_AUTO.rule_name),
        },
        udid='test-driver-id',
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    await taxi_driver_mode_subscription.invalidate_caches()

    @mockserver.json_handler(
        '/logistic-supply-conductor/internal/v1/courier/state',
    )
    def _logistic_supply_conductor_state(request):
        return lsc_state_response

    headers = {
        'User-Agent': 'Taximeter 8.80 (562)',
        'X-YaTaxi-Park-Id': test_profile.park_id(),
        'X-YaTaxi-Driver-Profile-Id': test_profile.profile_id(),
        'X-Request-Application-Version': '8.80 (562)',
        'X-Request-Application': 'taximeter',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'Accept-Language': 'ru',
        'Timezone': 'Europe/Moscow',
        'X-Ya-Service-Ticket': common.MOCK_TICKET,
    }

    response = await taxi_driver_mode_subscription.post(
        'driver/v1/logistic-workshifts/fetch-state', json={}, headers=headers,
    )

    assert response.status_code == expected_http_code

    if response.status_code == 200:
        assert response.json() == expected_response


@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.parametrize(
    'expected_policy',
    [
        pytest.param(
            _POWER_POLICY_CASE_1,
            marks=[
                pytest.mark.config(
                    TAXIMETER_POLLING_POWER_POLICY_DELAYS={
                        '__default__': _POWER_POLICY_DEFAULT,
                        '/driver/v1/logistic-workshifts/fetch-state': (
                            _POWER_POLICY_CASE_1
                        ),
                    },
                ),
            ],
        ),
        pytest.param(
            _POWER_POLICY_CASE_2,
            marks=[
                pytest.mark.config(
                    TAXIMETER_POLLING_POWER_POLICY_DELAYS={
                        '__default__': _POWER_POLICY_DEFAULT,
                        '/driver/v1/logistic-workshifts/fetch-state': (
                            _POWER_POLICY_CASE_2
                        ),
                    },
                ),
            ],
        ),
    ],
)
async def test_workshift_fetch_state_power_policy(
        taxi_driver_mode_subscription,
        driver_authorizer,
        mockserver,
        mocked_time,
        mode_rules_data,
        expected_policy: Dict[str, int],
):
    test_profile = driver.Profile(f'{_PARK_ID}_{_DRIVER_ID}')
    scene = scenario.Scene(
        profiles={
            test_profile: driver.Mode(_LOGISTIC_WORK_MODE_AUTO.rule_name),
        },
        udid='test-driver-id',
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    await taxi_driver_mode_subscription.invalidate_caches()

    @mockserver.json_handler(
        '/logistic-supply-conductor/internal/v1/courier/state',
    )
    def _logistic_supply_conductor_state(request):
        return {'is_logistic_workshifts_enabled': False}

    headers = {
        'User-Agent': 'Taximeter 8.80 (562)',
        'X-YaTaxi-Park-Id': test_profile.park_id(),
        'X-YaTaxi-Driver-Profile-Id': test_profile.profile_id(),
        'X-Request-Application-Version': '8.80 (562)',
        'X-Request-Application': 'taximeter',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'Accept-Language': 'ru',
        'Timezone': 'Europe/Moscow',
        'X-Ya-Service-Ticket': common.MOCK_TICKET,
    }

    response = await taxi_driver_mode_subscription.post(
        'driver/v1/logistic-workshifts/fetch-state', json={}, headers=headers,
    )

    assert (
        response.status_code == 200
    ), 'simple fetch-state failed, not tested here'

    assert (
        _unpack_polling_header(response.headers['X-Polling-Power-Policy'])
        == expected_policy
    )
