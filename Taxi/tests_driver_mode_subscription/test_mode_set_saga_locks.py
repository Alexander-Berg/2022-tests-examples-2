import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario

_DBID_1 = 'parkid1'
_UUID_1 = 'uuid1'

_DBID_2 = 'parkid2'
_UUID_2 = 'uuid2'


@pytest.mark.parametrize(
    'set_by_session',
    (
        pytest.param(True, id='set_by_session'),
        pytest.param(False, id='set_by_tvm'),
    ),
)
@pytest.mark.parametrize(
    'first_external_ref, second_external_ref, second_call_response_code',
    [
        pytest.param('same_key', 'same_key', 200, id='same_external_ref'),
        pytest.param('first_key', 'second', 400, id='different_external_ref'),
    ],
)
@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.now('2020-05-05T13:01:00+03:00')
async def test_mode_set_saga_multiple_calls_same_profile(
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
        first_external_ref: str,
        second_external_ref: str,
        second_call_response_code: int,
):
    test_profile = driver.Profile(f'{_DBID_1}_{_UUID_1}')
    scene = scenario.Scene(
        profiles={test_profile: driver.Mode('custom_orders')},
        udid='test-driver-id',
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode='orders',
        mode_settings=None,
        set_by_session=set_by_session,
        external_ref=first_external_ref,
    )

    assert response.status_code == 200

    assert response.json() == common.build_set_mode_result(
        set_by_session, 'orders', 'orders_type', '2020-05-05T10:01:00+00:00',
    )

    mocked_time.sleep(10)

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode='orders',
        mode_settings=None,
        set_by_session=set_by_session,
        external_ref=second_external_ref,
    )

    assert response.status_code == second_call_response_code

    if response.status_code == 200:
        assert response.json() == common.build_set_mode_result(
            set_by_session,
            'orders',
            'orders_type',
            '2020-05-05T10:01:00+00:00',
        )

    assert saga_tools.get_saga_db_data(test_profile, pgsql) == (
        1,
        datetime.datetime(2020, 5, 5, 10, 1),
        test_profile.park_id(),
        test_profile.profile_id(),
        'test-driver-id',
        'orders',
        datetime.datetime(2020, 5, 5, 10, 1),
        None,
        first_external_ref,
        'ru',
        None,
        saga_tools.get_compensation_policy(set_by_session),
        saga_tools.get_saga_source(set_by_session),
        'manual_mode_change' if set_by_session else 'service_request_mock',
    )


@pytest.mark.parametrize(
    'set_by_session',
    (
        pytest.param(True, id='set_by_session'),
        pytest.param(False, id='set_by_tvm'),
    ),
)
@pytest.mark.parametrize(
    'next_mode, next_mode_settings, expect_lock, second_call_response_code',
    [
        pytest.param('orders', None, False, 200, id='normal'),
        pytest.param(
            'driver_fix',
            {'rule_id': 'id', 'shift_close_time': '00:00'},
            True,
            400,
            id='has exclusive feature',
        ),
    ],
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name='driver_fix',
                display_mode='orders_type',
                features={'driver_fix': {}},
            ),
        ],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_FEATURES={
        '__default__': {'is_exclusive': False},
        'driver_fix': {'is_exclusive': True},
    },
)
@pytest.mark.now('2020-05-05T13:01:00+03:00')
async def test_mode_set_saga_multiple_calls_different_profile_same_udid(
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
        second_call_response_code: int,
        next_mode: str,
        next_mode_settings: Optional[Dict[str, Any]],
        expect_lock: bool,
):
    first_external_ref = 'first_key'
    second_external_ref = 'second_key'

    test_profile_1 = driver.Profile(f'{_DBID_1}_{_UUID_1}')
    test_profile_2 = driver.Profile(f'{_DBID_2}_{_UUID_2}')
    scene = scenario.Scene(
        profiles={
            test_profile_1: driver.Mode('custom_orders'),
            test_profile_2: driver.Mode('custom_orders'),
        },
        udid='test-driver-id',
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile_1,
        work_mode=next_mode,
        mode_settings=next_mode_settings,
        set_by_session=set_by_session,
        external_ref=first_external_ref,
    )

    assert response.status_code == 200

    assert response.json() == common.build_set_mode_result(
        set_by_session, next_mode, 'orders_type', '2020-05-05T10:01:00+00:00',
    )

    mocked_time.sleep(10)

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile_2,
        work_mode=next_mode,
        mode_settings=next_mode_settings,
        set_by_session=set_by_session,
        external_ref=second_external_ref,
    )

    assert response.status_code == second_call_response_code

    lock_id: Optional[str] = None

    if expect_lock:
        lock_id = scene.udid

    assert saga_tools.get_saga_db_data(test_profile_1, pgsql) == (
        1,
        datetime.datetime(2020, 5, 5, 10, 1),
        test_profile_1.park_id(),
        test_profile_1.profile_id(),
        'test-driver-id',
        next_mode,
        datetime.datetime(2020, 5, 5, 10, 1),
        next_mode_settings,
        first_external_ref,
        'ru',
        lock_id,
        saga_tools.get_compensation_policy(set_by_session),
        saga_tools.get_saga_source(set_by_session),
        'manual_mode_change' if set_by_session else 'service_request_mock',
    )

    if response.status_code == 200:
        assert response.json() == common.build_set_mode_result(
            set_by_session,
            next_mode,
            'orders_type',
            '2020-05-05T10:01:10+00:00',
        )

        assert saga_tools.get_saga_db_data(test_profile_2, pgsql) == (
            2,
            datetime.datetime(2020, 5, 5, 10, 1, 10),
            test_profile_2.park_id(),
            test_profile_2.profile_id(),
            'test-driver-id',
            next_mode,
            datetime.datetime(2020, 5, 5, 10, 1, 10),
            next_mode_settings,
            second_external_ref,
            'ru',
            lock_id,
            saga_tools.get_compensation_policy(set_by_session),
            saga_tools.get_saga_source(set_by_session),
            'manual_mode_change' if set_by_session else 'service_request_mock',
        )
    else:
        assert saga_tools.has_saga(test_profile_2, pgsql) is False


@pytest.mark.parametrize(
    'mode_change_tokens, expect_saga_started, expected_code',
    [
        pytest.param(
            ['some-random-token'],
            False,
            400,
            id='token changed before saga started',
        ),
        pytest.param(
            [common.DEFAULT_INDEX_EXTERNAL_REF],
            True,
            200,
            id='token not changed',
        ),
        pytest.param([], True, 200, id='no tokens exists'),
        pytest.param(
            ['old_token', common.DEFAULT_INDEX_EXTERNAL_REF],
            True,
            200,
            id='token order matter positive path',
        ),
        pytest.param(
            [common.DEFAULT_INDEX_EXTERNAL_REF, 'new_token'],
            False,
            400,
            id='token order matter negative path',
        ),
    ],
)
@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.now(datetime.datetime.now().isoformat())
async def test_mode_set_saga_race(
        pgsql,
        taxi_driver_mode_subscription,
        mode_rules_data,
        driver_authorizer,
        mockserver,
        taxi_config,
        testpoint,
        mocked_time,
        stq,
        mode_change_tokens: List[str],
        expected_code: int,
        expect_saga_started: bool,
):
    test_profile = driver.Profile(f'{_DBID_1}_{_UUID_1}')
    scene = scenario.Scene(
        profiles={test_profile: driver.Mode('custom_orders')},
        udid='test-driver-id',
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    @testpoint('before-start-saga-testpoint')
    def _wait_for_saga_cpp_testpoint(data):
        for token_idx, token in enumerate(mode_change_tokens, start=1):
            mocked_time.sleep(1)
            saga_tools.insert_saga_status(
                token_idx,
                saga_tools.SAGA_STATUS_EXECUTED,
                test_profile,
                token,
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

    sagas = saga_tools.get_all_sagas_db_data(pgsql, test_profile)

    if expect_saga_started:
        assert len(sagas) == 1
    else:
        assert not sagas
