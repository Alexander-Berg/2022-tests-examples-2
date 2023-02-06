import json
from typing import Any
from typing import Dict
from typing import List

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scenario

DRIVER_FIX_SETTINGS = {'rule_id': 'id', 'shift_close_time': '00:00:00+03:00'}

_NOW = '2019-05-01T05:00:00+00:00'

_DRIVER_MODE_RULES = mode_rules.default_mode_rules()

_ON_ORDER = {
    'statuses': [
        {
            'status': 'busy',
            'park_id': 'dbid0',
            'driver_id': 'uuid0',
            'orders': [{'id': 'order_id', 'status': 'transporting'}],
        },
    ],
}

_WITHOUT_ORDER = {
    'statuses': [
        {
            'status': 'online',
            'park_id': 'dbid0',
            'driver_id': 'uuid0',
            'orders': [],
        },
    ],
}


@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.parametrize(
    'config',
    [
        pytest.param(
            0,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_ENABLE_CHECK_NOT_ON_ORDER=True,
                ),
            ],
        ),
        pytest.param(
            1,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_ENABLE_CHECK_NOT_ON_ORDER=False,
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'docs, status_response, expected_successes',
    [
        pytest.param(
            [
                ('2019-11-14T04:00:00+03:00', 'driver_fix'),
                ('2019-11-14T03:02:00+03:00', 'orders'),
            ],
            _WITHOUT_ORDER,
            [True, True],
        ),
        pytest.param(
            [
                ('2019-11-14T04:00:00+03:00', 'driver_fix'),
                ('2019-11-14T03:02:00+03:00', 'orders'),
            ],
            _ON_ORDER,
            [False, True],
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
async def test_mode_set_validation_not_on_order(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        taxi_config,
        config,
        docs,
        mocked_time,
        expected_successes: List[bool],
        status_response: Dict[str, Any],
        set_by_session: bool,
):
    success = not set_by_session or expected_successes[config]

    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(profiles={test_profile: driver.Mode('orders')})
    scene.setup(mockserver, mocked_time, driver_authorizer)

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _v2_statuses(request):
        return status_response

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        documents = []

        for occured, mode in docs:
            documents.append(
                {
                    'kind': 'driver_mode_subscription',
                    'external_event_ref': 'idempotency',
                    'event_at': occured,
                    'data': {
                        'driver': {
                            'park_id': 'park_id_0',
                            'driver_profile_id': 'uuid',
                        },
                        'mode': mode,
                        'settings': {
                            'rule_id': 'some_id',
                            'shift_close_time': '00:00',
                        },
                    },
                },
            )

        return {'docs': documents, 'cursor': common.MODE_HISTORY_CURSOR}

    @mockserver.json_handler('/tags/v1/upload')
    def _v1_upload(request):
        data = json.loads(request.get_data())
        assert data['tags']
        return {'status': 'ok'}

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode='driver_fix',
        mode_settings=DRIVER_FIX_SETTINGS,
        set_by_session=set_by_session,
    )

    if success:
        assert response.status_code == 200
    else:
        assert response.status_code == 423
        response_body = response.json()
        if set_by_session:
            assert response_body == {
                'code': 'CHECK_NOT_ON_ORDER_FAILED',
                'localized_message': (
                    'Завершите заказ прежде чем изменять режим заработка.'
                ),
                'localized_message_title': 'Вы на заказе',
            }
        else:
            assert response_body['code'] == 'LOCKED'
        assert 'details' not in response_body


@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.config(DRIVER_MODE_SUBSCRIPTION_ENABLE_CHECK_NOT_ON_ORDER=True)
@pytest.mark.parametrize(
    'set_by_session',
    (
        pytest.param(True, id='set_by_session'),
        pytest.param(False, id='set_by_tvm'),
    ),
)
@pytest.mark.now('2019-11-14T04:01:00+03:00')
async def test_mode_set_validation_not_on_order_unknown_status(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        taxi_config,
        mocked_time,
        set_by_session: bool,
):
    test_profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene(profiles={test_profile: driver.Mode('orders')})
    scene.setup(mockserver, mocked_time, driver_authorizer)

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _v2_statuses(request):
        return {'statuses': []}

    response = await common.set_mode(
        taxi_driver_mode_subscription,
        profile=test_profile,
        work_mode='driver_fix',
        mode_settings=DRIVER_FIX_SETTINGS,
        set_by_session=set_by_session,
    )

    if set_by_session:
        assert response.status_code == 503
    else:
        assert response.status_code == 200
