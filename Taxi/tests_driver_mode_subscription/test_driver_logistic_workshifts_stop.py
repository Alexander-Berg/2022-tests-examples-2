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

_PARK_ID = 'parkid0'
_DRIVER_ID = 'uuid0'
_ORDERS_RULE_ID = 'a883a23977484000b870f0cfcc84e1f9'
_LOGISTIC_WORKSHIFTS_RULE_ID = 'e65516264faa4d2ca52fea538cb75bd1'
_LOGISTIC_WORKSHIFTS = 'logistic_workshifts'
_LOGISTIC_WORKSHIFTS_ACTUAL_MODE_SETTINGS_1 = {
    'slot_id': 'af31c824-066d-46df-981f-a8dc431d64e8',
    'rule_version': 43,
}
_LOGISTIC_WORKSHIFTS_MODE_SETTINGS_1 = {
    'logistic_offer_identity': {
        'slot_id': 'af31c824-066d-46df-981f-a8dc431d64e8',
        'rule_version': 43,
    },
}
_LOGISTIC_WORKSHIFTS_MODE_SETTINGS_2 = {
    'logistic_offer_identity': {
        'slot_id': 'af31c824-066d-46df-981f-a8dc431d64e8',
        'rule_version': 42,
    },
}
_CANCELATION_OFFER = {
    'logistic_cancelation_offer': {
        'fine_value': {'currency_code': 'RUB', 'value': '42'},
    },
}


@pytest.fixture(name='lsc_check_cancelation_offer')
def _mock_lsc_check_cancelation_offer(mockserver):
    @mockserver.json_handler(
        '/logistic-supply-conductor/internal/v1/'
        'offer/reservation/check-cancellation',
    )
    async def mock_check_cancelation_offer(request):
        return {}

    return mock_check_cancelation_offer


async def logistic_workshift_stop(
        taxi_driver_mode_subscription,
        current_rule_id: str,
        current_mode_settings: Dict[str, Any],
        cancellation_offer: Dict[str, Any],
        park_id: str,
        driver_profile_id: str,
        idempotency_token: Optional[str] = None,
):
    params: Dict[str, Any] = {
        'mode_rule_id': current_rule_id,
        'mode_rule_settings': current_mode_settings,
        'cancellation_offer': cancellation_offer,
    }

    headers = {
        'Accept-Language': 'ru',
        'Timezone': 'Europe/Moscow',
        'User-Agent': 'Taximeter 8.80 (562)',
        'X-Idempotency-Token': 'idempotency_key',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': driver_profile_id,
        'X-Request-Application-Version': '8.80 (562)',
        'X-Request-Application': 'taximeter',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'X-Ya-Service-Ticket': common.MOCK_TICKET,
    }

    if idempotency_token is not None:
        headers['X-Idempotency-Token'] = idempotency_token

    return await taxi_driver_mode_subscription.post(
        'driver/v1/logistic-workshifts/stop', json=params, headers=headers,
    )


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=_LOGISTIC_WORKSHIFTS,
                rule_id=_LOGISTIC_WORKSHIFTS_RULE_ID,
                display_mode=_LOGISTIC_WORKSHIFTS,
                features={_LOGISTIC_WORKSHIFTS: {}},
            ),
        ],
    ),
)
@pytest.mark.now('2020-05-05T13:01:00+03:00')
async def test_driver_mode_reset_unsubscribe_logistic_workshifts(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        driver_authorizer,
        mode_rules_data,
        mode_geography_defaults,
        lsc_check_cancelation_offer,
        pgsql,
):
    profile = driver.Profile(dbid_uuid=f'{_PARK_ID}_{_DRIVER_ID}')
    scene = scenario.Scene(
        profiles={
            profile: driver.Mode(
                _LOGISTIC_WORKSHIFTS,
                mode_settings=_LOGISTIC_WORKSHIFTS_ACTUAL_MODE_SETTINGS_1,
            ),
        },
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    response = await logistic_workshift_stop(
        taxi_driver_mode_subscription,
        _LOGISTIC_WORKSHIFTS_RULE_ID,
        _LOGISTIC_WORKSHIFTS_MODE_SETTINGS_1,
        _CANCELATION_OFFER,
        _PARK_ID,
        _DRIVER_ID,
    )

    assert response.status_code == 200
    assert response.text == ''

    saga_data = list(saga_tools.get_saga_db_data(profile, pgsql))
    saga_data[8] = 'idempotency_key'  # random uuid

    assert saga_data == [
        1,
        datetime.datetime(2020, 5, 5, 10, 1),
        profile.park_id(),
        profile.profile_id(),
        'unique-driver-id',
        'orders',
        datetime.datetime(2020, 5, 5, 10, 1),
        None,
        'idempotency_key',
        'ru',
        None,
        saga_tools.COMPENSATION_POLICY_FORBID,
        saga_tools.SOURCE_LOGISTIC_WORKSHIFT_STOP,
        'manual_mode_change',
    ]

    assert lsc_check_cancelation_offer.has_calls
    lsc_request = lsc_check_cancelation_offer.next_call()['request'].json
    assert lsc_request == {
        'cancellation_offer': {
            'fine_value': {'currency_code': 'RUB', 'value': '42'},
        },
        'contractor_id': {'driver_profile_id': 'uuid0', 'park_id': 'parkid0'},
        'actual_offer': {
            'slot_id': 'af31c824-066d-46df-981f-a8dc431d64e8',
            'rule_version': 43,
        },
        'last_accepted_offer': {
            'slot_id': 'af31c824-066d-46df-981f-a8dc431d64e8',
            'rule_version': 43,
        },
    }


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=_LOGISTIC_WORKSHIFTS,
                rule_id=_LOGISTIC_WORKSHIFTS_RULE_ID,
                display_mode=_LOGISTIC_WORKSHIFTS,
                features={_LOGISTIC_WORKSHIFTS: {}},
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'current_mode_settings, client_mode_rule_id, '
    'client_mode_settings, expected_code',
    [
        pytest.param(
            _LOGISTIC_WORKSHIFTS_ACTUAL_MODE_SETTINGS_1,
            _ORDERS_RULE_ID,
            _LOGISTIC_WORKSHIFTS_MODE_SETTINGS_1,
            409,
            id='wrong_rule_id',
        ),
        pytest.param(
            _LOGISTIC_WORKSHIFTS_ACTUAL_MODE_SETTINGS_1,
            _LOGISTIC_WORKSHIFTS_RULE_ID,
            _LOGISTIC_WORKSHIFTS_MODE_SETTINGS_2,
            409,
            id='wrong_mode_settings',
        ),
        pytest.param(
            None,
            _LOGISTIC_WORKSHIFTS_RULE_ID,
            _LOGISTIC_WORKSHIFTS_MODE_SETTINGS_1,
            409,
            id='redundant_mode_settings',
        ),
        pytest.param(
            _LOGISTIC_WORKSHIFTS_ACTUAL_MODE_SETTINGS_1,
            _LOGISTIC_WORKSHIFTS_RULE_ID,
            _LOGISTIC_WORKSHIFTS_MODE_SETTINGS_1,
            200,
            id='ok_equal_mode_settings',
        ),
    ],
)
@pytest.mark.now('2020-05-05T13:01:00+03:00')
async def test_driver_mode_reset_unsubscribe_conflict(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        driver_authorizer,
        mode_rules_data,
        mode_geography_defaults,
        lsc_check_cancelation_offer,
        current_mode_settings: Optional[Dict[str, Any]],
        client_mode_rule_id: str,
        client_mode_settings: Dict[str, Any],
        expected_code: int,
):
    profile = driver.Profile(dbid_uuid=f'{_PARK_ID}_{_DRIVER_ID}')
    scene = scenario.Scene(
        profiles={
            profile: driver.Mode(
                _LOGISTIC_WORKSHIFTS, mode_settings=current_mode_settings,
            ),
        },
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    response = await logistic_workshift_stop(
        taxi_driver_mode_subscription,
        client_mode_rule_id,
        client_mode_settings,
        _CANCELATION_OFFER,
        _PARK_ID,
        _DRIVER_ID,
    )

    assert response.status_code == expected_code


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            # no logistic_workshifts feature
            mode_rules.Patch(
                rule_name=_LOGISTIC_WORKSHIFTS,
                rule_id=_LOGISTIC_WORKSHIFTS_RULE_ID,
                display_mode=_LOGISTIC_WORKSHIFTS,
            ),
        ],
    ),
)
@pytest.mark.now('2020-05-05T13:01:00+03:00')
async def test_driver_mode_reset_preserve_mode(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        driver_authorizer,
        mode_rules_data,
        mode_geography_defaults,
        lsc_check_cancelation_offer,
):
    profile = driver.Profile(dbid_uuid=f'{_PARK_ID}_{_DRIVER_ID}')
    scene = scenario.Scene(
        profiles={
            profile: driver.Mode(
                _LOGISTIC_WORKSHIFTS,
                mode_settings=_LOGISTIC_WORKSHIFTS_ACTUAL_MODE_SETTINGS_1,
            ),
        },
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    response = await logistic_workshift_stop(
        taxi_driver_mode_subscription,
        _LOGISTIC_WORKSHIFTS_RULE_ID,
        _LOGISTIC_WORKSHIFTS_MODE_SETTINGS_1,
        _CANCELATION_OFFER,
        _PARK_ID,
        _DRIVER_ID,
    )

    assert response.status_code == 200


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=_LOGISTIC_WORKSHIFTS,
                rule_id=_LOGISTIC_WORKSHIFTS_RULE_ID,
                display_mode=_LOGISTIC_WORKSHIFTS,
                features={_LOGISTIC_WORKSHIFTS: {}},
            ),
        ],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_GROUPS={
        'taxi': {
            'orders_provider': 'taxi',
            'reset_modes': [_LOGISTIC_WORKSHIFTS],
        },
    },
)
@pytest.mark.now('2020-05-05T13:01:00+03:00')
async def test_driver_mode_reset_mode_not_found(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        driver_authorizer,
        mode_rules_data,
        mode_geography_defaults,
        lsc_check_cancelation_offer,
):
    profile = driver.Profile(dbid_uuid=f'{_PARK_ID}_{_DRIVER_ID}')
    scene = scenario.Scene(
        profiles={
            profile: driver.Mode(
                _LOGISTIC_WORKSHIFTS,
                mode_settings=_LOGISTIC_WORKSHIFTS_ACTUAL_MODE_SETTINGS_1,
            ),
        },
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    response = await logistic_workshift_stop(
        taxi_driver_mode_subscription,
        _LOGISTIC_WORKSHIFTS_RULE_ID,
        _LOGISTIC_WORKSHIFTS_MODE_SETTINGS_1,
        _CANCELATION_OFFER,
        _PARK_ID,
        _DRIVER_ID,
    )

    assert response.status_code == 400

    assert response.json() == {'code': '400', 'message': ''}


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_BLOCKING_TAGS={
        '__default__': {
            'disable_button': 'offer_card.blocked.freeze.button',
            'message_title': 'offer_card.blocked.freeze.title',
            'message_body': 'offer_card.blocked.body',
        },
    },
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=_LOGISTIC_WORKSHIFTS,
                rule_id=_LOGISTIC_WORKSHIFTS_RULE_ID,
                display_mode=_LOGISTIC_WORKSHIFTS,
                features={_LOGISTIC_WORKSHIFTS: {}, 'driver_fix': {}},
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'expected_code, expected_error_code, expected_message, '
    'expected_localized_title, expected_localized_message',
    [
        pytest.param(
            200,
            None,
            None,
            None,
            None,
            id='ignore_tags_check',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_RULES_BLOCKING_TAGS={
                        'orders': {'tags': ['frauder']},
                    },
                ),
            ],
        ),
        pytest.param(
            409,
            'CHECK_NOT_ON_ORDER_FAILED',
            'is on the order right now',
            'Вы на заказе',
            'Завершите заказ, прежде чем менять статус смены.',
            id='on_order',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_ENABLE_CHECK_NOT_ON_ORDER=True,
                ),
            ],
        ),
    ],
)
@pytest.mark.now('2020-05-05T13:01:00+03:00')
async def test_driver_mode_reset_validators(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        driver_authorizer,
        mode_rules_data,
        mode_geography_defaults,
        lsc_check_cancelation_offer,
        expected_code: int,
        expected_error_code: Optional[str],
        expected_message: Optional[str],
        expected_localized_title: Optional[str],
        expected_localized_message: Optional[str],
):
    profile = driver.Profile(dbid_uuid=f'{_PARK_ID}_{_DRIVER_ID}')
    scene = scenario.Scene(
        profiles={
            profile: driver.Mode(
                _LOGISTIC_WORKSHIFTS,
                mode_settings=_LOGISTIC_WORKSHIFTS_ACTUAL_MODE_SETTINGS_1,
            ),
        },
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)
    scene.mock_driver_tags(mockserver, tags=['frauder'])

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _v2_statuses(request):
        return {
            'statuses': [
                {
                    'status': 'busy',
                    'park_id': _PARK_ID,
                    'driver_id': _DRIVER_ID,
                    'orders': [{'id': 'order_id', 'status': 'transporting'}],
                },
            ],
        }

    response = await logistic_workshift_stop(
        taxi_driver_mode_subscription,
        _LOGISTIC_WORKSHIFTS_RULE_ID,
        _LOGISTIC_WORKSHIFTS_MODE_SETTINGS_1,
        _CANCELATION_OFFER,
        _PARK_ID,
        _DRIVER_ID,
    )

    assert response.status_code == expected_code
    if expected_code != 200:
        assert response.json() == {
            'code': expected_error_code,
            'message': expected_message,
            'details': {
                'title': expected_localized_title,
                'text': expected_localized_message,
            },
        }


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=_LOGISTIC_WORKSHIFTS,
                rule_id=_LOGISTIC_WORKSHIFTS_RULE_ID,
                display_mode=_LOGISTIC_WORKSHIFTS,
                features={_LOGISTIC_WORKSHIFTS: {}},
            ),
        ],
    ),
)
@pytest.mark.now('2020-05-05T13:01:00+03:00')
async def test_workshift_double_stop(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        driver_authorizer,
        mode_rules_data,
        mode_geography_defaults,
        lsc_check_cancelation_offer,
        pgsql,
):
    profile = driver.Profile(dbid_uuid=f'{_PARK_ID}_{_DRIVER_ID}')
    scene = scenario.Scene(
        profiles={
            profile: driver.Mode(
                _LOGISTIC_WORKSHIFTS,
                mode_settings=_LOGISTIC_WORKSHIFTS_ACTUAL_MODE_SETTINGS_1,
            ),
        },
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    idempotency_token = 'idempotency_token'

    response = await logistic_workshift_stop(
        taxi_driver_mode_subscription,
        _LOGISTIC_WORKSHIFTS_RULE_ID,
        _LOGISTIC_WORKSHIFTS_MODE_SETTINGS_1,
        _CANCELATION_OFFER,
        _PARK_ID,
        _DRIVER_ID,
        idempotency_token,
    )

    assert (
        response.status_code == 200
    ), 'Fail at first call - should be tested by another tests'

    response = await logistic_workshift_stop(
        taxi_driver_mode_subscription,
        _LOGISTIC_WORKSHIFTS_RULE_ID,
        _LOGISTIC_WORKSHIFTS_MODE_SETTINGS_1,
        _CANCELATION_OFFER,
        _PARK_ID,
        _DRIVER_ID,
        idempotency_token,
    )

    assert response.status_code == 200, 'Fail at second call'
