import datetime
from typing import Any
from typing import Dict
from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario

_DBID = 'parkid0'
_UUID = 'uuid0'

_MODE_RULE_SETTINGS = {'rule_id': 'id', 'shift_close_time': '00:00'}

_NEXT_MODE_RULE_ID = '22222222222222222222222222222222'
_NEXT_MODE_RULE_NAME = 'next_work_mode'


@pytest.mark.parametrize(
    'set_by_session, mode_settings, do_mock_locale, expect_accept_language,'
    'expect_driver_profiles_call',
    [
        pytest.param(
            True,
            None,
            False,
            'ru',
            False,
            id='set_by_session without mode_settings',
        ),
        pytest.param(
            False,
            None,
            True,
            'ru',
            True,
            id='set_by_tvm without mode_settings',
        ),
        pytest.param(
            False,
            None,
            False,
            None,
            True,
            id='set_by_tvm without mode_settings without locale',
        ),
    ],
)
@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.now('2020-05-05T13:01:00+03:00')
async def test_mode_set_saga(
        pgsql,
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        taxi_config,
        mocked_time,
        stq,
        set_by_session: bool,
        mode_settings: Optional[Dict[str, Any]],
        do_mock_locale: bool,
        expect_accept_language: Optional[str],
        expect_driver_profiles_call: bool,
):
    _expect_delay = 5
    test_profile = driver.Profile(f'{_DBID}_{_UUID}')
    scene = scenario.Scene(
        profiles={test_profile: driver.Mode('custom_orders')},
        udid='test-driver-id',
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def driver_profiles(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': test_profile.dbid_uuid(),
                    'data': {'locale': 'ru'} if do_mock_locale else {},
                },
            ],
        }

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode='orders',
        mode_settings=mode_settings,
        set_by_session=set_by_session,
    )

    assert response.status_code == 200

    assert response.json() == common.build_set_mode_result(
        set_by_session, 'orders', 'orders_type', '2020-05-05T10:01:00+00:00',
    )

    stq_data = stq.subscription_saga.next_call()
    stq_data['kwargs'].pop('log_extra')
    assert stq_data == {
        'args': [],
        'eta': datetime.datetime(2020, 5, 5, 10, 1, _expect_delay),
        'id': f'{_DBID}_{_UUID}',
        'kwargs': saga_tools.build_saga_kwargs_raw(_DBID, _UUID),
        'queue': 'subscription_saga',
    }

    stq_data = stq.subscription_saga.next_call()
    stq_data['kwargs'].pop('log_extra')
    assert stq_data == {
        'args': [],
        'eta': datetime.datetime(2020, 5, 5, 10, 1),
        'id': f'{_DBID}_{_UUID}',
        'kwargs': saga_tools.build_saga_kwargs_raw(_DBID, _UUID),
        'queue': 'subscription_saga',
    }

    assert saga_tools.get_saga_db_data(test_profile, pgsql) == (
        1,
        datetime.datetime(2020, 5, 5, 10, 1),
        test_profile.park_id(),
        test_profile.profile_id(),
        'test-driver-id',
        'orders',
        datetime.datetime(2020, 5, 5, 10, 1),
        mode_settings,
        'idempotency_key',
        expect_accept_language,
        None,
        saga_tools.get_compensation_policy(set_by_session),
        saga_tools.get_saga_source(set_by_session),
        'manual_mode_change' if set_by_session else 'service_request_mock',
    )

    assert driver_profiles.has_calls == expect_driver_profiles_call


@pytest.mark.parametrize(
    'set_by_session', [True, False], ids=['set_by_session_api', 'set_api'],
)
@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS={'wait_for_saga_delay_ms': 50},
)
@pytest.mark.now('2020-05-05T13:01:00+03:00')
async def test_mode_set_saga_not_crash_on_internal_polling(
        pgsql,
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        taxi_config,
        testpoint,
        mocked_time,
        stq,
        set_by_session: bool,
):
    test_profile = driver.Profile(f'{_DBID}_{_UUID}')
    scene = scenario.Scene(
        profiles={test_profile: driver.Mode('custom_orders')},
        udid='test-driver-id',
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    @testpoint('wait-for-saga-testpoint')
    def _wait_for_saga_cpp_testpoint(data):
        pass

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode='orders',
        mode_settings=None,
        set_by_session=set_by_session,
    )

    if set_by_session:
        assert _wait_for_saga_cpp_testpoint.times_called == 1
    else:
        assert _wait_for_saga_cpp_testpoint.times_called == 0

    assert response.status_code == 200

    assert response.json() == common.build_set_mode_result(
        set_by_session, 'orders', 'orders_type', '2020-05-05T10:01:00+00:00',
    )


@pytest.mark.parametrize(
    'saga_result_status, expected_code',
    [
        pytest.param(
            saga_tools.SAGA_STATUS_EXECUTED, 200, id='saga completed',
        ),
        pytest.param(
            saga_tools.SAGA_STATUS_COMPENSATED, 503, id='saga compensated',
        ),
        pytest.param(None, 503, id='saga running'),
    ],
)
@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS={
        'wait_for_saga_delay_ms': 50,
        'wait_for_saga_no_result_is_error': True,
    },
)
@pytest.mark.now('2020-05-05T13:01:00+03:00')
async def test_mode_set_saga_internal_polling(
        pgsql,
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        taxi_config,
        testpoint,
        mocked_time,
        stq,
        saga_result_status: Optional[str],
        expected_code: int,
):
    test_profile = driver.Profile(f'{_DBID}_{_UUID}')
    scene = scenario.Scene(
        profiles={test_profile: driver.Mode('custom_orders')},
        udid='test-driver-id',
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    @testpoint('wait-for-saga-testpoint')
    def _wait_for_saga_cpp_testpoint(data):
        if not saga_result_status:
            return
        deleted_sagas_id = saga_tools.delete_sagas(pgsql)
        assert len(deleted_sagas_id) == 1
        saga_id = deleted_sagas_id[0][0]
        assert saga_id == 1
        saga_tools.insert_saga_status(
            saga_id,
            saga_result_status,
            test_profile,
            'some-token',
            mocked_time.now(),
            pgsql,
        )

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode='orders',
        mode_settings=None,
        set_by_session=True,
    )

    assert response.status_code == expected_code

    if response.status_code == 200:
        assert response.json() == common.build_set_mode_result(
            True, 'orders', 'orders_type', '2020-05-05T10:01:00+00:00',
        )


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=_NEXT_MODE_RULE_NAME,
                billing_mode='driver_fix',
                features={
                    'booking': {'slot_policy': 'contractor_tariff_zone'},
                    'driver_fix': {},
                },
                rule_id=_NEXT_MODE_RULE_ID,
            ),
            mode_rules.Patch(rule_name='custom_orders', features={}),
        ],
    ),
)
@pytest.mark.now('2020-05-05T13:01:00+03:00')
@pytest.mark.parametrize('position_fallback', [False, True])
async def test_mode_set_by_mode_rule_id_saga(
        pgsql,
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        mocked_time,
        stq,
        position_fallback,
):
    _expect_delay = 5
    test_profile = driver.Profile(f'{_DBID}_{_UUID}')
    scene = scenario.Scene(
        profiles={test_profile: driver.Mode('custom_orders')},
        udid='test-driver-id',
    )
    scene.setup(
        mockserver,
        mocked_time,
        driver_authorizer,
        mock_driver_trackstory=False,
    )

    driver_position = scenario.MOSCOW_POSITION
    service_error = scenario.ServiceError.NoError
    location_data = None
    if position_fallback:
        driver_position = None
        service_error = scenario.ServiceError.ServerError
        location_data = {
            'positions': [
                {
                    'source': 'Verified',
                    'lat': scenario.MOSCOW_POSITION.lat,
                    'lon': scenario.MOSCOW_POSITION.lon,
                    'unix_timestamp': 0,
                },
            ],
        }

    scene.mock_driver_trackstory(mockserver, driver_position, service_error)
    response = await common.set_mode_by_rule_id(
        taxi_driver_mode_subscription,
        profile=test_profile,
        mode_rule_id=_NEXT_MODE_RULE_ID,
        mode_settings=_MODE_RULE_SETTINGS,
        location_data=location_data,
    )

    assert response.status_code == 200, response.json()

    assert response.json() == common.build_set_mode_result(
        True, _NEXT_MODE_RULE_NAME, 'orders_type', '2020-05-05T10:01:00+00:00',
    ), response.json()

    stq_data = stq.subscription_saga.next_call()
    stq_data['kwargs'].pop('log_extra')
    assert stq_data == {
        'args': [],
        'eta': datetime.datetime(2020, 5, 5, 10, 1, _expect_delay),
        'id': f'{_DBID}_{_UUID}',
        'kwargs': saga_tools.build_saga_kwargs_raw(_DBID, _UUID),
        'queue': 'subscription_saga',
    }

    stq_data = stq.subscription_saga.next_call()
    stq_data['kwargs'].pop('log_extra')
    assert stq_data == {
        'args': [],
        'eta': datetime.datetime(2020, 5, 5, 10, 1),
        'id': f'{_DBID}_{_UUID}',
        'kwargs': saga_tools.build_saga_kwargs_raw(_DBID, _UUID),
        'queue': 'subscription_saga',
    }

    assert saga_tools.get_saga_db_data(test_profile, pgsql) == (
        1,
        datetime.datetime(2020, 5, 5, 10, 1),
        test_profile.park_id(),
        test_profile.profile_id(),
        'test-driver-id',
        _NEXT_MODE_RULE_NAME,
        datetime.datetime(2020, 5, 5, 10, 1),
        _MODE_RULE_SETTINGS,
        'idempotency_key',
        'ru',
        None,
        saga_tools.get_compensation_policy(True),
        saga_tools.get_saga_source(True),
        'manual_mode_change',
    )
