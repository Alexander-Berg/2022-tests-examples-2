import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario


@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.now('2020-05-01T12:00:00+0300')
async def test_subscription_saga_do_nothing_without_data(
        pgsql, mocked_time, taxi_driver_mode_subscription, stq_runner,
):
    await stq_runner.subscription_saga.call(
        task_id='sample_task',
        kwargs=saga_tools.build_saga_kwargs_raw('someparkid', 'somedriverid'),
    )


_STEP_NAME = 'mode_change_step'


@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.now('2020-05-17T12:00:00+0300')
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name='custom_orders',
                billing_mode='custom_billing_mode',
                billing_mode_rule='custom_billing_mode_rule',
            ),
        ],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS=(
        saga_tools.SAGA_SETTINGS_ENABLE_FAILED_COMPENSATION
    ),
)
@pytest.mark.parametrize(
    'unique_driver_id, expected_park_id, expected_driver_id, '
    'expected_mode, expected_mode_settings, expected_billing_mode, '
    'expected_billing_mode_rule, expected_event_at, expected_external_ref, '
    'expected_saga_id, expected_saga_status, expected_change_reason',
    (
        pytest.param(
            'udi1',
            'parkid1',
            'uuid1',
            'orders',
            None,
            'some_billing_mode',
            'some_billing_mode_rule',
            '2020-04-04T13:00:00+00:00',
            saga_tools.make_idempotency_key(1, _STEP_NAME, False),
            1,
            saga_tools.SAGA_STATUS_EXECUTED,
            'unknown',
            id='new mode without mode_settings dbid_uuid',
        ),
        pytest.param(
            'udi2',
            'parkid2',
            'uuid2',
            'custom_orders',
            {'key': 'value'},
            'custom_billing_mode',
            'custom_billing_mode_rule',
            '2020-04-04T13:00:00+00:00',
            saga_tools.make_idempotency_key(2, _STEP_NAME, False),
            2,
            saga_tools.SAGA_STATUS_EXECUTED,
            'different_profile_usage',
            id='new mode with mode_settings',
        ),
        pytest.param(
            'udi1',
            'parkid1',
            'uuid1',
            'orders',
            None,
            'some_billing_mode',
            'some_billing_mode_rule',
            '2020-05-17T09:00:00+00:00',
            saga_tools.make_idempotency_key(1, _STEP_NAME, True),
            1,
            saga_tools.SAGA_STATUS_COMPENSATED,
            'saga_compensation',
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription', files=['failed_state.sql'],
                ),
            ],
            id='compensate new mode without mode_settings dbid_uuid',
        ),
        pytest.param(
            'udi2',
            'parkid2',
            'uuid2',
            'orders',
            {'prev_key': 'value'},
            'some_billing_mode',
            'some_billing_mode_rule',
            '2020-05-17T09:00:00+00:00',
            saga_tools.make_idempotency_key(2, _STEP_NAME, True),
            2,
            saga_tools.SAGA_STATUS_COMPENSATED,
            'saga_compensation',
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription', files=['failed_state.sql'],
                ),
            ],
            id='compensate new mode with mode_settings',
        ),
        pytest.param(
            'udi3',
            'parkid3',
            'uuid3',
            'custom_orders',
            None,
            'custom_billing_mode',
            'custom_billing_mode_rule',
            '2020-04-04T13:00:00+00:00',
            saga_tools.make_idempotency_key(3, _STEP_NAME, False),
            3,
            saga_tools.SAGA_STATUS_EXECUTED,
            'unknown',
            id='empty_reason_string_in_saga',
        ),
    ),
)
async def test_subscription_saga_mode_set(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        mockserver,
        unique_driver_id: str,
        expected_park_id: str,
        expected_driver_id: str,
        expected_mode: str,
        expected_mode_settings: Optional[Dict[str, Any]],
        expected_billing_mode: str,
        expected_billing_mode_rule: str,
        expected_event_at: str,
        expected_external_ref: str,
        expected_saga_id: int,
        expected_saga_status: str,
        expected_change_reason: str,
):
    _old_mode = 'orders'

    test_profile = driver.Profile(f'{expected_park_id}_{expected_driver_id}')

    scene = scenario.Scene(profiles={test_profile: driver.Mode(_old_mode)})
    scene.setup(mockserver, mocked_time)

    assert saga_tools.has_saga(test_profile, pgsql)

    await stq_runner.subscription_saga.call(
        task_id='sample_task',
        kwargs=saga_tools.build_saga_kwargs_raw(
            expected_park_id, expected_driver_id,
        ),
    )

    assert scene.driver_mode_index_mode_set_mock.times_called == 1

    mode_set_request = scene.driver_mode_index_mode_set_mock.next_call()[
        'request'
    ]

    mode_set_request_json = mode_set_request.json

    if expected_mode_settings:
        assert (
            mode_set_request_json['data']['settings'] == expected_mode_settings
        )
        del mode_set_request_json['data']['settings']

    assert mode_set_request_json == {
        'data': {
            'driver': {
                'driver_profile_id': expected_driver_id,
                'park_id': expected_park_id,
            },
            'work_mode': expected_mode,
            'billing_settings': {
                'mode': expected_billing_mode,
                'mode_rule': expected_billing_mode_rule,
            },
            'subscription_data': {
                'source': 'manual_mode_change',
                'reason': expected_change_reason,
            },
        },
        'event_at': expected_event_at,
        'external_ref': expected_external_ref,
    }

    assert not saga_tools.has_saga(test_profile, pgsql)

    saga_statuses = saga_tools.get_saga_statuses_with_tokens(pgsql)

    assert len(saga_statuses) == 1
    assert saga_statuses[0] == (
        expected_saga_id,
        expected_saga_status,
        expected_park_id,
        expected_driver_id,
        expected_external_ref,
    )


@pytest.mark.parametrize(
    'mode_settings',
    (
        pytest.param(None, id='without mode_settings'),
        pytest.param({'key': 'value'}, id='with mode_settings'),
    ),
)
@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.now('2020-05-01T12:00:00+0300')
async def test_subscription_saga_fetch_prev_mode_only_once(
        pgsql,
        mockserver,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        mode_settings: Optional[Dict[str, Any]],
):
    test_profile = driver.Profile('parkid3_uuid3')

    scene = scenario.Scene(
        profiles={
            test_profile: driver.Mode(
                'orders',
                started_at_iso='2020-04-04T13:00:00+00:00',
                mode_settings=mode_settings,
            ),
        },
    )
    scene.setup(mockserver, mocked_time)

    @mockserver.json_handler('/driver-mode-index/v1/mode/subscribe')
    def _driver_mode_index_mode_set(request):
        raise mockserver.TimeoutError()

    assert saga_tools.has_saga(test_profile, pgsql)
    assert saga_tools.saga_prev_mode(test_profile, pgsql) == (None, None, None)

    await stq_runner.subscription_saga.call(
        task_id='sample_task',
        args=[
            saga_tools.build_saga_args_raw(
                test_profile.park_id(), test_profile.profile_id(),
            ),
        ],
        expect_fail=True,
    )

    assert saga_tools.saga_prev_mode(test_profile, pgsql) == (
        'orders',
        datetime.datetime(2020, 4, 4, 13, 0),
        mode_settings,
    )

    scene = scenario.Scene(
        profiles={test_profile: driver.Mode('custom_orders')},
    )
    scene.setup(mockserver, mocked_time)

    @mockserver.json_handler('/driver-mode-index/v1/mode/subscribe')
    def _driver_mode_index_mode_set2(request):
        raise mockserver.TimeoutError()

    await stq_runner.subscription_saga.call(
        task_id='sample_task',
        args=saga_tools.build_saga_args_raw(
            test_profile.park_id(), test_profile.profile_id(),
        ),
        expect_fail=True,
    )

    assert saga_tools.saga_prev_mode(test_profile, pgsql) == (
        'orders',
        datetime.datetime(2020, 4, 4, 13, 0),
        mode_settings,
    )


@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.now('2020-05-17T12:00:00+0300')
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name='geobooking', features={'geobooking': {}},
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'park_id, driver_id, expected_mode_properties',
    (
        pytest.param('parkid1', 'uuid1', None, id='no_features'),
        pytest.param(
            'parkid4',
            'uuid4',
            ['time_based_subvention'],
            id='driver_fix_mapping',
        ),
        pytest.param(
            'parkid5',
            'uuid5',
            ['geobooking_unsubscribe'],
            id='geobooking_mapping',
        ),
    ),
)
async def test_subscription_saga_dmi_mode_properties(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        mockserver,
        park_id: str,
        driver_id: str,
        expected_mode_properties: Optional[List[str]],
):
    _old_mode = 'orders'

    test_profile = driver.Profile(f'{park_id}_{driver_id}')

    scene = scenario.Scene(profiles={test_profile: driver.Mode(_old_mode)})
    scene.setup(mockserver, mocked_time)

    @mockserver.json_handler('/driver-fix/v1/mode/on_start/')
    def _driver_fix_v1_mode_on_start(request):
        return {}

    @mockserver.json_handler('/driver-fix/v1/mode/on_stop/')
    def _driver_fix_v1_mode_on_stop(request):
        return {}

    @mockserver.json_handler('/driver-fix/v1/view/rule_key_params')
    async def _mock_view_offer(request):
        return {
            'rules': [
                {
                    'rule_id': 'next_rule_id',
                    'key_params': {
                        'tariff_zone': 'next_zone',
                        'subvention_geoarea': 'next_area',
                        'tag': 'next_tag',
                    },
                },
                {
                    'rule_id': 'prev_rule_id',
                    'key_params': {
                        'tariff_zone': 'prev_zone',
                        'subvention_geoarea': 'prev_area',
                        'tag': 'prev_tag',
                    },
                },
            ],
        }

    @mockserver.json_handler('/tags/v2/upload')
    def _v2_upload(request):
        return {'status': 'ok'}

    assert saga_tools.has_saga(test_profile, pgsql)

    await stq_runner.subscription_saga.call(
        task_id='sample_task',
        kwargs=saga_tools.build_saga_kwargs_raw(park_id, driver_id),
    )

    assert scene.driver_mode_index_mode_set_mock.times_called == 1

    mode_set_request = scene.driver_mode_index_mode_set_mock.next_call()[
        'request'
    ]
    mode_set_data = mode_set_request.json['data']

    if expected_mode_properties is None:
        assert 'mode_properties' not in mode_set_data
    else:
        assert mode_set_data['mode_properties'] == expected_mode_properties


@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.now('2020-05-17T12:00:00+0300')
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name='custom_orders',
                billing_mode='custom_billing_mode',
                billing_mode_rule='custom_billing_mode_rule',
            ),
        ],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS=(
        saga_tools.SAGA_SETTINGS_ENABLE_FAILED_COMPENSATION
    ),
)
async def test_subscription_saga_blocked_on_dmi_fail(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        mockserver,
):
    _old_mode = 'orders'

    test_profile = driver.Profile('parkid1_uuid1')

    scene = scenario.Scene(profiles={test_profile: driver.Mode(_old_mode)})
    scene.setup(mockserver, mocked_time, mock_dmi_set=False)

    assert saga_tools.has_saga(test_profile, pgsql)

    @mockserver.json_handler('/driver-mode-index/v1/mode/subscribe')
    def _driver_mode_index_mode_set(request):
        return mockserver.make_response(status=400)

    await saga_tools.call_stq_saga_task(
        stq_runner, test_profile, expect_fail=True,
    )

    steps = saga_tools.get_saga_steps_db_data(pgsql, 1)
    assert steps == [
        ('mode_change_step', 'blocked', None),
        ('ui_profile_change_step', 'ok', None),
    ]
