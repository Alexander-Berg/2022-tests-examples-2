# flake8: noqa
from typing import Dict

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scenario

DRIVER_FIX_SETTINGS = {'rule_id': 'id', 'shift_close_time': '00:00:00+03:00'}

_NOW = '2019-05-01T05:00:00+00:00'


@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_CHECK_NOT_IN_REPOSITION={
        'modes': [],
        'tanker_keys': {
            '__default__': {
                'disable_button': 'offer_screen.button_in_reposition',
                'message_title': (
                    'set_by_session.error.CHECK_NOT_IN_REPOSITION_FAILED.title'
                ),
                'message_body': 'set_by_session.error.CHECK_NOT_IN_REPOSITION_FAILED.message',
            },
        },
    },
)
@pytest.mark.parametrize(
    'reposition_config',
    [
        pytest.param(
            'with_reposition',
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        patches=[
                            mode_rules.Patch(
                                'driver_fix',
                                features={
                                    'driver_fix': {},
                                    'reposition': {'profile': 'driver_fix'},
                                },
                            ),
                        ],
                    ),
                ),
            ],
        ),
        pytest.param('without_reposition'),
    ],
)
@pytest.mark.parametrize(
    'current, desired, mode_settings, in_reposition, expected_success_configs',
    [
        pytest.param(
            'orders',
            'driver_fix',
            DRIVER_FIX_SETTINGS,
            False,
            {'with_reposition': True, 'without_reposition': True},
            id='orders_to_driver_fix',
        ),
        pytest.param(
            'orders',
            'driver_fix',
            DRIVER_FIX_SETTINGS,
            True,
            {'with_reposition': False, 'without_reposition': True},
            id='orders_to_driver_fix_in_reposition',
        ),
        pytest.param(
            'orders',
            'orders',
            None,
            False,
            {'with_reposition': True, 'without_reposition': True},
            id='orders_orders',
        ),
        pytest.param(
            'orders',
            'orders',
            None,
            True,
            {'with_reposition': True, 'without_reposition': True},
            id='orders_to_orders_in_reposition',
        ),
        pytest.param(
            'driver_fix',
            'orders',
            None,
            False,
            {'with_reposition': True, 'without_reposition': True},
            id='driver_fix_to_orders',
        ),
        pytest.param(
            'driver_fix',
            'orders',
            None,
            True,
            {'with_reposition': False, 'without_reposition': True},
            id='driver_fix_to_orders_in_reposition',
        ),
        pytest.param(
            'driver_fix',
            'driver_fix',
            DRIVER_FIX_SETTINGS,
            True,
            {'with_reposition': False, 'without_reposition': True},
            id='driver_fix_to_driver_fix_in_reposition',
        ),
        pytest.param(
            'driver_fix',
            'driver_fix',
            DRIVER_FIX_SETTINGS,
            False,
            {'with_reposition': True, 'without_reposition': True},
            id='driver_fix_to_driver_fix',
        ),
    ],
)
@pytest.mark.parametrize(
    'set_by_session',
    (
        pytest.param(True, id='set_by_session'),
        pytest.param(False, id='set_by_tvm'),
    ),
)
@pytest.mark.now('2019-11-14T04:01:00+03:00')
async def test_check_not_in_reposition(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        taxi_config,
        mode_settings,
        mocked_time,
        current: str,
        desired: str,
        in_reposition: bool,
        reposition_config: str,
        expected_success_configs: Dict[str, bool],
        set_by_session: bool,
):
    success = not set_by_session or expected_success_configs[reposition_config]

    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(profiles={test_profile: driver.Mode(current)})
    scene.setup(mockserver, mocked_time, driver_authorizer)

    @mockserver.json_handler('/reposition-api/v1/service/state')
    def _v1_service_state(request):
        if in_reposition:
            return {
                'active': True,
                'has_session': True,
                'mode': 'SurgeCharge',
                'point': [37.6548, 55.6434],
                'submode': '',
            }
        return {'has_session': False}

    @mockserver.json_handler('/tags/v1/upload')
    def _v1_upload(request):
        return {'status': 'ok'}

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode=desired,
        mode_settings=mode_settings,
        set_by_session=set_by_session,
    )

    if success:
        assert response.status_code == 200
    else:
        assert response.status_code == 423
        response_body = response.json()
        if set_by_session:
            assert response_body == {
                'code': 'CHECK_NOT_IN_REPOSITION_FAILED',
                'localized_message': 'Вы сейчас в состоянии перемещения',
                'localized_message_title': 'В состоянии перемещения',
            }
        else:
            assert response_body['code'] == 'LOCKED'
            assert not response_body['message']
        assert 'details' not in response_body
