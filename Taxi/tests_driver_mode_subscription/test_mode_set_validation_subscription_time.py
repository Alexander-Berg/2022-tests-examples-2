import datetime
from typing import List
from typing import Optional
from typing import Tuple

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scenario

_NOW = datetime.datetime.fromisoformat('2019-05-01T09:00:00+00:00')

_DRIVER_MODE_RULES = mode_rules.default_mode_rules()


def _build_restrictions_config(
        allowed_ranges: List[Tuple[Tuple[str, str], Tuple[str, str]]],
        time_zone: str,
        tariff_zone: str = '__default__',
):
    subscription_schedule = [
        {
            'start': {'time': time_range[0][0], 'weekday': time_range[0][1]},
            'stop': {'time': time_range[1][0], 'weekday': time_range[1][1]},
        }
        for time_range in allowed_ranges
    ]

    return pytest.mark.config(
        DRIVER_MODE_RULES_SUBSCRIPTION_TIME_V2={
            'orders': {
                'time_zone': time_zone,
                'tariff_zones_settings': {
                    tariff_zone: {
                        'subscription_schedule': subscription_schedule,
                    },
                },
            },
        },
    )


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.geoareas(filename='geoareas_samara.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'expect_error, expected_message, set_by_session',
    [
        pytest.param(False, None, True, id='no_restrictions'),
        pytest.param(
            False,
            None,
            True,
            marks=[
                _build_restrictions_config(
                    allowed_ranges=[(('08:59', 'wed'), ('09:01', 'wed'))],
                    time_zone='utc',
                ),
            ],
            id='ok',
        ),
        pytest.param(
            True,
            'Подписаться можно будет с Ср, 12:00',
            True,
            marks=[
                _build_restrictions_config(
                    allowed_ranges=[(('08:00', 'wed'), ('09:00', 'wed'))],
                    time_zone='utc',
                ),
            ],
            id='fail_lately',
        ),
        pytest.param(
            True,
            'Подписаться можно будет с 13:01',
            True,
            marks=[
                _build_restrictions_config(
                    allowed_ranges=[(('09:01', 'wed'), ('10:00', 'wed'))],
                    time_zone='utc',
                ),
            ],
            id='fail_early',
        ),
        pytest.param(
            False,
            None,
            True,
            marks=[
                _build_restrictions_config(
                    allowed_ranges=[(('12:00', 'wed'), ('12:01', 'wed'))],
                    time_zone='moscow',
                ),
            ],
            id='moscow_restriction_timezone',
        ),
        pytest.param(
            True,
            'Подписаться можно будет с Ср, 00:00',
            True,
            marks=[
                _build_restrictions_config(
                    allowed_ranges=[(('00:00', 'wed'), ('00:01', 'wed'))],
                    time_zone='local',
                ),
            ],
            id='local_restriction_timezone',
        ),
        pytest.param(
            True,
            'Подписаться можно будет с Чт, 13:00',
            True,
            marks=[
                _build_restrictions_config(
                    allowed_ranges=[(('09:00', 'thu'), ('09:01', 'thu'))],
                    time_zone='utc',
                ),
            ],
            id='fail_weekday',
        ),
        pytest.param(
            True,
            'Сейчас режим недоступен для подписки',
            True,
            marks=[
                _build_restrictions_config(allowed_ranges=[], time_zone='utc'),
            ],
            id='prohibited',
        ),
    ],
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
async def test_mode_set_subscription_time_timezones(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        mocked_time,
        expect_error: bool,
        expected_message: Optional[str],
        set_by_session: bool,
):
    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(profiles={test_profile: driver.Mode('orders')})
    scene.setup(
        mockserver,
        mocked_time,
        driver_authorizer,
        mock_driver_trackstory=False,
    )
    scene.mock_driver_trackstory(mockserver, scenario.SAMARA_POSITION)

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        documents = [
            {
                'kind': 'driver_mode_subscription',
                'external_event_ref': 'idempotency',
                'event_at': _NOW.isoformat(),
                'data': {
                    'driver': {
                        'park_id': 'dbid0',
                        'driver_profile_id': 'uuid0',
                    },
                    'mode': 'driver_fix',
                    'settings': {
                        'rule_id': 'some_id',
                        'shift_close_time': '00:00',
                    },
                },
            },
        ]

        return {'docs': documents, 'cursor': '0'}

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode='orders',
        mode_settings=None,
        set_by_session=set_by_session,
    )

    if expect_error:
        assert response.status_code == 423
        assert expected_message
        response_body = response.json()
        if set_by_session:
            assert response_body == {
                'code': 'SUBSCRIPTION_TIME_VALIDATION_FAILED',
                'localized_message': expected_message,
                'localized_message_title': 'Не сейчас',
            }

        else:
            assert response_body['code'] == 'LOCKED'
            assert not response_body['message']
        assert 'details' not in response_body
    else:
        assert response.status_code == 200


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.geoareas(filename='geoareas_samara.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.config(
    DRIVER_MODE_RULES_SUBSCRIPTION_TIME_V2={
        'orders': {
            'time_zone': 'utc',
            'tariff_zones_settings': {
                '__default__': {
                    'subscription_schedule': [
                        {
                            'start': {'time': '00:00', 'weekday': 'wed'},
                            'stop': {'time': '23:59', 'weekday': 'wed'},
                        },
                    ],
                },
            },
        },
    },
)
@pytest.mark.parametrize(
    'set_by_session, expected_code', [(True, 423), (False, 200)],
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
async def test_mode_set_subscription_time_validation_trackstory_error(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        driver_authorizer,
        mode_rules_data,
        mode_geography_defaults,
        set_by_session: bool,
        expected_code: int,
):
    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(profiles={test_profile: driver.Mode('orders')})
    scene.setup(
        mockserver,
        mocked_time,
        driver_authorizer,
        mock_driver_trackstory=False,
    )
    scene.mock_driver_trackstory(
        mockserver, None, scenario.ServiceError.NoError,
    )

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        documents = [
            {
                'kind': 'driver_mode_subscription',
                'external_event_ref': 'idempotency',
                'event_at': _NOW.isoformat(),
                'data': {
                    'driver': {
                        'park_id': 'dbid0',
                        'driver_profile_id': 'uuid0',
                    },
                    'mode': 'driver_fix',
                    'settings': {
                        'rule_id': 'some_id',
                        'shift_close_time': '00:00',
                    },
                },
            },
        ]

        return {'docs': documents, 'cursor': '0'}

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode='orders',
        mode_settings=None,
        set_by_session=set_by_session,
    )
    assert response.status_code == expected_code
