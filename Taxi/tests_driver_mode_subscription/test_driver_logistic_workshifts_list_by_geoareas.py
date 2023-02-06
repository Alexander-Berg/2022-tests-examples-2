import copy
import datetime as dt
from typing import Any
from typing import Dict
from typing import List

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scenario
from tests_driver_mode_subscription import scheduled_slots_tools

_PARK_ID = 'park-id-1'
_DRIVER_ID = 'driver-id-1'

_REQUEST_HEADERS = {
    'Accept-Language': 'ru',
    'Timezone': 'Europe/Moscow',
    'User-Agent': 'Taximeter 8.80 (562)',
    'X-YaTaxi-Park-Id': _PARK_ID,
    'X-YaTaxi-Driver-Profile-Id': _DRIVER_ID,
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '8.80 (562)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'X-Ya-Service-Ticket': common.MOCK_TICKET,
}

_REQUEST_BODY = {
    'time_range': {
        'begin': '2033-04-06T08:00:00+00:00',
        'end': '2033-04-06T20:00:00+00:00',
    },
    'viewport_region': {
        'top_left': {'lat': 63.5, 'lon': 52.5},
        'bottom_right': {'lat': 62.5, 'lon': 53.5},
    },
}

_QUOTA_ID_UNKNOWN = 'b923dec8-7a73-435a-a51c-a5348acc8cc3'
_QUOTA_ID_UNBOOKED = 'f5b7045b-ba10-40dc-9c55-e9d0c0f03b98'
_QUOTA_ID_ZERO = 'eb33130f-cc64-4004-a926-47703ac1f69b'
_QUOTA_ID_FULL = 'fd19a297-d465-4ab1-ac9c-067e26a69937'
_QUOTA_ID_ONE_AVAILABLE = '49900a7c-e0d8-4720-a361-caa22a496b91'
_QUOTA_ID_THREE_AVAILABLE = 'c373f36d-3a62-4167-8c29-e7de8a227942'

_QUOTAS: Dict[str, Any] = {
    _QUOTA_ID_UNKNOWN: {
        'expected_subtitle': 'Нет свободных мест',
        'current_count': None,
        'is_booked': False,
        'expected_availability_state': 'quota_is_over',
        'expected_booking_state': 'not_booked',
        'slot_id': '76a3176e-f759-44bc-8fc7-43ea091bd68b',
        'expected_description_value': '0 из 0',
        'expected_icon_value': 'forbidden',
    },
    _QUOTA_ID_UNBOOKED: {
        'expected_subtitle': '1 место',
        'current_count': None,
        'is_booked': False,
        'expected_availability_state': 'available',
        'expected_booking_state': 'not_booked',
        'slot_id': '6c2ec7ec-0df0-4fe0-8aa1-6b01f91a9b6e',
        'expected_description_value': '1 из 1',
        'expected_icon_value': 'waiting',
    },
    _QUOTA_ID_ZERO: {
        'expected_subtitle': '100 мест',
        'current_count': 0,
        'is_booked': False,
        'expected_availability_state': 'available',
        'expected_booking_state': 'not_booked',
        'slot_id': 'acb9f9c7-3774-4f19-8c9c-8257c8400cbb',
        'expected_description_value': '100 из 100',
        'expected_icon_value': 'waiting',
    },
    _QUOTA_ID_FULL: {
        'expected_subtitle': 'Нет свободных мест',
        'current_count': 100,
        'is_booked': False,
        'expected_availability_state': 'quota_is_over',
        'expected_booking_state': 'not_booked',
        'slot_id': 'd9200161-e34f-4aad-bc9d-3dc987aece5e',
        'expected_description_value': '0 из 100',
        'expected_icon_value': 'forbidden',
    },
    _QUOTA_ID_ONE_AVAILABLE: {
        'expected_subtitle': '1 место',
        'current_count': 99,
        'is_booked': False,
        'expected_availability_state': 'available',
        'expected_booking_state': 'not_booked',
        'slot_id': '7d7cc4cb-6297-48e5-b61d-6f8a27c7f2c3',
        'expected_description_value': '1 из 100',
        'expected_icon_value': 'waiting',
    },
    _QUOTA_ID_THREE_AVAILABLE: {
        'expected_subtitle': '3 места',
        'current_count': 97,
        'is_booked': True,
        'expected_availability_state': 'booked',
        'expected_booking_state': 'ready',
        'slot_id': '9fc85f28-f787-451f-8900-211330921c94',
        'expected_description_value': '3 из 100',
        'expected_icon_value': 'completed',
    },
}

_OFFER_TEMPLATE = {
    'identity': {
        'rule_version': 2,
        'slot_id': '6c2ec7ec-0df0-4fe0-8aa1-6b01f91a9b6e',
    },
    'description': {
        'captions': {},
        'icon': 'waiting',
        'items': [
            {
                'content_code_hint': 'expiration_timestamp',
                'text': 'Localized subtitle',
                'title': 'Localized title',
                'value': '2033-04-06T19:00:00+00:00',
                'free_time_end': '2033-04-06T19:00:00+00:00',
                'extra_time_end': '2033-04-06T19:05:00+00:00',
            },
            {'content_code_hint': 'capacity'},
        ],
    },
    'requirements': [
        {
            'is_satisfied': True,
            'items': [
                {
                    'captions': {
                        'title': 'Lorem ipsum',
                        'subtitle': 'Dolor sit\namet',
                    },
                    'is_satisfied': False,
                },
                {
                    'captions': {'title': 'Consectetur', 'subtitle': ''},
                    'is_satisfied': True,
                },
            ],
        },
    ],
    'time_range': {
        'begin': '2033-04-06T08:00:00+00:00',
        'end': '2033-04-06T20:00:00+00:00',
    },
    'visibility_info': {},
    'item_view': {'icon': 'waiting', 'captions': {'title': '12:32 - 17:32'}},
    'allowed_transport_types': 'PLACEHOLDER',
    'activation_state': 'starting',
    'cancellation_opportunity': {
        'offer': {'fine_value': {'value': '123', 'currency_code': 'rur'}},
    },
    'quota_id': _QUOTA_ID_UNBOOKED,
}

_OFFER_LIST_BY_GEOAREAS_RESPONSE = {
    'geoareas': [
        {
            'display_features': {'pin_size': 'big'},
            'offers': [],
            'pin_point': {'lat': 63.0, 'lon': 53.0},
            'polygon': {
                'coordinates': [
                    [
                        {'lat': 62.0, 'lon': 54.0},
                        {'lat': 64.0, 'lon': 54.0},
                        {'lat': 64.0, 'lon': 52.0},
                        {'lat': 62.0, 'lon': 52.0},
                        {'lat': 62.0, 'lon': 54.0},
                    ],
                ],
            },
            'title': 'The Second Geoarea',
        },
    ],
}


def _build_response_offer(
        mode_rule_id: str,
        slot_id: str,
        subtitle: str,
        booking_state: str,
        availability_state: str,
        description_value: str,
        icon: str,
):
    return {
        'mode_rule_id': mode_rule_id,
        'mode_rule_settings': {
            'logistic_offer_identity': {'rule_version': 2, 'slot_id': slot_id},
        },
        'description': {
            'captions': {},
            'icon': 'waiting',
            'items': [
                {
                    'content_type': 'expiration_timestamp',
                    'text': 'Localized subtitle',
                    'title': 'Localized title',
                    'value': '2033-04-06T19:00:00+00:00',
                    'paused_until': '2033-04-06T19:00:00+00:00',
                    'pause_penalty_deadline': '2033-04-06T19:05:00+00:00',
                },
                {'title': 'Свободных мест', 'value': description_value},
            ],
        },
        'requirements': [
            {
                'is_satisfied': True,
                'items': [
                    {
                        'captions': {
                            'title': 'Lorem ipsum',
                            'subtitle': 'Dolor sit\namet',
                        },
                        'is_satisfied': False,
                    },
                    {
                        'captions': {'title': 'Consectetur', 'subtitle': ''},
                        'is_satisfied': True,
                    },
                ],
            },
        ],
        'time_range': {
            'begin': '2033-04-06T08:00:00+00:00',
            'end': '2033-04-06T20:00:00+00:00',
        },
        'item_view': {
            'icon': icon,
            'captions': {'title': '12:32 - 17:32', 'subtitle': subtitle},
        },
        'activation_state': 'starting',
        'cancellation_opportunity': {
            'offer': {'fine_value': {'value': '123', 'currency_code': 'rur'}},
        },
        'booking_state': booking_state,
        'availability_state': availability_state,
    }


def _build_dms_response(offers: List[Dict[str, Any]], offers_available: int):
    return {
        'geoareas': [
            {
                'title': 'The Second Geoarea',
                'display_features': {
                    'pin_size': 'big',
                    'text': str(offers_available),
                },
                'slots': offers,
                'pin_point': {'lat': 63.0, 'lon': 53.0},
                'polygon': {
                    'coordinates': [
                        [
                            {'lat': 62.0, 'lon': 54.0},
                            {'lat': 64.0, 'lon': 54.0},
                            {'lat': 64.0, 'lon': 52.0},
                            {'lat': 62.0, 'lon': 52.0},
                            {'lat': 62.0, 'lon': 54.0},
                        ],
                    ],
                },
            },
        ],
    }


def _generate_lsc_response_simple(allowed_transport_types):
    result = copy.deepcopy(_OFFER_LIST_BY_GEOAREAS_RESPONSE)

    offer = copy.deepcopy(_OFFER_TEMPLATE)
    offer['allowed_transport_types'] = allowed_transport_types

    result['geoareas'][0]['offers'].append(offer)

    return result


def _generate_lsc_response_with_different_quotas():
    result = copy.deepcopy(_OFFER_LIST_BY_GEOAREAS_RESPONSE)

    geoarea = result['geoareas'][0]

    for quota_id, quota_params in _QUOTAS.items():
        offer = copy.deepcopy(_OFFER_TEMPLATE)

        offer['allowed_transport_types'] = ['auto', 'bicycle']
        offer['quota_id'] = quota_id
        offer['identity']['slot_id'] = quota_params['slot_id']

        geoarea['offers'].append(offer)

    return result


def _prepare_quotas(pgsql, driver_profile: driver.Profile):
    cursor = pgsql['driver_mode_subscription'].cursor()

    for quota_id, quota_params in _QUOTAS.items():
        if quota_params['current_count'] is None:
            continue

        slot_name = quota_params['slot_id']
        cursor.execute(
            scheduled_slots_tools.make_insert_slot_quota_query(
                slot_name.replace('-', ''),
                _LOGISTIC_WORK_MODE_AUTO.rule_name,
                {'slot_id': slot_name, 'rule_version': 1},
                dt.datetime.fromisoformat('2019-05-01T00:00:00+03:00'),
                dt.datetime.fromisoformat('2019-05-01T23:59:00+03:00'),
                quota_id.replace('-', ''),
                quota_params['current_count'],
            ),
        )

        if quota_params['is_booked']:
            cursor.execute(
                scheduled_slots_tools.make_slot_reservation_query(
                    _LOGISTIC_WORK_MODE_AUTO.rule_name,
                    slot_name.replace('-', ''),
                    driver_profile,
                ),
            )


_LOGISTIC_WORK_MODE_AUTO_NAME = 'logistic_work_mode_auto'
_LOGISTIC_WORK_MODE_BICYCLE_NAME = 'logistic_work_mode_bicycle'
_LOGISTIC_WORK_MODE_EMPTY_NAME = 'logistic_work_mode_empty'
_NOT_LOGISTIC_WORK_MODE_AUTO_NAME = 'not_logistic_work_mode_auto'
_NOT_LOGISTIC_WORK_MODE_BICYCLE_NAME = 'not_logistic_work_mode_bicycle'
_NOT_LOGISTIC_WORK_MODE_PEDESTRIAN_NAME = 'not_logistic_work_mode_pedestrian'
_NOT_LOGISTIC_WORK_MODE_EMPTY_NAME = 'not_logistic_work_mode_empty'

_LOGISTIC_WORK_MODE_AUTO_ID = 'a883a23977484000b870f0cfcc84e1f9'
_LOGISTIC_WORK_MODE_BICYCLE_ID = 'c590b29d0fbe4b4d81f8780126daab12'
_LOGISTIC_WORK_MODE_EMPTY_ID = 'c1041baf4a074d75941b70a5bd49fefd'
_NOT_LOGISTIC_WORK_MODE_AUTO_ID = '2dc1c90f5fe14809bf12ee0bebc8423c'
_NOT_LOGISTIC_WORK_MODE_BICYCLE_ID = '25259962734849eda5acddd4109496a0'
_NOT_LOGISTIC_WORK_MODE_PEDESTRIAN_ID = 'ec45c0415e68491da5f3bac951dc4222'
_NOT_LOGISTIC_WORK_MODE_EMPTY_ID = '4fb7f2cc69c44b1ebaea6b57b15059a8'

_LOGISTIC_WORK_MODE_AUTO = mode_rules.Patch(
    rule_name=_LOGISTIC_WORK_MODE_AUTO_NAME,
    features={'logistic_workshifts': {}, 'active_transport': {'type': 'auto'}},
    rule_id=_LOGISTIC_WORK_MODE_AUTO_ID,
)

_LOGISTIC_WORK_MODE_BICYCLE = mode_rules.Patch(
    rule_name=_LOGISTIC_WORK_MODE_BICYCLE_NAME,
    features={
        'logistic_workshifts': {},
        'active_transport': {'type': 'bicycle'},
    },
    rule_id=_LOGISTIC_WORK_MODE_BICYCLE_ID,
)

_LOGISTIC_WORK_MODE_EMPTY = mode_rules.Patch(
    rule_name=_LOGISTIC_WORK_MODE_EMPTY_NAME,
    features={'logistic_workshifts': {}},
    rule_id=_LOGISTIC_WORK_MODE_EMPTY_ID,
)

_NOT_LOGISTIC_WORK_MODE_AUTO = mode_rules.Patch(
    rule_name=_NOT_LOGISTIC_WORK_MODE_AUTO_NAME,
    features={'active_transport': {'type': 'auto'}},
    rule_id=_NOT_LOGISTIC_WORK_MODE_AUTO_ID,
)

_NOT_LOGISTIC_WORK_MODE_BICYCLE = mode_rules.Patch(
    rule_name=_NOT_LOGISTIC_WORK_MODE_BICYCLE_NAME,
    features={'active_transport': {'type': 'bicycle'}},
    rule_id=_NOT_LOGISTIC_WORK_MODE_BICYCLE_ID,
)

_NOT_LOGISTIC_WORK_MODE_PEDESTRIAN = mode_rules.Patch(
    rule_name=_NOT_LOGISTIC_WORK_MODE_PEDESTRIAN_NAME,
    features={'active_transport': {'type': 'pedestrian'}},
    rule_id=_NOT_LOGISTIC_WORK_MODE_PEDESTRIAN_ID,
)

_NOT_LOGISTIC_WORK_MODE_EMPTY = mode_rules.Patch(
    rule_name=_NOT_LOGISTIC_WORK_MODE_EMPTY_NAME,
    features={},
    rule_id=_NOT_LOGISTIC_WORK_MODE_EMPTY_ID,
)


@pytest.mark.config(
    API_OVER_DATA_ENABLE_CACHES=True,
    API_OVER_DATA_ENABLE_SPECIFIC_CACHE={'__default__': {'__default__': True}},
    API_OVER_DATA_OPENING_LAG_MS={'__default__': {'__default__': -1}},
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            _LOGISTIC_WORK_MODE_AUTO,
            _LOGISTIC_WORK_MODE_BICYCLE,
            _LOGISTIC_WORK_MODE_EMPTY,
            _NOT_LOGISTIC_WORK_MODE_AUTO,
            _NOT_LOGISTIC_WORK_MODE_BICYCLE,
            _NOT_LOGISTIC_WORK_MODE_PEDESTRIAN,
            _NOT_LOGISTIC_WORK_MODE_EMPTY,
        ],
    ),
)
@pytest.mark.parametrize(
    'prev_mode_rule, expected_mode_rule, allowed_transport_types',
    [
        pytest.param(
            _LOGISTIC_WORK_MODE_AUTO,
            _LOGISTIC_WORK_MODE_AUTO,
            ['auto', 'bicycle'],
        ),
        pytest.param(
            _NOT_LOGISTIC_WORK_MODE_AUTO,
            _LOGISTIC_WORK_MODE_AUTO,
            ['auto', 'bicycle'],
        ),
        pytest.param(
            _LOGISTIC_WORK_MODE_BICYCLE,
            _LOGISTIC_WORK_MODE_BICYCLE,
            ['auto', 'bicycle'],
        ),
        pytest.param(
            _NOT_LOGISTIC_WORK_MODE_BICYCLE,
            _LOGISTIC_WORK_MODE_BICYCLE,
            ['auto', 'bicycle'],
        ),
        pytest.param(
            _LOGISTIC_WORK_MODE_EMPTY, _LOGISTIC_WORK_MODE_EMPTY, ['auto'],
        ),
        pytest.param(
            _NOT_LOGISTIC_WORK_MODE_EMPTY, _LOGISTIC_WORK_MODE_EMPTY, ['auto'],
        ),
        pytest.param(
            _NOT_LOGISTIC_WORK_MODE_PEDESTRIAN, None, ['auto', 'bicycle'],
        ),
        pytest.param(_LOGISTIC_WORK_MODE_AUTO, None, ['bicycle']),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_list_by_geoareas(
        mockserver,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        prev_mode_rule,
        expected_mode_rule,
        allowed_transport_types,
):
    test_profile = driver.Profile(f'{_PARK_ID}_{_DRIVER_ID}')
    scene = scenario.Scene(
        profiles={test_profile: driver.Mode(prev_mode_rule.rule_name)},
        udid='test-driver-id',
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    await taxi_driver_mode_subscription.invalidate_caches()

    lsc_response = _generate_lsc_response_simple(allowed_transport_types)

    @mockserver.json_handler(
        '/logistic-supply-conductor/internal/v1/offer/list-by-geoareas',
    )
    def _logistic_supply_conductor_list_by_geoareas(request):
        return lsc_response

    response = await taxi_driver_mode_subscription.post(
        '/driver/v1/logistic-workshifts/slots/list-by-geoareas',
        json=_REQUEST_BODY,
        headers=_REQUEST_HEADERS,
    )

    assert response.status_code == 200, str(response.reason)

    if expected_mode_rule is None:
        assert not response.json()['geoareas']
    else:
        quota_params = _QUOTAS[_QUOTA_ID_UNBOOKED]
        assert response.json() == _build_dms_response(
            [
                _build_response_offer(
                    expected_mode_rule.rule_id,
                    quota_params['slot_id'],
                    quota_params['expected_subtitle'],
                    quota_params['expected_booking_state'],
                    quota_params['expected_availability_state'],
                    '1 из 1',
                    'waiting',
                ),
            ],
            1,
        )


@pytest.mark.config(
    API_OVER_DATA_ENABLE_CACHES=True,
    API_OVER_DATA_ENABLE_SPECIFIC_CACHE={'__default__': {'__default__': True}},
    API_OVER_DATA_OPENING_LAG_MS={'__default__': {'__default__': -1}},
)
@pytest.mark.mode_rules(rules=mode_rules.patched([_LOGISTIC_WORK_MODE_AUTO]))
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_quotas_available_subtitle(
        mockserver,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        driver_authorizer,
        pgsql,
):
    test_profile = driver.Profile(f'{_PARK_ID}_{_DRIVER_ID}')
    scene = scenario.Scene(
        profiles={
            test_profile: driver.Mode(_LOGISTIC_WORK_MODE_AUTO.rule_name),
        },
        udid='test-driver-id',
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    _prepare_quotas(pgsql, test_profile)

    await taxi_driver_mode_subscription.invalidate_caches()

    lsc_response = _generate_lsc_response_with_different_quotas()

    @mockserver.json_handler(
        '/logistic-supply-conductor/internal/v1/offer/list-by-geoareas',
    )
    def _logistic_supply_conductor_list_by_geoareas(request):
        return lsc_response

    response = await taxi_driver_mode_subscription.post(
        '/driver/v1/logistic-workshifts/slots/list-by-geoareas',
        json=_REQUEST_BODY,
        headers=_REQUEST_HEADERS,
    )

    assert response.status_code == 200, str(response.reason)
    assert response.json() == _build_dms_response(
        [
            _build_response_offer(
                _LOGISTIC_WORK_MODE_AUTO_ID,
                quota_params['slot_id'],
                quota_params['expected_subtitle'],
                quota_params['expected_booking_state'],
                quota_params['expected_availability_state'],
                quota_params['expected_description_value'],
                quota_params['expected_icon_value'],
            )
            for quota_id, quota_params in _QUOTAS.items()
        ],
        3,
    )
