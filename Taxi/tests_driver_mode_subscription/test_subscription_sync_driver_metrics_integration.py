from typing import Any
from typing import Dict

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario


_DRIVER_MODE_RULES = mode_rules.patched(
    [mode_rules.Patch(rule_name='blocked_mode')],
)

_DRIVER_MODE_RULES_BLOCKING_TAGS: Dict[str, Any] = {
    'blocked_mode': {'tags': ['many_rejects_recently']},
}

_FULL_UNSUBSCRIBE_REASONS: Dict[str, Any] = {
    'freemode_violations': {
        'current_mode_params': {'blocking_tags': ['many_rejects_recently']},
        'actions': {
            'send_unsubscribe_notification': {'type': 'freemode_violations'},
            'assign_tags': [
                {'name': 'many_rejects_recently', 'ttl_m': 120},
                {'name': 'some_tag'},
            ],
        },
    },
}

_NO_PARAMS_UNSUBSCRIBE_REASONS: Dict[str, Any] = {
    'freemode_violations': {
        'current_mode_params': {},
        'actions': {
            'send_unsubscribe_notification': {'type': 'freemode_violations'},
            'assign_tags': [
                {'name': 'many_rejects_recently', 'ttl_m': 120},
                {'name': 'some_tag'},
            ],
        },
    },
}

_EMPTY_UNSUBSCRIBE_REASONS: Dict[str, Any] = {
    'freemode_violations': {'current_mode_params': {}, 'actions': {}},
}


@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.config(
    DRIVER_MODE_RULES_BLOCKING_TAGS=_DRIVER_MODE_RULES_BLOCKING_TAGS,
    DRIVER_MODE_SUBSCRIPTION_PARK_VALIDATION_SETTINGS_V2={
        'check_enabled': True,
        'subscription_sync_enabled': False,
        'reschedule_timeshift_ms': 60,
    },
)
@pytest.mark.parametrize(
    'current_mode, unsubscribe_reason, expect_unsubscribe, '
    ' expect_tags_call ',
    [
        pytest.param(
            'blocked_mode',
            'freemode_violations',
            True,
            False,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_UNSUBSCRIBE_REASONS=(
                        _FULL_UNSUBSCRIBE_REASONS
                    ),
                ),
            ],
            id='unsubscribe mode with blocking_tags, assign_tags in saga',
        ),
        pytest.param(
            'custom_orders',
            'freemode_violations',
            False,
            True,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_UNSUBSCRIBE_REASONS=(
                        _FULL_UNSUBSCRIBE_REASONS
                    ),
                ),
            ],
            id='not unsubscribe mode without blocking_tags',
        ),
        pytest.param(
            'custom_orders',
            'freemode_violations',
            True,
            False,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_UNSUBSCRIBE_REASONS=(
                        _NO_PARAMS_UNSUBSCRIBE_REASONS
                    ),
                ),
            ],
            id='unsubscribe always if no params, assign_tags in saga',
        ),
        pytest.param(
            'custom_orders',
            'freemode_violations',
            True,
            False,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_UNSUBSCRIBE_REASONS=(
                        _EMPTY_UNSUBSCRIBE_REASONS
                    ),
                ),
            ],
            id='unsubscribe without actions',
        ),
    ],
)
# Integration tests with driver-metrics stq callbacks in config:
# DRIVER_METRICS_NEW_STQ_CALLBACK_RULES
async def test_subscription_sync_driver_metrics_integration(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        stq,
        stq_runner,
        taxi_config,
        mockserver,
        mocked_time,
        testpoint,
        current_mode: str,
        unsubscribe_reason: str,
        expect_unsubscribe: bool,
        expect_tags_call: bool,
):
    @testpoint('handle-mode-set-testpoint')
    def _handle_mode_set_cpp_testpoint(data):
        pass

    driver_profile = driver.Profile('parkid0_uuid0')
    scene = scenario.Scene(
        profiles={driver_profile: driver.Mode(current_mode)},
    )
    scene.setup(mockserver, mocked_time)

    @mockserver.json_handler('/tags/v2/upload')
    def _v2_upload(request):
        return {'status': 'ok'}

    kwargs = {
        'park_driver_id': driver_profile.dbid_uuid(),
        'unsubscribe_reason': unsubscribe_reason,
    }

    await stq_runner.subscription_sync.call(
        task_id='sample_task', kwargs=kwargs,
    )

    if expect_tags_call:
        assert _v2_upload.times_called == 1
        upload_request = _v2_upload.next_call()['request']

        assert upload_request.json == {
            'append': [
                {
                    'entity_type': 'dbid_uuid',
                    'tags': [
                        {
                            'entity': 'parkid0_uuid0',
                            'name': 'many_rejects_recently',
                            'ttl': 7200,
                        },
                        {'entity': 'parkid0_uuid0', 'name': 'some_tag'},
                    ],
                },
            ],
            'provider_id': 'driver-mode-subscription',
        }
    else:
        assert _v2_upload.times_called == 0

    if expect_unsubscribe:
        assert stq.subscription_sync.times_called == 0
        assert _handle_mode_set_cpp_testpoint.times_called == 1
        mode_set_data = _handle_mode_set_cpp_testpoint.next_call()['data']
        # external_ref is random uuid4
        expected_external_ref = mode_set_data['external_ref']
        assert mode_set_data == common.mode_set_testpoint_data(
            driver_profile,
            accept_language='ru',
            external_ref=expected_external_ref,
            active_since='2019-05-01T09:00:00+00:00',
            mode='orders',
            source=saga_tools.SOURCE_SUBSCRIPTION_SYNC,
            change_reason='freemode_violations',
        )
    else:
        assert stq.subscription_sync.times_called == 0
        assert _handle_mode_set_cpp_testpoint.times_called == 0
