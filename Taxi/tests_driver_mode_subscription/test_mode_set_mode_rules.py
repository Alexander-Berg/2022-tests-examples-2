import datetime
import enum
from typing import Any
from typing import Dict
from typing import Optional


import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scenario

_DRIVER_FIX_SETTINGS = {'rule_id': 'id', 'shift_close_time': '00:00:00+03:00'}

_INVALID_MODE_SETTINGS = {'mode': 'settings'}
_NOW = '2019-05-01T05:00:00+00:00'


def _get_bad_request_error_code(
        expected_error_code: str, is_set_by_session_call: bool,
):
    if is_set_by_session_call:
        return 'BAD REQUEST'

    return expected_error_code


def _check_errors(
        response_body: Dict[str, Any],
        expected_code: str,
        is_set_by_session=False,
):
    assert response_body['code'] == _get_bad_request_error_code(
        expected_code, is_set_by_session,
    )
    if is_set_by_session:
        assert not response_body['message']
        assert 'details' not in response_body


_DRIVER_FIX_DEPECHE_MODE = 'depeche_mode'
_DRIVER_FIX_WITHOUT_FEATURE = 'driver_fix_without_feature'
_ORDERS_WITH_DRIVER_FIX_FEATURE = 'orders_with_driver_fix_feature'
_ORDERS_WITH_DRIVER_FIX_UI = 'orders_with_driver_fix_ui'
_DRIVER_FIX_INACTIVE = 'driver_fix_inactive'


def _append_wrong_driver_fix_modes():
    return mode_rules.patched(
        patches=[
            mode_rules.Patch(
                rule_name=_DRIVER_FIX_WITHOUT_FEATURE,
                billing_mode='driver_fix',
                billing_mode_rule='driver_fix_type',
            ),
            mode_rules.Patch(
                rule_name=_DRIVER_FIX_DEPECHE_MODE,
                billing_mode='driver_fix',
                billing_mode_rule='depeche_mode_type',
                features={'driver_fix': {}},
            ),
            mode_rules.Patch(
                rule_name=_ORDERS_WITH_DRIVER_FIX_UI,
                display_mode='driver_fix',
            ),
            mode_rules.Patch(
                rule_name=_ORDERS_WITH_DRIVER_FIX_FEATURE,
                billing_mode='orders',
                billing_mode_rule='orders_type',
                features={'driver_fix': {}},
            ),
            mode_rules.Patch(
                rule_name=_DRIVER_FIX_INACTIVE,
                billing_mode='driver_fix',
                billing_mode_rule='depeche_mode_type',
                features={'driver_fix': {}},
                stops_at=datetime.datetime.fromisoformat(
                    '2018-05-01T05:00:00+00:00',
                ),
            ),
        ],
    )


_WRONG_DRIVER_FIX_RULES = _append_wrong_driver_fix_modes()


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_ENABLE_SAME_MODE_OPTIMIZATION=True,
)
@pytest.mark.now(_NOW)
@pytest.mark.parametrize(
    'set_by_session',
    (
        pytest.param(True, id='set_by_session'),
        pytest.param(False, id='set_by_tvm'),
    ),
)
@pytest.mark.parametrize(
    'mode_id, mode_settings, expected_code, expected_code_str',
    (
        pytest.param(
            'driver_fix',
            _DRIVER_FIX_SETTINGS,
            200,
            None,
            id='driver_fix_correct',
        ),
        pytest.param('custom_orders', None, 200, None, id='custom_orders'),
        pytest.param(
            'orders',
            {'key': 'value'},
            400,
            'WRONG_MODE_SETTINGS',
            id='orders with mode_settings',
        ),
        pytest.param(
            'driver_fix',
            {'fake_settings': 0},
            400,
            'WRONG_MODE_SETTINGS',
            id='driver_fix_fake_settings',
        ),
        pytest.param(
            'dms_unsupported_mode',
            None,
            400,
            'WRONG_MODE_RULE',
            id='unsupported_mode',
        ),
        pytest.param(
            _DRIVER_FIX_INACTIVE,
            _DRIVER_FIX_SETTINGS,
            400,
            'WRONG_MODE_RULE',
            id='inactive_mode',
        ),
        pytest.param(
            _DRIVER_FIX_WITHOUT_FEATURE,
            _DRIVER_FIX_SETTINGS,
            400,
            'WRONG_MODE_SETTINGS',
            id='driver_fix_mode_without_feature_specified',
        ),
        pytest.param(
            _ORDERS_WITH_DRIVER_FIX_FEATURE,
            _DRIVER_FIX_SETTINGS,
            400,
            'WRONG_MODE_RULE',
            id='orders_with_driver_fix_feature_specified',
        ),
        pytest.param(
            _ORDERS_WITH_DRIVER_FIX_UI,
            None,
            400,
            'WRONG_MODE_RULE',
            id='driver_fix_ui_without_driver_fix_feature',
        ),
        pytest.param(
            _DRIVER_FIX_DEPECHE_MODE,
            _DRIVER_FIX_SETTINGS,
            200,
            None,
            id='depeche_mode_with_proper_driver_fix_modes',
        ),
    ),
)
@pytest.mark.mode_rules(rules=_WRONG_DRIVER_FIX_RULES)
async def test_mode_set_driver_fix(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        taxi_config,
        mockserver,
        mocked_time,
        stq,
        driver_authorizer,
        set_by_session: bool,
        mode_id: str,
        mode_settings: Dict[str, Any],
        expected_code: int,
        expected_code_str: Optional[str],
):
    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(profiles={test_profile: driver.Mode('orders')})
    scene.setup(mockserver, mocked_time, driver_authorizer)

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode=mode_id,
        mode_settings=mode_settings,
        set_by_session=set_by_session,
    )

    assert response.status_code == expected_code

    response_body = response.json()
    if expected_code != 200:
        assert expected_code_str
        _check_errors(
            response_body, expected_code_str, is_set_by_session=set_by_session,
        )
    else:
        assert not expected_code_str
        display_mode = mode_rules.find_display_mode(
            mode_rules=_WRONG_DRIVER_FIX_RULES,
            mode_name=mode_id,
            time_point=datetime.datetime.fromisoformat(_NOW),
        )
        assert response_body == common.build_set_mode_result(
            set_by_session, mode_id, display_mode, '2019-05-01T05:00:00+00:00',
        )


@pytest.mark.now(_NOW)
@pytest.mark.parametrize(
    'set_by_session, prev_mode, next_mode, expected_code, expected_code_str',
    (
        pytest.param(
            False, 'uberdriver', 'custom_orders', 200, None, id='set_by_tvm',
        ),
        pytest.param(
            True,
            'uberdriver',
            'orders',
            400,
            'WRONG_MODE_RULE',
            id='set_by_session',
        ),
        pytest.param(
            True,
            'orders',
            'custom_orders',
            400,
            'WRONG_MODE_RULE',
            id='set_by_session',
        ),
    ),
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(rule_name='uberdriver'),
            mode_rules.Patch(
                rule_name='custom_orders', offers_group='no_group',
            ),
        ],
    ),
)
async def test_mode_set_mode_without_offers(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        taxi_config,
        mockserver,
        mocked_time,
        driver_authorizer,
        set_by_session: bool,
        prev_mode: str,
        next_mode: str,
        expected_code: int,
        expected_code_str: Optional[str],
):
    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(profiles={test_profile: driver.Mode(prev_mode)})
    scene.setup(mockserver, mocked_time, driver_authorizer)

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode=next_mode,
        mode_settings=None,
        set_by_session=set_by_session,
    )

    assert response.status_code == expected_code

    response_body = response.json()
    if response.status_code != 200:
        assert expected_code_str
        _check_errors(
            response_body, expected_code_str, is_set_by_session=set_by_session,
        )
    else:
        assert response_body == common.build_set_mode_result(
            set_by_session,
            next_mode,
            'orders_type',
            '2019-05-01T05:00:00+00:00',
        )


@pytest.mark.now(_NOW)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(rule_name='orders', offers_group='taxi'),
            mode_rules.Patch(rule_name='custom_orders', offers_group='taxi'),
            mode_rules.Patch(rule_name='lavka_orders', offers_group='lavka'),
        ],
    ),
)
@pytest.mark.parametrize(
    'set_by_session, prev_mode, next_mode, expected_code, expected_code_str',
    (
        pytest.param(
            False,
            'custom_orders',
            'lavka_orders',
            200,
            None,
            id='set_by_tvm different offers group',
        ),
        pytest.param(
            True,
            'custom_orders',
            'orders',
            200,
            None,
            id='set_by_session same offers group',
        ),
        pytest.param(
            True,
            'custom_orders',
            'lavka_orders',
            400,
            'WRONG_MODE_RULE',
            id='set_by_session different offers group',
        ),
    ),
)
async def test_mode_set_mode_offers_group(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        taxi_config,
        mockserver,
        mocked_time,
        driver_authorizer,
        set_by_session: bool,
        prev_mode: str,
        next_mode: str,
        expected_code: int,
        expected_code_str: Optional[str],
):
    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(profiles={test_profile: driver.Mode(prev_mode)})
    scene.setup(mockserver, mocked_time, driver_authorizer)

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode=next_mode,
        mode_settings=None,
        set_by_session=set_by_session,
    )

    assert response.status_code == expected_code

    response_body = response.json()
    if response.status_code != 200:
        assert expected_code_str
        _check_errors(
            response_body, expected_code_str, is_set_by_session=set_by_session,
        )
    else:
        assert response_body == common.build_set_mode_result(
            set_by_session,
            next_mode,
            'orders_type',
            '2019-05-01T05:00:00+00:00',
        )


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_ENABLE_SAME_MODE_OPTIMIZATION=True,
)
@pytest.mark.now(_NOW)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name='custom_orders',
                starts_at=datetime.datetime.fromisoformat(
                    '2018-05-01T08:00:00+00:00',
                ),
            ),
            mode_rules.Patch(
                rule_name='custom_orders',
                starts_at=datetime.datetime.fromisoformat(
                    '2019-05-01T08:00:00+00:00',
                ),
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'set_by_session',
    (
        pytest.param(True, id='set_by_session'),
        pytest.param(False, id='set_by_tvm'),
    ),
)
@pytest.mark.parametrize(
    'event_time, target_mode, target_mode_settings, current_mode, '
    'current_mode_settings, expect_change',
    (
        pytest.param(
            datetime.datetime(2019, 5, 1, 5, 0, 0),
            'custom_orders',
            None,
            'custom_orders',
            None,
            False,
            id='do nothing on same version',
        ),
        pytest.param(
            datetime.datetime(2019, 5, 1, 8, 0, 0),
            'custom_orders',
            None,
            'custom_orders',
            None,
            True,
            id='change mode with different version',
        ),
        pytest.param(
            datetime.datetime(2019, 5, 1, 5, 0, 0),
            'driver_fix',
            {'rule_id': 'id1', 'shift_close_time': '00:00'},
            'driver_fix',
            {'rule_id': 'id2', 'shift_close_time': '00:00'},
            True,
            id='change mode with mode_settings',
        ),
    ),
)
async def test_mode_set_same_mode(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        taxi_config,
        mockserver,
        testpoint,
        mocked_time,
        driver_authorizer,
        set_by_session: bool,
        event_time: datetime.datetime,
        target_mode: str,
        target_mode_settings: Optional[Dict[str, str]],
        current_mode: str,
        current_mode_settings: Optional[Dict[str, str]],
        expect_change: bool,
):
    _prev_event_time = datetime.datetime(2019, 5, 1, 4, 0, 0)
    mocked_time.set(event_time)

    @testpoint('handle-mode-set-testpoint')
    def _handle_mode_set_cpp_testpoint(data):
        pass

    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(
        profiles={
            test_profile: driver.Mode(
                current_mode,
                started_at=_prev_event_time,
                mode_settings=current_mode_settings,
            ),
        },
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode=target_mode,
        mode_settings=target_mode_settings,
        set_by_session=set_by_session,
    )

    assert response.status_code == 200

    if expect_change:
        assert _handle_mode_set_cpp_testpoint.times_called == 1
        expect_active_since = event_time
    else:
        assert _handle_mode_set_cpp_testpoint.times_called == 0
        expect_active_since = _prev_event_time

    assert response.json() == common.build_set_mode_result(
        set_by_session,
        target_mode,
        'driver_fix_type' if target_mode == 'driver_fix' else 'orders_type',
        expect_active_since.strftime('%Y-%m-%dT%H:%M:%S+00:00'),
    )


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[
            mode_rules.Patch(
                rule_name='orders_display_profile',
                billing_mode='orders',
                billing_mode_rule='orders_type',
                display_profile='usual_orders',
            ),
            mode_rules.Patch(
                rule_name='orders_no_display_profile',
                billing_mode='orders',
                billing_mode_rule='orders_type',
            ),
        ],
    ),
)
@pytest.mark.experiments3(filename='test_feature_toggles.json')
@pytest.mark.experiments3(filename='test_taximeter_polling_policy.json')
@pytest.mark.parametrize(
    'work_mode, expected_config_clause',
    [
        ('orders_display_profile', 'display_profile_passed'),
        ('orders_no_display_profile', 'work_mode_passed'),
    ],
)
@pytest.mark.now(_NOW)
async def test_feature_toggles(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        driver_authorizer,
        work_mode: str,
        expected_config_clause: str,
):
    test_profile = driver.Profile('dbid0_uuid0')
    _prev_event_time = datetime.datetime(2019, 5, 1, 4, 0, 0)
    mocked_time.set(_prev_event_time)
    scene = scenario.Scene(
        profiles={
            test_profile: driver.Mode(
                'custom_orders', started_at=_prev_event_time,
            ),
        },
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode=work_mode,
        mode_settings=None,
        set_by_session=True,
    )
    assert response.status_code == 200

    assert response.json() == common.build_set_mode_result(
        True,
        work_mode,
        'orders_type',
        _prev_event_time.strftime('%Y-%m-%dT%H:%M:%S+00:00'),
        {'clause': expected_config_clause},
        {'polling_policy': expected_config_clause},
    )


class ModeSettingsType(enum.Enum):
    NONE = 'none'
    VALID = 'valid'
    INVALID = 'invalid'


@pytest.mark.now(_NOW)
@pytest.mark.parametrize(
    'set_by_session',
    (
        pytest.param(True, id='set_by_session'),
        pytest.param(False, id='set_by_tvm'),
    ),
)
@pytest.mark.parametrize(
    'provided_mode_settings, expected_http_code',
    [
        pytest.param(ModeSettingsType.NONE, 400, id='no_settings'),
        pytest.param(ModeSettingsType.VALID, 200, id='valid_settings'),
        pytest.param(ModeSettingsType.INVALID, 400, id='invalid_settings'),
    ],
)
@pytest.mark.parametrize(
    'work_mode, valid_mode_settings',
    (
        pytest.param('driver_fix', _DRIVER_FIX_SETTINGS, id='driver_fix'),
        # TODO use geobooking settings after EFFICIENCYDEV-12820
        pytest.param('geobooking', _DRIVER_FIX_SETTINGS, id='geobooking'),
    ),
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[mode_rules.Patch('geobooking', features={'geobooking': {}})],
    ),
)
async def test_mode_set_check_mode_settings(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        taxi_config,
        mockserver,
        mocked_time,
        stq,
        driver_authorizer,
        set_by_session: bool,
        work_mode: str,
        valid_mode_settings: Dict[str, Any],
        provided_mode_settings: ModeSettingsType,
        expected_http_code: int,
):
    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(profiles={test_profile: driver.Mode('orders')})
    scene.setup(mockserver, mocked_time, driver_authorizer)

    @mockserver.json_handler('/driver-fix/v1/view/rule_key_params')
    async def _mock_view_offer(request):
        return {
            'rules': [
                {
                    'rule_id': 'id',
                    'key_params': {
                        'tariff_zone': 'next_zone',
                        'subvention_geoarea': 'next_area',
                        'tag': 'next_tag',
                    },
                },
            ],
        }

    mode_settings = None
    if provided_mode_settings == ModeSettingsType.VALID:
        mode_settings = valid_mode_settings
    elif provided_mode_settings == ModeSettingsType.INVALID:
        mode_settings = _INVALID_MODE_SETTINGS

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode=work_mode,
        mode_settings=mode_settings,
        set_by_session=set_by_session,
    )

    assert response.status_code == expected_http_code
