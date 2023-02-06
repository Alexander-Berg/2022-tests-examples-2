import datetime as dt
import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scenario
from tests_driver_mode_subscription import scheduled_slots_tools

_DBID = 'parkid0'
_UUID = 'uuid0'

_MODE_1 = 'logistic_work_mode'
_MODE_2 = 'orders'

_MODE_RULE_ID_1 = 'a883a23977484000b870f0cfcc84e1f9'
_MODE_RULE_ID_2 = 'c590b29d0fbe4b4d81f8780126daab12'
_MODE_RULE_ID_3 = '2dc1c90f5fe14809bf12ee0bebc8423c'

_SLOT_ID_1 = '0ea9b019-27df-4b73-bd98-bd25d8789daa'
_SLOT_ID_2 = 'b1aca90a-360f-499c-87bc-53fa41e58470'

_QUOTA_NAME_1 = '2762b26d-16ab-4748-88f3-18d0c59e364c'
_QUOTA_NAME_2 = '4d8b5be8-8a70-4a7a-8727-d74a747be10f'

_OFFER_IDENTITY_1 = {'slot_id': _SLOT_ID_1, 'rule_version': 1}
_OFFER_IDENTITY_2 = {'slot_id': _SLOT_ID_2, 'rule_version': 1}
_OFFER_IDENTITY_2_VER2 = {'slot_id': _SLOT_ID_2, 'rule_version': 2}


def _to_utc_datetime(time_str: str):
    return dt.datetime.fromisoformat(time_str).replace(tzinfo=None)


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


def _make_slot_reservation_response(booked: List[str], not_booked: List[str]):
    result: Dict[str, Any] = {'booked': [], 'not_booked': []}

    for date in booked:
        result['booked'].append({'title': date})

    for date in not_booked:
        result['not_booked'].append({'title': date})

    return result


async def logistic_reservation_create(
        taxi_driver_mode_subscription,
        slots: List[Dict[str, Any]],
        park_id: str,
        driver_profile_id: str,
):

    request: Dict[str, Any] = {'items': slots}

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
        'driver/v1/logistic-workshifts/offers/reservation/create',
        json=request,
        headers=headers,
    )


@pytest.mark.config(
    API_OVER_DATA_ENABLE_CACHES=True,
    API_OVER_DATA_ENABLE_SPECIFIC_CACHE={'__default__': {'__default__': True}},
    API_OVER_DATA_OPENING_LAG_MS={'__default__': {'__default__': -1}},
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=_MODE_1,
                features={'logistic_workshifts': {}},
                rule_id=_MODE_RULE_ID_1,
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'checked_slots, expected_code, expected_response',
    [
        pytest.param(
            [
                _make_mock_slot(
                    _OFFER_IDENTITY_2,
                    '2021-02-04T07:01:00+03:00',
                    '2021-02-04T08:01:00+03:00',
                ),
                _make_mock_slot(
                    _OFFER_IDENTITY_1,
                    '2021-02-01T04:01:00+03:00',
                    '2021-02-01T06:01:00+03:00',
                ),
            ],
            200,
            _make_slot_reservation_response(
                booked=['1 февраля', '4 февраля'], not_booked=[],
            ),
            id='book ok',
        ),
        pytest.param(
            [
                _make_mock_slot(
                    _OFFER_IDENTITY_2,
                    '2021-02-04T07:01:00+03:00',
                    '2021-02-04T08:01:00+03:00',
                    check_not_pass_reason='some_reason',
                ),
                _make_mock_slot(
                    _OFFER_IDENTITY_1,
                    '2021-02-01T04:01:00+03:00',
                    '2021-02-01T06:01:00+03:00',
                    check_not_pass_reason='some_reason',
                ),
            ],
            200,
            _make_slot_reservation_response(
                booked=[], not_booked=['1 февраля', '4 февраля'],
            ),
            id='book blocked by check reservation',
        ),
        pytest.param(
            [
                _make_mock_slot(
                    _OFFER_IDENTITY_1,
                    '2021-02-04T07:01:00+03:00',
                    '2021-02-04T08:01:00+03:00',
                    None,
                    _QUOTA_NAME_1,
                ),
                _make_mock_slot(
                    _OFFER_IDENTITY_2,
                    '2021-02-01T04:01:00+03:00',
                    '2021-02-01T06:01:00+03:00',
                    None,
                    _QUOTA_NAME_2,
                ),
            ],
            200,
            _make_slot_reservation_response(
                booked=['4 февраля'], not_booked=['1 февраля'],
            ),
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_update_slot_quota_query(
                            _QUOTA_NAME_1.replace('-', ''), 999,
                        ),
                    ],
                ),
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_update_slot_quota_query(
                            _QUOTA_NAME_2.replace('-', ''), 1000,
                        ),
                    ],
                ),
            ],
            id='no free slots',
        ),
        pytest.param(
            [
                _make_mock_slot(
                    _OFFER_IDENTITY_1,
                    '2021-02-04T07:01:00+03:00',
                    '2021-02-04T08:01:00+03:00',
                    None,
                    None,
                    ['auto'],
                ),
                _make_mock_slot(
                    _OFFER_IDENTITY_2,
                    '2021-02-01T04:01:00+03:00',
                    '2021-02-01T06:01:00+03:00',
                    None,
                    None,
                    ['pedestrian'],
                ),
            ],
            200,
            _make_slot_reservation_response(
                booked=['4 февраля'], not_booked=['1 февраля'],
            ),
            id='wrong transport type',
        ),
        pytest.param(
            [
                _make_mock_slot(
                    _OFFER_IDENTITY_2,
                    '2021-02-04T07:01:00+03:00',
                    '2021-02-04T08:01:00+03:00',
                ),
                _make_mock_slot(
                    _OFFER_IDENTITY_1,
                    '2021-02-01T04:01:00+03:00',
                    '2021-02-01T06:01:00+03:00',
                ),
            ],
            200,
            _make_slot_reservation_response(
                booked=['4 февраля'], not_booked=['1 февраля'],
            ),
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_slot_meta_query(
                            _SLOT_ID_1.replace('-', ''),
                            dt.datetime(
                                2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc,
                            ),
                        ),
                    ],
                ),
            ],
            id='already closed slot',
        ),
        pytest.param(
            [
                _make_mock_slot(
                    _OFFER_IDENTITY_1,
                    '2021-02-04T12:01:00+00:00',
                    '2021-02-04T16:01:00+00:00',
                ),
            ],
            200,
            _make_slot_reservation_response(
                booked=[], not_booked=['4 февраля'],
            ),
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_reservation_query(
                            '7459b0edf6fa494fa61b1806c4caa81b',
                            _MODE_1,
                            _OFFER_IDENTITY_2,
                            _OFFER_IDENTITY_2,
                            dt.datetime(
                                2021, 2, 4, 15, 1, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 2, 4, 18, 1, tzinfo=dt.timezone.utc,
                            ),
                            _QUOTA_NAME_1,
                            1,
                            _DBID,
                            _UUID,
                        ),
                        scheduled_slots_tools.make_insert_slot_meta_query(
                            '7459b0edf6fa494fa61b1806c4caa81b',
                        ),
                    ],
                ),
            ],
            id='slot time intersection',
        ),
        pytest.param(
            [
                _make_mock_slot(
                    _OFFER_IDENTITY_1,
                    '2021-02-04T12:01:00+00:00',
                    '2021-02-04T16:01:00+00:00',
                ),
            ],
            200,
            _make_slot_reservation_response(
                booked=['4 февраля'], not_booked=[],
            ),
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_reservation_query(
                            '7459b0edf6fa494fa61b1806c4caa81b',
                            _MODE_1,
                            _OFFER_IDENTITY_2,
                            _OFFER_IDENTITY_2,
                            dt.datetime(
                                2021, 2, 4, 16, 1, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 2, 4, 18, 1, tzinfo=dt.timezone.utc,
                            ),
                            _QUOTA_NAME_1,
                            1,
                            _DBID,
                            _UUID,
                        ),
                        scheduled_slots_tools.make_insert_slot_meta_query(
                            '7459b0edf6fa494fa61b1806c4caa81b',
                        ),
                    ],
                ),
            ],
            id='slot no intersection on borders',
        ),
        pytest.param(
            [
                _make_mock_slot(
                    _OFFER_IDENTITY_1,
                    '2021-02-04T12:01:00+00:00',
                    '2021-02-04T16:01:00+00:00',
                ),
            ],
            200,
            _make_slot_reservation_response(
                booked=['4 февраля'], not_booked=[],
            ),
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_reservation_query(
                            _SLOT_ID_1.replace('-', ''),
                            _MODE_1,
                            _OFFER_IDENTITY_1,
                            _OFFER_IDENTITY_1,
                            dt.datetime(
                                2021, 2, 4, 12, 1, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 2, 4, 16, 1, tzinfo=dt.timezone.utc,
                            ),
                            _QUOTA_NAME_1,
                            1,
                            _DBID,
                            _UUID,
                        ),
                        scheduled_slots_tools.make_insert_slot_meta_query(
                            _SLOT_ID_1.replace('-', ''),
                        ),
                    ],
                ),
            ],
            id='already reserved slot',
        ),
    ],
)
@pytest.mark.now('2021-06-14T04:01:00+03:00')
async def test_scheduled_slots_reservation_responses(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        mocked_time,
        checked_slots: List[Dict[str, Any]],
        expected_code: int,
        expected_response: Dict[str, Any],
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
        '/logistic-supply-conductor/'
        'internal/v1/offer/reservation/check-creation',
    )
    def _check_creation_mock(request):
        return {'items': checked_slots}

    response = await logistic_reservation_create(
        taxi_driver_mode_subscription,
        # This have no impact on test result,
        # because handler logic use data from check-creation api
        [
            {
                'mode_rule_id': _MODE_RULE_ID_1,
                'mode_rule_settings': {
                    'logistic_offer_identity': _OFFER_IDENTITY_1,
                },
            },
        ],
        profile.park_id(),
        profile.profile_id(),
    )

    assert response.status_code == expected_code

    assert response.json() == expected_response


@pytest.mark.config(
    API_OVER_DATA_ENABLE_CACHES=True,
    API_OVER_DATA_ENABLE_SPECIFIC_CACHE={'__default__': {'__default__': True}},
    API_OVER_DATA_OPENING_LAG_MS={'__default__': {'__default__': -1}},
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=_MODE_1,
                features={'logistic_workshifts': {}},
                rule_id=_MODE_RULE_ID_1,
            ),
            mode_rules.Patch(rule_name='orders', rule_id=_MODE_RULE_ID_2),
            mode_rules.Patch(
                rule_name='some_old_rule',
                stops_at=dt.datetime.fromisoformat(
                    '2020-05-01T05:00:00+00:00',
                ),
                features={'logistic_workshifts': {}},
                rule_id=_MODE_RULE_ID_3,
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'offers, expected_code, expected_response',
    [
        pytest.param(
            [
                {
                    'mode_rule_id': _MODE_RULE_ID_1,
                    'mode_rule_settings': {
                        'logistic_offer_identity': _OFFER_IDENTITY_1,
                    },
                },
                {
                    'mode_rule_id': _MODE_RULE_ID_2,
                    'mode_rule_settings': {
                        'logistic_offer_identity': _OFFER_IDENTITY_2,
                    },
                },
            ],
            400,
            {
                'code': 'BAD_MODE_RULES_IDS',
                'message': 'invalid mode rules ids',
            },
            id='all mode_rule_id must be the same',
        ),
        pytest.param(
            [
                {
                    'mode_rule_id': _MODE_RULE_ID_2,
                    'mode_rule_settings': {
                        'logistic_offer_identity': _OFFER_IDENTITY_2,
                    },
                },
            ],
            400,
            {
                'code': 'BAD_REQUEST',
                'message': 'only logistics offers supported',
            },
            id='only logistics offers supported',
        ),
        pytest.param(
            [
                {
                    'mode_rule_id': _MODE_RULE_ID_3,
                    'mode_rule_settings': {
                        'logistic_offer_identity': _OFFER_IDENTITY_1,
                    },
                },
            ],
            400,
            {'code': 'BAD_REQUEST', 'message': 'wrong mode_rule_id'},
            id='old rules not work',
        ),
    ],
)
@pytest.mark.now('2021-06-14T04:01:00+03:00')
async def test_scheduled_slots_reservation_bad_input(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        taxi_config,
        mocked_time,
        offers: List[Dict[str, Any]],
        expected_code: int,
        expected_response: Dict[str, Any],
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

    response = await logistic_reservation_create(
        taxi_driver_mode_subscription,
        offers,
        profile.park_id(),
        profile.profile_id(),
    )

    assert response.status_code == expected_code

    assert response.json() == expected_response


@pytest.mark.config(
    API_OVER_DATA_ENABLE_CACHES=True,
    API_OVER_DATA_ENABLE_SPECIFIC_CACHE={'__default__': {'__default__': True}},
    API_OVER_DATA_OPENING_LAG_MS={'__default__': {'__default__': -1}},
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=_MODE_1,
                features={'logistic_workshifts': {}},
                rule_id=_MODE_RULE_ID_1,
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'checked_slots, expected_sql_slots',
    [
        pytest.param(
            [
                _make_mock_slot(
                    _OFFER_IDENTITY_1,
                    '2021-02-01T04:01:00+03:00',
                    '2021-02-01T06:01:00+03:00',
                    None,
                    _QUOTA_NAME_1,
                ),
                _make_mock_slot(
                    _OFFER_IDENTITY_2,
                    '2021-02-04T07:01:00+03:00',
                    '2021-02-04T08:01:00+03:00',
                    None,
                    _QUOTA_NAME_2,
                ),
            ],
            [
                (
                    _SLOT_ID_1.replace('-', ''),
                    dt.datetime(2021, 2, 1, 1, 1, tzinfo=dt.timezone.utc),
                    dt.datetime(2021, 2, 1, 3, 1, tzinfo=dt.timezone.utc),
                    _MODE_1,
                    _OFFER_IDENTITY_1,
                    _QUOTA_NAME_1.replace('-', ''),
                    1,
                    _OFFER_IDENTITY_1,
                    None,
                ),
                (
                    _SLOT_ID_2.replace('-', ''),
                    dt.datetime(2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc),
                    dt.datetime(2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc),
                    _MODE_1,
                    _OFFER_IDENTITY_2,
                    _QUOTA_NAME_2.replace('-', ''),
                    1,
                    _OFFER_IDENTITY_2,
                    None,
                ),
            ],
            id='multiple new book ok',
        ),
        pytest.param(
            [
                _make_mock_slot(
                    _OFFER_IDENTITY_1,
                    '2021-02-01T04:01:00+03:00',
                    '2021-02-01T06:01:00+03:00',
                    None,
                    _QUOTA_NAME_1,
                ),
                _make_mock_slot(
                    _OFFER_IDENTITY_2,
                    '2021-02-04T07:01:00+03:00',
                    '2021-02-04T08:01:00+03:00',
                    None,
                    _QUOTA_NAME_2,
                ),
            ],
            [
                (
                    _SLOT_ID_1.replace('-', ''),
                    dt.datetime(2021, 2, 1, 1, 1, tzinfo=dt.timezone.utc),
                    dt.datetime(2021, 2, 1, 3, 1, tzinfo=dt.timezone.utc),
                    _MODE_1,
                    _OFFER_IDENTITY_1,
                    _QUOTA_NAME_1.replace('-', ''),
                    4,
                    _OFFER_IDENTITY_1,
                    None,
                ),
                (
                    _SLOT_ID_2.replace('-', ''),
                    dt.datetime(2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc),
                    dt.datetime(2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc),
                    _MODE_1,
                    _OFFER_IDENTITY_2,
                    _QUOTA_NAME_2.replace('-', ''),
                    25,
                    _OFFER_IDENTITY_2,
                    None,
                ),
            ],
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_update_slot_quota_query(
                            _QUOTA_NAME_1.replace('-', ''), 3,
                        ),
                        scheduled_slots_tools.make_insert_reservation_query(
                            _SLOT_ID_2.replace('-', ''),
                            _MODE_1,
                            _OFFER_IDENTITY_2,
                            _OFFER_IDENTITY_2,
                            dt.datetime(
                                2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc,
                            ),
                            _QUOTA_NAME_2.replace('-', ''),
                            24,
                            _DBID,
                            _UUID,
                            is_deleted=True,
                        ),
                        scheduled_slots_tools.make_insert_slot_meta_query(
                            _SLOT_ID_2.replace('-', ''),
                        ),
                    ],
                ),
            ],
            id='existing slot, quota and reservation book ok',
        ),
        pytest.param(
            [
                _make_mock_slot(
                    _OFFER_IDENTITY_2_VER2,
                    '2021-02-01T04:01:00+03:00',
                    '2021-02-01T06:01:00+03:00',
                    None,
                    _QUOTA_NAME_2,
                ),
            ],
            [
                (
                    _SLOT_ID_2.replace('-', ''),
                    dt.datetime(2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc),
                    dt.datetime(2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc),
                    _MODE_1,
                    _OFFER_IDENTITY_2,
                    _QUOTA_NAME_2.replace('-', ''),
                    2,
                    _OFFER_IDENTITY_2_VER2,
                    None,
                ),
            ],
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription',
                    queries=[
                        scheduled_slots_tools.make_insert_slot_quota_query(
                            _SLOT_ID_2.replace('-', ''),
                            _MODE_1,
                            _OFFER_IDENTITY_2,
                            dt.datetime(
                                2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc,
                            ),
                            dt.datetime(
                                2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc,
                            ),
                            _QUOTA_NAME_2.replace('-', ''),
                            1,
                        ),
                        scheduled_slots_tools.make_insert_slot_meta_query(
                            _SLOT_ID_2.replace('-', ''),
                        ),
                    ],
                ),
            ],
            id='existing slot with different settings',
        ),
    ],
)
@pytest.mark.now('2021-06-14T04:01:00+03:00')
async def test_scheduled_slots_reservation_in_db(
        taxi_driver_mode_subscription,
        pgsql,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        taxi_config,
        mocked_time,
        checked_slots: List[Dict[str, Any]],
        expected_sql_slots: List[Dict[str, Any]],
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
        '/logistic-supply-conductor/'
        'internal/v1/offer/reservation/check-creation',
    )
    def _check_creation_mock(request):
        return {'items': checked_slots}

    response = await logistic_reservation_create(
        taxi_driver_mode_subscription,
        # This have no impact on test result,
        # because handler logic use data from check-creation api
        [
            {
                'mode_rule_id': _MODE_RULE_ID_1,
                'mode_rule_settings': {
                    'logistic_offer_identity': _OFFER_IDENTITY_1,
                },
            },
        ],
        profile.park_id(),
        profile.profile_id(),
    )

    assert response.status_code == 200

    assert (
        scheduled_slots_tools.get_reservations_by_profile(pgsql, profile)
        == expected_sql_slots
    )


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=_MODE_1,
                features={'logistic_workshifts': {}},
                rule_id=_MODE_RULE_ID_1,
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'check_creation_code, check_creation_message, '
    'check_creation_title, check_creation_subtitle, '
    'check_creation_text',
    [
        pytest.param(
            409,
            'Some 409 error message',
            'Some 409 error title',
            'Some 409 error subtitle',
            'Some 409 error text',
        ),
        pytest.param(
            404,
            'Some 404 error message',
            'Some 404 error title',
            'Some 404 error subtitle',
            'Some 404 error text',
        ),
    ],
)
@pytest.mark.now('2021-06-14T04:01:00+03:00')
async def test_scheduled_slots_reservation_check_creation_fail(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        mockserver,
        mocked_time,
        check_creation_code: int,
        check_creation_message: str,
        check_creation_title: str,
        check_creation_subtitle: str,
        check_creation_text: str,
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

    expected_message = {
        'code': str(check_creation_code),
        'message': check_creation_message,
        'details': {
            'title': check_creation_title,
            'subtitle': check_creation_subtitle,
            'text': check_creation_text,
        },
    }

    @mockserver.json_handler(
        '/logistic-supply-conductor/'
        'internal/v1/offer/reservation/check-creation',
    )
    def check_creation_mock(request):
        nonlocal check_creation_code
        nonlocal expected_message

        return mockserver.make_response(
            json.dumps(expected_message), check_creation_code,
        )

    response = await logistic_reservation_create(
        taxi_driver_mode_subscription,
        # This have no impact on test result,
        # because handler logic use data from check-creation api
        [
            {
                'mode_rule_id': _MODE_RULE_ID_1,
                'mode_rule_settings': {
                    'logistic_offer_identity': _OFFER_IDENTITY_1,
                },
            },
        ],
        profile.park_id(),
        profile.profile_id(),
    )

    assert check_creation_mock.has_calls

    assert response.status_code == check_creation_code
    assert response.json() == expected_message
