from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario

_DBID = 'parkid0'
_UUID = 'uuid0'

NEXT_MODE = 'next_work_mode'
PREV_MODE = 'prev_work_mode'
_NEXT_MODE_SETTINGS = {'rule_id': 'next_rule_id', 'shift_close_time': '00:01'}
_PREV_MODE_SETTINGS = {'rule_id': 'prev_rule_id', 'shift_close_time': '00:01'}


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=NEXT_MODE,
                features={
                    'booking': {'slot_policy': 'contractor_tariff_zone'},
                },
            ),
            mode_rules.Patch(rule_name=PREV_MODE, features={}),
        ],
    ),
)
@pytest.mark.parametrize(
    'trackstory_error, trackstory_position, fallback_position, by_session, '
    'expected_code, expected_zone, code, message, message_title',
    [
        pytest.param(
            scenario.ServiceError.NoError,
            scenario.MOSCOW_POSITION,
            None,
            True,
            200,
            'moscow',
            None,
            None,
            None,
            id='set_by_session success',
        ),
        pytest.param(
            scenario.ServiceError.NoError,
            scenario.MOSCOW_POSITION,
            None,
            False,
            200,
            'moscow',
            None,
            None,
            None,
            id='set success',
        ),
        pytest.param(
            scenario.ServiceError.NoError,
            None,
            None,
            True,
            423,
            None,
            'POSITION_FETCH_FAILED',
            (
                'Переместитесь на более открытую местность, '
                'чтобы мы автоматически обновили данные.'
            ),
            'Нет доступа к GPS',
            id='set_by_session no position',
        ),
        pytest.param(
            scenario.ServiceError.TimeoutError,
            scenario.MOSCOW_POSITION,
            None,
            True,
            503,
            None,
            None,
            None,
            None,
            id='set_by_session failed fetch position',
        ),
        # just in case, booking in set handler not well supported
        pytest.param(
            scenario.ServiceError.NoError,
            None,
            None,
            False,
            423,
            None,
            None,
            None,
            None,
            id='set no position',
        ),
        pytest.param(
            scenario.ServiceError.NoError,
            None,
            scenario.MOSCOW_POSITION,
            False,
            200,
            'moscow',
            None,
            None,
            None,
            id='set_fallback_position',
        ),
    ],
)
@pytest.mark.now('2019-11-14T04:01:00+03:00')
async def test_mode_set_booking(
        taxi_driver_mode_subscription,
        pgsql,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        taxi_config,
        mocked_time,
        trackstory_position: Optional[common.Position],
        trackstory_error: scenario.ServiceError,
        by_session: bool,
        expected_code: int,
        code: Optional[str],
        message: Optional[str],
        message_title: Optional[str],
        expected_zone: Optional[str],
        fallback_position: Optional[common.Position],
):
    test_profile = driver.Profile(f'{_DBID}_{_UUID}')
    scene = scenario.Scene(
        profiles={test_profile: driver.Mode(PREV_MODE)}, udid='test-driver-id',
    )

    scene.setup(
        mockserver,
        mocked_time,
        driver_authorizer,
        mock_driver_trackstory=False,
    )

    scene.mock_driver_trackstory(
        mockserver, trackstory_position, trackstory_error,
    )

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode=NEXT_MODE,
        mode_settings=None,
        set_by_session=by_session,
        fallback_position=fallback_position,
    )

    assert response.status_code == expected_code
    response_body = response.json()
    if code:
        assert response_body['code'] == code
    if message:
        assert response_body['localized_message'] == message
    if message_title:
        assert response_body['localized_message_title'] == message_title

    if response.status_code == 200:
        saga_context = saga_tools.get_saga_context(test_profile, pgsql)
        assert saga_context['next_mode']['tariff_zone'] == 'moscow'


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=NEXT_MODE,
                billing_mode='driver_fix',
                features={
                    'booking': {'slot_policy': 'contractor_tariff_zone'},
                    'driver_fix': {},
                },
            ),
            mode_rules.Patch(
                rule_name=PREV_MODE,
                billing_mode='driver_fix',
                features={
                    'booking': {'slot_policy': 'contractor_tariff_zone'},
                    'driver_fix': {},
                },
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'trackstory_error, trackstory_position, by_session, target_mode, '
    'expected_code, expected_zone, code, message, message_title',
    [
        pytest.param(
            scenario.ServiceError.NoError,
            None,
            True,
            PREV_MODE,
            423,
            None,
            'POSITION_FETCH_FAILED',
            (
                'Переместитесь на более открытую местность, '
                'чтобы мы автоматически обновили данные.'
            ),
            'Нет доступа к GPS',
            id='set_by_session_no_position',
        ),
        pytest.param(
            scenario.ServiceError.NoError,
            None,
            False,
            PREV_MODE,
            200,
            'prev_area',
            None,
            None,
            None,
            id='set_no_position_same_mode',
        ),
        pytest.param(
            scenario.ServiceError.NoError,
            None,
            False,
            NEXT_MODE,
            423,
            None,
            None,
            None,
            None,
            id='set_no_position_different_mode',
        ),
        pytest.param(
            scenario.ServiceError.TimeoutError,
            scenario.MOSCOW_POSITION,
            True,
            PREV_MODE,
            503,
            None,
            None,
            None,
            None,
            id='set_by_session_trackstory_timeout',
        ),
        pytest.param(
            scenario.ServiceError.TimeoutError,
            scenario.MOSCOW_POSITION,
            False,
            PREV_MODE,
            200,
            None,
            None,
            None,
            None,
            id='set_trackstory_timeout',
        ),
    ],
)
@pytest.mark.now('2019-11-14T04:01:00+03:00')
async def test_mode_set_booking_resubscribe_no_position(
        taxi_driver_mode_subscription,
        pgsql,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        taxi_config,
        mocked_time,
        trackstory_position: Optional[common.Position],
        trackstory_error: scenario.ServiceError,
        by_session: bool,
        target_mode: str,
        expected_code: int,
        code: Optional[str],
        message: Optional[str],
        message_title: Optional[str],
        expected_zone: Optional[str],
):
    test_profile = driver.Profile(f'{_DBID}_{_UUID}')
    scene = scenario.Scene(
        profiles={
            test_profile: driver.Mode(
                PREV_MODE, mode_settings=_PREV_MODE_SETTINGS,
            ),
        },
        udid='test-driver-id',
    )

    scene.setup(
        mockserver,
        mocked_time,
        driver_authorizer,
        mock_driver_trackstory=False,
    )

    scene.mock_driver_trackstory(
        mockserver, trackstory_position, trackstory_error,
    )

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode=target_mode,
        mode_settings=_NEXT_MODE_SETTINGS,
        set_by_session=by_session,
    )

    assert response.status_code == expected_code
    response_body = response.json()
    if code:
        assert response_body['code'] == code
    if message:
        assert response_body['localized_message'] == message
    if message_title:
        assert response_body['localized_message_title'] == message_title

    if response.status_code == 200:
        saga_context = saga_tools.get_saga_context(test_profile, pgsql)
        assert 'tariff_zone' not in saga_context['next_mode']


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'set_by_session', [True, False], ids=['set_by_session_api', 'set_api'],
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=PREV_MODE,
                features={
                    'booking': {'slot_policy': 'contractor_tariff_zone'},
                },
            ),
            mode_rules.Patch(rule_name=NEXT_MODE, features={}),
        ],
    ),
)
@pytest.mark.now('2019-11-14T04:01:00+03:00')
async def test_mode_set_booking_not_crash_on_check_position_on_prev_mode(
        taxi_driver_mode_subscription,
        pgsql,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        taxi_config,
        mocked_time,
        set_by_session: bool,
):
    test_profile = driver.Profile(f'{_DBID}_{_UUID}')
    scene = scenario.Scene(
        profiles={test_profile: driver.Mode(PREV_MODE)}, udid='test-driver-id',
    )

    scene.setup(
        mockserver,
        mocked_time,
        driver_authorizer,
        mock_driver_trackstory=False,
    )

    scene.mock_driver_trackstory(
        mockserver, None, scenario.ServiceError.TimeoutError,
    )

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode=NEXT_MODE,
        mode_settings=None,
        set_by_session=set_by_session,
    )

    assert response.status_code == 200
