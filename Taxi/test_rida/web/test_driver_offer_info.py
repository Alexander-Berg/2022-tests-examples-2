import dataclasses
import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from test_rida import experiments_utils
from test_rida import helpers
from test_rida import maps_utils


@pytest.mark.mongodb_collections('rida_drivers', 'rida_offers')
@pytest.mark.filldb()
@pytest.mark.parametrize(
    ['user_id', 'offer_guid', 'expected_status'],
    [
        pytest.param(
            1234, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F', 200, id='happy_path',
        ),
        pytest.param(
            1234,
            '9373F48B-C6B4-4812-A2D0-413F3AFAAAAA',
            404,
            id='offer_not_found',
        ),
        pytest.param(
            3456,
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F',
            404,
            id='user_driver_rel_not_found',
        ),
        pytest.param(
            1234,
            '9373F48B-C6B4-4812-A2D0-413F3AFB0001',
            406,
            id='driver_guid_mismatch',
        ),
    ],
)
async def test_errors(
        taxi_rida_web,
        mongodb,
        mockserver,
        user_id: int,
        offer_guid: str,
        expected_status: int,
):
    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/distancematrix/json',
    )
    def _mock_google_maps(request):
        return mockserver.make_response(
            status=200,
            json=maps_utils.make_gmaps_distance_response(
                duration=510, distance=2300,
            ),
        )

    headers = helpers.get_auth_headers(user_id=user_id)
    response = await taxi_rida_web.post(
        '/v3/driver/offer/info',
        headers=headers,
        json={'offer_guid': offer_guid},
    )
    assert response.status == expected_status


@experiments_utils.get_distance_info_config('ruler', 'v3/driver/offer/info')
@pytest.mark.translations(
    rida={
        # we do not want to show information in this bid status
        # 'driver_offer_info.information.text.accepted': {'en': 'accepted'},
        'driver_offer_info.information.text.pending': {
            'en': 'Passenger is thinking',
        },
        'driver_offer_info.information.text.declined': {'en': 'declined'},
        'driver_offer_info.information.text.expired': {'en': 'expired'},
        'driver_offer_info.information.text.driver_canceled': {
            'en': 'driver_canceled',
        },
        'driver_offer_info.information.text.passenger_canceled': {
            'en': 'passenger_canceled',
        },
        'driver_offer_info.information.text.accepted_another_driver': {
            'en': 'accepted_another_driver',
        },
        'driver_offer_info.information.text.declined_without_open': {
            'en': 'declined_without_open',
        },
    },
)
@pytest.mark.parametrize(
    [
        'bid_status',
        'expected_can_make_bid',
        'expected_text',
        'expect_driver_bid',
    ],
    [
        pytest.param('ACCEPTED', False, None, True, id='ACCEPTED'),
        pytest.param(
            'PENDING', False, 'Passenger is thinking', True, id='PENDING',
        ),
        pytest.param('DECLINED', True, 'declined', True, id='DECLINED'),
        pytest.param('EXPIRED', True, 'expired', True, id='EXPIRED'),
        pytest.param(
            'DRIVER_CANCELED',
            True,
            'driver_canceled',
            False,
            id='DRIVER_CANCELED',
        ),
        pytest.param(
            'PASSENGER_CANCELED',
            True,
            'passenger_canceled',
            True,
            id='PASSENGER_CANCELED',
        ),
        pytest.param(
            'ACCEPTED_ANOTHER_DRIVER',
            True,
            'accepted_another_driver',
            True,
            id='ACCEPTED_ANOTHER_DRIVER',
        ),
        pytest.param(
            'DECLINED_WITHOUT_OPEN',
            True,
            'declined_without_open',
            True,
            id='DECLINED_WITHOUT_OPEN',
        ),
    ],
)
async def test_can_make_bid_in_different_bid_statuses(
        taxi_rida_web,
        mongodb,
        mockserver,
        bid_status,
        expected_can_make_bid,
        expected_text,
        expect_driver_bid,
):
    mongodb.rida_bids.update(
        {'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A'},
        {'$set': {'bid_status': bid_status}},
    )
    headers = helpers.get_auth_headers(user_id=1234)
    response = await taxi_rida_web.post(
        '/v3/driver/offer/info',
        headers=headers,
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F'},
    )
    assert response.status == 200
    data = await response.json()
    offer = data['data']['offer']
    assert offer['can_make_bid'] == expected_can_make_bid
    if expected_text:
        assert offer['information']['text'] == expected_text
        assert offer['bid_status_log'] == [
            {'text': expected_text, 'color': '#666666'},
        ]
    else:
        assert 'information' not in offer
        assert offer['bid_status_log'] == []

    if expect_driver_bid:
        assert 'driver_bid' in offer
    else:
        assert 'driver_bid' not in offer


@experiments_utils.get_distance_info_config('ruler', 'v3/driver/offer/info')
@pytest.mark.translations(
    rida={
        'driver_offer_info.information.text.restrict': {'en': 'restrict'},
        'driver_offer_info.information.text.allow': {'en': 'allow'},
    },
)
@pytest.mark.parametrize(
    ['bid_exists', 'expected_can_make_bid', 'expected_text'],
    [
        pytest.param(True, False, 'restrict', id='pending_bid_exists'),
        pytest.param(False, True, 'allow', id='no_one_bid_exists'),
    ],
)
async def test_restrict_and_first_bid(
        taxi_rida_web,
        mongodb,
        mockserver,
        bid_exists: bool,
        expected_can_make_bid: bool,
        expected_text: str,
):
    if not bid_exists:
        mongodb.rida_bids.remove(
            {'bid_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5A'},
        )
    headers = helpers.get_auth_headers(user_id=1234)
    response = await taxi_rida_web.post(
        '/v3/driver/offer/info',
        headers=headers,
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFB0002'},
    )
    assert response.status == 200
    data = await response.json()
    offer = data['data']['offer']
    assert offer['can_make_bid'] == expected_can_make_bid
    assert offer['information']['text'] == expected_text


@dataclasses.dataclass
class DriverSuggestPriceExpCondition:
    percent_bigger_than: Optional[float] = None
    percent_smaller_than: Optional[float] = None
    bigger_by: Optional[float] = None
    smaller_by: Optional[float] = None


def _get_driver_suggest_price_exp_marks(
        condition_clauses: List[DriverSuggestPriceExpCondition],
        empty_default: bool = False,
):
    conditions = list()
    for i, condition_clause in enumerate(condition_clauses):
        condition = dataclasses.asdict(condition_clause)
        condition = {k: v for k, v in condition.items() if v is not None}
        condition['view'] = {
            'suggested_price_tk': 'driver_suggested_price',
            'suggested_price_color': f'#33300{i}',
            'comment_tk': 'driver_suggested_price_comment',
            'comment_color': f'#33300{i}',
        }
        conditions.append(condition)
    default_view = {
        'suggested_price_tk': 'default_driver_suggested_price',
        'comment_tk': 'default_driver_suggested_price_comment',
    }
    exp_mark = pytest.mark.client_experiments3(
        consumer='rida',
        config_name='rida_driver_suggested_price',
        args=experiments_utils.get_default_user_args(),
        value={
            'default_view': {} if empty_default else default_view,
            'conditions': conditions,
        },
    )
    return [exp_mark]


@experiments_utils.get_distance_info_config('ruler', 'v3/driver/offer/info')
@pytest.mark.config(
    CURRENCY_FORMATTING_RULES={
        '__default__': {'__default__': 0, 'surge': 1, 'ip': 2},
        'NGN': {'__default__': 0},
    },
)
@pytest.mark.translations(
    rida={
        'driver_offer_info.information.text.restrict': {'en': 'restrict'},
        'driver_suggested_price': {'en': '{suggested_price} {currency}'},
        'driver_suggested_price_comment': {'en': 'Great deal!'},
        'default_driver_suggested_price': {'en': 'DEFAULT PRICE'},
        'default_driver_suggested_price_comment': {'en': 'DEFAULT COMMENT'},
    },
)
@pytest.mark.parametrize(
    ['offer_guid', 'country_id', 'expected_additional_info_rows'],
    [
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFB0002',
            2,
            None,
            marks=_get_driver_suggest_price_exp_marks(
                condition_clauses=[], empty_default=True,
            ),
            id='empty_default_value_only',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFB0002',
            2,
            [
                {'text': 'DEFAULT PRICE', 'color': '#000000'},
                {'text': 'DEFAULT COMMENT', 'color': '#000000'},
            ],
            marks=_get_driver_suggest_price_exp_marks(condition_clauses=[]),
            id='default_value_only',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFB0002',
            2,
            [
                {'text': 'DEFAULT PRICE', 'color': '#000000'},
                {'text': 'DEFAULT COMMENT', 'color': '#000000'},
            ],
            marks=_get_driver_suggest_price_exp_marks(
                condition_clauses=[
                    DriverSuggestPriceExpCondition(bigger_by=9001),
                ],
            ),
            id='no_matching_clause',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFB0002',
            2,
            [
                {'text': '1,000 NGN', 'color': '#333000'},
                {'text': 'Great deal!', 'color': '#333000'},
            ],
            marks=_get_driver_suggest_price_exp_marks(
                condition_clauses=[
                    DriverSuggestPriceExpCondition(bigger_by=100),
                ],
            ),
            id='matching_bigger_by_clause',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFB0002',
            2,
            [
                {'text': '1,000 NGN', 'color': '#333000'},
                {'text': 'Great deal!', 'color': '#333000'},
            ],
            marks=_get_driver_suggest_price_exp_marks(
                condition_clauses=[
                    DriverSuggestPriceExpCondition(percent_bigger_than=1.1),
                ],
            ),
            id='matching_percent_bigger_than_clause',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFB0003',
            2,
            [
                {'text': '1,300 NGN', 'color': '#333000'},
                {'text': 'Great deal!', 'color': '#333000'},
            ],
            marks=_get_driver_suggest_price_exp_marks(
                condition_clauses=[
                    DriverSuggestPriceExpCondition(smaller_by=100),
                ],
            ),
            id='matching_smaller_by_clause',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFB0003',
            2,
            [
                {'text': '1,300 NGN', 'color': '#333000'},
                {'text': 'Great deal!', 'color': '#333000'},
            ],
            marks=_get_driver_suggest_price_exp_marks(
                condition_clauses=[
                    DriverSuggestPriceExpCondition(percent_smaller_than=0.9),
                ],
            ),
            id='matching_percent_smaller_than_clause',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFB0002',
            2,
            [
                {'text': '1,000 NGN', 'color': '#333001'},
                {'text': 'Great deal!', 'color': '#333001'},
            ],
            marks=_get_driver_suggest_price_exp_marks(
                condition_clauses=[
                    DriverSuggestPriceExpCondition(bigger_by=150),
                    DriverSuggestPriceExpCondition(bigger_by=100),
                    DriverSuggestPriceExpCondition(bigger_by=50),
                ],
            ),
            id='matching_first_correct_clause',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFB0002',
            2,
            [
                {'text': '1,000 NGN', 'color': '#333000'},
                {'text': 'Great deal!', 'color': '#333000'},
            ],
            marks=_get_driver_suggest_price_exp_marks(
                condition_clauses=[
                    DriverSuggestPriceExpCondition(
                        bigger_by=100, percent_bigger_than=1.1,
                    ),
                ],
            ),
            id='matching_multiple_rules_clause',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFB0002',
            2,
            [
                {'text': 'DEFAULT PRICE', 'color': '#000000'},
                {'text': 'DEFAULT COMMENT', 'color': '#000000'},
            ],
            marks=_get_driver_suggest_price_exp_marks(
                condition_clauses=[
                    DriverSuggestPriceExpCondition(
                        bigger_by=100, percent_bigger_than=1.2,
                    ),
                ],
            ),
            id='not_matching_multiple_rules_clause',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFB0002',
            13,
            [
                {'text': '1,000 SLL', 'color': '#333000'},
                {'text': 'Great deal!', 'color': '#333000'},
            ],
            marks=_get_driver_suggest_price_exp_marks(
                condition_clauses=[
                    DriverSuggestPriceExpCondition(bigger_by=100),
                ],
            ),
            id='Sierra_Leone_driver',
        ),
    ],
)
async def test_driver_suggested_price_exp(
        web_app_client,
        mockserver,
        offer_guid: str,
        country_id: int,
        mongodb,
        expected_additional_info_rows: Optional[List[Dict[str, Any]]],
):
    mongodb.rida_offers.update_one(
        {'offer_guid': offer_guid}, {'$set': {'country_id': country_id}},
    )
    response = await web_app_client.post(
        '/v3/driver/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': offer_guid},
    )
    assert response.status == 200
    data = await response.json()
    additional_info = data['data']['offer'].get('additional_info')
    expected_additional_info = None
    if expected_additional_info_rows is not None:
        expected_additional_info = list()
        for row in expected_additional_info_rows:
            expected_additional_info.append({'type': 1, 'data': row})
        expected_additional_info.append({'type': 101, 'data': {}})
    assert additional_info == expected_additional_info


PRICE_VALIDATION_EXP_ARGS = experiments_utils.PriceValidationSettingsExpArgs(
    country_id=2,
    zone_id=0,
    is_driver=True,
    user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5E',
    device_uuid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
)


@experiments_utils.get_distance_info_config('ruler', 'v3/driver/offer/info')
@pytest.mark.parametrize(
    ['expected_min_value', 'expected_max_value'],
    [
        pytest.param(0, 111200, id='price_restrictions_exp_disabled'),
        pytest.param(
            800,
            1400,
            marks=experiments_utils.get_price_validation_marks(
                PRICE_VALIDATION_EXP_ARGS,
                bid_min_value=800,
                bid_max_value=1400,
            ),
            id='price_restrictions_exp_static_value_borders',
        ),
        pytest.param(
            900,
            1300,
            marks=experiments_utils.get_price_validation_marks(
                PRICE_VALIDATION_EXP_ARGS,
                bid_min_percent=0.8,
                bid_max_percent=1.2,
            ),
            id='price_restrictions_exp_percent_value_borders',
        ),
    ],
)
async def test_bid_settings(
        web_app_client,
        mockserver,
        expected_min_value: float,
        expected_max_value: float,
):
    response = await web_app_client.post(
        '/v3/driver/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F'},
    )
    assert response.status == 200
    data = await response.json()
    bid_settings = data['data']['offer']['bid_settings']
    expected_bid_settings = {
        'button_text_template': 'Accept for {price} NGN',
        'button_text_price_key': '{price}',
        'default_price': 1111.59,
        'is_price_change_allowed': True,
        'min_price': expected_min_value,
        'max_price': expected_max_value,
        'additional_info': [],
    }
    assert bid_settings == expected_bid_settings


async def test_optional_avatar(web_app_client, mockserver):
    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/distancematrix/json',
    )
    def _mock_google_maps(request):
        return mockserver.make_response(
            status=200, json=maps_utils.make_gmaps_distance_response(1, 1),
        )

    response = await web_app_client.post(
        '/v3/driver/offer/info',
        headers=helpers.get_auth_headers(user_id=1449),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFB000Z'},
    )
    assert response.status == 200
    data = await response.json()
    user = data['data']['offer']['user']
    assert user.get('avatar') is None


def _build_optional_template(
        tanker_key: str = 'driver_offer_info.comment',
        is_optional: bool = True,
):
    return [{'tanker_key': tanker_key, 'is_optional': is_optional}]


@pytest.mark.translations(
    rida={'driver_offer_info.comment': {'en': '{comment}'}},
    tariff={
        'currency.ngn': {'en': 'NGN'},
        'currency_with_sign.default': {'en': '$VALUE$ $SIGN$$CURRENCY$'},
    },
)
@pytest.mark.parametrize(
    ['comment'],
    [
        pytest.param(
            None,
            marks=experiments_utils.get_offer_info_units(
                _build_optional_template(),
            ),
            id='comment_is_none',
        ),
        pytest.param(
            '',
            marks=experiments_utils.get_offer_info_units(
                _build_optional_template(),
            ),
            id='empty_string_comment',
        ),
        pytest.param(
            'I made a comment',
            marks=experiments_utils.get_offer_info_units(
                _build_optional_template(),
            ),
            id='valid_comment',
        ),
    ],
)
async def test_optional_additional_route_info(
        web_app_client, mockserver, mongodb, comment,
):
    mongodb.rida_offers.update(
        {'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFB000Z'},
        {'$set': {'comment': comment}},
    )

    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/distancematrix/json',
    )
    def _mock_google_maps(request):
        return mockserver.make_response(
            status=200,
            json=maps_utils.make_gmaps_distance_response(
                duration=510, distance=2300,
            ),
        )

    response = await web_app_client.post(
        '/v3/driver/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFB000Z'},
    )
    assert response.status == 200
    data = await response.json()
    offer = data['data']['offer']
    additional_info = offer.get('additional_info')

    if comment:
        assert additional_info
        comment_additional_info = additional_info[-2]
        assert comment_additional_info['data']['text'] == comment
        assert offer['comment'] == ''
    else:
        assert not additional_info


@pytest.mark.translations(
    rida={'driver_offer_info.comment': {'en': '{comment}'}},
    tariff={
        'currency.ngn': {'en': 'NGN'},
        'currency_with_sign.default': {'en': '$VALUE$ $SIGN$$CURRENCY$'},
    },
)
@pytest.mark.parametrize(
    ['offer_guid', 'router_times_called'],
    [
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFB000Z', 1, id='pending_offer',
        ),
        pytest.param(
            '9373F48B-C6B4-4812-A2D0-413F3AFBAD5F', 0, id='driving_offer',
        ),
    ],
)
async def test_using_router(
        web_app_client, mockserver, offer_guid, router_times_called,
):
    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/distancematrix/json',
    )
    def _mock_google_maps(request):
        return mockserver.make_response(
            status=200,
            json=maps_utils.make_gmaps_distance_response(
                duration=510, distance=2300,
            ),
        )

    response = await web_app_client.post(
        '/v3/driver/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': offer_guid},
    )
    assert response.status == 200
    assert _mock_google_maps.times_called == router_times_called


@pytest.mark.translations(
    rida={
        'valid_tanker_key': {'en': '{driver_to_start_duration}'},
        'invalid_template': {'en': '{unknown_template}'},
    },
    tariff={
        'currency.ngn': {'en': 'NGN'},
        'currency_with_sign.default': {'en': '$VALUE$ $SIGN$$CURRENCY$'},
    },
)
@pytest.mark.parametrize(
    ['expected_status'],
    [
        pytest.param(
            200,
            marks=experiments_utils.get_offer_info_units(
                _build_optional_template('valid_tanker_key'),
            ),
            id='valid_tanker_key',
        ),
        pytest.param(
            200,
            marks=experiments_utils.get_offer_info_units(
                [{'tanker_key': 'invalid'}],
            ),
            id='invalid_tanker_key_allows_optional',
        ),
        pytest.param(
            500,
            marks=experiments_utils.get_offer_info_units(
                _build_optional_template('invalid', False),
            ),
            id='invalid_tanker_key_does_not_allow_optional',
        ),
        pytest.param(
            500,
            marks=experiments_utils.get_offer_info_units(
                _build_optional_template('invalid_template', False),
            ),
            id='invalid_template',
        ),
    ],
)
async def test_strong_additional_route_info(
        web_app_client, mockserver, expected_status,
):
    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/distancematrix/json',
    )
    def _mock_google_maps(request):
        return mockserver.make_response(
            status=200,
            json=maps_utils.make_gmaps_distance_response(
                duration=510, distance=2300,
            ),
        )

    response = await web_app_client.post(
        '/v3/driver/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFB000Z'},
    )
    assert response.status == expected_status


@pytest.mark.translations(
    rida={'valid_tanker_key': {'en': '{driver_to_start_duration}'}},
    tariff={
        'currency.ngn': {'en': 'NGN'},
        'currency_with_sign.default': {'en': '$VALUE$ $SIGN$$CURRENCY$'},
    },
)
@experiments_utils.get_offer_info_units([{'tanker_key': 'valid_tanker_key'}])
async def test_unavailable_router(web_app_client, mockserver):
    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/distancematrix/json',
    )
    def _mock_google_maps(request):
        return mockserver.make_response(status=500)

    response = await web_app_client.post(
        '/v3/driver/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFB000Z'},
    )
    additional_info = (await response.json())['data']['offer'].get(
        'additional_info',
    )
    assert additional_info == [
        {'type': 1, 'data': {'color': '#000000', 'text': 'N/A'}},
        {'type': 101, 'data': {}},
    ]


@pytest.mark.now('2020-04-29T10:12:00.000+0000')
@pytest.mark.config(
    RIDA_GEO_CACHE_SETTINGS=dict(
        is_enabled=True, ttl=300, cache_key_ttl_seconds=35,
    ),
)
@pytest.mark.translations(
    rida={'valid_tanker_key': {'en': '{driver_to_start_duration}'}},
    tariff={
        'currency.ngn': {'en': 'NGN'},
        'currency_with_sign.default': {'en': '$VALUE$ $SIGN$$CURRENCY$'},
    },
)
@experiments_utils.get_offer_info_units(
    _build_optional_template('valid_tanker_key'),
)
async def test_distance_model_cache(web_app_client, mockserver, mongodb):
    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/distancematrix/json',
    )
    def _mock_google_maps(request):
        return mockserver.make_response(
            status=200,
            json=maps_utils.make_gmaps_distance_response(
                duration=510, distance=2300,
            ),
        )

    user_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B'
    offer_guid = '9373F48B-C6B4-4812-A2D0-413F3AFB000Z'
    headers = helpers.get_auth_headers(user_id=1234)
    response = await web_app_client.post(
        '/v3/driver/offer/info',
        headers=headers,
        json={'offer_guid': offer_guid},
    )
    assert response.status == 200

    cached_value = mongodb.rida_distances.find_one(
        {'cache_key': f'{user_guid}_{offer_guid}'},
    )
    assert cached_value['distance'] == 2300
    assert cached_value['duration'] == 510
    assert cached_value['expired_at'] == datetime.datetime(
        2020, 4, 29, 10, 12, 35,
    )

    response = await web_app_client.post(
        '/v3/driver/position',
        headers=headers,
        json={'position': [56.45, 45.56], 'heading': 1.234},
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/v3/driver/offer/info',
        headers=headers,
        json={'offer_guid': offer_guid},
    )
    assert response.status == 200
    assert _mock_google_maps.times_called == 1


def _get_passenger_info_exp_mark(tanker_key: str):
    exp_mark = pytest.mark.client_experiments3(
        consumer='rida',
        experiment_name='rida_driver_offer_passenger_info_templates',
        args=experiments_utils.get_default_user_args(),
        value={'unit_templates': [{'tanker_key': tanker_key}]},
    )
    return exp_mark


@pytest.mark.translations(
    rida={
        'key.plain': {'en': 'value plain'},
        'key.first_name': {'en': 'value {first_name}'},
        'key.last_name': {'en': 'value {last_name}'},
        'key.rating': {'en': 'value {rating}'},
        'key.number_of_trips': {'en': 'value {number_of_trips}'},
    },
    tariff={
        'currency.ngn': {'en': 'NGN'},
        'currency_with_sign.default': {'en': '$VALUE$ $SIGN$$CURRENCY$'},
    },
)
@pytest.mark.parametrize(
    ['expected_text'],
    [
        pytest.param(
            'value plain',
            marks=_get_passenger_info_exp_mark('key.plain'),
            id='plain_tanker_key',
        ),
        pytest.param(
            'value first_name',
            marks=_get_passenger_info_exp_mark('key.first_name'),
            id='tk_formatting_first_name',
        ),
        pytest.param(
            'value last_name',
            marks=_get_passenger_info_exp_mark('key.last_name'),
            id='tk_formatting_last_name',
        ),
        pytest.param(
            'value 5.0',
            marks=_get_passenger_info_exp_mark('key.rating'),
            id='tk_formatting_rating',
        ),
        pytest.param(
            'value 0',
            marks=_get_passenger_info_exp_mark('key.number_of_trips'),
            id='tk_formatting_number_of_trips',
        ),
    ],
)
async def test_passenger_info_exp(web_app_client, expected_text: str):
    response = await web_app_client.post(
        '/v3/driver/offer/info',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'offer_guid': '9373F48B-C6B4-4812-A2D0-413F3AFB000Z'},
    )
    assert response.status == 200
    data = await response.json()

    additional_info = data['data']['offer'].get('additional_info')
    assert additional_info is not None
    assert len(additional_info) == 2  # text + spacer

    text_unit = additional_info[0]
    assert text_unit['type'] == 1
    assert text_unit['data']['color'] == '#000000'
    assert text_unit['data']['text'] == expected_text
