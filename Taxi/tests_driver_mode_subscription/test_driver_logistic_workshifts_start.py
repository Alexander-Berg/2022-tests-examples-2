import datetime as dt
import json
from typing import Any
from typing import Dict
from typing import Optional


import pytest

from testsuite import utils

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario
from tests_driver_mode_subscription import scheduled_slots_tools


_DBID = 'parkid0'
_UUID = 'uuid0'

_RULE_ID = '4cf2c2ff205d47469aecf896e9d7dfc1'

_NEXT_MODE = 'next_work_mode'
_PREV_MODE = 'prev_work_mode'

_NEXT_MODE_SETTINGS = {
    'slot_id': 'af31c824-066d-46df-981f-a8dc431d64e8',
    'rule_version': 43,
}
_PREV_MODE_SETTINGS = {
    'slot_id': 'af31c824-066d-46df-981f-a8dc431d64e8',
    'rule_version': 2,
}

_NEXT_MODE_SETTINGS_WRONG_VERSION = {
    'slot_id': 'af31c824-066d-46df-981f-a8dc431d64e8',
    'rule_version': 1,
}

_NEXT_MODE_SETTINGS_WRONG_SLOT_ID = {
    'slot_id': 'f514b1d8-a939-4927-84b5-b023e55ae928',
    'rule_version': 43,
}

_TEST_PROFILE = driver.Profile(f'{_DBID}_{_UUID}')


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=_NEXT_MODE,
                features={'logistic_workshifts': {}},
                rule_id=_RULE_ID,
            ),
            mode_rules.Patch(rule_name=_PREV_MODE, features={}),
        ],
    ),
)
@pytest.mark.parametrize(
    'current_time_iso, mode_settings, '
    'check_should_be_called, '
    'check_before_start_should_fail, '
    'check_before_start_fail_reason, '
    'expected_http_code, '
    'expected_code, expected_message, '
    'expected_title, expected_text',
    [
        pytest.param(
            '2021-02-04T17:00:00+00:00',
            _NEXT_MODE_SETTINGS,
            True,
            False,
            None,
            200,
            None,
            None,
            None,
            None,
            id='success',
        ),
        pytest.param(
            '2021-02-04T17:00:00+00:00',
            _NEXT_MODE_SETTINGS,
            True,
            False,
            None,
            409,
            'CHECK_NOT_ON_ORDER_FAILED',
            'is on the order right now',
            'Вы на заказе',
            'Завершите заказ, прежде чем менять статус смены.',
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_ENABLE_CHECK_NOT_ON_ORDER=True,
                ),
            ],
            id='fail on order',
        ),
        pytest.param(
            '2021-02-04T17:00:00+00:00',
            _NEXT_MODE_SETTINGS,
            False,
            False,
            None,
            400,
            'BAD_REQUEST',
            'Not logistic mode rule',
            None,
            None,
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        [
                            mode_rules.Patch(
                                rule_name=_NEXT_MODE,
                                features={},
                                rule_id=_RULE_ID,
                            ),
                            mode_rules.Patch(
                                rule_name=_PREV_MODE, features={},
                            ),
                        ],
                    ),
                ),
            ],
            id='fail on not logistic feature',
        ),
        pytest.param(
            '2021-02-04T17:00:00+00:00',
            _NEXT_MODE_SETTINGS_WRONG_SLOT_ID,
            False,
            False,
            None,
            409,
            'SLOT_PROBLEM',
            'No slot reserved',
            None,
            None,
            id='fail without reserved scheduled slot',
        ),
        pytest.param(
            '2021-02-04T17:00:00+00:00',
            _NEXT_MODE_SETTINGS_WRONG_VERSION,
            False,
            False,
            None,
            409,
            'SLOT_PROBLEM',
            'No slot reserved',
            None,
            None,
            id='fail with wrong version',
        ),
        pytest.param(
            '2020-02-04T17:00:00+00:00',
            _NEXT_MODE_SETTINGS,
            False,
            False,
            None,
            409,
            'SLOT_PROBLEM',
            'Current time not in slot range',
            None,
            None,
            id='fail too early time',
        ),
        pytest.param(
            '2022-02-04T17:00:00+00:00',
            _NEXT_MODE_SETTINGS,
            False,
            False,
            None,
            409,
            'SLOT_PROBLEM',
            'Current time not in slot range',
            None,
            None,
            id='fail too later time',
        ),
        pytest.param(
            '2021-02-04T17:00:00+00:00',
            _NEXT_MODE_SETTINGS,
            True,
            False,
            'Some unexpected error reason',
            409,
            '409',
            'Some unexpected error reason',
            None,
            None,
            id='lsc check wasn\'t passed',
        ),
        pytest.param(
            '2021-02-04T17:00:00+00:00',
            _NEXT_MODE_SETTINGS,
            True,
            True,
            None,
            409,
            '409',
            'Some error reason from lsc',
            'Some title from lsc',
            'Some text from lsc',
            id='lsc check failed',
        ),
    ],
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        scheduled_slots_tools.make_insert_reservation_query(
            'af31c824066d46df981fa8dc431d64e8',
            _NEXT_MODE,
            _NEXT_MODE_SETTINGS,
            _NEXT_MODE_SETTINGS,
            dt.datetime(2021, 2, 4, 16, 0, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 2, 4, 18, 0, 0, tzinfo=dt.timezone.utc),
            'some_quota',
            1,
            _DBID,
            _UUID,
        ),
        scheduled_slots_tools.make_slot_reservation_query(
            _NEXT_MODE,
            'af31c824066d46df981fa8dc431d64e8',
            _TEST_PROFILE,
            is_deleted=True,
        ),
    ],
)
async def test_workshift_start(
        taxi_driver_mode_subscription,
        pgsql,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        taxi_config,
        mocked_time,
        current_time_iso: str,
        check_should_be_called: bool,
        check_before_start_should_fail: bool,
        check_before_start_fail_reason: Optional[str],
        mode_settings: Dict[str, Any],
        expected_http_code: int,
        expected_code: Optional[str],
        expected_message: Optional[str],
        expected_text: Optional[str],
        expected_title: Optional[str],
):
    mocked_time.set(utils.to_utc(dt.datetime.fromisoformat(current_time_iso)))

    scene = scenario.Scene(
        profiles={_TEST_PROFILE: driver.Mode(_PREV_MODE)},
        udid='test-driver-id',
    )

    scene.setup(
        mockserver,
        mocked_time,
        driver_authorizer,
        mock_driver_trackstory=True,
    )

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _v2_statuses(request):
        return {
            'statuses': [
                {
                    'status': 'busy',
                    'park_id': _TEST_PROFILE.park_id(),
                    'driver_id': _TEST_PROFILE.profile_id(),
                    'orders': [{'id': 'order_id', 'status': 'transporting'}],
                },
            ],
        }

    @mockserver.json_handler(
        '/logistic-supply-conductor/internal/v1/offer/'
        'reservation/check-before-start',
    )
    def check_before_start_handler(request):
        nonlocal check_before_start_fail_reason
        nonlocal check_before_start_should_fail
        nonlocal expected_code
        nonlocal expected_http_code
        nonlocal expected_message
        nonlocal expected_text
        nonlocal expected_title
        nonlocal mode_settings

        if check_before_start_should_fail:
            return mockserver.make_response(
                json.dumps(
                    {
                        'code': expected_code,
                        'message': expected_message,
                        'details': {
                            'title': expected_title,
                            'text': expected_text,
                        },
                    },
                ),
                expected_http_code,
            )

        response = {
            'offer_identity': mode_settings,
            'short_info': {
                'time_range': {
                    'begin': '2021-02-04T16:00:00+00:00',
                    'end': '2021-02-04T18:00:00+00:00',
                },
                'quota_id': '31fa15ed-6291-4739-a2df-a6706b9c9100',
                'allowed_transport_types': ['auto', 'bicycle', 'pedestrian'],
            },
        }

        if check_before_start_fail_reason is not None:
            response['check_not_pass_reason'] = check_before_start_fail_reason

        return response

    response = await common.logistic_workshifts_start(
        taxi_driver_mode_subscription,
        profile=_TEST_PROFILE,
        mode_rule_id=_RULE_ID,
        mode_rule_settings={'logistic_offer_identity': mode_settings},
    )

    assert response.status_code == expected_http_code
    assert check_before_start_handler.has_calls == check_should_be_called

    if check_should_be_called:
        check_request = check_before_start_handler.next_call()['request'].json
        assert (
            check_request['contractor_id']['park_id']
            == _TEST_PROFILE.park_id()
        )
        assert (
            check_request['contractor_id']['driver_profile_id']
            == _TEST_PROFILE.profile_id()
        )

        assert check_request['offer_identity'] == mode_settings

    if expected_http_code != 200:
        response_body = response.json()

        assert response_body.get('code') == expected_code
        assert response_body.get('message') == expected_message

        if expected_title or expected_text:
            assert response_body['details'].get('text') == expected_text
            assert response_body['details'].get('title') == expected_title
        else:
            assert response_body.get('details') is None

    if response.status_code == 200:
        actual_saga_data = saga_tools.get_saga_db_data(_TEST_PROFILE, pgsql)
        # ignore generated data
        expected_idempotency_token = actual_saga_data[8]
        assert actual_saga_data == (
            1,
            dt.datetime(2021, 2, 4, 17, 0),
            'parkid0',
            'uuid0',
            'test-driver-id',
            'next_work_mode',
            dt.datetime(2021, 2, 4, 17, 0),
            {
                'rule_version': 43,
                'slot_id': 'af31c824-066d-46df-981f-a8dc431d64e8',
            },
            expected_idempotency_token,
            'ru',
            None,
            'forbid',
            saga_tools.SOURCE_LOGISTIC_WORKSHIFT_START,
            'manual_mode_change',
        )


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=_NEXT_MODE,
                features={'logistic_workshifts': {}},
                rule_id=_RULE_ID,
            ),
            mode_rules.Patch(rule_name=_PREV_MODE, features={}),
        ],
    ),
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        scheduled_slots_tools.make_insert_reservation_query(
            'af31c824066d46df981fa8dc431d64e8',
            _NEXT_MODE,
            _NEXT_MODE_SETTINGS,
            _NEXT_MODE_SETTINGS,
            dt.datetime(2021, 2, 4, 16, 0, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 2, 4, 18, 0, 0, tzinfo=dt.timezone.utc),
            'some_quota',
            1,
            _DBID,
            _UUID,
        ),
        scheduled_slots_tools.make_slot_reservation_query(
            _NEXT_MODE,
            'af31c824066d46df981fa8dc431d64e8',
            _TEST_PROFILE,
            is_deleted=True,
        ),
    ],
)
@pytest.mark.now('2021-02-04T17:00:00+00:00')
async def test_workshift_double_start(
        taxi_driver_mode_subscription,
        pgsql,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        taxi_config,
        mocked_time,
):
    scene = scenario.Scene(
        profiles={_TEST_PROFILE: driver.Mode(_PREV_MODE)},
        udid='test-driver-id',
    )

    scene.setup(
        mockserver,
        mocked_time,
        driver_authorizer,
        mock_driver_trackstory=True,
    )

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _v2_statuses(request):
        return {
            'statuses': [
                {
                    'status': 'busy',
                    'park_id': _TEST_PROFILE.park_id(),
                    'driver_id': _TEST_PROFILE.profile_id(),
                    'orders': [{'id': 'order_id', 'status': 'transporting'}],
                },
            ],
        }

    @mockserver.json_handler(
        '/logistic-supply-conductor/internal/v1/offer/'
        'reservation/check-before-start',
    )
    def _check_before_start_handler(request):
        return {
            'offer_identity': _NEXT_MODE_SETTINGS,
            'short_info': {
                'time_range': {
                    'begin': '2021-02-04T16:00:00+00:00',
                    'end': '2021-02-04T18:00:00+00:00',
                },
                'quota_id': '31fa15ed-6291-4739-a2df-a6706b9c9100',
                'allowed_transport_types': ['auto', 'bicycle', 'pedestrian'],
            },
        }

    idempotency_token = 'idempotency_token'

    response = await common.logistic_workshifts_start(
        taxi_driver_mode_subscription,
        profile=_TEST_PROFILE,
        mode_rule_id=_RULE_ID,
        mode_rule_settings={'logistic_offer_identity': _NEXT_MODE_SETTINGS},
        idempotency_token=idempotency_token,
    )

    assert (
        response.status_code == 200
    ), 'Fail at first call - should be tested by another tests'

    # Second call
    response = await common.logistic_workshifts_start(
        taxi_driver_mode_subscription,
        profile=_TEST_PROFILE,
        mode_rule_id=_RULE_ID,
        mode_rule_settings={'logistic_offer_identity': _NEXT_MODE_SETTINGS},
        idempotency_token=idempotency_token,
    )

    assert response.status_code == 200, 'Fail at second call'


@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=_NEXT_MODE,
                features={'logistic_workshifts': {}},
                rule_id=_RULE_ID,
            ),
            mode_rules.Patch(rule_name=_PREV_MODE, features={}),
        ],
    ),
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        scheduled_slots_tools.make_insert_reservation_query(
            'af31c824066d46df981fa8dc431d64e8',
            _NEXT_MODE,
            _NEXT_MODE_SETTINGS,
            _NEXT_MODE_SETTINGS,
            dt.datetime(2021, 2, 4, 16, 0, 0, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 2, 4, 18, 0, 0, tzinfo=dt.timezone.utc),
            'some_quota',
            1,
            _DBID,
            _UUID,
        ),
    ],
)
@pytest.mark.parametrize(
    'expected_code',
    [
        pytest.param(
            200,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_SCHEDULED_SLOTS={
                        'slot_change_delay_s': 60,
                        'allowed_time_before_start_s': 45 * 60,
                    },
                ),
            ],
            id='success, hit the allowed time',
        ),
        pytest.param(
            409,
            marks=[
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_SCHEDULED_SLOTS={
                        'slot_change_delay_s': 60,
                        'allowed_time_before_start_s': 15 * 60,
                    },
                ),
            ],
            id='fail, miss the allowed time',
        ),
    ],
)
@pytest.mark.now('2021-02-04T15:30:00+00:00')
async def test_allowed_time_before_start(
        taxi_driver_mode_subscription,
        pgsql,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        taxi_config,
        mocked_time,
        expected_code,
):
    scene = scenario.Scene(
        profiles={_TEST_PROFILE: driver.Mode(_PREV_MODE)},
        udid='test-driver-id',
    )

    scene.setup(
        mockserver,
        mocked_time,
        driver_authorizer,
        mock_driver_trackstory=True,
    )

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _v2_statuses(request):
        return {
            'statuses': [
                {
                    'status': 'busy',
                    'park_id': _TEST_PROFILE.park_id(),
                    'driver_id': _TEST_PROFILE.profile_id(),
                    'orders': [{'id': 'order_id', 'status': 'transporting'}],
                },
            ],
        }

    @mockserver.json_handler(
        '/logistic-supply-conductor/internal/v1/offer/'
        'reservation/check-before-start',
    )
    def _check_before_start_handler(request):
        return {
            'offer_identity': _NEXT_MODE_SETTINGS,
            'short_info': {
                'time_range': {
                    'begin': '2021-02-04T16:00:00+00:00',
                    'end': '2021-02-04T18:00:00+00:00',
                },
                'quota_id': '31fa15ed-6291-4739-a2df-a6706b9c9100',
                'allowed_transport_types': ['auto', 'bicycle', 'pedestrian'],
            },
        }

    response = await common.logistic_workshifts_start(
        taxi_driver_mode_subscription,
        profile=_TEST_PROFILE,
        mode_rule_id=_RULE_ID,
        mode_rule_settings={'logistic_offer_identity': _NEXT_MODE_SETTINGS},
    )

    assert response.status_code == expected_code
