import datetime
from typing import Dict
from typing import List

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_groups
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario


_NO_MODE_MATCHED_CODE = 'NO_MATCHING_MODE_FOUND'
_NO_MODE_MATCHED_MSG = 'no mode matched requested params'

_NOW = '2020-07-30T05:00:00+00:00'
_TNOW = datetime.datetime.fromisoformat(_NOW)
_TNOW_NO_OFFSET = datetime.datetime(2020, 7, 30, 5, 0, 0)
_INBETWEEN = '2020-07-29T00:00:00+00:00'
_TINBETWEEN = datetime.datetime.fromisoformat(_INBETWEEN)
_MONTH_AGO = '2020-06-29T00:00:00+00:00'
_TMONTH_AGO = datetime.datetime.fromisoformat(_MONTH_AGO)
_EPOCH = '1970-01-01T00:00:00+00:00'
_TEPOCH = datetime.datetime.fromisoformat(_EPOCH)

_RESET_TO_ORDERS = common.ResetModeRequest(
    supported_display_modes=['orders_type'], reason='low_taximeter_version',
)

_UNSUBSCRIBE_REASONS = {
    'low_taximeter_version': {
        'current_mode_params': {},
        'actions': {
            'send_unsubscribe_notification': {
                'type': 'unsupported_taximeter_version',
            },
        },
    },
}


@pytest.mark.nofilldb()
@pytest.mark.now(_NOW)
@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.parametrize(
    'default_mode, expected_mode, extected_title',
    [
        pytest.param('orders', 'orders', 'За заказы', id='reset to orders'),
        pytest.param(
            'custom_orders',
            'custom_orders',
            'Карточка.Заголовок(default)',
            id='reset to custom_orders',
        ),
    ],
)
async def test_mode_reset(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        taxi_config,
        mockserver,
        mocked_time,
        testpoint,
        pgsql,
        stq,
        driver_authorizer,
        default_mode: str,
        expected_mode: str,
        extected_title: str,
):
    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(profiles={test_profile: driver.Mode('driver_fix')})
    scene.setup(mockserver, mocked_time, driver_authorizer)

    taxi_config.set_values(
        dict(
            DRIVER_MODE_GROUPS={
                'taxi': {
                    'orders_provider': 'taxi',
                    'reset_modes': [default_mode],
                },
            },
            DRIVER_MODE_SUBSCRIPTION_UNSUBSCRIBE_REASONS=_UNSUBSCRIBE_REASONS,
        ),
    )
    await taxi_driver_mode_subscription.invalidate_caches()

    @testpoint('handle-mode-set-testpoint')
    def _handle_mode_set_cpp_testpoint(data):
        pass

    response = await _RESET_TO_ORDERS.post(
        taxi_driver_mode_subscription, driver_profile=test_profile,
    )

    response_code = response.status_code
    response_body = response.json()

    assert response_code == 200
    assert response_body == {
        'active_mode': expected_mode,
        'active_mode_type': 'orders_type',
        'active_since': _NOW,
    }

    assert _handle_mode_set_cpp_testpoint.times_called == 1
    mode_set_data = _handle_mode_set_cpp_testpoint.next_call()['data']
    assert mode_set_data == common.mode_set_testpoint_data(
        test_profile,
        accept_language='ru',
        external_ref='idempotency_key',
        active_since=_NOW,
        mode=expected_mode,
        source=saga_tools.SOURCE_SERVICE_MODE_RESET,
        change_reason='low_taximeter_version',
    )

    assert saga_tools.get_saga_db_data(test_profile, pgsql) == (
        1,
        _TNOW_NO_OFFSET,
        test_profile.park_id(),
        test_profile.profile_id(),
        scene.udid,
        expected_mode,
        _TNOW_NO_OFFSET,
        None,
        'idempotency_key',
        'ru',
        None,
        saga_tools.COMPENSATION_POLICY_FORBID,
        saga_tools.SOURCE_SERVICE_MODE_RESET,
        'low_taximeter_version',
    )


@pytest.mark.nofilldb()
@pytest.mark.now(_NOW)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name='orders', display_mode='unsupported_type',
            ),
            mode_rules.Patch(rule_name='uberdriver'),
            mode_rules.Patch(
                rule_name='no_offers_mode',
                display_mode='unsupported_type',
                offers_group='no_group',
            ),
            mode_rules.Patch(
                rule_name='driver_fix',
                display_mode='driver_fix',
                features={'driver_fix': {}},
            ),
            mode_rules.Patch(
                rule_name='custom_driver_fix',
                display_mode='orders_type',
                features={'driver_fix': {}},
            ),
            mode_rules.Patch(
                rule_name='eda_orders',
                display_mode='eda_type',
                offers_group='eda',
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
@pytest.mark.parametrize(
    'current_mode, default_mode, reset_request, expected_http_code, '
    'expected_code, expected_message',
    [
        pytest.param(
            'eda_orders',
            'orders',
            _RESET_TO_ORDERS,
            400,
            _NO_MODE_MATCHED_CODE,
            _NO_MODE_MATCHED_MSG,
            id='reset from not taxi mode',
        ),
        pytest.param(
            'no_offers_mode',
            'orders',
            _RESET_TO_ORDERS,
            400,
            _NO_MODE_MATCHED_CODE,
            _NO_MODE_MATCHED_MSG,
            id='reset no_offers_mode',
        ),
        pytest.param(
            'uberdriver',
            'orders',
            _RESET_TO_ORDERS,
            400,
            _NO_MODE_MATCHED_CODE,
            _NO_MODE_MATCHED_MSG,
            id='reset uberdriver',
        ),
        pytest.param(
            'orders',
            'driver_fix',
            _RESET_TO_ORDERS,
            400,
            _NO_MODE_MATCHED_CODE,
            _NO_MODE_MATCHED_MSG,
            id='reset to mode with unsupported display_mode',
        ),
        pytest.param(
            'orders',
            'custom_driver_fix',
            _RESET_TO_ORDERS,
            400,
            _NO_MODE_MATCHED_CODE,
            _NO_MODE_MATCHED_MSG,
            id='reset to mode with exclusive features',
        ),
        pytest.param(
            'orders',
            'custom_driver_fix',
            common.ResetModeRequest(
                supported_display_modes=['orders_type'],
                reason='low_taximeter_version',
                language=None,
            ),
            400,
            '400',
            'Missing Accept-Language in header',
            id='reset without accept_language',
        ),
    ],
)
async def test_mode_reset_bad(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        taxi_config,
        mockserver,
        mocked_time,
        stq,
        driver_authorizer,
        current_mode: str,
        default_mode: str,
        reset_request: common.ResetModeRequest,
        expected_code: str,
        expected_http_code: int,
        expected_message: str,
):
    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(profiles={test_profile: driver.Mode(current_mode)})
    scene.setup(mockserver, mocked_time, driver_authorizer)

    taxi_config.set_values(
        dict(
            DRIVER_MODE_GROUPS={
                'taxi': {
                    'orders_provider': 'taxi',
                    'reset_modes': [default_mode],
                },
            },
        ),
    )

    await taxi_driver_mode_subscription.invalidate_caches()

    response = await reset_request.post(
        taxi_driver_mode_subscription, driver_profile=test_profile,
    )

    response_code = response.status_code
    response_body = response.json()

    assert response_code == expected_http_code
    if response_code == 400:
        assert response_body['code'] == expected_code
        assert response_body['message'] == expected_message


@pytest.mark.nofilldb()
@pytest.mark.now(_NOW)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(rule_name='orders', display_mode='orders'),
            mode_rules.Patch(
                rule_name='eda_orders',
                offers_group='eda',
                display_mode='orders',
            ),
            mode_rules.Patch(
                rule_name='lavka_orders',
                offers_group='lavka',
                display_mode='orders',
            ),
            mode_rules.Patch(
                rule_name='lavka_fancy',
                offers_group='lavka',
                display_mode='fancy_type',
            ),
            mode_rules.Patch(
                rule_name='lavka_pedestrian',
                display_mode='2gis',
                offers_group='lavka',
                features={'active_transport': {'type': 'pedestrian'}},
            ),
            mode_rules.Patch(
                rule_name='lavka_bicycle',
                display_mode='strava',
                offers_group='lavka',
                features={'active_transport': {'type': 'bicycle'}},
            ),
            mode_rules.Patch(
                rule_name='lavka_disabled',
                display_mode='orders',
                offers_group='lavka',
                stops_at=_TNOW,
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
@pytest.mark.parametrize(
    'current_mode, reset_request, groups, expected_code, expected_response',
    [
        pytest.param(
            'orders',
            common.ResetModeRequest(
                orders_provider='lavka',
                supported_transport_types=['pedestrian', 'bicycle'],
                reason='import_profile',
            ),
            [
                mode_groups.Group(
                    name='taxi',
                    orders_provider='taxi',
                    reset_modes=['orders'],
                ),
                mode_groups.Group(
                    name='lavka',
                    orders_provider='lavka',
                    reset_modes=[
                        'lavka_bicycle',
                        'lavka_pedestrian',
                        'lavka_orders',
                    ],
                ),
            ],
            200,
            common.build_reset_mode_response('lavka_bicycle', 'strava', _NOW),
            id='orders_into_bicycle_lavka',
        ),
        pytest.param(
            'orders',
            common.ResetModeRequest(
                orders_provider='lavka',
                supported_transport_types=['pedestrian', 'bicycle'],
                reason='import_profile',
            ),
            [
                mode_groups.Group(
                    name='taxi',
                    orders_provider='taxi',
                    reset_modes=['orders'],
                ),
                mode_groups.Group(
                    name='lavka',
                    orders_provider='lavka',
                    reset_modes=[
                        'lavka_pedestrian',
                        'lavka_bicycle',
                        'lavka_orders',
                    ],
                ),
            ],
            200,
            common.build_reset_mode_response('lavka_pedestrian', '2gis', _NOW),
            id='orders_into_pedestrian_(reordered_reset_modes)',
        ),
        pytest.param(
            'orders',
            common.ResetModeRequest(
                orders_provider='lavka',
                supported_transport_types=['pedestrian', 'bicycle'],
                reason='import_profile',
            ),
            [
                mode_groups.Group(
                    name='taxi',
                    orders_provider='taxi',
                    reset_modes=['orders'],
                ),
            ],
            400,
            {
                'code': _NO_MODE_MATCHED_CODE,
                'message': 'no mode group found for lavka orders provider',
            },
            id='no_lavka_mode_group_specified',
        ),
        pytest.param(
            'orders',
            common.ResetModeRequest(
                orders_provider='lavka',
                supported_transport_types=['pedestrian', 'bicycle'],
                reason='import_profile',
            ),
            [
                mode_groups.Group(
                    name='lavka',
                    orders_provider='lavka',
                    reset_modes=['lavka_orders'],
                ),
            ],
            400,
            {'code': _NO_MODE_MATCHED_CODE, 'message': _NO_MODE_MATCHED_MSG},
            id='no_fitting_mode_lavka',
        ),
        pytest.param(
            'lavka_pedestrian',
            common.ResetModeRequest(
                orders_provider='lavka',
                supported_transport_types=['pedestrian', 'bicycle'],
                reason='import_profile',
            ),
            [
                mode_groups.Group(
                    name='lavka',
                    orders_provider='lavka',
                    reset_modes=[
                        'lavka_pedestrian',
                        'lavka_bicycle',
                        'lavka_orders',
                    ],
                ),
            ],
            200,
            common.build_reset_mode_response(
                'lavka_pedestrian', '2gis', _INBETWEEN,
            ),
            id='preserve_pedestrian_mode',
        ),
        pytest.param(
            'orders',
            common.ResetModeRequest(
                orders_provider='lavka', reason='import_profile',
            ),
            [
                mode_groups.Group(
                    name='lavka',
                    orders_provider='lavka',
                    reset_modes=[
                        'lavka_pedestrian',
                        'lavka_bicycle',
                        'lavka_orders',
                    ],
                ),
            ],
            200,
            common.build_reset_mode_response('lavka_orders', 'orders', _NOW),
            id='orders_into_lavka_orders_(no_transport_specified)',
        ),
        pytest.param(
            'lavka_orders',
            common.ResetModeRequest(
                supported_display_modes=['strava'], reason='import_profile',
            ),
            [
                mode_groups.Group(
                    name='lavka',
                    orders_provider='lavka',
                    reset_modes=[
                        'lavka_pedestrian',
                        'lavka_bicycle',
                        'lavka_orders',
                    ],
                ),
            ],
            400,
            {'code': _NO_MODE_MATCHED_CODE, 'message': _NO_MODE_MATCHED_MSG},
            id='orders_into_display_mode_strava_(prohibit_changing_transport)',
        ),
        pytest.param(
            'lavka_fancy',
            common.ResetModeRequest(
                supported_display_modes=['orders'],
                reason='low_taximeter_version',
            ),
            [
                mode_groups.Group(
                    name='taxi',
                    orders_provider='taxi',
                    reset_modes=['orders'],
                ),
                mode_groups.Group(
                    name='eda',
                    orders_provider='eda',
                    reset_modes=['eda_orders'],
                ),
                mode_groups.Group(
                    name='lavka',
                    orders_provider='lavka',
                    reset_modes=[
                        'lavka_pedestrian',
                        'lavka_bicycle',
                        'lavka_orders',
                    ],
                ),
            ],
            200,
            common.build_reset_mode_response('lavka_orders', 'orders', _NOW),
            id='downgrade_display_mode_into_orders_in_same_group',
        ),
        pytest.param(
            'lavka_fancy',
            common.ResetModeRequest(
                supported_display_modes=['orders', 'fancy_type'],
                reason='low_taximeter_version',
            ),
            [
                mode_groups.Group(
                    name='lavka',
                    orders_provider='lavka',
                    reset_modes=['lavka_orders'],
                ),
            ],
            200,
            common.build_reset_mode_response(
                'lavka_fancy', 'fancy_type', _INBETWEEN,
            ),
            id='preserve_current_non_reset_mode_since_it_fits',
        ),
    ],
)
async def test_import_profiles(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        taxi_config,
        mockserver,
        mocked_time,
        stq,
        driver_authorizer,
        current_mode: str,
        reset_request: common.ResetModeRequest,
        groups: List[mode_groups.Group],
        expected_code: int,
        expected_response: Dict[str, str],
):
    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(
        profiles={
            test_profile: driver.Mode(
                work_mode=current_mode, started_at_iso=_INBETWEEN,
            ),
        },
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    taxi_config.set_values(dict(DRIVER_MODE_GROUPS=mode_groups.values(groups)))

    await taxi_driver_mode_subscription.invalidate_caches()

    response = await reset_request.post(
        taxi_driver_mode_subscription, driver_profile=test_profile,
    )

    assert expected_code == response.status_code
    assert expected_response == response.json()


@pytest.mark.nofilldb()
@pytest.mark.now(_NOW)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name='orders',
                display_mode='orders',
                offers_group='taxi',
                starts_at=_TEPOCH,
            ),
            mode_rules.Patch(
                rule_name='orders',
                display_mode='orders_new',
                offers_group='taxi',
                starts_at=_TINBETWEEN,
            ),
            mode_rules.Patch(
                rule_name='eda_stopped',
                display_mode='orders',
                offers_group='eda',
                starts_at=_TEPOCH,
                stops_at=_TMONTH_AGO,
            ),
            mode_rules.Patch(
                rule_name='lavka', display_mode='orders', offers_group='lavka',
            ),
        ],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_GROUPS=mode_groups.values(
        [
            mode_groups.Group(
                name='taxi', orders_provider='taxi', reset_modes=['orders'],
            ),
            mode_groups.Group(
                name='eda', orders_provider='eda', reset_modes=['lavka'],
            ),
            mode_groups.Group(
                name='lavka', orders_provider='lavka', reset_modes=['lavka'],
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'current_mode, reset_request, expected_code, expected_response',
    [
        pytest.param(
            'orders',
            common.ResetModeRequest(
                supported_display_modes=['orders', 'orders_new'],
            ),
            200,
            common.build_reset_mode_response('orders', 'orders', _MONTH_AGO),
        ),
    ],
)
async def test_preserve_current_mode(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        taxi_config,
        mockserver,
        mocked_time,
        stq,
        driver_authorizer,
        current_mode: str,
        reset_request: common.ResetModeRequest,
        expected_code: int,
        expected_response: Dict[str, str],
):
    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(
        profiles={
            test_profile: driver.Mode(
                work_mode=current_mode, started_at_iso=_MONTH_AGO,
            ),
        },
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    await taxi_driver_mode_subscription.invalidate_caches()

    response = await reset_request.post(
        taxi_driver_mode_subscription, driver_profile=test_profile,
    )

    assert expected_code == response.status_code
    assert expected_response == response.json()
