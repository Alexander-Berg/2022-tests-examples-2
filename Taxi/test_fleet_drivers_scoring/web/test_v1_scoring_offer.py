import copy

import pytest

from test_fleet_drivers_scoring.web import defaults
from test_fleet_drivers_scoring.web import utils


ENDPOINT = 'v1/paid/drivers/scoring/offer'

PARK = {
    'id': 'park1',
    'login': 'login1',
    'name': 'super_park1',
    'is_active': True,
    'city_id': 'city1',
    'locale': 'locale1',
    'is_billing_enabled': False,
    'is_franchising_enabled': False,
    'demo_mode': False,
    'country_id': 'rus',
    'provider_config': {'clid': 'clid1', 'type': 'production'},
    'tz_offset': 3,
    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
}

FLEET_PARKS_RESPONSE_1 = [{'parks': [PARK]}]

PARK2 = copy.deepcopy(PARK)
PARK2['provider_config'] = {'clid': 'clid2', 'type': 'production'}
FLEET_PARKS_RESPONSE_2 = [{'parks': [PARK2]}]

PARK3 = copy.deepcopy(PARK)
PARK3['provider_config'] = {'clid': 'clid3', 'type': 'production'}
FLEET_PARKS_RESPONSE_3 = [{'parks': [PARK3]}]

PARK4 = copy.deepcopy(PARK)
PARK4['provider_config'] = {'clid': 'clid4', 'type': 'production'}
FLEET_PARKS_RESPONSE_4 = [{'parks': [PARK4]}]


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_PRICES_2={
        'countries': {
            'rus': {
                'main_amount': '100',
                'simple_version_amount': '10',
                'basic_version_amount': '1',
                'currency': 'RUB',
            },
        },
        'clids': {},
    },
    **defaults.SCORING_ENABLED_CONFIG1,
)
@pytest.mark.pgsql('fleet_drivers_scoring', files=['last_check.sql'])
@pytest.mark.parametrize(
    'license_pd_id, offer',
    [
        pytest.param(
            'license_pd_id',
            {
                'decision': {
                    'can_buy': False,
                    'reason': {'code': 'nothing_changed'},
                },
                'last_check_id': 'req_done',
                'price': {
                    'amount': '10',
                    'amount_without_discount': '100',
                    'currency': 'RUB',
                },
                'discounts': {'discount_type': 'basic_price'},
            },
            marks=pytest.mark.now('2020-07-26T00:00:00'),
            id='has recent check',
        ),
        pytest.param(
            'license_pd_id',
            {
                'decision': {'can_buy': True},
                'last_check_id': 'req_done',
                'price': {
                    'amount': '10',
                    'amount_without_discount': '100',
                    'currency': 'RUB',
                },
                'discounts': {'discount_type': 'basic_price'},
            },
            marks=pytest.mark.now('2020-07-31T00:00:00'),
            id='check long ago',
        ),
        pytest.param(
            'license_pd_id_no_checks',
            {
                'decision': {'can_buy': True},
                'price': {
                    'amount': '10',
                    'amount_without_discount': '100',
                    'currency': 'RUB',
                },
                'discounts': {'discount_type': 'basic_price'},
            },
            marks=pytest.mark.now('2020-07-26T00:00:00'),
            id='no checks',
        ),
        pytest.param(
            'license_pd_id',
            {
                'decision': {'can_buy': True},
                'last_check_id': 'req_done',
                'price': {
                    'amount': '10',
                    'amount_without_discount': '100',
                    'currency': 'RUB',
                },
                'discounts': {'discount_type': 'basic_price'},
            },
            marks=[
                pytest.mark.now('2020-07-24T00:00:00'),
                pytest.mark.config(
                    FLEET_DRIVERS_SCORING_CANNOT_BUY_AGAIN_DAYS=0,
                ),
            ],
            id='disabled cannot buy period',
        ),
    ],
)
async def test_ok(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_fleet_payouts,
        license_pd_id,
        offer,
):
    _mock_fleet_parks.set_parks_list_responses(FLEET_PARKS_RESPONSE_1)
    _mock_fleet_payouts.set_fleet_version_response({'fleet_version': 'simple'})
    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers={**utils.TVM_HEADERS},
        json={'query': {'driver': {'license_pd_id': license_pd_id}}},
        params={'park_id': 'park1'},
    )
    assert response.status == 200, response.text
    response_json = await response.json()
    assert response_json == {'offer': offer}


@pytest.mark.config(**defaults.SCORING_ENABLED_CONFIG1)
@pytest.mark.parametrize(
    'parks_call_times, expected_response',
    [
        pytest.param(
            0,
            {'code': '400', 'message': 'Scoring is disabled'},
            marks=pytest.mark.config(
                FLEET_DRIVERS_SCORING_PAID_ENABLED={
                    'cities': [],
                    'countries': ['rus', 'kaz'],
                    'dbs': [],
                    'dbs_disable': [],
                    'enable': False,
                },
            ),
            id='paid disabled',
        ),
        pytest.param(
            1,
            {'code': '400', 'message': 'Scoring is disabled for park park1'},
            marks=pytest.mark.config(
                FLEET_DRIVERS_SCORING_PAID_ENABLED={
                    'cities': [],
                    'countries': [],
                    'dbs': [],
                    'dbs_disable': [],
                    'enable': True,
                },
            ),
            id='no paid scoring in country',
        ),
    ],
)
async def test_paid_disabled(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        parks_call_times,
        expected_response,
):
    _mock_fleet_parks.set_parks_list_responses(FLEET_PARKS_RESPONSE_1)
    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers={**utils.TVM_HEADERS},
        json={'query': {'driver': {'license_pd_id': 'asd'}}},
        params={'park_id': 'park1'},
    )
    assert response.status == 400, response.text
    response_json = await response.json()
    assert response_json == expected_response
    assert _mock_fleet_parks.parks_list.times_called == parks_call_times


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_PRICES_2={
        'countries': {
            'rus': {
                'main_amount': '200',
                'simple_version_amount': '20',
                'basic_version_amount': '2',
                'currency': 'RUB',
            },
        },
        'clids': {
            'clid1': {
                'main_amount': '100',
                'simple_version_amount': '10',
                'basic_version_amount': '1',
                'currency': 'RUB',
            },
            'clid3': {'main_amount': '1', 'currency': 'RUB'},
            'clid4': {
                'main_amount': '1',
                'simple_version_amount': '10',
                'basic_version_amount': '1',
                'currency': 'RUB',
            },
        },
    },
    **defaults.SCORING_ENABLED_CONFIG1,
)
@pytest.mark.pgsql('fleet_drivers_scoring', files=['last_check.sql'])
@pytest.mark.parametrize(
    'fleet_parks_response, fleet_version_response, expected_price',
    [
        # clid price
        (
            FLEET_PARKS_RESPONSE_1,
            {'fleet_version': 'simple'},
            {
                'amount': '10',
                'amount_without_discount': '100',
                'currency': 'RUB',
            },
        ),
        (
            FLEET_PARKS_RESPONSE_1,
            {'fleet_version': 'basic'},
            {
                'amount': '1',
                'amount_without_discount': '100',
                'currency': 'RUB',
            },
        ),
        # country price
        (
            FLEET_PARKS_RESPONSE_2,
            {'fleet_version': 'simple'},
            {
                'amount': '20',
                'amount_without_discount': '200',
                'currency': 'RUB',
            },
        ),
        (
            FLEET_PARKS_RESPONSE_2,
            {'fleet_version': 'basic'},
            {
                'amount': '2',
                'amount_without_discount': '200',
                'currency': 'RUB',
            },
        ),
        # just main price
        (
            FLEET_PARKS_RESPONSE_3,
            {'fleet_version': 'simple'},
            {'amount': '1', 'currency': 'RUB'},
        ),
        (
            FLEET_PARKS_RESPONSE_3,
            {'fleet_version': 'basic'},
            {'amount': '1', 'currency': 'RUB'},
        ),
        # fallback if discounted_price >= price
        (
            FLEET_PARKS_RESPONSE_4,
            {'fleet_version': 'simple'},
            {'amount': '10', 'currency': 'RUB'},
        ),
        (
            FLEET_PARKS_RESPONSE_4,
            {'fleet_version': 'basic'},
            {'amount': '1', 'currency': 'RUB'},
        ),
    ],
)
@pytest.mark.now('2020-07-26T00:00:00')
async def test_prices_config(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_fleet_payouts,
        fleet_parks_response,
        fleet_version_response,
        expected_price,
):
    _mock_fleet_parks.set_parks_list_responses(fleet_parks_response)
    _mock_fleet_payouts.set_fleet_version_response(fleet_version_response)
    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers={**utils.TVM_HEADERS},
        json={'query': {'driver': {'license_pd_id': 'license_pd_id'}}},
        params={'park_id': 'park1'},
    )
    assert response.status == 200, response.text
    response_json = await response.json()
    assert response_json == {
        'offer': {
            'decision': {
                'can_buy': False,
                'reason': {'code': 'nothing_changed'},
            },
            'last_check_id': 'req_done',
            'price': expected_price,
            'discounts': {'discount_type': 'basic_price'},
        },
    }


@pytest.mark.now('2020-07-25T11:00:00+00')
@pytest.mark.pgsql('fleet_drivers_scoring', files=['discount.sql'])
@pytest.mark.config(
    FLEET_DRIVERS_SCORING_PRICES_2={
        'countries': {
            'rus': {
                'main_amount': '100',
                'simple_version_amount': '10',
                'basic_version_amount': '9',
                'currency': 'RUB',
            },
        },
        'clids': {},
    },
    **defaults.SCORING_ENABLED_CONFIG1,
)
@pytest.mark.parametrize(
    'expected_offer',
    [
        pytest.param(
            {
                'decision': {'can_buy': True},
                'price': {
                    'amount': '1',
                    'amount_without_discount': '100',
                    'currency': 'RUB',
                },
                'discounts': {
                    'buy_x_get_y': {
                        'discounted_price': {'amount': '1', 'currency': 'RUB'},
                        'discounted_to_buy_count': 2,
                        'discounted_to_buy_count_left': 1,
                        'is_achieved': True,
                        'normal_to_buy_count': 2,
                        'normal_to_buy_count_left': 0,
                    },
                    'discount_type': 'buy_x_get_y',
                },
            },
            marks=[
                pytest.mark.config(
                    FLEET_DRIVERS_SCORING_BUY_X_GET_Y_PRICE=[
                        {
                            'begin_at': '1900-01-01',
                            'checks_with_discounted_price': 2,
                            'checks_with_normal_price': 2,
                            'countries': {
                                'rus': {'amount': '1', 'currency': 'RUB'},
                            },
                            'clids': {},
                        },
                    ],
                ),
            ],
            id='discounted offer',
        ),
        pytest.param(
            {
                'decision': {'can_buy': True},
                'price': {
                    'amount': '1',
                    'amount_without_discount': '100',
                    'currency': 'RUB',
                },
                'discounts': {
                    'buy_x_get_y': {
                        'discounted_price': {'amount': '1', 'currency': 'RUB'},
                        'discounted_to_buy_count': 2,
                        'discounted_to_buy_count_left': 1,
                        'is_achieved': True,
                        'normal_to_buy_count': 2,
                        'normal_to_buy_count_left': 0,
                    },
                    'discount_type': 'buy_x_get_y',
                },
            },
            marks=[
                pytest.mark.config(
                    FLEET_DRIVERS_SCORING_BUY_X_GET_Y_PRICE=[
                        {
                            'begin_at': '1900-01-01',
                            'checks_with_discounted_price': 2,
                            'checks_with_normal_price': 2,
                            'countries': {
                                'rus': {'amount': '1', 'currency': 'RUB'},
                            },
                            'clids': {},
                        },
                    ],
                    FLEET_DRIVERS_SCORING_PRICES_2={
                        'countries': {
                            'rus': {'main_amount': '100', 'currency': 'RUB'},
                        },
                        'clids': {},
                    },
                ),
            ],
            id='discounted offer and one normal price',
        ),
        pytest.param(
            {
                'decision': {'can_buy': True},
                'price': {
                    'amount': '10',
                    'amount_without_discount': '100',
                    'currency': 'RUB',
                },
                'discounts': {
                    'buy_x_get_y': {
                        'discounted_price': {'amount': '1', 'currency': 'RUB'},
                        'discounted_to_buy_count': 2,
                        'discounted_to_buy_count_left': 0,
                        'is_achieved': False,
                        'normal_to_buy_count': 3,
                        'normal_to_buy_count_left': 1,
                    },
                    'discount_type': 'basic_price',
                },
            },
            marks=[
                pytest.mark.config(
                    FLEET_DRIVERS_SCORING_BUY_X_GET_Y_PRICE=[
                        {
                            'begin_at': '1900-01-01',
                            'checks_with_discounted_price': 2,
                            'checks_with_normal_price': 3,
                            'countries': {
                                'rus': {'amount': '1', 'currency': 'RUB'},
                            },
                            'clids': {},
                        },
                    ],
                ),
            ],
            id='not enough normals',
        ),
        pytest.param(
            {
                'decision': {'can_buy': True},
                'price': {
                    'amount': '10',
                    'amount_without_discount': '100',
                    'currency': 'RUB',
                },
                'discounts': {
                    'buy_x_get_y': {
                        'discounted_price': {'amount': '1', 'currency': 'RUB'},
                        'discounted_to_buy_count': 1,
                        'discounted_to_buy_count_left': 0,
                        'is_achieved': False,
                        'normal_to_buy_count': 2,
                        'normal_to_buy_count_left': 2,
                    },
                    'discount_type': 'basic_price',
                },
            },
            marks=[
                pytest.mark.config(
                    FLEET_DRIVERS_SCORING_BUY_X_GET_Y_PRICE=[
                        {
                            'begin_at': '1900-01-01',
                            'checks_with_discounted_price': 1,
                            'checks_with_normal_price': 2,
                            'countries': {
                                'rus': {'amount': '1', 'currency': 'RUB'},
                            },
                            'clids': {},
                        },
                    ],
                ),
            ],
            id='too many discounted',
        ),
        pytest.param(
            {
                'decision': {'can_buy': True},
                'price': {
                    'amount': '10',
                    'amount_without_discount': '100',
                    'currency': 'RUB',
                },
                'discounts': {'discount_type': 'basic_price'},
            },
            marks=[
                pytest.mark.config(
                    FLEET_DRIVERS_SCORING_BUY_X_GET_Y_PRICE=[
                        {
                            'begin_at': '2020-07-26',
                            'checks_with_discounted_price': 2,
                            'checks_with_normal_price': 2,
                            'countries': {
                                'rus': {'amount': '1', 'currency': 'RUB'},
                            },
                            'clids': {},
                        },
                    ],
                ),
            ],
            id='discount in the future',
        ),
        pytest.param(
            {
                'decision': {'can_buy': True},
                'price': {
                    'amount': '5',
                    'amount_without_discount': '100',
                    'currency': 'RUB',
                },
                'discounts': {
                    'buy_x_get_y': {
                        'discounted_price': {'amount': '5', 'currency': 'RUB'},
                        'discounted_to_buy_count': 2,
                        'discounted_to_buy_count_left': 1,
                        'is_achieved': True,
                        'normal_to_buy_count': 2,
                        'normal_to_buy_count_left': 0,
                    },
                    'discount_type': 'buy_x_get_y',
                },
            },
            marks=[
                pytest.mark.config(
                    FLEET_DRIVERS_SCORING_BUY_X_GET_Y_PRICE=[
                        {
                            'begin_at': '2020-07-24',
                            'checks_with_discounted_price': 2,
                            'checks_with_normal_price': 2,
                            'countries': {},
                            'clids': {
                                'clid1': {'amount': '3', 'currency': 'RUB'},
                            },
                        },
                        {
                            'begin_at': '2020-07-25',
                            'checks_with_discounted_price': 2,
                            'checks_with_normal_price': 2,
                            'countries': {},
                            'clids': {
                                'clid1': {'amount': '5', 'currency': 'RUB'},
                            },
                        },
                        {
                            'begin_at': '2020-07-26',
                            'checks_with_discounted_price': 2,
                            'checks_with_normal_price': 2,
                            'countries': {
                                'rus': {'amount': '1', 'currency': 'RUB'},
                            },
                            'clids': {},
                        },
                    ],
                ),
            ],
            id='between discounts',
        ),
    ],
)
async def test_discount_buy_x_get_y(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        _mock_fleet_payouts,
        expected_offer,
):
    _mock_fleet_parks.set_parks_list_responses(FLEET_PARKS_RESPONSE_1)
    _mock_fleet_payouts.set_fleet_version_response({'fleet_version': 'simple'})
    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers={**utils.TVM_HEADERS},
        json={'query': {'driver': {'license_pd_id': 'some'}}},
        params={'park_id': 'park1'},
    )
    assert response.status == 200, response.text
    response_json = await response.json()
    assert response_json == {'offer': expected_offer}
