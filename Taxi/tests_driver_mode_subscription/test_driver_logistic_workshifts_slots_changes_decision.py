import dataclasses
import datetime as dt
import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
import uuid

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scenario
from tests_driver_mode_subscription import scheduled_slots_tools

_DBID = 'parkid0'
_UUID = 'uuid0'

_MODE_1 = 'logistic_work_mode'
_MODE_2 = 'logistic_work_mode_2'
_NON_LOGISTIC_MODE = 'orders'

_MODE_RULE_ID_1 = 'a883a23977484000b870f0cfcc84e1f9'
_MODE_RULE_ID_2 = 'c590b29d0fbe4b4d81f8780126daab12'
_MODE_RULE_ID_3 = '2dc1c90f5fe14809bf12ee0bebc8423c'

_SLOT_ID_1 = uuid.UUID('0ea9b019-27df-4b73-bd98-bd25d8789daa')
_SLOT_ID_2 = uuid.UUID('b1aca90a-360f-499c-87bc-53fa41e58470')
_NOT_EXISTED_SLOT = uuid.UUID('779aba0e-e2a3-4f7a-acb6-2a82b3e6efe3')

_QUOTA_NAME_1 = '2762b26d16ab474888f318d0c59e364c'
_QUOTA_NAME_2 = '4d8b5be88a704a7a8727d74a747be10f'

_OFFER_IDENTITY_1 = {'slot_id': str(_SLOT_ID_1), 'rule_version': 1}
_OFFER_IDENTITY_2 = {'slot_id': str(_SLOT_ID_2), 'rule_version': 1}
_OFFER_IDENTITY_2_VER2 = {'slot_id': str(_SLOT_ID_2), 'rule_version': 2}
_NOT_EXISTED_SLOT_IDENTITY = {
    'slot_id': str(_NOT_EXISTED_SLOT),
    'rule_version': 1,
}

_DECISION_ACCEPT = 'accept'
_DECISION_REJECT = 'decline'


@dataclasses.dataclass
class CancellationOffer:
    value: str
    currency_code: str

    def json(self):
        return {
            'fine_value': {
                'currency_code': self.currency_code,
                'value': self.value,
            },
        }


def _make_mock_slot(
        offer_identity: Dict[str, Any],
        begin: str,
        end: str,
        check_not_pass_reason: Optional[str] = None,
        quota_name_override: Optional[str] = None,
        allowed_transport_type_override: Optional[List[str]] = None,
):
    result: Dict[str, Any] = {
        'offer_identity': offer_identity,
        'short_info': {
            'time_range': {'begin': begin, 'end': end},
            'quota_id': _QUOTA_NAME_1,
            'allowed_transport_types': ['auto'],
        },
    }

    if check_not_pass_reason:
        result['check_not_pass_reason'] = check_not_pass_reason

    if quota_name_override:
        result['short_info']['quota_id'] = quota_name_override

    if allowed_transport_type_override:
        result['short_info'][
            'allowed_transport_types'
        ] = allowed_transport_type_override

    return result


async def logistic_changes_decision(
        taxi_driver_mode_subscription,
        actual_mode_rule_id: str,
        actual_mode_rule_settings: Dict[str, Any],
        previous_mode_rule_id: str,
        previous_mode_rule_settings: Dict[str, Any],
        cancellation_offer: Optional[Dict[str, Any]],
        decision: str,
        park_id: str,
        driver_profile_id: str,
):

    request: Dict[str, Any] = {
        'actual_mode_rule_id': actual_mode_rule_id,
        'actual_mode_rule_settings': actual_mode_rule_settings,
        'previous_mode_rule_id': previous_mode_rule_id,
        'previous_mode_rule_settings': previous_mode_rule_settings,
        'decision': decision,
    }

    if cancellation_offer is not None:
        request['cancellation_offer'] = cancellation_offer

    headers = {
        'User-Agent': 'Taximeter 8.80 (562)',
        'Timezone': 'Europe/Moscow',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': driver_profile_id,
        'Accept-Language': 'ru',
        'X-Request-Application-Version': '8.80 (562)',
        'X-Request-Application': 'taximeter',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'X-Ya-Service-Ticket': common.MOCK_TICKET,
    }

    return await taxi_driver_mode_subscription.post(
        'driver/v1/logistic-workshifts/offers/changes/decision',
        json=request,
        headers=headers,
    )


def _make_error_response(code: int):
    return {
        'code': str(code),
        'message': f'Some {code} error message',
        'details': {
            'title': f'Some {code} error title',
            'text': f'Some {code} error text',
        },
    }


def _check_contractor_id(
        contractor_id: Dict[str, str], expected_profile: driver.Profile,
):
    assert contractor_id['park_id'] == expected_profile.park_id()
    assert contractor_id['driver_profile_id'] == expected_profile.profile_id()


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=_MODE_1,
                features={'logistic_workshifts': {}},
                rule_id=_MODE_RULE_ID_1,
            ),
            mode_rules.Patch(
                rule_name=_NON_LOGISTIC_MODE,
                features={},
                rule_id=_MODE_RULE_ID_3,
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'actual_mode_rule_id, actual_mode_rule_settings, previous_mode_rule_id, '
    'previous_mode_rule_settings, cancellation_offer, '
    'decision, lsc_check_response_code, lsc_check_call_expected, '
    'expected_code, expected_response',
    [
        pytest.param(
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_2,
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_1,
            CancellationOffer('0', 'RUB'),
            _DECISION_ACCEPT,
            200,
            True,
            200,
            None,
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_reservation_query(
                            _SLOT_ID_2.hex,
                            _MODE_1,
                            _OFFER_IDENTITY_2,
                            _OFFER_IDENTITY_1,
                            dt.datetime(
                                2021, 11, 15, 4, 1, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 11, 15, 5, 1, tzinfo=dt.timezone.utc,
                            ),
                            _QUOTA_NAME_1,
                            1,
                            _DBID,
                            _UUID,
                        ),
                    ],
                ),
            ],
            id='Correct accept scenario',
        ),
        pytest.param(
            _MODE_RULE_ID_3,
            _OFFER_IDENTITY_2,
            _MODE_RULE_ID_3,
            _OFFER_IDENTITY_1,
            CancellationOffer('0', 'RUB'),
            _DECISION_ACCEPT,
            200,
            False,
            400,
            f'Mode rule with id {_MODE_RULE_ID_3} is not logistic mode rule',
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_reservation_query(
                            _SLOT_ID_2.hex,
                            _NON_LOGISTIC_MODE,
                            _OFFER_IDENTITY_2,
                            _OFFER_IDENTITY_1,
                            dt.datetime(
                                2021, 11, 15, 4, 1, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 11, 15, 5, 1, tzinfo=dt.timezone.utc,
                            ),
                            _QUOTA_NAME_1,
                            1,
                            _DBID,
                            _UUID,
                        ),
                    ],
                ),
            ],
            id='Non logistic mode',
        ),
        pytest.param(
            _MODE_RULE_ID_1,
            _NOT_EXISTED_SLOT_IDENTITY,
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_1,
            CancellationOffer('0', 'RUB'),
            _DECISION_ACCEPT,
            200,
            False,
            409,
            'Failed to find slot with ' f'name {_NOT_EXISTED_SLOT.hex}',
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_reservation_query(
                            _SLOT_ID_2.hex,
                            _MODE_1,
                            _NOT_EXISTED_SLOT_IDENTITY,
                            _OFFER_IDENTITY_1,
                            dt.datetime(
                                2021, 11, 15, 4, 1, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 11, 15, 5, 1, tzinfo=dt.timezone.utc,
                            ),
                            _QUOTA_NAME_1,
                            1,
                            _DBID,
                            _UUID,
                        ),
                    ],
                ),
            ],
            id='Non existed slot',
        ),
        pytest.param(
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_2,
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_1,
            CancellationOffer('0', 'RUB'),
            _DECISION_ACCEPT,
            200,
            False,
            400,
            'actual_mode_rule_settings is incorrect',
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_reservation_query(
                            _SLOT_ID_2.hex,
                            _MODE_1,
                            None,
                            _OFFER_IDENTITY_1,
                            dt.datetime(
                                2021, 11, 15, 4, 1, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 11, 15, 5, 1, tzinfo=dt.timezone.utc,
                            ),
                            _QUOTA_NAME_1,
                            1,
                            _DBID,
                            _UUID,
                        ),
                    ],
                ),
            ],
            id='Empty mode_settings',
        ),
        pytest.param(
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_2,
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_1,
            CancellationOffer('0', 'RUB'),
            _DECISION_ACCEPT,
            200,
            False,
            400,
            'previous_mode_rule_settings is incorrect',
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_reservation_query(
                            _SLOT_ID_2.hex,
                            _MODE_1,
                            _OFFER_IDENTITY_2,
                            None,
                            dt.datetime(
                                2021, 11, 15, 4, 1, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 11, 15, 5, 1, tzinfo=dt.timezone.utc,
                            ),
                            _QUOTA_NAME_1,
                            1,
                            _DBID,
                            _UUID,
                        ),
                    ],
                ),
            ],
            id='Empty accepted_mode_settings',
        ),
        pytest.param(
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_2,
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_1,
            CancellationOffer('0', 'RUB'),
            _DECISION_ACCEPT,
            200,
            False,
            400,
            'actual_mode_rule_settings is incorrect',
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_reservation_query(
                            _SLOT_ID_2.hex,
                            _MODE_1,
                            _OFFER_IDENTITY_2_VER2,
                            _OFFER_IDENTITY_1,
                            dt.datetime(
                                2021, 11, 15, 4, 1, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 11, 15, 5, 1, tzinfo=dt.timezone.utc,
                            ),
                            _QUOTA_NAME_1,
                            1,
                            _DBID,
                            _UUID,
                        ),
                    ],
                ),
            ],
            id='Outdated mode_settings',
        ),
        pytest.param(
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_2,
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_1,
            CancellationOffer('0', 'RUB'),
            _DECISION_REJECT,
            200,
            True,
            200,
            None,
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_reservation_query(
                            _SLOT_ID_2.hex,
                            _MODE_1,
                            _OFFER_IDENTITY_2,
                            _OFFER_IDENTITY_1,
                            dt.datetime(
                                2021, 11, 15, 4, 1, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 11, 15, 5, 1, tzinfo=dt.timezone.utc,
                            ),
                            _QUOTA_NAME_1,
                            1,
                            _DBID,
                            _UUID,
                        ),
                    ],
                ),
            ],
            id='Correct reject scenario',
        ),
        pytest.param(
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_2,
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_1,
            None,
            _DECISION_REJECT,
            200,
            False,
            400,
            'Missing required field cancellation_offer',
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_reservation_query(
                            _SLOT_ID_2.hex,
                            _MODE_1,
                            _OFFER_IDENTITY_2,
                            _OFFER_IDENTITY_1,
                            dt.datetime(
                                2021, 11, 15, 4, 1, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 11, 15, 5, 1, tzinfo=dt.timezone.utc,
                            ),
                            _QUOTA_NAME_1,
                            1,
                            _DBID,
                            _UUID,
                        ),
                    ],
                ),
            ],
            id='Missing cancellation_offer',
        ),
        pytest.param(
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_2,
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_1,
            CancellationOffer('0', 'RUB'),
            _DECISION_ACCEPT,
            404,
            True,
            404,
            _make_error_response(404)['message'],
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_reservation_query(
                            _SLOT_ID_2.hex,
                            _MODE_1,
                            _OFFER_IDENTITY_2,
                            _OFFER_IDENTITY_1,
                            dt.datetime(
                                2021, 11, 15, 4, 1, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 11, 15, 5, 1, tzinfo=dt.timezone.utc,
                            ),
                            _QUOTA_NAME_1,
                            1,
                            _DBID,
                            _UUID,
                        ),
                    ],
                ),
            ],
            id='lsc check-creation fail with 404',
        ),
        pytest.param(
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_2,
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_1,
            CancellationOffer('0', 'RUB'),
            _DECISION_ACCEPT,
            409,
            True,
            409,
            _make_error_response(409)['message'],
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_reservation_query(
                            _SLOT_ID_2.hex,
                            _MODE_1,
                            _OFFER_IDENTITY_2,
                            _OFFER_IDENTITY_1,
                            dt.datetime(
                                2021, 11, 15, 4, 1, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 11, 15, 5, 1, tzinfo=dt.timezone.utc,
                            ),
                            _QUOTA_NAME_1,
                            1,
                            _DBID,
                            _UUID,
                        ),
                    ],
                ),
            ],
            id='lsc check-creation fail with 409',
        ),
        pytest.param(
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_2,
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_1,
            CancellationOffer('0', 'RUB'),
            _DECISION_REJECT,
            404,
            True,
            404,
            _make_error_response(404)['message'],
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_reservation_query(
                            _SLOT_ID_2.hex,
                            _MODE_1,
                            _OFFER_IDENTITY_2,
                            _OFFER_IDENTITY_1,
                            dt.datetime(
                                2021, 11, 15, 4, 1, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 11, 15, 5, 1, tzinfo=dt.timezone.utc,
                            ),
                            _QUOTA_NAME_1,
                            1,
                            _DBID,
                            _UUID,
                        ),
                    ],
                ),
            ],
            id='lsc check-cancellation fail with 404',
        ),
        pytest.param(
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_2,
            _MODE_RULE_ID_1,
            _OFFER_IDENTITY_1,
            CancellationOffer('0', 'RUB'),
            _DECISION_REJECT,
            409,
            True,
            409,
            _make_error_response(409)['message'],
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_reservation_query(
                            _SLOT_ID_2.hex,
                            _MODE_1,
                            _OFFER_IDENTITY_2,
                            _OFFER_IDENTITY_1,
                            dt.datetime(
                                2021, 11, 15, 4, 1, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 11, 15, 5, 1, tzinfo=dt.timezone.utc,
                            ),
                            _QUOTA_NAME_1,
                            1,
                            _DBID,
                            _UUID,
                        ),
                    ],
                ),
            ],
            id='lsc check-cancellation fail with 409',
        ),
    ],
)
@pytest.mark.now('2021-11-14T04:01:00+03:00')
async def test_scheduled_slots_changes_decision(
        taxi_driver_mode_subscription,
        pgsql,
        mode_rules_data,
        driver_authorizer,
        mockserver,
        taxi_config,
        mocked_time,
        actual_mode_rule_id: str,
        actual_mode_rule_settings: Dict[str, Any],
        previous_mode_rule_id: str,
        previous_mode_rule_settings: Dict[str, Any],
        cancellation_offer: Optional[CancellationOffer],
        decision: str,
        lsc_check_response_code: int,
        lsc_check_call_expected: bool,
        expected_code: int,
        expected_response: Optional[str],
):
    profile = driver.Profile(f'{_DBID}_{_UUID}')
    scene = scenario.Scene(
        profiles={profile: driver.Mode('orders')}, udid='test-driver-id',
    )

    scene.setup(
        mockserver,
        mocked_time,
        driver_authorizer,
        mock_driver_trackstory=False,
    )

    @mockserver.json_handler(
        '/logistic-supply-conductor/internal/v1/'
        'offer/reservation/check-cancellation',
    )
    async def check_cancellation_offer_hndl(request):
        nonlocal lsc_check_response_code

        if lsc_check_response_code == 200:
            return {}

        return mockserver.make_response(
            json.dumps(_make_error_response(lsc_check_response_code)),
            lsc_check_response_code,
        )

    @mockserver.json_handler(
        '/logistic-supply-conductor/internal/v1/'
        'offer/reservation/check-creation',
    )
    async def check_creation_offer_handler(request):
        nonlocal lsc_check_response_code
        nonlocal actual_mode_rule_settings

        if lsc_check_response_code == 200:
            return {
                'items': [
                    {
                        'offer_identity': actual_mode_rule_settings,
                        'short_info': {
                            'time_range': {
                                'begin': '2021-02-04T16:00:00+00:00',
                                'end': '2021-02-04T18:00:00+00:00',
                            },
                            'quota_id': '31fa15ed-6291-4739-a2df-a6706b9c9100',
                            'allowed_transport_types': [
                                'auto',
                                'bicycle',
                                'pedestrian',
                            ],
                        },
                    },
                ],
            }

        return mockserver.make_response(
            json.dumps(_make_error_response(lsc_check_response_code)),
            lsc_check_response_code,
        )

    response = await logistic_changes_decision(
        taxi_driver_mode_subscription,
        actual_mode_rule_id,
        {'logistic_offer_identity': actual_mode_rule_settings},
        previous_mode_rule_id,
        {'logistic_offer_identity': previous_mode_rule_settings},
        {'logistic_cancelation_offer': (cancellation_offer.json())}
        if cancellation_offer is not None
        else None,
        decision,
        profile.park_id(),
        profile.profile_id(),
    )

    if lsc_check_call_expected and decision == _DECISION_ACCEPT:
        assert check_creation_offer_handler.has_calls

        lsc_request = check_creation_offer_handler.next_call()['request'].json

        _check_contractor_id(lsc_request['contractor_id'], profile)

        assert len(lsc_request['items']) == 1
        assert lsc_request['items'][0] == actual_mode_rule_settings

        assert lsc_request['check_reason'] == 'decision'
    elif lsc_check_call_expected and decision == _DECISION_REJECT:
        assert check_cancellation_offer_hndl.has_calls

        lsc_request = check_cancellation_offer_hndl.next_call()['request'].json

        _check_contractor_id(lsc_request['contractor_id'], profile)

        assert cancellation_offer is not None
        assert lsc_request['cancellation_offer'] == cancellation_offer.json()
        assert lsc_request['actual_offer'] == actual_mode_rule_settings
        assert (
            lsc_request['last_accepted_offer'] == previous_mode_rule_settings
        )

    assert response.status_code == expected_code

    if expected_code != 200:
        assert response.json()['message'] == expected_response
