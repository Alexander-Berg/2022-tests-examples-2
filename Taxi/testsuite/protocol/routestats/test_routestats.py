import collections
import copy
import datetime
import json

import pytest

from order_offers_switch_parametrize import ORDER_OFFERS_SAVE_SWITCH
from protocol.routestats import utils


SurchargeParams = collections.namedtuple(
    'SurchargeParams', ['alpha', 'beta', 'surcharge'],
)


CARD_LIKE_PAYMENT_METHODS = [
    'card',
    'applepay',
    'googlepay',
    'coop_account',
    'yandex_card',
    'cargocorp',
    'sbp',
]


DEFAULT_ALL_CATEGORIES = [
    'econom',
    'comfortplus',
    'vip',
    'minivan',
    'pool',
    'child_tariff',
]

_set_default_tariff_info_and_prices = utils.set_default_tariff_info_and_prices


@pytest.mark.now('2017-05-25T11:30:00+0300')
def test_wizard_city_not_found(
        local_services, taxi_protocol, pricing_data_preparer, db, load_json,
):
    request = load_json('request.json')
    expected_response = load_json('expected_response.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 400
    assert response.json() == expected_response

    offer = utils.get_saved_offer(db)
    assert offer is None


@pytest.mark.now('2017-05-25T11:30:00+0300')
def test_wizard(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        mockserver,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')

    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    assert response.json() == expected_response

    offer = utils.get_saved_offer(db)
    assert offer is None


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(filename='experiments3_01.json')
def test_wizard_with_exp3(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        now,
        mockserver,
):
    request = load_json('request.json')

    user_agent = (
        'ru.yandex.taxi.inhouse/3.98.8966 '
        '(iPhone; iPhone7,1; iOS 10.3.3; Darwin)'
    )
    response = taxi_protocol.post(
        '3.0/routestats', request, headers={'User-Agent': user_agent},
    )

    assert response.status_code == 200
    content = response.json()
    assert len(content['typed_experiments']['items']) == 2


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(filename='user_tags/experiments3_01.json')
@pytest.mark.user_experiments('child_tariff')
@pytest.mark.config(
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
    ALL_CATEGORIES=DEFAULT_ALL_CATEGORIES,
    APPLICATION_BRAND_CATEGORIES_SETS={'__default__': DEFAULT_ALL_CATEGORIES},
    ROUTESTATS_FETCH_USER_TAGS=True,
    PROTOCOL_USE_SURGE_CALCULATOR=True,
)
@pytest.mark.parametrize(
    'category_requires_user_tag, hidden_by_tag',
    [
        (
            {
                '__default__': {
                    '__default__': {'requires_tag': False, 'tag': ''},
                },
            },
            [],
        ),
        (
            {
                '__default__': {
                    '__default__': {
                        'requires_tag': True,
                        'tag': 'supervipuser',
                    },
                    'comfortplus': {
                        'requires_tag': True,
                        'tag': 'nosuchtagonuser',
                    },
                },
            },
            ['comfortplus'],
        ),
        (
            {
                '__default__': {
                    '__default__': {
                        'requires_tag': False,
                        'tag': 'nosuchtagonuser',
                    },
                    'comfortplus': {
                        'requires_tag': True,
                        'tag': 'nosuchtagonuser',
                    },
                },
                'moscow': {
                    '__default__': {'requires_tag': False, 'tag': ''},
                    'econom': {'requires_tag': True, 'tag': 'nosuchtagonuser'},
                    'minivan': {'requires_tag': True, 'tag': 'supervipuser'},
                },
            },
            ['econom'],
        ),
    ],
)
@pytest.mark.parametrize('enable_individual_tariffs', [True, False])
def test_main_screen(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        config,
        category_requires_user_tag,
        hidden_by_tag,
        mockserver,
        now,
        enable_individual_tariffs,
        mock_individual_tariffs,
):
    config.set_values(
        {
            'INDIVIDUAL_TARIFFS_USING': {
                '__default__': {
                    '__default__': {'enabled': enable_individual_tariffs},
                },
            },
        },
    )
    _set_default_tariff_info_and_prices(pricing_data_preparer)
    pricing_data_preparer.set_user_tags(['supervipuser'])

    config.set_values(
        dict(CATEGORY_REQUIRES_USER_TAG=category_requires_user_tag),
    )
    hidden_categories = hidden_by_tag

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')
    expected_response['service_levels'] = list(
        filter(
            lambda x: x['class'] not in hidden_categories,
            expected_response['service_levels'],
        ),
    )
    headers = {
        'User-Agent': (
            'ru.yandex.taxi.inhouse/4.99.8769 '
            '(iPhone; iPhone7,2; iOS 11.0; Darwin)'
        ),
    }
    taxi_protocol.tests_control(now=now, invalidate_caches=True)
    response = taxi_protocol.post('3.0/routestats', request, headers=headers)

    assert response.status_code == 200
    assert response.json() == expected_response

    offer = utils.get_saved_offer(db)
    assert offer is None
    if enable_individual_tariffs:
        assert mock_individual_tariffs.tariffs_list.times_called > 0


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('child_tariff')
@pytest.mark.config(
    SURGE_ENABLED=False,
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
    ALL_CATEGORIES=DEFAULT_ALL_CATEGORIES,
    APPLICATION_BRAND_CATEGORIES_SETS={'__default__': DEFAULT_ALL_CATEGORIES},
)
@ORDER_OFFERS_SAVE_SWITCH
def test_main_screen_fallback_surger(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        db,
        mock_order_offers,
        order_offers_save_enabled,
        load_json,
        config,
        mockserver,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')
    headers = {
        'User-Agent': (
            'ru.yandex.taxi.inhouse/4.99.8769 '
            '(iPhone; iPhone7,2; iOS 11.0; Darwin)'
        ),
    }
    response = taxi_protocol.post('3.0/routestats', request, headers=headers)

    assert response.status_code == 200
    assert response.json() == expected_response

    offer = utils.get_saved_offer(
        db, mock_order_offers, order_offers_save_enabled,
    )
    assert offer is None


@pytest.mark.now('2017-05-25T11:30:00+0300')
@ORDER_OFFERS_SAVE_SWITCH
def test_summary_no_destination(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        mockserver,
        mock_order_offers,
        order_offers_save_enabled,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    request = load_json('request.json')

    expected_response = load_json('expected_response.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    assert response.json() == expected_response

    offer = utils.get_saved_offer(
        db, mock_order_offers, order_offers_save_enabled,
    )
    assert offer is None


@pytest.mark.now('2020-04-28T15:36:09+0300')
@pytest.mark.experiments3(filename='user_tags/experiments3_01.json')
@pytest.mark.parametrize('fetch_user_tags', [False, True])
@pytest.mark.config(DEFAULT_URGENCY=600)
@ORDER_OFFERS_SAVE_SWITCH
def test_summary_with_destination(
        local_services,
        taxi_protocol,
        db,
        load_json,
        now,
        config,
        fetch_user_tags,
        pricing_data_preparer,
        mock_order_offers,
        order_offers_save_enabled,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_fixed_price(category='econom', enable=False)
    pricing_data_preparer.set_trip_information(
        time=1421.5866954922676, distance=7514.629286628636,
    )
    pricing_data_preparer.set_cost(
        category='econom', user_cost=317, driver_cost=317,
    )
    if fetch_user_tags:
        pricing_data_preparer.set_user_tags(tags=['preved', 'medved'])

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offer = response.json()
    offer_id = response_without_offer.pop('offer')
    for service_level in expected_response['service_levels']:
        service_level['offer'] = offer_id
    assert response_without_offer == expected_response

    offer = utils.get_saved_offer(
        db, mock_order_offers, order_offers_save_enabled,
    )
    assert offer['_id'] == offer_id
    assert offer['routestats_link']
    assert offer['routestats_type']
    assert offer['authorized']
    assert offer['created'] == now.replace(microsecond=0)
    assert not offer['destination_is_airport']
    assert offer['distance'] == 7514.629286628636
    assert offer['due'] == (
        now.replace(microsecond=0) + datetime.timedelta(minutes=10)
    )
    assert not offer['is_fixed_price']
    assert 'payment_type' in offer
    assert offer['payment_type'] == 'corp'
    del offer['prices'][0]['pricing_data']
    assert offer['prices'] == [
        {
            'cls': 'econom',
            'cat_type': 'application',
            'category_id': '0a6297a87cd247eb8d14a346995c6d50',
            'driver_price': 317.0,
            'is_fixed_price': False,
            'price': 317.0,
            'sp': 1.0,
            'using_new_pricing': True,
        },
    ]
    assert offer['classes_requirements'] == {}
    assert offer['route'] == [
        [37.647932797875484, 55.742884944005525],
        [37.58992385864258, 55.73382568359375],
    ]
    assert offer['time'] == 1421.5866954922676
    assert offer['user_id'] == 'b300bda7d41b4bae8d58dfa93221ef16'
    if fetch_user_tags:
        assert 'user_tags' in offer
        assert set(offer['user_tags']) == set(['preved', 'medved'])
    else:
        assert 'user_tags' not in offer


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(PROTOCOL_USE_SURGE_CALCULATOR=True)
def test_summary_no_destination_surge(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        mockserver,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_user_surge(sp=2, category='econom')
    pricing_data_preparer.set_cost(
        user_cost=198, driver_cost=198, category='econom',
    )
    pricing_data_preparer.set_meta('min_price', 198, category='econom')

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    assert response.json() == expected_response

    offer = utils.get_saved_offer(db)
    assert offer is None


@pytest.mark.config(SURGE_SURCHARGE_ENABLE=True)
@pytest.mark.now('2017-05-25T11:30:00+0300')
def test_summary_no_destination_surcharge(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        mockserver,
):
    pricing_data_preparer.set_tariff_info(
        price_per_minute=4.5,
        price_per_kilometer=4.5,
        included_minutes=5,
        included_kilometers=2,
        category='econom',
    )

    pricing_data_preparer.set_user_surge(
        sp=2, alpha=0.0, beta=1.0, surcharge=1000.5, category='econom',
    )
    pricing_data_preparer.set_cost(
        user_cost=1100, driver_cost=1100, category='econom',
    )
    pricing_data_preparer.set_meta('min_price', 1100, category='econom')

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    assert response.json() == expected_response

    offer = utils.get_saved_offer(db)
    assert offer is None


@pytest.mark.now('2017-05-25T11:30:00+0300')
def test_summary_with_destination_surge(
        local_services,
        taxi_protocol,
        db,
        load_json,
        mockserver,
        now,
        pricing_data_preparer,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_fixed_price(category='econom', enable=False)
    pricing_data_preparer.set_trip_information(
        time=1421.5866954922676, distance=7514.629286628636,
    )
    pricing_data_preparer.set_cost(
        category='econom', user_cost=633, driver_cost=633,
    )

    pricing_data_preparer.set_user_surge(category='econom', sp=2)

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(request, 2)

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offer = response.json()
    offer_id = response_without_offer.pop('offer')
    for service_level in expected_response['service_levels']:
        service_level['offer'] = offer_id
    assert response_without_offer == expected_response


@pytest.mark.now('2017-05-25T11:30:00+0300')
def test_no_nearestdrivers(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        mockserver,
):
    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    data = response.json()
    for service_level in data['service_levels']:
        assert service_level['tariff_unavailable'] == {
            'code': 'no_free_cars_nearby',
            'message': 'No available cars',
        }

    offer = utils.get_saved_offer(db)
    assert offer is None


ENABLE_NO_CARS_REQUEST_UMLAAS_EXPERIMENT = pytest.mark.experiments3(
    filename='paid_supply/exp3_request_umlaas_no_cars_verdict.json',
)

USE_UMLAAS_NO_CARS_VERDICT = [
    pytest.mark.experiments3(
        filename='paid_supply/exp3_request_umlaas_no_cars_verdict.json',
    ),
    pytest.mark.experiments3(
        filename='paid_supply/use_no_cars_verdict_from_umlaas.json',
    ),
]


@pytest.mark.config(
    NO_CARS_ORDER_MIN_VERSIONS={'android': {'version': [3, 15, 0]}},
    NO_CARS_ORDER_AVAILABLE_BY_ZONES=['moscow'],
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('no_cars_order_available')
@pytest.mark.parametrize(
    'destination_point, expect_offer',
    [(None, False), ([37.58992385864258, 55.73382568359375], True)],
)
@pytest.mark.parametrize(
    'make_umlaas_request,use_umlaas_verdict',
    [
        (False, False),
        pytest.param(
            True, False, marks=ENABLE_NO_CARS_REQUEST_UMLAAS_EXPERIMENT,
        ),
        pytest.param(True, True, marks=USE_UMLAAS_NO_CARS_VERDICT),
    ],
)
def test_allowed_no_nearestdrivers(
        local_services,
        taxi_protocol,
        db,
        load_json,
        mockserver,
        destination_point,
        expect_offer,
        make_umlaas_request,
        use_umlaas_verdict,
        pricing_data_preparer,
):
    if destination_point is not None:
        pricing_data_preparer.set_trip_information(
            time=1421.5866954922676, distance=7514.629286628636,
        )
    pricing_data_preparer.set_cost(
        user_cost=633, driver_cost=633, category='econom',
    )

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(
            request, 2, SurchargeParams(0.7, 0.3, 1000.5),
        )

    @mockserver.json_handler('/mlaas/no_cars_order/v1')
    def mock_no_cars_order_mlaas(request):
        return load_json('no_cars_order_mlaas.json')

    @mockserver.json_handler('/umlaas/umlaas/v1/no-cars-order')
    def mock_no_cars_order_umlaas(request):
        return load_json('no_cars_order_umlaas.json')

    request = load_json('request.json')
    if destination_point is not None:
        request['route'].append(destination_point)

    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    data = response.json()
    not_permitted_classes = ['vip', 'minivan']
    assert len(data['service_levels']) == 5
    for service_level in data['service_levels']:
        if service_level['class'] in not_permitted_classes:
            assert 'tariff_unavailable' in service_level
            assert service_level['tariff_unavailable'] == {
                'message': 'No available cars',
                'code': 'no_free_cars_nearby',
            }
        else:
            assert 'tariff_unavailable' not in service_level

    offer = utils.get_saved_offer(db)
    if expect_offer:
        assert 'offer' in data
        expected_offer_id = data['offer']
        assert offer is not None
        assert offer['_id'] == expected_offer_id
        assert len(offer['prices']) == 5
        for item in offer['prices']:
            if item['cls'] in not_permitted_classes:
                assert 'no_cars_order' not in item
            else:
                assert 'no_cars_order' in item
                assert item['no_cars_order']
    else:
        assert 'offer' not in data
        assert offer is None

    if make_umlaas_request:
        assert mock_no_cars_order_umlaas.times_called == 1
    else:
        assert mock_no_cars_order_umlaas.times_called == 0

    if use_umlaas_verdict:
        assert mock_no_cars_order_mlaas.times_called == 0


@pytest.mark.filldb(tariff_settings='disable_zone_leave')
def test_disabled_zone_leave(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        mockserver,
):
    request = load_json('request.json')

    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    data = response.json()
    for service_level in data['service_levels']:
        if service_level['class'] == 'business':
            assert service_level['tariff_unavailable'] == {
                'code': 'cant_leave_zone',
                'message': 'Can\'t leave zone',
            }
        else:
            assert 'tariff_unavailable' not in service_level


@pytest.mark.filldb(tariff_settings='disable_zone_leave')
def test_disabled_zone_leave_without_b(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        mockserver,
):
    request = load_json('request_no_destination.json')

    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    data = response.json()
    for service_level in data['service_levels']:
        if service_level['class'] == 'business':
            assert service_level['tariff_unavailable'] == {
                'code': 'cant_leave_zone',
                'message': 'Can\'t leave zone',
            }
        else:
            assert 'tariff_unavailable' not in service_level


@pytest.mark.filldb(tariff_settings='disable_zone_leave')
def test_enable_zone_leave(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        mockserver,
):
    request = load_json('request_inside_zone.json')

    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    data = response.json()
    for service_level in data['service_levels']:
        assert 'tariff_unavailable' not in service_level


@pytest.mark.config(
    NO_CARS_ORDER_MIN_VERSIONS={'android': {'version': [3, 15, 0]}},
    NO_CARS_ORDER_AVAILABLE_BY_ZONES=['moscow'],
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.user_experiments('no_cars_order_available')
def test_allowed_no_nearestdrivers_and_eta(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        mockserver,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(
            request, 2, SurchargeParams(0.7, 0.3, 1000.5),
        )

    @mockserver.json_handler('/mlaas/eta')
    def mock_eta_mlaas(request):
        return load_json('eta_mlaas.json')

    @mockserver.json_handler('/mlaas/no_cars_order/v1')
    def mock_no_cars_order_mlaas(request):
        return load_json('no_cars_order_mlaas.json')

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    data = response.json()
    no_eta_classes = ['vip', 'minivan']
    original_eta = 300.0
    ml_eta_corrections = {
        'econom': 100.0,
        'comfortplus': 200.0,
        'business': 300.0,
    }
    for service_level in data['service_levels']:
        if service_level['class'] in no_eta_classes:
            assert 'tariff_unavailable' not in service_level
            assert 'estimated_waiting' not in service_level
        else:
            assert 'estimated_waiting' in service_level
            estimated_eta = (
                original_eta + ml_eta_corrections[service_level['class']]
            )
            round_seconds = 120
            estimated_eta = int(estimated_eta / round_seconds) * round_seconds
            assert (
                service_level['estimated_waiting']['seconds'] == estimated_eta
            )

    offer = utils.get_saved_offer(db)
    assert offer is None


def test_tariff_requirements(
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        local_services,
        mockserver,
):
    request = load_json('request.json')

    response = taxi_protocol.post('3.0/routestats', request)
    expected_response = load_json('expected_response.json')

    assert response.status_code == 200
    response_json = response.json()

    for level, expected_level in zip(
            response_json['service_levels'],
            expected_response['service_levels'],
    ):
        assert level['class'] == expected_level['class']
        assert (
            level['tariff_requirements']
            == expected_level['tariff_requirements']
        )


TRIP_CRITERIA_BOTH_WITHOUT_LONG_TRIP = (
    {
        'moscow': {
            '__default__': {
                'apply': 'both',
                'distance': 1000,
                'duration': 2400,
            },
        },
    },
    False,
)
TRIP_CRITERIA_EITHER_WITHOUT_LONG_TRIP = (
    {
        'moscow': {
            '__default__': {
                'apply': 'either',
                'distance': 20000,
                'duration': 2400,
            },
        },
    },
    False,
)
TRIP_CRITERIA_BOTH_WITH_LONG_TRIP = (
    {
        'moscow': {
            '__default__': {
                'apply': 'both',
                'distance': 1000,
                'duration': 1400,
            },
        },
    },
    True,
)
TRIP_CRITERIA_EITHER_WITH_LONG_TRIP = (
    {
        'moscow': {
            '__default__': {
                'apply': 'either',
                'distance': 1000,
                'duration': 2400,
            },
        },
    },
    True,
)

ANDROID_WITH_PAID_SUPPLY = (
    'yandex-taxi/3.82.0.7675 Android/7.0 (android test client)',
    True,
)
ANDROID_WITHOUT_PAID_SUPPLY = (
    'yandex-taxi/3.81.0.7675 Android/7.0 (android test client)',
    False,
)
IOS_WITH_PAID_SUPPLY = (
    'ru.yandex.taxi.inhouse/4.50.8769 (iPhone; iOS 11.0; Darwin)',
    True,
)
IOS_WITHOUT_PAID_SUPPLY = (
    'ru.yandex.taxi.inhouse/4.49.8769 (iPhone; iOS 11.0; Darwin)',
    False,
)


# TODO: move altpin in a separate test
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'business', 'comfortplus', 'vip', 'minivan'],
    NO_CARS_ORDER_AVAILABLE_BY_ZONES=['moscow'],
    NO_CARS_ORDER_MIN_VERSIONS={
        'android': {'version': [3, 45, 0]},
        'iphone': {'version': [3, 98, 0]},
    },
    PAID_SUPPLY_MIN_VERSIONS={
        'android': {'version': [3, 82, 0]},
        'iphone': {'version': [4, 50, 0]},
    },
    PAID_SUPPLY_MIN_TAXIMETER_VERSION='8.99',
    ENABLE_PAID_CANCEL=True,
    ALTPIN_PRICE_GAIN_RATIO_DEGRADATION=-0.03,
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments(
    'fixed_price', 'no_cars_order_available', 'surge_distance',
)
@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
@pytest.mark.experiments3(filename='exp3_paid_supply_paid_cancel.json')
@pytest.mark.experiments3(filename='exp3_alt_point_switcher_b.json')
@pytest.mark.experiments3(filename='exp3_altpin_b_paid_supply_allowed.json')
@pytest.mark.parametrize(
    'params',
    [
        ('with_paid_supply', 'alternatives'),
        ('dont_use_umlaas', 'with_paid_supply'),
        'remove_destination',
        ('remove_destination', 'cash'),
        'cash',
        'obsolete_android',
        'obsolete_ios',
        ('actual_android', 'with_paid_supply'),
        ('actual_ios', 'with_paid_supply'),
        ('trip_criteria_both_with_long_trip', 'with_paid_supply'),
        'trip_criteria_both_without_long_trip',
        ('trip_criteria_either_with_long_trip', 'with_paid_supply'),
        'trip_criteria_either_without_long_trip',
    ],
)
def test_paid_supply(
        config,
        local_services,
        taxi_protocol,
        db,
        load_json,
        now,
        mockserver,
        pricing_data_preparer,
        params,
):
    remove_destination = False
    payment_type = None
    (user_agent, app_supported) = ANDROID_WITH_PAID_SUPPLY
    (trip_criteria, long_trip) = TRIP_CRITERIA_BOTH_WITH_LONG_TRIP

    if 'dont_use_umlass' not in params:
        pytest.param(True, marks=USE_UMLAAS_NO_CARS_VERDICT)
    if 'remove_destination' in params:
        remove_destination = True
    if 'cash' in params:
        payment_type = 'cash'
    if 'obsolete_android' in params:
        (user_agent, app_supported) = ANDROID_WITHOUT_PAID_SUPPLY
    if 'obsolete_ios' in params:
        (user_agent, app_supported) = IOS_WITHOUT_PAID_SUPPLY
    if 'actual_android' in params:
        (user_agent, app_supported) = ANDROID_WITH_PAID_SUPPLY
    if 'actual_ios' in params:
        (user_agent, app_supported) = IOS_WITH_PAID_SUPPLY
    if 'trip_criteria_both_with_long_trip' in params:
        (trip_criteria, long_trip) = TRIP_CRITERIA_BOTH_WITH_LONG_TRIP
    if 'trip_criteria_both_without_long_trip' in params:
        (trip_criteria, long_trip) = TRIP_CRITERIA_BOTH_WITHOUT_LONG_TRIP
    if 'trip_criteria_either_with_long_trip' in params:
        (trip_criteria, long_trip) = TRIP_CRITERIA_EITHER_WITH_LONG_TRIP
    if 'trip_criteria_either_without_long_trip' in params:
        (trip_criteria, long_trip) = TRIP_CRITERIA_EITHER_WITHOUT_LONG_TRIP

    set_payment_by_cash = False

    request = load_json('request.json')
    if payment_type:
        request['payment']['type'] = payment_type
        if payment_type == 'cash':
            set_payment_by_cash = True

    paid_supply_possible = (
        app_supported
        and not set_payment_by_cash
        and not remove_destination
        and long_trip
    )
    assert paid_supply_possible == ('with_paid_supply' in params)

    expected_paid_supply_prices = {'econom': 146, 'comfortplus': 312}
    expected_paid_supply_info = {
        'econom': {'distance': 18765, 'time': 1944},
        'comfortplus': {'distance': 17661, 'time': 1339},
    }

    expected_prices = {  # without paid supply
        'econom': 317,
        'business': 489,
        'comfortplus': 539,
        'vip': 770,
        'minivan': 513,
    }
    expected_category_ids = {
        'econom': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
        'business': '471995706dc948489584c4179f7a6827',
        'comfortplus': '3387540cf7014c12b8a2a82fef47efc0',
        'vip': 'e8e55e10ee3042d68cc608e3f6dd6cbb',
        'minivan': '77e2662d81da47d48204571d324993a6',
    }

    for time, distance, price_koef, point_id in zip(
            [1000.0, 1000.0, 1000.0, 1000.0, 1421.5866954922676],
            [7500.0, 7500.0, 7500.0, 7500.0, 7514.629286628636],
            [0.8, 0.8, 0.8, 0.8, 1.0],
            [
                '37.6479328037.65151620',
                '37.6479328037.65136435',
                '37.6479328037.65107812',
                '37.6479328037.64941692',
                '37.64793280',
            ],
    ):
        for cls, base_price in expected_prices.items():
            pricing_data_preparer.set_fixed_price(category=cls, enable=True)
            price = int(price_koef * base_price)
            pricing_data_preparer.set_cost(
                category=cls, user_cost=price, driver_cost=price,
            )
        if paid_supply_possible:
            for cls, price in expected_paid_supply_prices.items():
                pricing_data_preparer.set_paid_supply(
                    category=cls, price={'price': price},
                )
        for cls, id in expected_category_ids.items():
            pricing_data_preparer.set_user_category_prices_id(
                category=cls, category_prices_id='c/' + id, category_id=id,
            )
        pricing_data_preparer.set_trip_information(
            time=time, distance=distance,
        )
        pricing_data_preparer.push(id=point_id)
        price_econom = float(int(price_koef * expected_prices['econom']))
        pricing_data_preparer.push(id=price_econom, is_calc_paid_supply=True)

    @mockserver.json_handler('/alt/alt/v1/pin')
    def mock_pickup_altpoints(request):
        body = json.loads(request.get_data())
        assert body['selected_class'] == 'econom'
        assert len(body['extra']['prices']) == 1
        assert body['surge_value']
        assert body['altoffer_types'] == ['b']
        return load_json('altpoints.json')

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(request, 1)

    @mockserver.json_handler('/mlaas/no_cars_order/v1')
    def mock_no_cars_order_mlaas(request):
        return load_json('paid_supply/no_cars_order_mlaas.json')

    @mockserver.json_handler('/umlaas/umlaas/v1/no-cars-order')
    def mock_no_cars_order_umlaas(request):
        return load_json('paid_supply/no_cars_order_umlaas.json')

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        req = json.loads(request.get_data())
        if 'extended_radius' in req and req['extended_radius']:
            assert req['classes'] == ['econom', 'business', 'comfortplus']
            assert 'min_taximeter_version' in req
            assert req['min_taximeter_version'] == '8.99'
            assert 'extended_radius_by_classes' in req
            assert len(req['extended_radius_by_classes']) == 3
            assert req['extended_radius_by_classes'] == [
                {'max_line_dist': 20000, 'max_dist': 16093, 'max_time': 1835},
                {'max_line_dist': 20000, 'max_dist': 30000, 'max_time': 1234},
                {'max_line_dist': 20000, 'max_dist': 20000, 'max_time': 2100},
            ]
            return utils.mock_driver_eta(
                load_json, 'driver_eta_extended_radius.json',
            )(request)
        else:
            assert req['classes'] == [
                'econom',
                'business',
                'comfortplus',
                'vip',
                'minivan',
            ]
            assert 'min_taximeter_version' not in req
            return utils.mock_driver_eta(load_json, 'driver_eta.json')(request)

    config.set_values(dict(PAID_SUPPLY_LONG_TRIP_CRITERIA=trip_criteria))

    if remove_destination:
        request['route'] = request['route'][0:1]  # keep only first point

    response = taxi_protocol.post(
        '3.0/routestats', request, headers={'User-Agent': user_agent},
    )

    assert response.status_code == 200
    data = response.json()

    expected_no_cars_for_classes = ['vip', 'minivan']

    assert len(data['service_levels']) == 5
    for service_level in data['service_levels']:
        assert 'class' in service_level
        cls = service_level['class']

        assert 'description_parts' in service_level
        assert 'value' in service_level['description_parts']
        if not remove_destination:
            exp_price = expected_prices[cls]

            if cls in expected_paid_supply_prices and paid_supply_possible:
                exp_price += expected_paid_supply_prices[cls]
            exp_price_str = str(exp_price) + '\xa0$SIGN$$CURRENCY$'
            assert service_level['description_parts']['value'] == exp_price_str

        if cls in expected_no_cars_for_classes or (
                cls == 'business' and not remove_destination
        ):
            assert 'tariff_unavailable' in service_level
            assert service_level['tariff_unavailable'] == {
                'message': 'No available cars',
                'code': 'no_free_cars_nearby',
            }
        else:
            if paid_supply_possible:
                assert 'tariff_unavailable' not in service_level
            else:
                assert 'tariff_unavailable' in service_level
                if (not app_supported) or (
                        not long_trip and not remove_destination
                ):
                    assert service_level['tariff_unavailable'] == {
                        'message': 'No available cars',
                        'code': 'no_free_cars_nearby',
                    }
                elif remove_destination:
                    assert service_level['tariff_unavailable'] == {
                        'message': 'Paid supply requires destination point',
                        'code': 'paid_supply_no_b',
                    }
                elif set_payment_by_cash:
                    assert service_level['tariff_unavailable'] == {
                        'message': 'Paid supply does not support cash',
                        'code': 'paid_supply_no_cash',
                    }

        if cls in expected_paid_supply_prices and paid_supply_possible:
            assert service_level['paid_options'] == {
                'value': 1.0,
                'alert_properties': {
                    'button_text': 'Got it',
                    'description': 'Paid supply',
                    'label': 'Taxi is far away',
                    'title': 'Taxi is far away',
                },
                'color_button': False,
                'display_card_icon': True,
                'show_order_popup': False,
            }
        else:
            assert 'paid_options' not in service_level

    if remove_destination:
        assert 'offer' not in data
        return

    expected_offer_id = data['offer']
    expected_offer_prices_map = {}
    for cls, price in expected_prices.items():
        driver_price = price
        expected_offer_prices_map[cls] = {
            'price': price,
            'driver_price': driver_price,
            'cls': cls,
            'cat_type': 'application',
            'sp': 1.0,
            'is_fixed_price': True,
            'using_new_pricing': True,
        }
    for cls, ci in expected_category_ids.items():
        expected_offer_prices_map[cls]['category_id'] = ci

    if paid_supply_possible:
        for cls, ps_price in expected_paid_supply_prices.items():
            target = expected_offer_prices_map[cls]
            target['paid_supply_price'] = ps_price
            target['paid_supply_info'] = expected_paid_supply_info[cls]

    offer = utils.get_saved_offer(db)
    assert offer['_id'] == expected_offer_id
    assert offer['authorized']
    assert offer['created'] == now.replace(microsecond=0)
    assert not offer['destination_is_airport']
    assert offer['is_fixed_price']
    assert 'payment_type' in offer
    assert offer['payment_type'] == 'cash' if set_payment_by_cash else 'card'

    for p in offer['prices']:
        del p['pricing_data']

    assert (
        utils.prices_array_to_map(offer['prices']) == expected_offer_prices_map
    )
    assert offer['classes_requirements'] == {}
    assert offer['route'] == [
        [37.647932797875484, 55.742884944005525],
        [37.58992385864258, 55.73382568359375],
    ]
    assert offer['user_id'] == request['id']

    if 'alternatives' in params:
        assert 'alternatives' in data


@pytest.mark.config(
    ALL_CATEGORIES=['econom'],
    NO_CARS_ORDER_AVAILABLE_BY_ZONES=['moscow'],
    NO_CARS_ORDER_MIN_VERSIONS={'android': {'version': [3, 45, 0]}},
    PAID_SUPPLY_MIN_VERSIONS={'android': {'version': [3, 82, 0]}},
    PAID_SUPPLY_MIN_TAXIMETER_VERSION='8.99',
    PAID_SUPPLY_LONG_TRIP_CRITERIA={
        'moscow': {
            '__default__': {'apply': 'either', 'distance': 1, 'duration': 1},
        },
    },
    ENABLE_PAID_CANCEL=True,
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments(
    'fixed_price', 'no_cars_order_available', 'surge_distance',
)
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
@pytest.mark.experiments3(filename='exp3_paid_supply_paid_cancel.json')
@pytest.mark.parametrize(
    'allow_cash_setting, paid_supply_possible, allow_cash_exp3',
    [
        (
            {
                'allow_cash': False,
                'enable_max_allowed_price': False,
                'max_allowed_price': 145,
            },
            False,
            None,
        ),
        (
            {
                'allow_cash': True,
                'enable_max_allowed_price': False,
                'max_allowed_price': 145,
            },
            True,
            None,
        ),
        (
            {
                'allow_cash': True,
                'enable_max_allowed_price': True,
                'max_allowed_price': 145,
            },
            False,
            None,
        ),
        (
            {
                'allow_cash': True,
                'enable_max_allowed_price': True,
                'max_allowed_price': 146,
            },
            True,
            None,
        ),
        (
            {
                'allow_cash': False,
                'enable_max_allowed_price': False,
                'max_allowed_price': 145,
            },
            False,
            'paid_supply_allow_cash_01.json',
        ),
        (
            {
                'allow_cash': True,
                'enable_max_allowed_price': False,
                'max_allowed_price': 145,
            },
            True,
            'paid_supply_allow_cash_02.json',
        ),
        (
            {
                'allow_cash': True,
                'enable_max_allowed_price': True,
                'max_allowed_price': 145,
            },
            False,
            'paid_supply_allow_cash_03.json',
        ),
        (
            {
                'allow_cash': True,
                'enable_max_allowed_price': True,
                'max_allowed_price': 146,
            },
            True,
            'paid_supply_allow_cash_04.json',
        ),
    ],
)
def test_paid_supply_by_cash(
        config,
        local_services,
        taxi_protocol,
        db,
        load_json,
        now,
        mockserver,
        allow_cash_setting,
        paid_supply_possible,
        allow_cash_exp3,
        experiments3,
        pricing_data_preparer,
):
    pricing_data_preparer.set_cost(
        category='econom', user_cost=317, driver_cost=317,
    )
    pricing_data_preparer.set_user_category_prices_id(
        category='econom',
        category_prices_id='c/b7c4d5f6aa3b40a3807bb74b3bc042af',
        category_id='b7c4d5f6aa3b40a3807bb74b3bc042af',
    )

    pricing_data_preparer.set_paid_supply(
        category='econom', price={'price': 146},
    )

    experiments3.add_experiments_json(load_json('experiments3_01.json'))

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(request, 1)

    @mockserver.json_handler('/mlaas/no_cars_order/v1')
    def mock_no_cars_order_mlaas(request):
        return load_json('no_cars_order_mlaas.json')

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        req = json.loads(request.get_data())
        assert req['classes'] == ['econom']
        if 'extended_radius' in req and req['extended_radius']:
            assert 'min_taximeter_version' in req
            assert req['min_taximeter_version'] == '8.99'
            assert 'extended_radius_by_classes' not in req
            return utils.mock_driver_eta(
                load_json, 'driver_eta_extended_radius.json',
            )(request)
        else:
            assert 'min_taximeter_version' not in req
            return utils.mock_driver_eta(load_json, 'driver_eta.json')(request)

    if allow_cash_exp3 is not None:
        experiments3.add_experiments_json(load_json(allow_cash_exp3))
    else:
        config.set_values(
            dict(
                PAID_SUPPLY_ALLOW_CASH_FALLBACK={
                    '__default__': {'__default__': allow_cash_setting},
                },
            ),
        )

    request = load_json('request.json')
    response = taxi_protocol.post(
        '3.0/routestats',
        request,
        headers={
            'User-Agent': 'yandex-taxi/3.82.0.7675 Android/7.0 (test client)',
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data['service_levels']) == 1
    service_level = data['service_levels'][0]
    assert 'class' in service_level
    assert service_level['class'] == 'econom'

    assert 'description_parts' in service_level
    assert 'value' in service_level['description_parts']
    assert service_level['description_parts']['value'] == (
        '463\xa0$SIGN$$CURRENCY$'
        if allow_cash_setting['allow_cash']
        else '317\xa0$SIGN$$CURRENCY$'
    )

    if paid_supply_possible:
        assert 'tariff_unavailable' not in service_level
        assert service_level['paid_options'] == {
            'value': 1.0,
            'alert_properties': {
                'button_text': 'Got it',
                'description': 'Paid supply',
                'label': 'Taxi is far away',
                'title': 'Taxi is far away',
            },
            'color_button': False,
            'display_card_icon': True,
            'show_order_popup': False,
        }
    else:
        assert 'tariff_unavailable' in service_level
        assert service_level['tariff_unavailable'] == {
            'message': 'Paid supply does not support cash',
            'code': 'paid_supply_no_cash',
        }
        assert 'paid_options' not in service_level

    expected_offer_id = data['offer']
    expected_offer_prices = [
        {
            'price': 317,
            'driver_price': 317,
            'cls': 'econom',
            'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
            'cat_type': 'application',
            'sp': 1.0,
            'is_fixed_price': True,
            'using_new_pricing': True,
        },
    ]
    if allow_cash_setting['allow_cash']:
        expected_offer_prices[0]['paid_supply_price'] = 146
        expected_offer_prices[0]['paid_supply_info'] = {
            'distance': 18765,
            'time': 1944,
        }

    offer = utils.get_saved_offer(db)
    assert offer['_id'] == expected_offer_id
    assert offer['authorized']
    assert offer['created'] == now.replace(microsecond=0)
    assert not offer['destination_is_airport']
    assert offer['is_fixed_price']
    assert 'payment_type' in offer
    assert offer['payment_type'] == 'cash'
    del offer['prices'][0]['pricing_data']
    assert offer['prices'] == expected_offer_prices
    assert offer['classes_requirements'] == {}
    assert offer['route'] == [
        [37.647932797875484, 55.742884944005525],
        [37.58992385864258, 55.73382568359375],
    ]
    assert offer['user_id'] == request['id']


BASE_PAID_SUPPLY_CONFIG = {
    'ALL_CATEGORIES': ['econom'],
    'NO_CARS_ORDER_AVAILABLE_BY_ZONES': ['moscow'],
    'NO_CARS_ORDER_MIN_VERSIONS': {'android': {'version': [3, 45, 0]}},
    'PAID_SUPPLY_MIN_VERSIONS': {'android': {'version': [3, 82, 0]}},
    'PAID_SUPPLY_MIN_TAXIMETER_VERSION': '8.99',
    'PAID_SUPPLY_LONG_TRIP_CRITERIA': {
        'moscow': {
            '__default__': {'apply': 'either', 'distance': 1, 'duration': 1},
        },
    },
    'ENABLE_PAID_CANCEL': True,
}


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments(
    'fixed_price', 'no_cars_order_available', 'surge_distance',
)
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
@pytest.mark.experiments3(filename='exp3_paid_supply_paid_cancel.json')
@pytest.mark.parametrize(
    'decoupling, config_values, paid_supply_possible',
    [
        (True, {'PAID_SUPPLY_FOR_DECOUPLING_ENABLED': False}, False),
        (
            True,
            {
                'PAID_SUPPLY_FOR_DECOUPLING_ENABLED': True,
                'PAID_SUPPLY_FOR_DECOUPLING_EXCLUDED_CLIENTS': [
                    'corp-decoupled-client',
                    'corp-another-client',
                ],
            },
            False,
        ),
        # checked at another test about combining decoupling and paid_supply
        # (True, {'PAID_SUPPLY_FOR_DECOUPLING_ENABLED': True}, True),
        (False, {}, True),
    ],
)
def test_paid_supply_disable_check(
        config,
        local_services,
        taxi_protocol,
        db,
        load_json,
        now,
        mockserver,
        decoupling,
        paid_supply_possible,
        config_values,
        experiments3,
        pricing_data_preparer,
):
    pricing_data_preparer.set_cost(
        category='econom', user_cost=317, driver_cost=317,
    )
    pricing_data_preparer.set_user_category_prices_id(
        category='econom',
        category_prices_id='c/b7c4d5f6aa3b40a3807bb74b3bc042af',
        category_id='b7c4d5f6aa3b40a3807bb74b3bc042af',
    )

    pricing_data_preparer.set_paid_supply(
        category='econom', price={'price': 146},
    )

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(request, 1)

    @mockserver.json_handler('/mlaas/no_cars_order/v1')
    def mock_no_cars_order_mlaas(request):
        return load_json('no_cars_order_mlaas.json')

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        req = json.loads(request.get_data())
        assert req['classes'] == ['econom']
        if 'extended_radius' in req and req['extended_radius']:
            assert 'min_taximeter_version' in req
            assert req['min_taximeter_version'] == '8.99'
            assert 'extended_radius_by_classes' not in req
            return utils.mock_driver_eta(
                load_json, 'driver_eta_extended_radius.json',
            )(request)
        else:
            assert 'min_taximeter_version' not in req
            return utils.mock_driver_eta(load_json, 'driver_eta.json')(request)

    config_values.update(BASE_PAID_SUPPLY_CONFIG)
    config.set_values(config_values)

    if decoupling:
        experiments3.add_experiments_json(
            load_json('decoupling/experiments3_01.json'),
        )
    else:
        experiments3.add_experiments_json(load_json('experiments3_01.json'))

    taxi_protocol.tests_control(now=now, invalidate_caches=True)

    request = load_json('request.json')
    if decoupling:
        request['payment']['payment_method_id'] = 'corp-decoupled-client'

    response = taxi_protocol.post(
        '3.0/routestats',
        request,
        headers={
            'User-Agent': 'yandex-taxi/3.82.0.7675 Android/7.0 (test client)',
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data['service_levels']) == 1
    service_level = data['service_levels'][0]
    assert 'class' in service_level
    assert service_level['class'] == 'econom'

    assert 'description_parts' in service_level
    assert 'value' in service_level['description_parts']
    assert service_level['description_parts']['value'] == (
        '463\xa0$SIGN$$CURRENCY$'
        if paid_supply_possible
        else '317\xa0$SIGN$$CURRENCY$'
    )

    if paid_supply_possible:
        assert 'tariff_unavailable' not in service_level
        assert service_level['paid_options'] == {
            'value': 1.0,
            'alert_properties': {
                'button_text': 'Got it',
                'description': 'Paid supply',
                'label': 'Taxi is far away',
                'title': 'Taxi is far away',
            },
            'color_button': False,
            'display_card_icon': True,
            'show_order_popup': False,
        }
    else:
        assert 'tariff_unavailable' in service_level
        assert 'paid_options' not in service_level

    expected_offer_id = data['offer']
    expected_offer_prices = [
        {
            'price': 317,
            'driver_price': 317,
            'cls': 'econom',
            'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
            'cat_type': 'application',
            'sp': 1.0,
            'is_fixed_price': True,
            'using_new_pricing': True,
        },
    ]
    if paid_supply_possible:
        expected_offer_prices[0]['paid_supply_price'] = 146
        expected_offer_prices[0]['paid_supply_info'] = {
            'distance': 18765,
            'time': 1944,
        }

    offer = utils.get_saved_offer(db)
    assert offer['_id'] == expected_offer_id
    assert offer['authorized']
    assert offer['created'] == now.replace(microsecond=0)
    assert not offer['destination_is_airport']
    assert offer['is_fixed_price']
    del offer['prices'][0]['pricing_data']
    assert offer['prices'] == expected_offer_prices
    assert offer['classes_requirements'] == {}
    assert offer['route'] == [
        [37.647932797875484, 55.742884944005525],
        [37.58992385864258, 55.73382568359375],
    ]
    assert offer['user_id'] == request['id']


OFFER_EXTRA_DATA_TEST_PAID_SUPPLY_FOR_DECOUPLING = {
    'decoupling': {
        'success': True,
        'user': {
            'tariff': (
                '585a6f47201dd1b2017a0eab-'
                '507000939f17427e951df9791573ac7e-'
                '7fc5b2d1115d4341b7be206875c40e11'
            ),
            'prices': [
                {
                    'cls': 'econom',
                    'cat_type': 'application',
                    'category_id': '5f40b7f324414f51a1f9549c65211ea5',
                    'price': 633.0,
                    'sp': 1.0,
                    'is_fixed_price': True,
                    'using_new_pricing': True,
                },
            ],
        },
        'driver': {
            'tariff': '585a6f47201dd1b2017a0eab',
            'prices': [
                {
                    'cls': 'econom',
                    'cat_type': 'application',
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                    'price': 1582.0,
                    'sp': 5.0,
                    'is_fixed_price': True,
                    'using_new_pricing': True,
                },
            ],
        },
    },
}


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'business', 'comfortplus', 'vip', 'minivan'],
    NO_CARS_ORDER_AVAILABLE_BY_ZONES=['moscow'],
    NO_CARS_ORDER_MIN_VERSIONS={
        'android': {'version': [3, 45, 0]},
        'iphone': {'version': [3, 98, 0]},
    },
    PAID_SUPPLY_LONG_TRIP_CRITERIA={
        'moscow': {
            '__default__': {'apply': 'either', 'distance': 1, 'duration': 1},
        },
    },
    PAID_SUPPLY_MIN_VERSIONS={
        'android': {'version': [3, 82, 0]},
        'iphone': {'version': [4, 50, 0]},
    },
    PAID_SUPPLY_MIN_TAXIMETER_VERSION='8.99',
    ENABLE_PAID_CANCEL=True,
    PAID_SUPPLY_FOR_DECOUPLING_ENABLED=True,
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments(
    'fixed_price', 'no_cars_order_available', 'surge_distance',
)
@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
@pytest.mark.experiments3(filename='exp3_paid_supply_paid_cancel.json')
@pytest.mark.parametrize(
    'user_agent, app_supported',
    [IOS_WITHOUT_PAID_SUPPLY, IOS_WITH_PAID_SUPPLY],
)
@pytest.mark.parametrize(
    'offer_extra_data, user_price,' 'surge, decoupling_fallback',
    [
        (OFFER_EXTRA_DATA_TEST_PAID_SUPPLY_FOR_DECOUPLING, 633, 5.0, False),
        (
            {
                'decoupling': {
                    'success': False,
                    'error': {
                        'reason': 'plugin_internal_error',
                        'stage': 'calculating_offer',
                    },
                },
            },
            317,
            1.0,
            True,
        ),
    ],
    ids=['decoupled_paid_supply', 'decoupling_failed'],
)
def test_paid_supply_with_decoupling(
        config,
        local_services,
        taxi_protocol,
        db,
        load_json,
        now,
        mockserver,
        user_agent,
        app_supported,
        offer_extra_data,
        surge,
        user_price,
        decoupling_fallback,
        experiments3,
        pricing_data_preparer,
):
    pricing_data_preparer.set_cost(
        user_cost=user_price,
        driver_cost=user_price if decoupling_fallback else 1582,
    )

    pricing_data_preparer.set_driver_surge(5)

    pricing_data_preparer.set_user_category_prices_id(
        category_prices_id='d/585a6f47201dd1b2017a0eab-'
        '507000939f17427e951df9791573ac7e-'
        '7fc5b2d1115d4341b7be206875c40e11/'
        + (
            'b7c4d5f6aa3b40a3807bb74b3bc042af'
            if decoupling_fallback
            else '5f40b7f324414f51a1f9549c65211ea5'
        ),
        category_id=(
            'b7c4d5f6aa3b40a3807bb74b3bc042af'
            if decoupling_fallback
            else '5f40b7f324414f51a1f9549c65211ea5'
        ),
        tariff_id='585a6f47201dd1b2017a0eab-'
        '507000939f17427e951df9791573ac7e-'
        '7fc5b2d1115d4341b7be206875c40e11',
    )

    pricing_data_preparer.set_driver_category_prices_id(
        category_prices_id='c/b7c4d5f6aa3b40a3807bb74b3bc042af',
        category_id='b7c4d5f6aa3b40a3807bb74b3bc042af',
    )

    if decoupling_fallback:
        pricing_data_preparer.set_corp_decoupling(enable=True)
    else:
        pricing_data_preparer.set_decoupling(enable=True)

    if app_supported:
        pricing_data_preparer.set_paid_supply(
            category='econom',
            driver_price={'price': 146},
            price={'price': 146},
        )

    experiments3.add_experiments_json(
        load_json('decoupling/experiments3_01.json'),
    )

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(request, surge)

    @mockserver.json_handler('/mlaas/no_cars_order/v1')
    def mock_no_cars_order_mlaas(request):
        return load_json('paid_supply/no_cars_order_mlaas.json')

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        req = json.loads(request.get_data())
        if 'extended_radius' in req and req['extended_radius']:
            assert req['classes'] == ['econom']
            assert 'min_taximeter_version' in req
            assert req['min_taximeter_version'] == '8.99'
            assert 'extended_radius_by_classes' in req
            assert len(req['extended_radius_by_classes']) == 1
            assert req['extended_radius_by_classes'] == [
                {'max_line_dist': 20000, 'max_dist': 16093, 'max_time': 1835},
            ]
            return utils.mock_driver_eta(
                load_json, 'driver_eta_extended_radius.json',
            )(request)
        else:
            assert req['classes'] == ['econom']
            assert 'min_taximeter_version' not in req
            return utils.mock_driver_eta(load_json, 'driver_eta.json')(request)

    request = load_json('request.json')

    response = taxi_protocol.post(
        '3.0/routestats', request, headers={'User-Agent': user_agent},
    )

    assert response.status_code == 200
    data = response.json()

    paid_supply_possible = app_supported

    expected_prices = {'econom': user_price}  # without paid supply
    # if decoupling ok - users cat from corp tariff,
    # otherwise - cat from db.tariffs aka driver cat
    expected_category_ids = {
        'econom': (
            'b7c4d5f6aa3b40a3807bb74b3bc042af'
            if decoupling_fallback
            else '5f40b7f324414f51a1f9549c65211ea5'
        ),
    }
    expected_paid_supply_info = {'econom': {'distance': 18765, 'time': 1944}}

    econom_price = 146

    expected_paid_supply_prices = {'econom': econom_price}

    assert len(data['service_levels']) == 1
    for service_level in data['service_levels']:
        assert 'class' in service_level
        cls = service_level['class']

        assert 'description_parts' in service_level
        assert 'value' in service_level['description_parts']
        exp_price = expected_prices[cls]

        if cls in expected_paid_supply_prices and paid_supply_possible:
            exp_price += expected_paid_supply_prices[cls]
        exp_price_str = str(exp_price) + '\xa0$SIGN$$CURRENCY$'
        assert service_level['description_parts']['value'] == exp_price_str

        if paid_supply_possible:
            assert 'tariff_unavailable' not in service_level
        else:
            assert 'tariff_unavailable' in service_level
            assert service_level['tariff_unavailable'] == {
                'message': 'No available cars',
                'code': 'no_free_cars_nearby',
            }

        if cls in expected_paid_supply_prices and paid_supply_possible:
            assert service_level['paid_options'] == {
                'value': 1.0,
                'alert_properties': {
                    'button_text': 'Got it',
                    'description': 'Paid supply',
                    'label': 'Taxi is far away',
                    'title': 'Taxi is far away',
                },
                'color_button': False,
                'display_card_icon': True,
                'show_order_popup': False,
            }
        else:
            assert 'paid_options' not in service_level

    expected_offer_id = data['offer']
    expected_offer_prices_map = {}
    for cls, price in expected_prices.items():
        driver_price = price
        expected_offer_prices_map[cls] = {
            'price': price,
            'driver_price': driver_price,
            'cls': cls,
            'cat_type': 'application',
            'sp': 1.0,
            'is_fixed_price': True,
            'using_new_pricing': True,
        }
    for cls, ci in expected_category_ids.items():
        expected_offer_prices_map[cls]['category_id'] = ci

    if paid_supply_possible:
        for cls, ps_price in expected_paid_supply_prices.items():
            target = expected_offer_prices_map[cls]
            target['paid_supply_price'] = ps_price
            target['paid_supply_info'] = expected_paid_supply_info[cls]

    offer = utils.get_saved_offer(db)
    assert offer['_id'] == expected_offer_id
    assert offer['authorized']
    assert offer['created'] == now.replace(microsecond=0)
    assert not offer['destination_is_airport']
    assert offer['is_fixed_price']
    assert 'payment_type' in offer
    assert offer['payment_type'] == 'corp'
    for p in offer['prices']:
        del p['pricing_data']
    assert (
        utils.prices_array_to_map(offer['prices']) == expected_offer_prices_map
    )
    assert offer['classes_requirements'] == {}
    assert offer['route'] == [
        [37.647932797875484, 55.742884944005525],
        [37.58992385864258, 55.73382568359375],
    ]
    assert offer['user_id'] == request['id']
    offer_extra_data_with_paid_supply = copy.deepcopy(offer_extra_data)
    decoupling = offer_extra_data_with_paid_supply['decoupling']
    if decoupling['success'] and paid_supply_possible:
        driver_paid_supply_price = float(econom_price)
        decoupling['driver']['prices'][0][
            'paid_supply_price'
        ] = driver_paid_supply_price
        decoupling['user']['prices'][0]['paid_supply_price'] = float(
            expected_paid_supply_prices['econom'],
        )

    assert offer['extra_data'] == offer_extra_data_with_paid_supply


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(filename='user_tags/experiments3_01.json')
@pytest.mark.parametrize('payment_type', ['cash', 'card'])
@pytest.mark.parametrize('tariff_class', ['econom', 'business'])
@pytest.mark.parametrize('user_has_restriction_tags', [False, True])
@pytest.mark.parametrize(
    'category_config',
    [
        pytest.param(
            value,
            marks=pytest.mark.experiments3(
                is_config=True,
                name='forbid_tag_cash_classes',
                consumers=['protocol/routestats'],
                clauses=[],
                match={'predicate': {'type': 'true'}, 'enabled': True},
                default_value={'classes': [value]},
            ),
        )
        for value in ('econom', 'not_econom')
    ],
)
def test_cash_restrictions_by_tags_and_category(
        config,
        local_services,
        taxi_protocol,
        db,
        load_json,
        now,
        user_has_restriction_tags,
        payment_type,
        pricing_data_preparer,
        category_config,
        tariff_class,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_cost(
        user_cost=317, driver_cost=317, category=tariff_class,
    )
    pricing_data_preparer.set_trip_information(time=1440, distance=7600)
    if user_has_restriction_tags:
        pricing_data_preparer.set_meta(
            'paid_cancel_by_tags_price', 198, category=tariff_class,
        )

    request = load_json('request.json')
    request['payment'] = {'type': payment_type}

    response = taxi_protocol.post('3.0/routestats', request)

    unavailable_info = {
        'message': 'Cash option is not available: driver rides from afar',
        'code': 'cash_restricted_by_tags',
    }

    response_without_offer = response.json()
    if (
            payment_type == 'cash'
            and category_config == 'econom'
            and tariff_class == 'econom'
            and user_has_restriction_tags
    ):
        assert (
            response_without_offer['service_levels'][0]['tariff_unavailable']
            == unavailable_info
        )
    else:
        assert (
            not (
                'tariff_unavailable'
                in response_without_offer['service_levels'][0]
            )
            or response_without_offer['service_levels'][0][
                'tariff_unavailable'
            ]
            == unavailable_info
        )


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(filename='user_tags/experiments3_01.json')
@pytest.mark.parametrize('payment_type', ['cash', 'card'])
@pytest.mark.parametrize(
    (
        'routestats_fetch_user_tags, user_has_restriction_tags,'
        'eta_suits_cash, cash_available'
    ),
    [
        (False, None, None, True),
        (True, None, None, True),
        (True, True, True, True),
        (True, True, False, False),
    ],
)
def test_cash_restrictions_by_tags(
        config,
        local_services,
        taxi_protocol,
        db,
        load_json,
        now,
        routestats_fetch_user_tags,
        user_has_restriction_tags,
        eta_suits_cash,
        cash_available,
        payment_type,
        pricing_data_preparer,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_cost(
        user_cost=317, driver_cost=317, category='econom',
    )
    pricing_data_preparer.set_trip_information(time=1440, distance=7600)
    if user_has_restriction_tags:
        pricing_data_preparer.set_user_tags(
            ['light_cash_restriction', 'strict_cash_restriction'],
        )

    config.set_values(
        dict(
            ROUTESTATS_FETCH_USER_TAGS=routestats_fetch_user_tags,
            CASH_RESTRICTIONS_BY_TAGS={
                '__default__': {
                    '__default__': {
                        'light_cash_restriction': 1200,
                        'strict_cash_restriction': (
                            900 if eta_suits_cash else 800
                        ),
                    },
                },
            },
        ),
    )

    request = load_json('request.json')
    request['payment'] = {'type': payment_type}

    response = taxi_protocol.post('3.0/routestats', request)

    unavailable_info = {
        'message': 'Cash option is not available: driver rides from afar',
        'code': 'cash_restricted_by_tags',
    }

    expected_response = load_json('expected_response.json')
    if not cash_available and payment_type == 'cash':
        for service_level in expected_response['service_levels']:
            service_level['tariff_unavailable'] = unavailable_info

    assert response.status_code == 200
    response_without_offer = response.json()
    offer_id = response_without_offer.pop('offer')
    for service_level in expected_response['service_levels']:
        service_level['offer'] = offer_id
    assert response_without_offer == expected_response


@pytest.mark.config(ALTPIN_PRICE_GAIN_RATIO_DEGRADATION=-0.03)
@pytest.mark.experiments3(filename='exp3_alt_point_switcher.json')
@pytest.mark.now('2017-05-25T11:30:00+0300')
@ORDER_OFFERS_SAVE_SWITCH
def test_altpin_from_ppaas(
        local_services,
        taxi_protocol,
        db,
        experiments3,
        load_json,
        pricing_data_preparer,
        mock_order_offers,
        order_offers_save_enabled,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_trip_information(time=1320, distance=5900)
    pricing_data_preparer.set_cost(
        user_cost=161, driver_cost=161, category='econom',
    )
    pricing_data_preparer.push(id='37.64941692')

    pricing_data_preparer.set_trip_information(time=120, distance=500)
    pricing_data_preparer.set_cost(
        user_cost=212, driver_cost=212, category='econom',
    )
    pricing_data_preparer.push(id='37.65107812')
    pricing_data_preparer.push(id='37.65136435')
    pricing_data_preparer.push(id='37.65151620')
    pricing_data_preparer.set_trip_information(time=600, distance=4200)
    pricing_data_preparer.set_cost(
        user_cost=164, driver_cost=164, category='econom',
    )
    pricing_data_preparer.push(id='37.65051928')

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offers = response.json()
    main_offer_id = response_without_offers.pop('offer')
    for service_level in expected_response['service_levels']:
        service_level['offer'] = main_offer_id
    alt_offer_id = response_without_offers['alternatives']['options'][0].pop(
        'offer',
    )
    for alt_opt in expected_response['alternatives']['options']:
        for service_level in alt_opt['service_levels']:
            service_level['offer'] = alt_offer_id
    assert response_without_offers == expected_response

    main_offer = utils.get_offer(
        main_offer_id, db, mock_order_offers, order_offers_save_enabled,
    )
    alt_offer = utils.get_offer(
        alt_offer_id, db, mock_order_offers, order_offers_save_enabled,
    )
    if order_offers_save_enabled:
        assert mock_order_offers.mock_save_offer.times_called == 2

    assert main_offer
    assert alt_offer

    assert 'alternative_type' not in main_offer
    assert alt_offer['alternative_type'] == 'altpin'
    assert alt_offer['prices']
    for price in alt_offer['prices']:
        assert 'pricing_data' in price
        assert 'driver' in price['pricing_data']
        assert 'user' in price['pricing_data']


@pytest.mark.config(PPAAS_FALLBACK_METHODS=['altpoints'])
@pytest.mark.now('2017-05-25T11:30:00+0300')
@ORDER_OFFERS_SAVE_SWITCH
def test_altpins_fallback(
        local_services,
        taxi_protocol,
        db,
        load_json,
        pricing_data_preparer,
        mock_order_offers,
        order_offers_save_enabled,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_trip_information(time=600, distance=4200)
    pricing_data_preparer.set_cost(
        user_cost=164, driver_cost=164, category='econom',
    )
    request = load_json('request.json')
    expected_response = load_json('expected_response.json')

    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offers = response.json()
    main_offer_id = response_without_offers.pop('offer')
    for service_level in expected_response['service_levels']:
        service_level['offer'] = main_offer_id

    assert response_without_offers == expected_response
    assert utils.get_offer(
        main_offer_id, db, mock_order_offers, order_offers_save_enabled,
    )
    if order_offers_save_enabled:
        assert mock_order_offers.mock_save_offer.times_called == 1


@pytest.mark.config(PPAAS_TRACKER_FALLBACK_METHODS=['nearest-drivers'])
@pytest.mark.now('2017-05-25T11:30:00+0300')
def test_altpins_failed_fallback(
        local_services,
        taxi_protocol,
        db,
        load_json,
        mockserver,
        pricing_data_preparer,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    @mockserver.json_handler('/alt/alt/v1/pin')
    def mock_pickup_altpoints(request):
        return mockserver.make_response('', 500)

    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_trip_information(time=600, distance=4200)
    pricing_data_preparer.set_cost(
        user_cost=164, driver_cost=164, category='econom',
    )

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offers = response.json()
    main_offer_id = response_without_offers.pop('offer')
    for service_level in expected_response['service_levels']:
        service_level['offer'] = main_offer_id

    assert response_without_offers == expected_response
    assert utils.get_offer(main_offer_id, db)


@pytest.mark.experiments3(
    name='hide_altpin',
    consumers=['protocol/routestats'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'hide': True},
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
def test_hide_altpin(
        local_services, taxi_protocol, load_json, pricing_data_preparer,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')

    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_trip_information(time=600, distance=4200)
    pricing_data_preparer.set_cost(
        user_cost=164, driver_cost=164, category='econom',
    )

    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offer = response.json()
    offer_id = response_without_offer.pop('offer')
    for service_level in expected_response['service_levels']:
        service_level['offer'] = offer_id
    assert response_without_offer == expected_response


@pytest.mark.now('2017-05-25T11:30:00+0300')
def test_no_altpin_from_pp_zone(
        local_services,
        taxi_protocol,
        db,
        load_json,
        now,
        pricing_data_preparer,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_trip_information(time=660, distance=4300)
    pricing_data_preparer.set_cost(
        user_cost=165, driver_cost=165, category='econom',
    )

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')

    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offer = response.json()
    offer_id = response_without_offer.pop('offer')
    for service_level in expected_response['service_levels']:
        service_level['offer'] = offer_id
    assert response_without_offer == expected_response


@pytest.mark.config(ALTPIN_PRICE_GAIN_RATIO_DEGRADATION=-0.03)
@pytest.mark.experiments3(filename='exp3_alt_point_switcher.json')
@pytest.mark.now('2017-05-25T11:30:00+0300')
def test_no_altpin_no_pp_zone(
        local_services,
        taxi_protocol,
        db,
        load_json,
        now,
        pricing_data_preparer,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_trip_information(time=1320, distance=5900)

    pricing_data_preparer.set_cost(
        user_cost=161, driver_cost=161, category='econom',
    )
    pricing_data_preparer.push(id='37.64941692')

    pricing_data_preparer.set_trip_information(time=120, distance=500)
    pricing_data_preparer.set_cost(
        user_cost=212, driver_cost=212, category='econom',
    )
    pricing_data_preparer.push(id='37.65107812')
    pricing_data_preparer.push(id='37.65136435')
    pricing_data_preparer.push(id='37.65151620')
    pricing_data_preparer.set_trip_information(time=600, distance=4200)
    pricing_data_preparer.set_cost(
        user_cost=164, driver_cost=164, category='econom',
    )
    pricing_data_preparer.push(id='37.65051928')

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')

    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offer = response.json()
    offer_id = response_without_offer.pop('offer')
    for service_level in expected_response['service_levels']:
        service_level['offer'] = offer_id
    for option in response_without_offer['alternatives']['options']:
        alt_offer_id = option.pop('offer')
        for service_level in option['service_levels']:
            assert 'offer' in service_level
            assert alt_offer_id == service_level.pop('offer')
    assert response_without_offer == expected_response


@pytest.mark.config(
    ALTPIN_MONEY_ZONES={
        '__default__': {
            'price_gain_absolute': 10,
            'price_gain_absolute_minorder': 0,
            'price_gain_ratio': 0,
            'route_gain_ratio': 0,
            'time_gain_ratio': 0,
        },
    },
    ALTPIN_PRICE_GAIN_RATIO_DEGRADATION=-0.03,
)
@pytest.mark.experiments3(filename='exp3_alt_point_switcher.json')
@pytest.mark.now('2017-05-25T11:30:00+0300')
@ORDER_OFFERS_SAVE_SWITCH
def test_altpin_price_delta_not_zero(
        local_services,
        taxi_protocol,
        db,
        load_json,
        now,
        pricing_data_preparer,
        mock_order_offers,
        order_offers_save_enabled,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')

    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_trip_information(time=1380, distance=6300)
    pricing_data_preparer.set_cost(
        user_cost=99, driver_cost=99, category='econom',
    )
    pricing_data_preparer.push()
    pricing_data_preparer.set_trip_information(time=600, distance=4200)
    pricing_data_preparer.set_cost(
        user_cost=164, driver_cost=164, category='econom',
    )

    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offer = response.json()
    main_offer_id = response_without_offer.pop('offer')
    alt_offer_id = response_without_offer['alternatives']['options'][0].pop(
        'offer',
    )
    for service_level in expected_response['service_levels']:
        service_level['offer'] = main_offer_id
    for option in expected_response['alternatives']['options']:
        for service_level in option['service_levels']:
            service_level['offer'] = alt_offer_id
    assert response_without_offer == expected_response

    main_offer = utils.get_offer(
        main_offer_id, db, mock_order_offers, order_offers_save_enabled,
    )
    alt_offer = utils.get_offer(
        alt_offer_id, db, mock_order_offers, order_offers_save_enabled,
    )

    assert main_offer
    assert alt_offer

    assert 'alternative_type' not in main_offer
    assert alt_offer['alternative_type'] == 'altpin'


@pytest.mark.config(
    ALTPIN_MONEY_ZONES={
        '__default__': {
            'price_gain_absolute': 10,
            'price_gain_absolute_minorder': 0.7,
            'price_gain_ratio': 0,
            'route_gain_ratio': 0,
            'time_gain_ratio': 0,
        },
    },
    ALTPIN_PRICE_GAIN_RATIO_DEGRADATION=-0.03,
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
def test_altpin_price_gain_absolute_minorder(
        local_services,
        taxi_protocol,
        db,
        load_json,
        now,
        mockserver,
        pricing_data_preparer,
):
    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_trip_information(time=1380, distance=6300)
    pricing_data_preparer.set_cost(user_cost=99, driver_cost=99)
    pricing_data_preparer.push()
    pricing_data_preparer.set_trip_information(time=600, distance=4200)
    pricing_data_preparer.set_cost(user_cost=164, driver_cost=164)

    @mockserver.json_handler('/alt/alt/v1/pin')
    def _mock_pickup_altpoints(request):
        body = json.loads(request.get_data())
        assert body['eta_classes'] == ['business']
        assert len(body['prices']) == 1
        assert len(body['svs']) == 1
        return load_json('altpoints.json')

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def _mock_surge_get_surge(request):
        data = json.loads(request.get_data())
        if data['point_a'] == [37.60000000111, 55.7380111]:
            assert len(data['classes']) == 1
        return utils.get_surge_calculator_response(request, 1)

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offer = response.json()
    main_offer_id = response_without_offer.pop('offer')

    assert 'alternatives' not in response_without_offer

    main_offer = utils.get_offer(main_offer_id, db)

    assert main_offer

    assert 'alternative_type' not in main_offer


@pytest.mark.config(
    ALTPIN_MONEY_ZONES={
        '__default__': {
            'price_gain_absolute': 10,
            'price_gain_absolute_minorder': 0,
            'price_gain_ratio': 0,
            'route_gain_ratio': 0,
            'time_gain_ratio': 0,
        },
    },
    ALTPIN_PRICE_GAIN_RATIO_DEGRADATION=-0.03,
)
@pytest.mark.experiments3(filename='exp3_alt_point_switcher.json')
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('fixed_price')
def test_altpin_price_delta_not_zero_fixed_price(
        local_services_fixed_price,
        taxi_protocol,
        db,
        load_json,
        now,
        pricing_data_preparer,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_trip_information(time=1380, distance=6300)
    pricing_data_preparer.set_cost(
        user_cost=99, driver_cost=99, category='econom',
    )
    pricing_data_preparer.push()
    pricing_data_preparer.set_trip_information(time=780, distance=800)
    pricing_data_preparer.set_cost(
        user_cost=209, driver_cost=209, category='econom',
    )

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')

    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offer = response.json()
    main_offer_id = response_without_offer.pop('offer')
    alt_offer_id = response_without_offer['alternatives']['options'][0].pop(
        'offer',
    )
    for service_level in expected_response['service_levels']:
        service_level['offer'] = main_offer_id
    for option in expected_response['alternatives']['options']:
        for service_level in option['service_levels']:
            service_level['offer'] = alt_offer_id
    assert response_without_offer == expected_response

    main_offer = utils.get_offer(main_offer_id, db)
    alt_offer = utils.get_offer(alt_offer_id, db)

    assert main_offer
    assert alt_offer

    assert 'alternative_type' not in main_offer
    assert alt_offer['alternative_type'] == 'altpin'


@pytest.mark.config(ALTPIN_PRICE_GAIN_RATIO_DEGRADATION=0.0)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(filename='exp3_alt_point_switcher.json')
def test_altpin_uri(
        local_services,
        taxi_protocol,
        db,
        load_json,
        mockserver,
        experiments3,
        pricing_data_preparer,
):
    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_trip_information(time=1380, distance=6300)
    pricing_data_preparer.set_cost(user_cost=99, driver_cost=99)
    pricing_data_preparer.push()
    pricing_data_preparer.set_trip_information(time=600, distance=4200)
    pricing_data_preparer.set_cost(user_cost=164, driver_cost=164)

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        geo_docs = load_json('yamaps.json')
        return geo_docs

    request = load_json('request.json')
    load_json('expected_response.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    assert 'uri' in response.json()['alternatives']['options'][0]['address']


@pytest.mark.now('2017-05-25T11:30:00+0300')
def test_altpin_without_eta(
        local_services,
        taxi_protocol,
        db,
        load_json,
        now,
        pricing_data_preparer,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_trip_information(time=600, distance=4200)
    pricing_data_preparer.set_cost(
        user_cost=164, driver_cost=164, category='econom',
    )

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')

    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offer = response.json()
    offer_id = response_without_offer.pop('offer')
    for service_level in expected_response['service_levels']:
        service_level['offer'] = offer_id
    assert response_without_offer == expected_response


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('child_tariff')
@pytest.mark.config(
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
    ALL_CATEGORIES=DEFAULT_ALL_CATEGORIES,
    APPLICATION_BRAND_CATEGORIES_SETS={'__default__': DEFAULT_ALL_CATEGORIES},
    DEFAULT_URGENCY=600,
)
@pytest.mark.parametrize('with_tariff_reqs', [True, False])
def test_summary_with_tariff_specific(
        local_services,
        taxi_protocol,
        db,
        load_json,
        now,
        config,
        pricing_data_preparer,
        with_tariff_reqs,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_cost(
        user_cost=317, driver_cost=317, category='econom',
    )
    pricing_data_preparer.set_cost(
        user_cost=432, driver_cost=432, category='child_tariff',
    )
    pricing_data_preparer.set_cost(
        user_cost=539, driver_cost=539, category='comfortplus',
    )
    pricing_data_preparer.set_cost(
        user_cost=770, driver_cost=770, category='vip',
    )
    pricing_data_preparer.set_cost(
        user_cost=513, driver_cost=513, category='minivan',
    )
    pricing_data_preparer.set_trip_information(
        time=1421.5866954922676, distance=7514.629286628636,
    )
    request = load_json('request.json')

    if with_tariff_reqs:
        tariff_requirements = [
            {'class': 'child_tariff', 'requirements': request['requirements']},
        ]
        for _class in ['econom', 'comfortplus', 'vip', 'minivan']:
            tariff_requirements.append({'class': _class, 'requirements': {}})
        request['tariff_requirements'] = tariff_requirements

    expected_response = load_json('expected_response.json')

    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offer = response.json()
    offer_id = response_without_offer.pop('offer')
    for service_level in expected_response['service_levels']:
        service_level['offer'] = offer_id
    if not with_tariff_reqs:
        for sl in expected_response['service_levels']:
            sl.pop('tariff_requirements', None)

    assert response_without_offer == expected_response

    offer = utils.get_saved_offer(db)
    assert offer['_id'] == offer_id
    assert offer['authorized']
    assert offer['created'] == now.replace(microsecond=0)
    assert not offer['destination_is_airport']
    assert offer['distance'] == 7514.629286628636
    assert offer['due'] == (
        now.replace(microsecond=0) + datetime.timedelta(minutes=10)
    )
    assert not offer['is_fixed_price']
    assert len(offer['prices']) == 6
    for price in offer['prices']:
        assert not price['is_fixed_price']
    assert offer['classes_requirements']['child_tariff'] == {
        'childchair_for_child_tariff': 3,
    }
    assert offer['route'] == [
        [37.647932797875484, 55.742884944005525],
        [37.58992385864258, 55.73382568359375],
    ]
    assert offer['time'] == 1421.5866954922676
    assert offer['user_id'] == 'b300bda7d41b4bae8d58dfa93221ef16'


@pytest.mark.now('2017-05-25T11:30:00+0300')
def test_summary_with_discount(
        local_services,
        taxi_protocol,
        db,
        load_json,
        now,
        pricing_data_preparer,
):
    pricing_data_preparer.set_discount(
        category='econom',
        discount={
            'value': 0.35,
            'original_value': 0.35,
            'price': 317.0,
            'description': '',
            'reason': 'for_all',
            'method': 'subvention-fix',
            'limited_rides': False,
        },
    )
    pricing_data_preparer.set_discount_meta(
        category='econom', price=317, value=0.35,
    )

    pricing_data_preparer.set_discount(
        category='vip',
        discount={
            'value': 0.35,
            'original_value': 0.35,
            'price': 770.0,
            'reason': 'analytics',
            'method': 'full-driver-less',
            'limited_rides': False,
        },
    )

    pricing_data_preparer.set_discount_meta(
        category='vip', price=770, value=0.35,
    )

    pricing_data_preparer.set_discount(
        category='business',
        discount={
            'value': 0.14,
            'original_value': 0.14,
            'price': 489.0,
            'reason': 'analytics',
            'method': 'full-driver-less',
            'limited_rides': False,
        },
    )

    pricing_data_preparer.set_discount_meta(
        category='business', price=489, value=0.14,
    )

    pricing_data_preparer.set_discount(
        category='comfortplus',
        discount={
            'value': 0.2,
            'original_value': 0.2,
            'price': 539.0,
            'reason': 'analytics',
            'method': 'full-driver-less',
            'limited_rides': False,
        },
    )

    pricing_data_preparer.set_discount_meta(
        category='comfortplus', price=539, value=0.2,
    )

    request = load_json('request.json')

    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200
    response_without_offer = response.json()
    offer_id = response_without_offer.pop('offer')
    offer = utils.get_offer(offer_id, db)
    assert 'discount' in offer
    last_class = offer['discount']['by_classes'][-1]
    offer['discount']['by_classes'].sort(key=lambda x: x['class'])
    assert offer['discount'] == {
        'cashbacks': [],
        'by_classes': [
            {
                'price': 489,
                'class': 'business',
                'value': 0.14,
                'reason': 'analytics',
                'method': 'full-driver-less',
                'limited_rides': False,
            },
            {
                'price': 539,
                'class': 'comfortplus',
                'value': 0.2,
                'reason': 'analytics',
                'method': 'full-driver-less',
                'limited_rides': False,
            },
            {
                'price': 317,
                'class': 'econom',
                'value': 0.35,
                'description': '',
                'reason': 'for_all',
                'method': 'subvention-fix',
                'limited_rides': False,
            },
            {
                'price': 770,
                'class': 'vip',
                'value': 0.35,
                'reason': 'analytics',
                'method': 'full-driver-less',
                'limited_rides': False,
            },
        ],
        'reason': last_class['reason'],
        'method': last_class['method'],
        'price': 0,
        'value': 0,
        'driver_less_coeff': 1.0,
        'limited_rides': False,
        'with_restriction_by_usages': False,
    }

    for price in offer['prices']:
        assert 'driver_price' in price


@pytest.mark.user_experiments('discount_strike', 'fixed_price')
@pytest.mark.now('2017-05-25T11:30:00+0300')
def test_summary_with_discount_show_strikethrough_price(
        local_services_fixed_price,
        taxi_protocol,
        db,
        load_json,
        now,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(category='business', price=1000)
    request = load_json('request.json')

    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200
    response_without_offer = response.json()
    levels = response_without_offer.pop('service_levels')
    for level in levels:
        if level['class'] == 'business':
            assert 'original_price' in level
        else:
            assert 'original_price' not in level


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('fixed_price')
def test_summary_eta(
        local_services_fixed_price,
        taxi_protocol,
        db,
        load_json,
        now,
        mockserver,
        pricing_data_preparer,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_trip_information(
        time=1421.5866954922676, distance=7514.629286628636,
    )
    pricing_data_preparer.set_user_category_prices_id(
        category_id='b7c4d5f6aa3b40a3807bb74b3bc042af',
        category_prices_id='c/b7c4d5f6aa3b40a3807bb74b3bc042af',
    )
    pricing_data_preparer.set_cost(
        user_cost=317, driver_cost=317, category='econom',
    )
    request = load_json('request.json')
    expected_response = load_json('expected_response.json')

    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offer = response.json()
    offer_id = response_without_offer.pop('offer')
    for service_level in expected_response['service_levels']:
        service_level['offer'] = offer_id
    assert response_without_offer == expected_response

    offer = utils.get_saved_offer(db)
    assert offer['_id'] == offer_id
    assert offer['authorized']
    assert offer['created'] == now.replace(microsecond=0)
    assert not offer['destination_is_airport']
    assert offer['distance'] == 7514.629286628636
    assert offer['due'] == (
        now.replace(microsecond=0) + datetime.timedelta(minutes=10)
    )
    assert offer['is_fixed_price']
    del offer['prices'][0]['pricing_data']
    assert offer['prices'] == [
        {
            'cls': 'econom',
            'cat_type': 'application',
            'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
            'driver_price': 317.0,
            'price': 317.0,
            'sp': 1.0,
            'is_fixed_price': True,
            'using_new_pricing': True,
        },
    ]
    assert offer['classes_requirements'] == {}
    assert offer['route'] == [
        [37.647932797875484, 55.742884944005525],
        [37.58992385864258, 55.73382568359375],
    ]
    assert offer['time'] == 1421.5866954922676
    assert offer['user_id'] == 'b300bda7d41b4bae8d58dfa93221ef16'


@pytest.mark.config(ALTPIN_PRICE_GAIN_RATIO_DEGRADATION=-0.03)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(filename='exp3_alt_point_switcher.json')
def test_altpin_eta(
        local_services,
        taxi_protocol,
        db,
        load_json,
        mockserver,
        now,
        pricing_data_preparer,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    @mockserver.json_handler('/pin_storage/v1/create_pin')
    def mock_pin_storage_create_pin(request):
        request_json = json.loads(request.get_data()).get('pin')
        assert 'tariff_zone' in request_json
        assert 'altpin_offer_id' in request_json

    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_trip_information(time=1320, distance=5900)
    pricing_data_preparer.set_cost(
        user_cost=206, driver_cost=206, category='econom',
    )
    pricing_data_preparer.push(id='37.64941692')

    pricing_data_preparer.set_trip_information(time=120, distance=500)
    pricing_data_preparer.set_cost(
        user_cost=212, driver_cost=212, category='econom',
    )
    pricing_data_preparer.push(id='37.65107812')
    pricing_data_preparer.push(id='37.65136435')
    pricing_data_preparer.push(id='37.65151620')
    pricing_data_preparer.set_trip_information(time=780, distance=800)
    pricing_data_preparer.set_cost(
        user_cost=209, driver_cost=209, category='econom',
    )
    pricing_data_preparer.push(id='37.65051928')

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offer = response.json()
    main_offer_id = response_without_offer.pop('offer')
    alt_offer_id = response_without_offer['alternatives']['options'][0].pop(
        'offer',
    )
    for service_level in expected_response['service_levels']:
        service_level['offer'] = main_offer_id
    for option in expected_response['alternatives']['options']:
        for service_level in option['service_levels']:
            service_level['offer'] = alt_offer_id
    assert response_without_offer == expected_response

    main_offer = utils.get_offer(main_offer_id, db)
    alt_offer = utils.get_offer(alt_offer_id, db)

    assert main_offer
    assert alt_offer

    assert 'alternative_type' not in main_offer
    assert alt_offer['alternative_type'] == 'altpin'


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('fixed_price')
@pytest.mark.parametrize(
    'config_enabled',
    [
        pytest.param(
            value,
            marks=pytest.mark.experiments3(
                is_config=True,
                name='plugin_offer_coupon',
                consumers=['protocol/routestats'],
                match={'predicate': {'type': 'true'}, 'enabled': True},
                clauses=[],
                default_value={'enabled': value},
            ),
        )
        for value in (False, True)
    ],
)
def test_coupon_saved_in_offer(
        local_services_fixed_price,
        taxi_protocol,
        db,
        load_json,
        config_enabled,
        pricing_data_preparer,
):
    pricing_data_preparer.set_coupon(
        valid=True,
        value=100,
        percent=10,
        limit=50,
        description='description',
        valid_classes=['econom'],
        details=['some_detail'],
        format_currency=True,
    )

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    content = response.json()

    offer = utils.get_offer(content['offer'], db)
    coupon_info = offer.get('extra_data', {}).get('coupon')

    if config_enabled:
        assert coupon_info == {
            'code': 'discount300',
            'value': 100,
            'percent': 10,
            'limit': 50,
            'valid': True,
            'classes': ['econom'],
        }
    else:
        assert coupon_info is None


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments(
    'valid_promo',
    'invalid_promo_wrong_zone',
    'invalid_promo_unavailable_class',
    'invalid_promo_no_tanker_key',
)
@pytest.mark.config(
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
    ALL_CATEGORIES=['econom', 'comfortplus', 'vip', 'pool'],
    ROUTESTATS_PROMOTION_TARIFFS={
        'moscow': {
            'econom': {
                'for_selected_classes': ['econom', 'comfortplus'],
                'show_count': 3,
                'delta_present': 100,
                'experiment': 'valid_promo',
            },
            'pool': {
                'for_selected_classes': ['econom'],
                'show_count': 5,
                'experiment': 'valid_promo_for_pool',
            },
            'comfort': {
                'for_selected_classes': ['comfortplus'],
                'show_count': 3,
                'experiment': 'invalid_promo_unavailable_class',
            },
            'comfortplus': {
                'for_selected_classes': ['econom', 'comfortplus'],
                'show_count': 3,
                'experiment': 'invalid_promo_no_tanker_key',
            },
            'vip': {
                'delta_present': 100,
                'for_selected_classes': ['comfortplus'],
                'show_count': 3,
                'experiment': 'invalid_promo_user_without_experiment',
            },
        },
    },
)
@pytest.mark.translations(
    client_messages={
        'econom.highlight_moscow': {
            'en': 'New Econom Tariff For Moscow Region',
        },
        'vip.highlight_spb': {'en': 'New Vip Tariff For Spb Region'},
    },
)
def test_promotion_tariffs(
        local_services,
        taxi_protocol,
        db,
        load_json,
        now,
        mockserver,
        pricing_data_preparer,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_trip_information(time=1440, distance=7600)
    pricing_data_preparer.set_cost(
        category='econom', user_cost=317, driver_cost=317,
    )
    pricing_data_preparer.set_cost(
        category='child_tariff', user_cost=432, driver_cost=432,
    )
    pricing_data_preparer.set_cost(
        category='comfortplus', user_cost=539, driver_cost=539,
    )
    pricing_data_preparer.set_cost(
        category='vip', user_cost=770, driver_cost=770,
    )
    pricing_data_preparer.set_cost(
        category='minivan', user_cost=513, driver_cost=513,
    )

    headers = {
        'User-Agent': (
            'ru.yandex.taxi.inhouse/4.99.8769 '
            '(iPhone; iPhone7,2; iOS 11.0; Darwin)'
        ),
    }
    request = load_json('request.json')
    expected_response = load_json('expected_response.json')
    taxi_protocol.tests_control(invalidate_caches=True, now=now)

    response = taxi_protocol.post('3.0/routestats', request, headers=headers)

    assert response.status_code == 200
    response_without_offer = response.json()
    offer_id = response_without_offer.pop('offer')
    for service_level in expected_response['service_levels']:
        service_level['offer'] = offer_id
    assert response_without_offer == expected_response


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments(
    'valid_promo',
    'invalid_promo_wrong_zone',
    'invalid_promo_unavailable_class',
    'invalid_promo_no_tanker_key',
)
@pytest.mark.config(
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
    ALL_CATEGORIES=['econom', 'comfortplus', 'vip', 'pool'],
    ROUTESTATS_PROMOTION_TARIFFS={
        'moscow': {
            'econom': {
                'for_selected_classes': ['econom', 'comfortplus'],
                'show_count': 3,
                'delta_present': 0,
                'experiment': 'valid_promo',
            },
            'vip': {
                'delta_present': 0,
                'for_selected_classes': ['comfortplus'],
                'show_count': 3,
                'experiment': 'invalid_promo_user_without_experiment',
            },
        },
    },
)
@pytest.mark.translations(
    client_messages={
        'econom.highlight_moscow': {
            'en': 'New Econom Tariff For Moscow Region',
        },
        'vip.highlight_spb': {'en': 'New Vip Tariff For Spb Region'},
    },
)
def test_promotion_tariffs_delta(
        local_services,
        taxi_protocol,
        db,
        load_json,
        mockserver,
        pricing_data_preparer,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_trip_information(time=1440, distance=7600)
    pricing_data_preparer.set_cost(
        category='econom', user_cost=317, driver_cost=317,
    )
    pricing_data_preparer.set_cost(
        category='child_tariff', user_cost=432, driver_cost=432,
    )
    pricing_data_preparer.set_cost(
        category='comfortplus', user_cost=539, driver_cost=539,
    )
    pricing_data_preparer.set_cost(
        category='vip', user_cost=770, driver_cost=770,
    )
    pricing_data_preparer.set_cost(
        category='minivan', user_cost=513, driver_cost=513,
    )

    headers = {
        'User-Agent': (
            'ru.yandex.taxi.inhouse/4.99.8769 '
            '(iPhone; iPhone7,2; iOS 11.0; Darwin)'
        ),
    }
    request = load_json('request.json')
    expected_response = load_json('expected_response.json')

    response = taxi_protocol.post('3.0/routestats', request, headers=headers)

    assert response.status_code == 200
    response_without_offer = response.json()
    offer_id = response_without_offer.pop('offer')
    for service_level in expected_response['service_levels']:
        service_level['offer'] = offer_id
    assert response_without_offer == expected_response


@pytest.mark.filldb(users='with_ya_plus')
@pytest.mark.user_experiments('discount_strike', 'fixed_price', 'ya_plus')
@pytest.mark.config(
    YANDEX_PLUS_DISCOUNT={'rus': {'econom': 0.1, 'minivan': 0.1}},
)
def test_ya_plus_multiplier(
        local_services_fixed_price,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        now,
        mockserver,
):
    pricing_data_preparer.set_cost(100, 100)
    pricing_data_preparer.set_strikeout(120)

    request = load_json('request.json')
    headers = {
        'User-Agent': (
            'ru.yandex.taxi.inhouse/4.99.8769 '
            '(iPhone; iPhone7,2; iOS 11.0; Darwin)'
        ),
    }

    response = taxi_protocol.post('3.0/routestats', request, headers=headers)
    assert response.status_code == 200
    data = response.json()
    offer_id = data['offer']
    res = utils.get_offer(offer_id, db)
    assert 'price_modifiers' in res
    price_modifiers = res['price_modifiers']
    assert price_modifiers['items'][0]['reason'] == 'ya_plus'
    assert price_modifiers['items'][0]['pay_subventions']
    # 'econom' has a discount by 'ya_plus' reason
    assert data['service_levels'][0]['class'] == 'econom'
    assert data['service_levels'][0]['discount'] == 'ya_plus'
    assert 'original_price' in data['service_levels'][0]
    # 'comfortplus' doesn't have a discount
    assert data['service_levels'][5]['class'] == 'minivan'
    assert data['service_levels'][5]['discount'] == 'ya_plus'
    assert 'original_price' in data['service_levels'][5]


@pytest.mark.user_experiments('fixed_price')
@pytest.mark.parametrize(
    ['requirements', 'expected_multipliers'],
    (
        ({'cargo_loaders': 2}, ('22.000000',)),
        ({'cargo_loaders': [2]}, ('22.000000',)),
        ({'cargo_loaders': 1}, ('11.000000',)),
        ({'cargo_type': 'lcv_m'}, ('55.000000',)),
        ({'cargo_loaders': [1, 1]}, ('121.000000',)),
        (
            {'cargo_type': ['lcv_l'], 'cargo_loaders': [1, 1]},
            ('121.000000', '66.000000'),
        ),
    ),
)
@pytest.mark.filldb(
    requirements='with_multiplier', tariffs='with_multiplier_req',
)
def test_requirements_multiplier(
        local_services_fixed_price,
        taxi_protocol,
        db,
        load_json,
        now,
        requirements,
        expected_multipliers,
        mockserver,
        pricing_data_preparer,
):
    request = load_json('request.json')
    for req_name, req_value in requirements.items():
        request['requirements'][req_name] = req_value
        request['tariff_requirements'][0]['requirements'][req_name] = req_value

    headers = {
        'User-Agent': (
            'ru.yandex.taxi.inhouse/4.99.8769 '
            '(iPhone; iPhone7,2; iOS 11.0; Darwin)'
        ),
    }

    response = taxi_protocol.post('3.0/routestats', request, headers=headers)
    assert response.status_code == 200
    data = response.json()
    offer_id = data['offer']
    res = utils.get_offer(offer_id, db)
    assert 'price_modifiers' in res
    price_modifiers = res['price_modifiers']
    assert len(price_modifiers['items']) == len(requirements)
    for price_modifier_item, expected_multiplier in zip(
            price_modifiers['items'], expected_multipliers,
    ):
        assert price_modifier_item['reason'] == 'requirements'
        assert price_modifier_item['pay_subventions'] is False
        assert price_modifier_item['tariff_categories'] == ['business']
        assert price_modifier_item['type'] == 'multiplier'
        assert price_modifier_item['value'] == expected_multiplier


@pytest.mark.filldb(users='with_ya_plus')
@pytest.mark.user_experiments('mastercard_discount')
@pytest.mark.config(YANDEX_PLUS_DISCOUNT={'rus': {'econom': 0.1}})
@pytest.mark.parametrize(
    'payment_method_id,discounts_from_service',
    [
        (
            'cash',
            {
                'discounts': [
                    {
                        'class': 'econom',
                        'discount': {
                            'value': 0.12,
                            'price': 150.0,
                            'reason': 'analytics',
                            'method': 'full',
                        },
                    },
                    {
                        'class': 'business',
                        'discount': {
                            'value': 0.12,
                            'price': 150.0,
                            'reason': 'for_all',
                            'method': 'full',
                        },
                    },
                ],
                'discount_offer_id': '123456',
            },
        ),
        (
            'card-discount-mastercard',
            {
                'discounts': [
                    {
                        'class': 'econom',
                        'discount': {
                            'value': 0.12,
                            'price': 150.0,
                            'description': 'discount012',
                            'reason': 'analytics',
                            'method': 'full',
                            'payment_system': 'Mastercard',
                        },
                    },
                    {
                        'class': 'business',
                        'discount': {
                            'value': 0.12,
                            'price': 150.0,
                            'description': 'discount_mastercard',
                            'reason': 'for_all',
                            'method': 'full',
                            'payment_system': 'Mastercard',
                        },
                    },
                ],
                'discount_offer_id': '123456',
            },
        ),
    ],
)
def test_discount_tag(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        now,
        discounts,
        payment_method_id,
        discounts_from_service,
        mockserver,
):
    for item in discounts_from_service['discounts']:
        category = item['class']
        discount = item['discount']
        pdp_discount = {}
        if 'payment_system' in discount:
            pdp_discount['payment_system'] = discount['payment_system']
        if 'description' in discount:
            pdp_discount['description'] = discount['description']
        if 'reason' in discount:
            pdp_discount['reason'] = discount['reason']
        if 'method' in discount:
            pdp_discount['method'] = discount['method']
        pdp_discount['discount_offer_id'] = discounts_from_service[
            'discount_offer_id'
        ]
        pricing_data_preparer.set_discount(
            discount=pdp_discount, category=category,
        )
        pricing_data_preparer.set_discount_meta(
            price=discount['price'],
            value=discount['value'],
            category=category,
        )

    request = load_json('request.json')
    if payment_method_id == 'cash':
        payment = {'type': 'cash'}
    else:
        payment = {'type': 'card', 'payment_method_id': payment_method_id}
    request['payment'] = payment

    headers = {
        'User-Agent': (
            'ru.yandex.taxi.inhouse/4.99.8769 '
            '(iPhone; iPhone7,2; iOS 11.0; Darwin)'
        ),
    }

    response = taxi_protocol.post('3.0/routestats', request, headers=headers)
    assert response.status_code == 200
    data = response.json()

    if payment_method_id == 'cash':
        assert data['service_levels'][0]['class'] == 'econom'
        assert data['service_levels'][0]['discount'] == 'ya_plus'
        assert data['service_levels'][2]['class'] == 'business'
        assert data['service_levels'][2]['discount'] == 'other'
    elif payment_method_id == 'card-discount-mastercard':
        assert data['service_levels'][0]['class'] == 'econom'
        assert data['service_levels'][0]['discount'] == 'ya_plus_mastercard'
        assert data['service_levels'][2]['class'] == 'business'
        assert data['service_levels'][2]['discount'] == 'mastercard'


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('discount_strike', 'fixed_price')
def test_apply_discount_from_service(
        local_services,
        taxi_protocol,
        db,
        load_json,
        now,
        pricing_data_preparer,
):
    pricing_data_preparer.set_discount(
        category='econom',
        discount={
            'value': 0.12,
            'original_value': 0.12,
            'price': 150.0,
            'description': 'discount012',
            'reason': 'analytics',
            'method': 'full',
        },
    )
    pricing_data_preparer.set_discount_meta(
        category='econom', value=0.12, price=150,
    )
    request = load_json('request.json')

    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200
    data = response.json()
    offer_id = data['offer']
    res = utils.get_offer(offer_id, db)
    assert 'discount' in res
    assert 'by_classes' in res['discount']
    discounts = res['discount']['by_classes']
    for d in discounts:
        assert d['class'] == 'econom'
        assert d['value'] == 0.12
        assert d['description'] == 'discount012'


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.filldb(users='with_ya_plus')
@pytest.mark.user_experiments('discount_strike', 'fixed_price', 'ya_plus')
def test_driver_fix_price_with_unpaid_modifier(
        local_services_fixed_price,
        taxi_protocol,
        db,
        load_json,
        now,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(1000)
    pricing_data_preparer.set_user_category_prices_id(
        category_id='b7c4d5f6aa3b40a3807bb74b3bc042af',
        category_prices_id='c/b7c4d5f6aa3b40a3807bb74b3bc042af',
    )
    pricing_data_preparer.set_cost(user_cost=285, driver_cost=285)

    request = load_json('request.json')
    headers = {
        'User-Agent': (
            'ru.yandex.taxi.inhouse/4.99.8769 '
            '(iPhone; iPhone7,2; iOS 11.0; Darwin)'
        ),
    }

    response = taxi_protocol.post('3.0/routestats', request, headers=headers)
    assert response.status_code == 200
    data = response.json()
    offer_id = data['offer']
    res = utils.get_offer(offer_id, db)
    assert 'price_modifiers' in res
    price_modifiers = res['price_modifiers']
    assert price_modifiers['items'][0]['reason'] == 'ya_plus'
    assert not price_modifiers['items'][0]['pay_subventions']
    # 'econom' has a discount by 'ya_plus' reason
    assert data['service_levels'][0]['class'] == 'econom'
    assert data['service_levels'][0]['discount'] == 'ya_plus'
    assert 'original_price' in data['service_levels'][0]

    offer = utils.get_saved_offer(db)
    assert offer['is_fixed_price']
    del offer['prices'][0]['pricing_data']
    assert offer['prices'] == [
        {
            'cls': 'econom',
            'cat_type': 'application',
            'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
            'driver_price': 285.0,
            'price': 285.0,
            'sp': 1.0,
            'is_fixed_price': True,
            'using_new_pricing': True,
        },
    ]


@pytest.mark.filldb(users='with_ya_plus')
@pytest.mark.user_experiments('discount_strike', 'fixed_price', 'ya_plus')
def test_ya_plus_multiplier_mongo_config(
        local_services_fixed_price,
        taxi_protocol,
        db,
        pricing_data_preparer,
        load_json,
        mockserver,
        now,
):
    pricing_data_preparer.set_cost(100, 100)
    pricing_data_preparer.set_strikeout(120)

    request = load_json('request.json')
    headers = {
        'User-Agent': (
            'ru.yandex.taxi.inhouse/4.99.8769 '
            '(iPhone; iPhone7,2; iOS 11.0; Darwin)'
        ),
    }
    response = taxi_protocol.post('3.0/routestats', request, headers=headers)
    assert response.status_code == 200
    data = response.json()
    offer_id = data['offer']
    res = utils.get_offer(offer_id, db)
    assert 'price_modifiers' in res
    price_modifiers = res['price_modifiers']
    assert len(price_modifiers) == 1
    assert price_modifiers['items'][0]['reason'] == 'ya_plus'
    assert price_modifiers['items'][0]['pay_subventions']
    # 'econom' has a discount by 'ya_plus' reason
    assert data['service_levels'][0]['class'] == 'econom'
    assert data['service_levels'][0]['discount'] == 'ya_plus'
    assert 'original_price' in data['service_levels'][0]


@pytest.mark.filldb(users='with_ya_plus')
@pytest.mark.user_experiments('discount_strike', 'fixed_price', 'ya_plus')
@pytest.mark.config(PERSONAL_WALLET_DISCOUNTS_ENABLED=True)
def test_additional_discounts(
        local_services_fixed_price,
        taxi_protocol,
        db,
        load_json,
        pricing_data_preparer,
        now,
):
    pricing_data_preparer.set_fixed_price(enable=False)

    reasons = {'ya_plus'}

    request = load_json('request.json')
    headers = {
        'User-Agent': (
            'ru.yandex.taxi.inhouse/4.99.8769 '
            '(iPhone; iPhone7,2; iOS 11.0; Darwin)'
        ),
    }
    response = taxi_protocol.post('3.0/routestats', request, headers=headers)
    assert response.status_code == 200
    data = response.json()
    offer_id = data['offer']
    res = utils.get_offer(offer_id, db)

    assert 'price_modifiers' in res
    price_modifiers_items = res['price_modifiers']['items']
    modifier_reasons = {item['reason'] for item in price_modifiers_items}
    assert modifier_reasons == reasons

    for i, level in enumerate(data['service_levels']):
        if i == 0:
            assert set(level['additional_discounts']) == reasons
        else:
            assert 'additional_discounts' not in level


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('order_button_text_back')
@pytest.mark.parametrize(
    'search_title',
    (None, {'search_title': 'routestats.tariff.econom.button_title'}),
)
@pytest.mark.parametrize(
    'button_title',
    (None, {'button_title': 'routestats.tariff.econom.button_title'}),
)
@pytest.mark.parametrize(
    'button_title_glued',
    (
        None,
        {'button_title_glued': 'routestats.tariff.econom.button_title_glued'},
    ),
)
@pytest.mark.parametrize(
    'requirements_params',
    (
        pytest.param({'need_title_glued': False}, id='no_glued_requirements'),
        pytest.param(
            {
                'need_title_glued': False,
                'update_tafiff': {
                    's.0.glued_requirements': ['check'],
                    's.0.glued_optional_requirements': ['check'],
                },
            },
            id='no_required_glued_requirements',
        ),
        pytest.param(
            {
                'need_title_glued': True,
                'update_tafiff': {'s.0.glued_requirements': ['check']},
                'request_requirements': {'conditioner': False},
            },
            id='need_glued_requirements',
        ),
        pytest.param(
            {
                'need_title_glued': False,
                'update_tafiff': {'s.0.glued_requirements': ['check']},
                'request_requirements': {'check': True},
            },
            id='have_all_glued_requirements',
        ),
    ),
)
def test_button_texts(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        config,
        db,
        load_json,
        search_title,
        button_title,
        button_title_glued,
        requirements_params,
        mockserver,
):
    # prepare config ZONES_TARIFFS_SETTINGS
    zones_tariffs_settings = {'__default__': {'econom': {'keys': {}}}}
    for key in [search_title, button_title, button_title_glued]:
        if key:
            zones_tariffs_settings['__default__']['econom']['keys'].update(key)
    config.set_values({'ZONES_TARIFFS_SETTINGS': zones_tariffs_settings})

    # prepare tariff_settings
    if 'update_tafiff' in requirements_params:
        db.tariff_settings.update_one(
            {'hz': 'moscow'}, {'$set': requirements_params['update_tafiff']},
        )

    # prepare request
    request = load_json('request.json')
    if 'request_requirements' in requirements_params:
        request['requirements'] = requirements_params['request_requirements']

    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    service_level = response.json()['service_levels'][0]

    expected_title = None
    if button_title_glued and requirements_params['need_title_glued']:
        expected_title = 'Test title text glued'
    elif button_title:
        expected_title = 'Test title text'
    assert service_level.get('title') == expected_title

    if search_title:
        assert 'subtitle' not in service_level['search_screen']
        assert service_level['search_screen']['title'] == 'Test title text'


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(
    ZONES_TARIFFS_SETTINGS={
        '__default__': {
            'econom': {
                'search_animations': [
                    {
                        'match': {'status': 'searching'},
                        'phases': [
                            {
                                'duration': 10000,
                                'subtitle': (
                                    'routestats.tariff.econom.button_title'
                                ),
                                'title': (
                                    'routestats.tariff.econom.button_title'
                                ),
                                'type': 'call_for_drivers',
                            },
                        ],
                    },
                ],
            },
        },
    },
)
@pytest.mark.user_experiments('routestats_search_animations')
def test_search_screen_animations(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        now,
        mockserver,
):
    request = load_json('request.json')

    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    service_level = response.json()['service_levels'][0]
    assert service_level['search_screen'] == {
        'animations': [
            {
                'match': {'status': 'searching'},
                'phases': [
                    {
                        'duration': 10000,
                        'subtitle': 'Test title text',
                        'title': 'Test title text',
                        'type': 'call_for_drivers',
                    },
                ],
            },
        ],
    }


@pytest.mark.filldb(users='with_ya_plus')
@pytest.mark.user_experiments('discount_strike', 'fixed_price', 'ya_plus')
@pytest.mark.config(
    YANDEX_PLUS_DISCOUNT={'rus': {'econom': 0.1, 'minivan': 0.1}},
)
def test_ya_plus_user_with_corp_payment(
        local_services_fixed_price,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        now,
        mockserver,
):
    request = load_json('request.json')
    headers = {
        'User-Agent': (
            'ru.yandex.taxi.inhouse/4.99.8769 '
            '(iPhone; iPhone7,2; iOS 11.0; Darwin)'
        ),
    }

    response = taxi_protocol.post('3.0/routestats', request, headers=headers)
    assert response.status_code == 200
    data = response.json()
    offer_id = data['offer']
    assert 'discount' not in data['service_levels'][0]
    res = utils.get_offer(offer_id, db)
    assert 'price_modifiers' not in res


@pytest.mark.filldb(users='with_ya_plus')
@pytest.mark.user_experiments('discount_strike', 'fixed_price', 'ya_plus')
@pytest.mark.config(
    YANDEX_PLUS_DISCOUNT={'rus': {'econom': 0.1, 'minivan': 0.1}},
)
@pytest.mark.parametrize(
    'config_override',
    [
        None,
        (
            {
                'IGNORED_MODIFIER_BY_REQUIREMENTS': [
                    'childchair_for_child_tariff',
                ],
            }
        ),
    ],
)
def test_ya_plus_ignored_requirements(
        local_services_fixed_price,
        config,
        taxi_protocol,
        db,
        pricing_data_preparer,
        load_json,
        now,
        config_override,
        mockserver,
):
    if config_override is not None:
        config.set_values(config_override)

    request = load_json('request.json')
    headers = {
        'User-Agent': (
            'ru.yandex.taxi.inhouse/4.99.8769 '
            '(iPhone; iPhone7,2; iOS 11.0; Darwin)'
        ),
    }

    response = taxi_protocol.post('3.0/routestats', request, headers=headers)
    assert response.status_code == 200
    data = response.json()
    offer_id = data['offer']
    res = utils.get_offer(offer_id, db)
    if config_override:
        assert 'discount' not in data['service_levels'][0]
        assert 'price_modifiers' not in res
    else:
        assert 'discount' in data['service_levels'][0]
        assert 'price_modifiers' in res


@pytest.mark.translations(
    client_messages={
        'routestats.tariff_unavailable.'
        'unsupported_requirements_for_payment_method': {
            'ru': 'Payment method is not supported for selected requirement',
        },
    },
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('fixed_price')
@pytest.mark.config(ALL_CATEGORIES=['business'])
@pytest.mark.parametrize(
    'payment_type, method_id, payment_is_unavailable',
    [('cash', None, True), ('card', 'card-default', False)],
)
@pytest.mark.parametrize(
    'config_values',
    [
        pytest.param(
            {
                '__default__': {
                    'allowed_by_default': True,
                    'non_default_payment_types': [],
                },
                'nosmoking': {
                    'allowed_by_default': True,
                    'non_default_payment_types': ['cash'],
                },
            },
            id='allowed_by_default',
        ),
        pytest.param(
            {
                '__default__': {
                    'allowed_by_default': True,
                    'non_default_payment_types': [],
                },
                'nosmoking': {
                    'allowed_by_default': False,
                    'non_default_payment_types': ['card'],
                },
            },
            id='not_allowed_by_default',
        ),
    ],
)
@pytest.mark.parametrize(
    'add_unavailable_requirement',
    [
        pytest.param(False, id='no_requirement'),
        pytest.param(True, id='add_bad_requirement'),
    ],
)
@pytest.mark.parametrize(
    'prefiltration_enabled',
    [
        pytest.param(
            value,
            marks=pytest.mark.experiments3(
                is_config=True,
                name='routestats_tariffs_experimental_prefiltration',
                consumers=['protocol/routestats'],
                match={'predicate': {'type': 'true'}, 'enabled': True},
                clauses=[],
                default_value={'enabled': value},
            ),
        )
        for value in (False, True)
    ],
)
def test_allowed_payment_types_for_requirements(
        local_services,
        mockserver,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        now,
        config,
        config_values,
        payment_type,
        method_id,
        payment_is_unavailable,
        add_unavailable_requirement,
        prefiltration_enabled,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(request, 1)

    config.set_values(
        {'ALLOWED_PAYMENT_TYPES_FOR_REQUIREMENTS': config_values},
    )
    exp_unsupported_req = set()

    request = load_json('request.json')
    request['payment'] = {'type': payment_type, 'payment_method_id': method_id}

    if add_unavailable_requirement:
        request['requirements']['custom_req'] = True
        exp_unsupported_req.add('custom_req')
    if payment_is_unavailable:
        exp_unsupported_req.add('nosmoking')

    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200
    service_levels = response.json()['service_levels']
    assert len(service_levels) == 1
    service_level = service_levels[0]

    if payment_is_unavailable:
        assert (
            set(service_level['unsupported_requirements'])
            == exp_unsupported_req
        )
        assert service_level['tariff_unavailable'] == {
            'code': 'unsupported_requirements_for_payment_method',
            'message': (
                'Payment method is not supported for selected requirement'
            ),
        }
    elif add_unavailable_requirement:
        assert (
            set(service_level['unsupported_requirements'])
            == exp_unsupported_req
        )
        assert service_level['tariff_unavailable'] == {
            'code': 'unsupported_requirement',
            'message': 'Unsupported requirement',
        }
    else:
        assert 'unsupported_requirements' not in service_level
        assert 'tariff_unavailable' not in service_level


@pytest.mark.translations(
    client_messages={
        'routestats.tariff_unavailable.'
        'unsupported_payment_method': {'ru': 'Смените способ оплаты'},
    },
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('fixed_price')
@pytest.mark.parametrize(
    'enable_resctriction',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                ALLOWED_TARIFFS_BY_PAYMENT_TYPE={
                    'cargocorp': {'allowed_for_tariffs': ['express']},
                },
            ),
        ),
        pytest.param(False),
    ],
)
def test_paymentmethods_restrictions(
        local_services,
        mockserver,
        taxi_protocol,
        db,
        pricing_data_preparer,
        load_json,
        enable_resctriction,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(request, 1)

    request = load_json('request.json')
    request['payment'] = {
        'type': 'cargocorp',
        'payment_method_id': 'cargocorp-123',
    }

    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200
    econom_service_level = response.json()['service_levels'][0]

    if enable_resctriction:
        assert econom_service_level['tariff_unavailable'] == {
            'code': 'unsupported_payment_method',
            'message': 'Смените способ оплаты',
        }
    else:
        assert 'tariff_unavailable' not in econom_service_level


@pytest.mark.translations(
    client_messages={
        'routestats.tariff_unavailable.closed_country_border': {
            'ru': 'Cant build route over country border',
        },
    },
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('fixed_price')
@pytest.mark.config(ALL_CATEGORIES=['business'])
@pytest.mark.parametrize(
    ['is_unavailable'],
    [
        pytest.param(
            False,
            marks=pytest.mark.config(
                ROUTE_COUNTRY_BORDER_RESTRICTIONS={
                    'enabled': False,
                    'restricted_countries': [],
                },
            ),
            id='config_disabled',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                ROUTE_COUNTRY_BORDER_RESTRICTIONS={
                    'enabled': True,
                    'restricted_countries': [],
                },
            ),
            id='config_enabled_no_countries',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                ROUTE_COUNTRY_BORDER_RESTRICTIONS={
                    'enabled': True,
                    'restricted_countries': ['rus'],
                },
            ),
            id='config_enabled_A_point_country_match',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                ROUTE_COUNTRY_BORDER_RESTRICTIONS={
                    'enabled': True,
                    'restricted_countries': ['kaz'],
                },
            ),
            id='config_enabled_B_point_country_match',
        ),
        pytest.param(
            True,
            marks=pytest.mark.config(
                ROUTE_COUNTRY_BORDER_RESTRICTIONS={
                    'enabled': True,
                    'restricted_countries': ['rus', 'kaz'],
                },
            ),
            id='config_enabled_A_and_B_points_country_match',
        ),
    ],
)
def test_route_restrictions_config(
        local_services,
        mockserver,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        is_unavailable,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(request, 1)

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def mock_zones(request):
        pass

    request = load_json('request.json')

    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200
    service_levels = response.json()['service_levels']
    assert len(service_levels) == 1
    service_level = service_levels[0]

    if is_unavailable:
        assert 'tariff_unavailable' in service_level
        assert service_level['tariff_unavailable'] == {
            'code': 'closed_country_border',
            'message': 'Cant build route over country border',
        }
    else:
        assert 'tariff_unavailable' not in service_level


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('disable_zone_name_request')
@pytest.mark.config(DEFAULT_URGENCY=600)
def test_summary_without_zone_name(
        local_services,
        taxi_protocol,
        db,
        load_json,
        now,
        mockserver,
        pricing_data_preparer,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_trip_information(
        time=1421.5866954922676, distance=7514.629286628636,
    )
    pricing_data_preparer.set_cost(
        user_cost=317, driver_cost=317, category='econom',
    )
    pricing_data_preparer.set_user_category_prices_id(
        category='econom',
        category_prices_id='c/b7c4d5f6aa3b40a3807bb74b3bc042af',
        category_id='b7c4d5f6aa3b40a3807bb74b3bc042af',
    )

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offer = response.json()
    offer_id = response_without_offer.pop('offer')
    for service_level in expected_response['service_levels']:
        service_level['offer'] = offer_id
    assert response_without_offer == expected_response

    offer = utils.get_saved_offer(db)
    assert offer['_id'] == offer_id
    assert offer['authorized']
    assert offer['created'] == now.replace(microsecond=0)
    assert not offer['destination_is_airport']
    assert offer['distance'] == 7514.629286628636
    assert offer['due'] == (
        now.replace(microsecond=0) + datetime.timedelta(minutes=10)
    )
    assert not offer['is_fixed_price']
    del offer['prices'][0]['pricing_data']
    assert offer['prices'] == [
        {
            'cls': 'econom',
            'cat_type': 'application',
            'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
            'driver_price': 317.0,
            'price': 317.0,
            'sp': 1.0,
            'is_fixed_price': False,
            'using_new_pricing': True,
        },
    ]
    assert offer['classes_requirements'] == {}
    assert offer['route'] == [
        [37.647932797875484, 55.742884944005525],
        [37.58992385864258, 55.73382568359375],
    ]
    assert offer['time'] == 1421.5866954922676
    assert offer['user_id'] == 'b300bda7d41b4bae8d58dfa93221ef16'


@pytest.mark.user_experiments('disable_zone_name_request')
def test_no_route(taxi_protocol, pricing_data_preparer, load_json, mockserver):
    request = load_json('request.json')

    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 400


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.parametrize(
    'config_override,forced_surge_override',
    [
        pytest.param(
            {
                'SURGE_SURCHARGE_ENABLE': True,
                'SURGE_COLOR_BUTTON_MIN_VALUE_ZONE': {'__default__': 1.6},
                'SURGE_POPUP_MIN_COEFF_ZONE': {'__default__': 2.5},
            },
            {'color_button': True, 'show_popup': False, 'value': 2},
        ),
        pytest.param(
            {
                'SURGE_SURCHARGE_ENABLE': True,
                'SURGE_COLOR_BUTTON_MIN_VALUE_ZONE': {'__default__': 1.6},
                'SURGE_POPUP_MIN_COEFF_ZONE': {'__default__': 2.5},
            },
            {'color_button': False, 'show_popup': False, 'value': 2},
            marks=pytest.mark.experiments3(filename='experiments3.json'),
            id='disable_color_button_uber_exp',
        ),
    ],
)
def test_surge_overrides(
        local_services,
        taxi_protocol,
        db,
        load_json,
        config,
        mockserver,
        forced_surge_override,
        config_override,
        now,
        pricing_data_preparer,
):
    pricing_data_preparer.set_user_surge(
        2, alpha=0.7, beta=0.3, surcharge=1000.5,
    )

    def _surge(response):
        return response['service_levels'][0]['forced_surge']

    def _paid_options(response):
        return response['service_levels'][0]['paid_options']

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(
            request, 2, SurchargeParams(0.7, 0.3, 1000.5),
        )

    exp_response = load_json('expected_response.json')
    expected_forced_surge = _surge(exp_response)
    expected_paid_options = _paid_options(exp_response)

    if forced_surge_override is not None:
        expected_forced_surge.update(forced_surge_override)
        expected_paid_options.update(forced_surge_override)
        if 'show_popup' in expected_paid_options:
            expected_paid_options[
                'show_order_popup'
            ] = expected_paid_options.pop('show_popup')
        if not expected_paid_options['show_order_popup']:
            del expected_paid_options['order_popup_properties']

    if config_override is not None:
        config.set_values(config_override)

    taxi_protocol.tests_control(now=now, invalidate_caches=True)

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    # not checking whole response because for unknown reason
    # tariff description is flapping
    data = response.json()
    assert _surge(data) == expected_forced_surge
    assert _paid_options(data) == expected_paid_options

    offer = utils.get_saved_offer(db)
    assert offer is None


@pytest.mark.now('2017-05-25T11:30:00+0300')
def test_exact_order(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        mockserver,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    assert response.json() == expected_response

    offer = utils.get_saved_offer(db)
    assert offer is None


@pytest.mark.parametrize(
    'payment_type, method_id',
    [
        ('cash', None),
        ('corp', 'corp-default'),
        ('card', 'card-default'),
        ('applepay', 'card-default'),
        ('googlepay', 'card-default'),
        ('coop_account', 'coop-12324'),
        ('yandex_card', 'some_id'),
        ('cargocorp', 'cargocorp-123'),
        ('sbp', None),
    ],
)
@pytest.mark.parametrize('use_card_like', [True, False])
def test_payment_types(
        local_services,
        mockserver,
        db,
        load_json,
        taxi_protocol,
        pricing_data_preparer,
        payment_type,
        method_id,
        use_card_like,
        config,
):
    # This mock checks payment_method
    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        data = json.loads(request.get_data())
        received_payment_method = data['payment_method']
        if use_card_like:
            if received_payment_method in CARD_LIKE_PAYMENT_METHODS:
                assert received_payment_method == 'card'
            else:
                assert received_payment_method == payment_type
        else:
            assert received_payment_method == payment_type

        return utils.mock_driver_eta(load_json, 'driver_eta.json')(request)

    config.set_values(dict(USE_CARD_LIKE_NEARES_DRIVERS_REQUEST=use_card_like))

    request = load_json('request.json')
    request['payment'] = {'type': payment_type, 'payment_method_id': method_id}
    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(
    ALL_CATEGORIES=['econom'],
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {'econom': {'show_approximate_price': True}},
    },
)
@pytest.mark.translations(
    tariff={'tilda_key': {'en': '~'}, 'approx_key': {'en': 'approximately'}},
)
@pytest.mark.parametrize(
    'country,tanker_key,expected',
    [
        ('__default__', 'tilda_key', '~'),
        ('rus', 'no_key', '~'),
        ('rus', 'tilda_key', '~'),
        ('rus', 'approx_key', 'approximately'),
    ],
)
def test_price_approximation(
        local_services,
        taxi_protocol,
        config,
        load_json,
        now,
        country,
        tanker_key,
        expected,
        mockserver,
        pricing_data_preparer,
):
    pricing_data_preparer.set_fixed_price(enable=False)
    config.set_values(
        dict(
            TARIFF_CURRENCY_APPROXIMATION_BY_COUNTRY={
                country: {'tanker_key': tanker_key},
            },
        ),
    )
    taxi_protocol.tests_control(now=now, invalidate_caches=True)

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    data = response.json()

    for cls in data['service_levels']:
        value = cls['description_parts']['value']
        assert value[0] == expected[0]


@pytest.mark.parametrize(
    'show_original_price, use_coupon',
    [(True, True), (True, False), (False, False)],
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('discount_strike')
def test_original_price_with_free_route(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        now,
        config,
        discounts,
        show_original_price,
        use_coupon,
        blackbox_service,
        mockserver,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_strikeout(price=99, category='econom')
    pricing_data_preparer.set_cost(
        user_cost=0, driver_cost=99, category='econom',
    )

    pricing_data_preparer.set_discount(
        {'discount_offer_id': '123456', 'reason': 'for_all', 'methon': 'full'},
    )
    pricing_data_preparer.set_discount_meta(value=0.1, price=150.0)
    if use_coupon:
        pricing_data_preparer.set_coupon(
            valid=False,
            format_currency=False,
            description='Unauthorized',
            details=[],
            value=100,
        )

    config.set_values(
        dict(
            ROUTESTATS_ZONES_USING_ORIGINAL_PRICE_WITH_FREE_ROUTE=(
                ['moscow'] if show_original_price else []
            ),
        ),
    )

    request = load_json('request.json')

    if use_coupon:
        blackbox_service.set_token_info('test_token', uid='4003514353')
        request['requirements']['coupon'] = 'discount300'
    response = taxi_protocol.post(
        '3.0/routestats', request, bearer='test_token',
    )
    assert response.status_code == 200
    for level in response.json()['service_levels']:
        if show_original_price:
            assert 'original_price' in level
            assert (
                level['original_price']
                == '99\xa0$SIGN$$CURRENCY$ for the first 5 min and 2 km'
            )
        else:
            assert 'original_price' not in level


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('child_tariff')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.config(
    FETCH_CANDIDATES_FROM_TRACKER=True,
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
    ALL_CATEGORIES=[
        'econom',
        'comfortplus',
        'vip',
        'minivan',
        'pool',
        'child_tariff',
    ],
)
def test_umlaas_candidates(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        mockserver,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(
            request, 2, SurchargeParams(0.7, 0.3, 1000.5),
        )

    @mockserver.json_handler('/umlaas/eta/v1')
    def mock_eta_umlaas(request):
        data = json.loads(request.get_data())
        candidates = data['candidates']
        assert len(candidates) > 0
        return load_json('eta_umlaas.json')

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    assert mock_eta_umlaas.has_calls


def sane_compare(name, a, b, a_name=None, b_name=None, ignore_space_type=True):
    def normalize(val):
        if type(val) is str:
            if ignore_space_type:
                # treat different types of spaces as one
                return val.replace('\xa0', ' ')
        return val

    a = normalize(a)
    b = normalize(b)

    if a == b:
        return []

    t_a = type(a)
    t_b = type(b)

    a_name = a_name or 'a'
    b_name = b_name or 'b'

    if t_a is not t_b:
        return [
            '%s type differs: %s: %s, %s: %s'
            % (name, a_name, t_a, b_name, t_b),
        ]

    t = t_a

    if t is dict:
        diffs = []
        for k in set(a.keys()).union(b.keys()):
            nested_name = '%s["%s"]' % (name, k)
            if k not in a:
                diffs.append(
                    '%s is in %s, but not in %s'
                    % (nested_name, b_name, a_name),
                )
                continue
            if k not in b:
                diffs.append(
                    '%s is in %s, but not in %s'
                    % (nested_name, a_name, b_name),
                )
                continue
            diffs.extend(
                sane_compare(
                    nested_name,
                    a[k],
                    b[k],
                    a_name,
                    b_name,
                    ignore_space_type=ignore_space_type,
                ),
            )
        return diffs

    if t is list:
        if len(a) != len(b):
            return [
                'list len mismatch - %s: %i, %s: %i'
                % (a_name, len(a), b_name, len(b)),
            ]

        diffs = []
        for i in range(len(a)):
            diffs.extend(
                sane_compare(
                    '%s[%i]' % (name, i),
                    a[i],
                    b[i],
                    a_name,
                    b_name,
                    ignore_space_type=ignore_space_type,
                ),
            )

        return diffs

    return ['%s: %s: %s, %s: %s' % (name, a_name, a, b_name, b)]


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.parametrize(
    'offer_extra_data, offer_prices,' 'surge, fallback',
    [
        (
            {
                'decoupling': {
                    'success': True,
                    'user': {
                        'tariff': (
                            '585a6f47201dd1b2017a0eab-'
                            '507000939f17427e951df9791573ac7e-'
                            '7fc5b2d1115d4341b7be206875c40e11'
                        ),
                        'prices': [
                            {
                                'cls': 'econom',
                                'cat_type': 'application',
                                'category_id': (
                                    '5f40b7f324414f51a1f9549c65211ea5'
                                ),
                                'price': 633.0,
                                'sp': 1.0,
                                'is_fixed_price': False,
                                'using_new_pricing': True,
                            },
                        ],
                    },
                    'driver': {
                        'tariff': '585a6f47201dd1b2017a0eab',
                        'prices': [
                            {
                                'cls': 'econom',
                                'cat_type': 'application',
                                'category_id': (
                                    'b7c4d5f6aa3b40a3807bb74b3bc042af'
                                ),
                                'price': 1582.0,
                                'sp': 5.0,
                                'is_fixed_price': False,
                                'using_new_pricing': True,
                            },
                        ],
                    },
                },
            },
            [
                {
                    'cls': 'econom',
                    'cat_type': 'application',
                    'category_id': '5f40b7f324414f51a1f9549c65211ea5',
                    'price': 633.0,
                    'driver_price': 633.0,
                    'sp': 1.0,
                    'is_fixed_price': False,
                    'using_new_pricing': True,
                },
            ],
            5.0,
            False,
        ),
        (
            {
                'decoupling': {
                    'success': False,
                    'error': {
                        'reason': 'plugin_internal_error',
                        'stage': 'calculating_offer',
                    },
                },
            },
            [
                {
                    'cls': 'econom',
                    'cat_type': 'application',
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                    'price': 317.0,
                    'driver_price': 317.0,
                    'sp': 1.0,
                    'is_fixed_price': False,
                    'using_new_pricing': True,
                },
            ],
            1.0,
            True,
        ),
    ],
    ids=['decoupled', 'decoupling_failed'],
)
@pytest.mark.config(DEFAULT_URGENCY=600)
@pytest.mark.experiments3(filename='decoupling/experiments3_01.json')
def test_decoupling(
        local_services,
        taxi_protocol,
        db,
        load_json,
        mockserver,
        now,
        offer_extra_data,
        surge,
        offer_prices,
        fallback,
        pricing_data_preparer,
):
    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_trip_information(
        time=1421.5866954922676, distance=7514.629286628636,
    )

    if fallback:
        pricing_data_preparer.set_cost(user_cost=317, driver_cost=317)
    else:
        pricing_data_preparer.set_cost(user_cost=633, driver_cost=1582)

    pricing_data_preparer.set_user_surge(1.0)
    pricing_data_preparer.set_driver_surge(surge)

    if fallback:
        pricing_data_preparer.set_corp_decoupling(enable=True)
    else:
        pricing_data_preparer.set_decoupling(enable=True)

    if fallback:
        pricing_data_preparer.set_tariff_info(
            price_per_minute=9,
            price_per_kilometer=9,
            included_minutes=5,
            included_kilometers=2,
        )
    else:
        pricing_data_preparer.set_meta('min_price', 198)
        pricing_data_preparer.set_tariff_info(
            price_per_minute=18,
            price_per_kilometer=18,
            included_minutes=5,
            included_kilometers=2,
        )

    pricing_data_preparer.set_user_category_prices_id(
        category_prices_id='d/585a6f47201dd1b2017a0eab-'
        '507000939f17427e951df9791573ac7e-'
        '7fc5b2d1115d4341b7be206875c40e11/'
        + (
            'b7c4d5f6aa3b40a3807bb74b3bc042af'
            if fallback
            else '5f40b7f324414f51a1f9549c65211ea5'
        ),
        category_id=(
            'b7c4d5f6aa3b40a3807bb74b3bc042af'
            if fallback
            else '5f40b7f324414f51a1f9549c65211ea5'
        ),
        tariff_id='585a6f47201dd1b2017a0eab-'
        '507000939f17427e951df9791573ac7e-'
        '7fc5b2d1115d4341b7be206875c40e11',
    )

    pricing_data_preparer.set_driver_category_prices_id(
        category_prices_id='c/b7c4d5f6aa3b40a3807bb74b3bc042af',
        category_id='b7c4d5f6aa3b40a3807bb74b3bc042af',
    )

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(request, surge)

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    if fallback:
        expected_response = load_json('expected_response.json')
    else:
        expected_response = load_json('expected_response_decoupled.json')
    response_without_offer = response.json()
    offer_id = response_without_offer.pop('offer')
    for service_level in expected_response['service_levels']:
        service_level['offer'] = offer_id
    response_without_offer.pop('typed_experiments')
    expected_response.pop('typed_experiments')
    assert response_without_offer == expected_response

    offer = utils.get_saved_offer(db)
    assert offer['_id'] == offer_id
    assert offer['authorized']
    assert offer['created'] == now.replace(microsecond=0)
    assert not offer['destination_is_airport']
    assert offer['distance'] == 7514.629286628636
    assert offer['due'] == (
        now.replace(microsecond=0) + datetime.timedelta(minutes=10)
    )
    assert not offer['is_fixed_price']

    for p in offer['prices']:
        del p['pricing_data']

    assert offer['prices'] == offer_prices
    assert offer['classes_requirements'] == {}
    assert offer['route'] == [
        [37.647932797875484, 55.742884944005525],
        [37.58992385864258, 55.73382568359375],
    ]
    assert offer['time'] == 1421.5866954922676
    assert offer['user_id'] == 'b300bda7d41b4bae8d58dfa93221ef16'
    assert offer['extra_data'] == offer_extra_data


@pytest.mark.config(
    ENABLE_TARIFF_COURIER_POINT_A_ETA_SUBSTITUTION=True,
    TARIFF_COURIER_POINT_A_ETA_SUBSTITUTION_STUB_PARAMETERS={
        'use_stub_values': False,
        'eta_seconds': 300,
    },
    ALL_CATEGORIES=['econom', 'courier'],
    APPLICATION_BRAND_CATEGORIES_SETS={'__default__': ['econom', 'courier']},
)
@pytest.mark.parametrize(
    'cargo_misc_response',
    [
        {
            'candidate': {
                'uuid': 'some_uuid',
                'dbid': 'some_dbid',
                'id': 'some_id',
                'position': [55, 35],
                'status': {},
                'route_info': {'time': 300},
            },
        },
        {},
    ],
)
@pytest.mark.experiments3(filename='exp3.json')
def test_tariff_courier_eta(
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        mockserver,
        local_services,
        cargo_misc_response,
):
    @mockserver.json_handler('/cargo_misc/couriers/v1/courier-for-order')
    def mock_cargo_misc(request):
        return cargo_misc_response

    request = load_json('request.json')
    resp = taxi_protocol.post('3.0/routestats', request)
    assert resp.status_code == 200
    assert mock_cargo_misc.times_called == 1


@pytest.mark.config(
    ENABLE_TARIFF_COURIER_POINT_A_ETA_SUBSTITUTION=False,
    TARIFF_COURIER_POINT_A_ETA_SUBSTITUTION_STUB_PARAMETERS={
        'use_stub_values': True,
        'eta_seconds': 300,
    },
    ALL_CATEGORIES=['econom', 'courier'],
    APPLICATION_BRAND_CATEGORIES_SETS={'__default__': ['econom', 'courier']},
)
@pytest.mark.experiments3(filename='test_tariff_courier_eta/exp3.json')
def test_tariff_courier_eta_disable(
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        mockserver,
        local_services,
):
    @mockserver.json_handler('/cargo_misc/couriers/v1/courier-for-order')
    def mock_cargo_misc(request):
        assert False  # could not call

    request = load_json('test_tariff_courier_eta/request.json')
    resp = taxi_protocol.post('3.0/routestats', request)
    assert resp.status_code == 200
    assert mock_cargo_misc.times_called == 0


@pytest.mark.config(
    ENABLE_TARIFF_COURIER_POINT_A_ETA_SUBSTITUTION=True,
    TARIFF_COURIER_POINT_A_ETA_SUBSTITUTION_STUB_PARAMETERS={
        'use_stub_values': True,
        'eta_seconds': 300,
    },
    ALL_CATEGORIES=['econom', 'courier'],
    APPLICATION_BRAND_CATEGORIES_SETS={'__default__': ['econom', 'courier']},
)
@pytest.mark.experiments3(filename='test_tariff_courier_eta/exp3.json')
def test_tariff_courier_eta_fallback(
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        mockserver,
        local_services,
):
    @mockserver.json_handler('/cargo_misc/couriers/v1/courier-for-order')
    def mock_cargo_misc(request):
        assert False  # could not call

    request = load_json('test_tariff_courier_eta/request.json')
    resp = taxi_protocol.post('3.0/routestats', request)
    assert resp.status_code == 200
    assert mock_cargo_misc.times_called == 0


@pytest.mark.config(USE_TARIFFS_TO_FILTER_SUPPLY=True)
def test_virtual_tariffs(
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        mockserver,
        local_services_base,
):
    @mockserver.json_handler('/virtual_tariffs/v1/match')
    def mock_virtual_tariffs_view(request):
        return {
            'virtual_tariffs': [
                {
                    'class': 'comfort',
                    'special_requirements': [{'id': 'food_delivery'}],
                },
                {
                    'class': 'econom',
                    'special_requirements': [{'id': 'food_delivery'}],
                },
            ],
        }

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        return utils.mock_driver_eta(load_json, 'driver_eta.json')(request)

    request = load_json('request.json')
    resp = taxi_protocol.post('3.0/routestats', request)
    assert resp.status_code == 200

    assert mock_virtual_tariffs_view.times_called == 1
    assert mock_driver_eta.times_called == 1


@pytest.mark.config(
    CARGO_CLAIMS_CORP_CLIENTS_WITH_LOGISTIC_CONTRACTS={'__default__': True},
    CORP_BILLING_PAYMENT_KINDS_BY_CATEGORIES={
        'logistic_econom': {
            'client': 'client_payment',
            'partner': 'partner_payment',
        },
    },
)
def test_logistic_contract(
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        mockserver,
        local_services_base,
):
    @mockserver.json_handler('/billing_replication/v1/active-contracts/')
    def mock_v1_active_contracts(request):
        assert request.args['client_id'] == 'billing_client_id'
        return [{'ID': 123}]

    @mockserver.json_handler('/corp_integration_api/v1/client/')
    def mock_v1_client(request):
        client_id = request.args['client_id']
        assert client_id == 'decoupled-client'
        return {
            'client_id': client_id,
            'contract_id': '123',
            'billing_contract_id': '321',
            'name': 'name',
            'billing_client_id': 'billing_client_id',
            'services': {},
            'country': 'ru',
        }

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        assert json.loads(request.get_data())['order']['request'][
            'check_new_logistic_contract'
        ]
        return utils.mock_driver_eta(load_json, 'driver_eta.json')(request)

    request = load_json('request.json')
    resp = taxi_protocol.post('3.0/routestats', request)
    assert resp.status_code == 200
    assert mock_driver_eta.times_called == 1
    assert mock_v1_client.times_called == 1
    assert mock_v1_active_contracts.times_called == 1


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.filldb(
    requirements='with_multiplier', tariffs='with_multiplier_req',
)
@pytest.mark.config(ROUTER_MAPS_ENABLED=True)
@pytest.mark.user_experiments('fixed_price')
@pytest.mark.experiments3(filename='decoupling/experiments3_01.json')
def test_decoupling_requirements_multiplier(
        local_services_fixed_price,
        taxi_protocol,
        db,
        load_json,
        mockserver,
        now,
        pricing_data_preparer,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_trip_information(
        time=1421.5866954922676, distance=7514.629286628636,
    )

    pricing_data_preparer.set_cost(
        user_cost=1070, driver_cost=535, category='econom',
    )

    pricing_data_preparer.set_decoupling(enable=True)

    pricing_data_preparer.set_user_category_prices_id(
        category_prices_id='d/585a6f47201dd1b2017a0eab-'
        '507000939f17427e951df9791573ac7e-'
        '7fc5b2d1115d4341b7be206875c40e11/'
        '5f40b7f324414f51a1f9549c65211ea5',
        category_id='5f40b7f324414f51a1f9549c65211ea5',
        tariff_id='585a6f47201dd1b2017a0eab-'
        '507000939f17427e951df9791573ac7e-'
        '7fc5b2d1115d4341b7be206875c40e11',
    )

    pricing_data_preparer.set_driver_category_prices_id(
        category_prices_id='c/b7c4d5f6aa3b40a3807bb74b3bc042af',
        category_id='b7c4d5f6aa3b40a3807bb74b3bc042af',
    )

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(request, 1.0)

    headers = {
        'User-Agent': (
            'ru.yandex.taxi.inhouse/4.99.8769 '
            '(iPhone; iPhone7,2; iOS 11.0; Darwin)'
        ),
    }

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request, headers=headers)

    assert response.status_code == 200
    data = response.json()
    offer_id = data['offer']
    offer = utils.get_offer(offer_id, db)
    assert 'price_modifiers' in offer
    price_modifiers = offer['price_modifiers']
    assert len(price_modifiers) == 1
    assert price_modifiers['items'][0]['reason'] == 'requirements'
    assert price_modifiers['items'][0]['pay_subventions'] is False
    assert price_modifiers['items'][0]['tariff_categories'] == ['econom']
    assert price_modifiers['items'][0]['type'] == 'multiplier'
    assert price_modifiers['items'][0]['value'] == '1.690000'
    decoupling = offer['extra_data']['decoupling']
    # base 317 * 1.69 by cargo requirement
    assert decoupling['driver']['prices'][0]['price'] == 535
    # base 317 * 2 by corp tariff * 1.69 by cargo requirement
    assert offer['prices'][0]['price'] == 1070
    assert decoupling['user']['prices'][0]['price'] == 1070


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(USE_REQUIREMENT_INTERVALS=True)
@pytest.mark.config(HOURLY_RENTAL_ENABLED=True)
@pytest.mark.experiments3(filename='decoupling/experiments3_01.json')
@pytest.mark.experiments3(filename='exp3_hourly_rental.json')
def test_decoupling_hourly_rental_requirement(
        local_services_base,
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        mockserver,
        db,
):
    pricing_data_preparer.set_cost(
        user_cost=4000, driver_cost=4000, category='business',
    )

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    data = response.json()
    category = data['service_levels'][0]
    assert category['class'] == 'business'
    assert category['price'] == '4,000\xa0$SIGN$$CURRENCY$'
    assert 'offer' not in data  # only free route is allowed


@pytest.mark.config(
    ALTPIN_MONEY_ZONES={
        '__default__': {
            'price_gain_absolute': 10,
            'price_gain_absolute_minorder': 0,
            'price_gain_ratio': 0,
            'route_gain_ratio': 0,
            'time_gain_ratio': 0,
        },
    },
    ALTPIN_PRICE_GAIN_RATIO_DEGRADATION=-0.03,
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('fixed_price', 'alternatives_from_ppaas')
@pytest.mark.parametrize(
    'payment, altpins_disabled_by_decoupling',
    [('corp-decoupled-client', True), ('corp-nondecoupled-client', False)],
)
@pytest.mark.experiments3(filename='decoupling/experiments3_01.json')
@pytest.mark.experiments3(filename='exp3_alt_point_switcher.json')
def test_decoupling_disable_altpin(
        local_services_fixed_price,
        taxi_protocol,
        db,
        load_json,
        mockserver,
        now,
        payment,
        altpins_disabled_by_decoupling,
        pricing_data_preparer,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_decoupling(enable=True)

    pricing_data_preparer.set_user_category_prices_id(
        category_prices_id='d/585a6f47201dd1b2017a0eab-'
        '507000939f17427e951df9791573ac7e-'
        '7fc5b2d1115d4341b7be206875c40e11/'
        '5f40b7f324414f51a1f9549c65211ea5',
        category_id='5f40b7f324414f51a1f9549c65211ea5',
        tariff_id='585a6f47201dd1b2017a0eab-'
        '507000939f17427e951df9791573ac7e-'
        '7fc5b2d1115d4341b7be206875c40e11',
    )

    pricing_data_preparer.set_driver_category_prices_id(
        category_prices_id='c/b7c4d5f6aa3b40a3807bb74b3bc042af',
        category_id='b7c4d5f6aa3b40a3807bb74b3bc042af',
    )

    pricing_data_preparer.set_trip_information(time=1380, distance=6300)
    pricing_data_preparer.set_cost(
        user_cost=99, driver_cost=535, category='econom',
    )
    pricing_data_preparer.push()
    pricing_data_preparer.set_trip_information(time=780, distance=800)
    pricing_data_preparer.set_cost(
        user_cost=209, driver_cost=535, category='econom',
    )

    request = load_json('decoupling/request.json')
    request['payment']['payment_method_id'] = payment
    expected_response = load_json('expected_response_with_altpins.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offer = response.json()
    offer_id = response_without_offer.pop('offer')
    for service_level in expected_response['service_levels']:
        service_level['offer'] = offer_id
    if altpins_disabled_by_decoupling:
        assert 'alternatives' not in response_without_offer
    else:
        options = response_without_offer['alternatives']['options']
        alt_offer_id = options[0].pop('offer')
        for option in expected_response['alternatives']['options']:
            for service_level in option['service_levels']:
                service_level['offer'] = alt_offer_id
        assert response_without_offer == expected_response


@pytest.mark.parametrize('disable_fixed_price', [True, False])
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('fixed_price')
@pytest.mark.experiments3(filename='decoupling/experiments3_01.json')
def test_decoupling_disable_fixed_price(
        local_services,
        taxi_protocol,
        db,
        load_json,
        mockserver,
        now,
        disable_fixed_price,
        pricing_data_preparer,
):
    pricing_data_preparer.set_fixed_price(enable=not disable_fixed_price)
    pricing_data_preparer.set_decoupling(enable=True)

    pricing_data_preparer.set_user_category_prices_id(
        category_prices_id='d/585a6f47201dd1b2017a0eab-'
        '507000939f17427e951df9791573ac7e-'
        '7fc5b2d1115d4341b7be206875c40e11/'
        '5f40b7f324414f51a1f9549c65211ea5',
        category_id='5f40b7f324414f51a1f9549c65211ea5',
        tariff_id='585a6f47201dd1b2017a0eab-'
        '507000939f17427e951df9791573ac7e-'
        '7fc5b2d1115d4341b7be206875c40e11',
    )

    pricing_data_preparer.set_driver_category_prices_id(
        category_prices_id='c/b7c4d5f6aa3b40a3807bb74b3bc042af',
        category_id='b7c4d5f6aa3b40a3807bb74b3bc042af',
    )

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(request, 1)

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offer = response.json()
    offer_id = response_without_offer.pop('offer')

    offer = utils.get_saved_offer(db)
    assert offer['_id'] == offer_id
    assert not disable_fixed_price == offer['is_fixed_price']
    price_types = (
        offer['prices'],
        offer['extra_data']['decoupling']['user']['prices'],
        offer['extra_data']['decoupling']['driver']['prices'],
    )
    for price_type in price_types:
        for price in price_type:
            assert not disable_fixed_price == price['is_fixed_price']

    for service_level in response_without_offer['service_levels']:
        assert not disable_fixed_price == service_level.get(
            'is_fixed_price', False,
        )


def custom_fixed_price_modifier(mockserver, user_experiments, **kwargs):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        _data = json.loads(request.get_data())
        assert set(_data['fixed_price_classes']) >= set(_data['classes'])
        return utils.get_surge_calculator_response(request, 1)

    user_experiments.set_value(['multiclass', 'child_tariff', 'fixed_price'])


def fully_custom_invalid_config(config, **kwargs):
    config.set_values(
        dict(
            MULTICLASS_TARIFFS_BY_ZONE={
                '__default__': ['unknown1', 'unknown2'],
            },
        ),
    )


def custom_invalid_config_one_valid(config, **kwargs):
    config.set_values(
        dict(
            MULTICLASS_TARIFFS_BY_ZONE={'__default__': ['econom', 'unknown2']},
        ),
    )


def custom_decoupling(mockserver, experiments3, load_json, **kwargs):
    experiments3.add_experiments_json(
        load_json('decoupling/experiments3_01.json'),
    )


def custom_tariff_hidden(config, **kwargs):
    config.set_values(
        dict(
            TARIFF_CATEGORIES_VISIBILITY={
                '__default__': {'econom': {'visible_by_default': False}},
            },
        ),
    )


def custom_complements(
        mockserver,
        experiments3,
        load_json,
        config,
        user_experiments,
        **kwargs,
):
    custom_fixed_price_modifier(
        mockserver=mockserver, user_experiments=user_experiments,
    )
    experiments3.add_experiments_json(
        load_json('valid_with_complements/experiments3.json'),
    )
    config.set_values(
        dict(
            PERSONAL_WALLET_ENABLED=True,
            PLUS_WALLET_PROTOCOL_BALANCES_ENABLED=True,
            CURRENCY_ROUNDING_RULES={'__default__': {'__default__': 10}},
            CURRENCY_FORMATTING_RULES={'__default__': {'__default__': 2}},
            COMPLEMENT_TYPES_COMPATIBILITY_MAPPING={
                'personal_wallet': ['card', 'applepay', 'googlepay'],
            },
        ),
    )

    @mockserver.json_handler('/plus_wallet/v1/balances')
    def mock_balances(request):
        return load_json('test_multiclass/valid_with_complements/balance.json')


@pytest.mark.config(
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
    ALL_CATEGORIES=DEFAULT_ALL_CATEGORIES,
    APPLICATION_BRAND_CATEGORIES_SETS={'__default__': DEFAULT_ALL_CATEGORIES},
    MULTICLASS_ENABLED=True,
    MULTICLASS_TARIFFS_BY_ZONE={'__default__': ['econom', 'comfortplus']},
    MULTICLASS_SELECTOR_ICON='',
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('child_tariff', 'multiclass')
@pytest.mark.translations(
    client_messages={
        'routestats.tariff_unavailable.multiclass_invalid': {
            'ru': 'Multiclass invalid selection',
        },
        'routestats.tariff_unavailable.multiclass_unavailable': {
            'ru': 'Multiclass unavailable',
        },
        'routestats.tariff_unavailable.unsupported_payment_method': {
            'ru': 'Payment method is not supported',
        },
        'multiclass.min_selected_count.text': {
            'ru': 'Выберите %(min_count)s и более классов',
        },
        'multiclass.popup.text': {'ru': 'Кто быстрей'},
    },
    tariff={
        'routestats.multiclass.name': {'ru': 'Fast'},
        'routestats.multiclass.details.fixed_price': {'ru': 'below %(price)s'},
        'routestats.multiclass.details.not_fixed_price': {
            'ru': 'more than %(price)s',
        },
        'routestats.multiclass.details.description': {
            'ru': 'description of multiclass',
        },
        'routestats.multiclass.search_screen.title': {'ru': 'Searching'},
        'routestats.multiclass.search_screen.subtitle': {'ru': 'fastest car'},
        'routestats.multiclass.details.order_button.text': {
            'ru': 'choose tariffs',
        },
    },
)
@pytest.mark.parametrize(
    # hard (and not obvious) to modify requests/response in code,
    # so they are fully presented in `static/test_routestats/test_multiclass`
    'data_directory, custom_modifier',
    [
        # checking if device don't sending multiclass_support
        ('no_multiclass_support', None),
        # checking request with requirements - all fields must be filled,
        # but tariff is unavailable because of requirements
        ('requirements', None),
        # checking request with all tariffs unavailable -
        # price can be filled, but no eta
        # tariff is unavailable because of requirements
        ('unavailable', None),
        # checking no selected valid answer
        ('valid_no_selected', None),
        # checking valid with selected classes
        ('valid_with_selected', None),
        # checking the same valid with selected classes,
        # but sending empty specific requirements
        ('valid_with_selected_2', None),
        # checking the same valid with selected classes,
        # but sending capacity and coupon requirements, which must be ignored
        ('valid_with_selected_3', None),
        # checking availability with complement payment
        ('valid_with_complements', custom_complements),
        # checking invalid, where selected only one class
        # (this case is not multiclass)
        ('invalid_selected_only_one', None),
        # checking invalid case with all unknown classes -
        # the answer will be valid with no selected classes, but with classes
        # from current zone
        ('invalid_selected_unknown_classes_only', None),
        # checking valid fixed price case
        ('valid_with_fixed_price', custom_fixed_price_modifier),
        # checking valid fixed price case
        ('valid_with_fixed_price_below', custom_fixed_price_modifier),
        # checking invalid multiclass response,
        # than less than 1 class is available
        ('invalid_config', fully_custom_invalid_config),
        ('invalid_config', custom_invalid_config_one_valid),
        # checking decoupling ignoring
        ('decoupling', custom_decoupling),
        # sending specific requirement,
        # which answers with only one service level
        ('specific_requirement', None),
        # hidden tariff answers with only one service level
        ('hidden_tariff', custom_tariff_hidden),
    ],
)
def test_multiclass(
        local_services_base,
        mockserver,
        taxi_protocol,
        db,
        load_json,
        data_directory,
        custom_modifier,
        user_experiments,
        config,
        experiments3,
        pricing_data_preparer,
):
    if custom_modifier == custom_decoupling:
        pricing_data_preparer.set_meta('min_price', 198, category='econom')
        pricing_data_preparer.set_tariff_info(
            price_per_minute=18,
            price_per_kilometer=18,
            included_minutes=5,
            included_kilometers=2,
            category='econom',
        )

        pricing_data_preparer.set_trip_information(time=1440, distance=7600)
        pricing_data_preparer.set_cost(
            category='econom', user_cost=633, driver_cost=633,
        )
        pricing_data_preparer.set_active(category='child_tariff', active=False)
        pricing_data_preparer.set_active(category='comfortplus', active=False)
        pricing_data_preparer.set_active(category='vip', active=False)
        pricing_data_preparer.set_active(category='minivan', active=False)
    else:
        _set_default_tariff_info_and_prices(pricing_data_preparer)

        pricing_data_preparer.set_trip_information(time=1440, distance=7600)
        pricing_data_preparer.set_cost(
            category='econom', user_cost=317, driver_cost=317,
        )
        pricing_data_preparer.set_cost(
            category='child_tariff', user_cost=432, driver_cost=432,
        )
        pricing_data_preparer.set_cost(
            category='comfortplus', user_cost=539, driver_cost=539,
        )
        pricing_data_preparer.set_cost(
            category='vip', user_cost=770, driver_cost=770,
        )
        pricing_data_preparer.set_cost(
            category='minivan', user_cost=513, driver_cost=513,
        )

    if custom_modifier in (custom_fixed_price_modifier, custom_complements):
        pricing_data_preparer.set_fixed_price(enable=True)
    else:
        pricing_data_preparer.set_fixed_price(enable=False)

    if custom_modifier == custom_complements:
        pricing_data_preparer.set_meta('display_price', 17, category='econom')
        pricing_data_preparer.set_meta(
            'display_price', 132, category='comfortplus',
        )
        pricing_data_preparer.set_meta(
            'display_min_price', 0, category='econom',
        )
        pricing_data_preparer.set_meta(
            'display_min_price', 0, category='comfortplus',
        )

    pricing_data_preparer.set_coupon(
        value=100,
        price_before_coupon=None,
        valid=False,
        description='Unauthorized',
    )

    @mockserver.json_handler('/driver-eta/eta')
    def mock(request):
        return utils.mock_driver_eta(
            load_json, data_directory + '/driver_eta.json',
        )(request)

    if custom_modifier:
        custom_modifier(
            mockserver=mockserver,
            user_experiments=user_experiments,
            config=config,
            experiments3=experiments3,
            load_json=load_json,
        )

    request = load_json(data_directory + '/request.json')
    expected_response = load_json(data_directory + '/expected_response.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offer = response.json()
    main_offer_id = None
    if 'offer' in response_without_offer:
        main_offer_id = response_without_offer['offer']
        for service_level in expected_response['service_levels']:
            service_level['offer'] = main_offer_id
    response_without_offer.pop('offer')
    for ignored_field in ['typed_experiments']:
        response_without_offer.pop(ignored_field)
        expected_response.pop(ignored_field)
    if 'alternatives' in response_without_offer:
        assert 'options' in response_without_offer['alternatives']
        options = response_without_offer['alternatives']['options']
        for option in options:
            assert 'offer' in option
            assert 'type' in option
            if option['type'] == 'multiclass':
                assert option['offer'] == main_offer_id
            for service_level in option['service_levels']:
                assert 'offer' in service_level
                assert service_level['offer'] == main_offer_id
                service_level.pop('offer')
            option.pop('offer')
    assert response_without_offer == expected_response


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(
    ROUTESTATS_POPUP_BY_TARIFF={
        'econom': {
            'description': 'routestats.description',
            'reason': 'routestats.reason',
            'button_text': 'routestats.button_text',
            'title': 'routestats.title',
            'comment': 'routestats.comment',
            'button_color': 'D4D0CE',
            'display_card_icon': False,
        },
    },
)
@pytest.mark.translations(
    tariff={
        'routestats.description': {'ru': 'translated description'},
        'routestats.reason': {'ru': 'translated reason'},
        'routestats.button_text': {'ru': 'translated button_text'},
        'routestats.title': {'ru': 'translated title'},
        'routestats.comment': {'ru': 'translated comment'},
    },
)
def test_tariff_popup(
        local_services,
        local_services_base,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        mockserver,
):
    personal_driver_popup = {
        'type': 'default',
        'description': 'translated description',
        'reason': 'translated reason',
        'button_text': 'translated button_text',
        'title': 'translated title',
        'comment': 'translated comment',
        'button_color': 'D4D0CE',
    }

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    data = response.json()

    for service_level in data['service_levels']:
        if service_level['class'] == 'econom':
            paid_options = service_level['paid_options']
            assert paid_options['show_order_popup']
            assert not paid_options['display_card_icon']
            assert (
                paid_options['order_popup_properties'] == personal_driver_popup
            )
        else:
            show_order_popup = service_level['paid_options'][
                'show_order_popup'
            ]
            if 'paid_options' in service_level and show_order_popup:
                order_popup_properties = service_level['paid_options'][
                    'order_popup_properties'
                ]
                assert order_popup_properties != personal_driver_popup


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.filldb(tariff_settings='max_eta')
@pytest.mark.config(
    TARIFF_KEY_OVERRIDE={
        '__default__': [
            {
                'from': 'routestats.tariff_unavailable.eta_too_big',
                'to': (
                    'routestats.some_big_event.tariff_unavailable.'
                    'eta_too_big'
                ),
            },
        ],
        'econom': [
            {
                'from': 'routestats.tariff_unavailable.no_free_cars_nearby',
                'to': (
                    'routestats.personal_driver.tariff_unavailable.'
                    'no_free_cars_nearby'
                ),
            },
        ],
    },
)
@pytest.mark.translations(
    client_messages={
        'routestats.personal_driver.tariff_unavailable.no_free_cars_nearby': {
            'en': 'No available drivers',
        },
        'routestats.some_big_event.tariff_unavailable.eta_too_big': {
            'en': 'ETA too big (Some Big Event)',
        },
        'routestats.tariff_unavailable.eta_too_big': {
            'en': 'You won\'t see this message',
        },
        'routestats.tariff_unavailable.no_free_cars_nearby': {
            'en': 'No available cars',
        },
    },
)
@pytest.mark.parametrize('reason', ['eta_too_big', 'no_free_cars_nearby'])
@pytest.mark.parametrize('tariff', ['econom', 'comfortplus'])
def test_keys_override(
        local_services_base,
        mockserver,
        taxi_protocol,
        load_json,
        reason,
        tariff,
        pricing_data_preparer,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_trip_information(time=600, distance=3800)
    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_cost(
        user_cost=152, driver_cost=152, category='econom',
    )
    pricing_data_preparer.set_cost(
        user_cost=301, driver_cost=301, category='comfortplus',
    )

    @mockserver.json_handler('/driver-eta/eta')
    def mock(request):
        return utils.mock_driver_eta(load_json, path_ + 'driver_eta.json')(
            request,
        )

    path_ = '{}/{}/'.format(tariff, reason)

    request = load_json(path_ + 'request.json')
    expected_response = load_json(path_ + 'expected_response.json')

    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offer = response.json()
    offer_id = response_without_offer.pop('offer')
    for service_level in expected_response['service_levels']:
        service_level['offer'] = offer_id
    assert response_without_offer == expected_response


@pytest.mark.config(
    TARIFF_KEY_OVERRIDE={
        '__default__': [
            {
                'from': 'routestats.tariff_unavailable.tariff_is_inactive',
                'to': 'some_missing_key',
            },
        ],
    },
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
def test_tariff_unavailable_localization(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        mockserver,
):
    # delete the original translation
    db.localization_client_messages.delete_one(
        {'_id': 'routestats.tariff_unavailable.tariff_is_inactive'},
    )
    # Make econom tariff category not active (delete from categories)
    db.tariffs.update({}, {'$pull': {'categories': {'name': 'econom'}}})

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    data = response.json()
    for service_level in data['service_levels']:
        assert service_level['class'] != 'econom'


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(USE_REQUIREMENT_INTERVALS=True)
@pytest.mark.config(HOURLY_RENTAL_ENABLED=True)
@pytest.mark.experiments3(filename='exp3_hourly_rental.json')
def test_hourly_rental_requirement(
        local_services_base,
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        mockserver,
        db,
):
    pricing_data_preparer.set_cost(
        user_cost=2000, driver_cost=2000, category='business',
    )

    unavailable_classes = ['econom', 'comfortplus', 'vip', 'minivan']

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    data = response.json()
    categories = data['service_levels']
    for category in categories:
        if category['class'] in unavailable_classes:
            assert (
                category['tariff_unavailable']['code']
                == 'unsupported_requirement'
            )
        else:
            assert category['class'] == 'business'
            assert category['price'] == '2,000\xa0$SIGN$$CURRENCY$'


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.filldb(tariff_settings='fixed_price_mixed')
@pytest.mark.user_experiments('fixed_price')
@pytest.mark.config(
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
    ALL_CATEGORIES=['econom', 'comfortplus'],
    DEFAULT_URGENCY=600,
)
def test_tariff_fixed_price_mixed(
        local_services,
        mockserver,
        taxi_protocol,
        db,
        load_json,
        now,
        pricing_data_preparer,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    pricing_data_preparer.set_trip_information(
        time=1421.5866954922676, distance=7514.629286628636,
    )
    pricing_data_preparer.set_fixed_price(enable=True, category='comfortplus')
    pricing_data_preparer.set_fixed_price(enable=False, category='econom')
    pricing_data_preparer.set_cost(
        user_cost=317, driver_cost=317, category='econom',
    )
    pricing_data_preparer.set_cost(
        user_cost=539, driver_cost=539, category='comfortplus',
    )

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(request, 1)

    ts = db.tariff_settings.find_one()
    econom_cat = ts['s'][0]
    assert econom_cat['n'] == 'econom'
    assert not econom_cat['fixed_price_enabled']

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    response_without_offer = response.json()
    offer_id = response_without_offer.pop('offer')
    for service_level in expected_response['service_levels']:
        service_level['offer'] = offer_id
    assert response_without_offer == expected_response

    offer = utils.get_saved_offer(db)
    assert offer['_id'] == offer_id
    assert offer['authorized']
    assert offer['created'] == now.replace(microsecond=0)
    assert not offer['destination_is_airport']
    assert offer['distance'] == 7514.629286628636
    assert offer['due'] == (
        now.replace(microsecond=0) + datetime.timedelta(minutes=10)
    )
    assert not offer['is_fixed_price']
    assert len(offer['prices']) == 2
    for price in offer['prices']:
        if price['cls'] == 'econom':
            assert not price['is_fixed_price']
        else:
            assert price['is_fixed_price']
    assert offer['route'] == [
        [37.647932797875484, 55.742884944005525],
        [37.58992385864258, 55.73382568359375],
    ]
    assert offer['time'] == 1421.5866954922676
    assert offer['user_id'] == 'b300bda7d41b4bae8d58dfa93221ef16'


@pytest.mark.parametrize(
    'pickup_zones_response, unavailable_tarrifs',
    [
        pytest.param(
            None,
            [],
            marks=[pytest.mark.config(MODES=[{'mode': 'black'}])],
            id='no_blocked_activation_zones',
        ),
        pytest.param(
            'pickup_no_zones.json', ['business'], id='pickup_no_zones',
        ),
        pytest.param('pickup_common_zone.json', [], id='pickup_common_zone'),
        pytest.param(
            'pickup_different_zones.json',
            ['business'],
            id='pickup_different_zones',
        ),
        pytest.param(None, ['business'], id='fallback_for_pickup_zones_error'),
    ],
)
def test_availability_tariffs_by_blocked_zones(
        local_services_base,
        mockserver,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        pickup_zones_response,
        unavailable_tarrifs,
):
    @mockserver.json_handler('/driver-eta/eta')
    def mock(request):
        return utils.mock_driver_eta(load_json, 'driver_eta.json')(request)

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def mock_pickup_zones(request):
        if pickup_zones_response:
            return load_json(pickup_zones_response)
        else:
            return mockserver.make_response(status=500)

    response = taxi_protocol.post('3.0/routestats', load_json('request.json'))

    assert response.status_code == 200
    response_json = response.json()

    assert unavailable_tarrifs == [
        level['class']
        for level in response_json['service_levels']
        if level['tariff_unavailable']['code'] != 'no_free_cars_nearby'
    ]


@pytest.mark.config(
    NO_CARS_ORDER_MIN_VERSIONS={'android': {'version': [3, 15, 0]}},
    NO_CARS_ORDER_AVAILABLE_BY_ZONES=['moscow'],
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.user_experiments('no_cars_order_available')
@pytest.mark.parametrize(
    'use_umlaas',
    [False, pytest.param(True, marks=USE_UMLAAS_NO_CARS_VERDICT)],
)
def test_driver_eta(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        mockserver,
        use_umlaas,
):
    SEARCH_SETTINGS = {
        'limit': 10,
        'max_distance': 10000,
        'max_route_distance': 10000,
        'max_route_time': 720,
    }

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(
            request, 2, SurchargeParams(0.7, 0.3, 1000.5),
        )

    @mockserver.json_handler('/mlaas/eta')
    def mock_eta_mlaas(request):
        return load_json('eta_mlaas.json')

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        data = {
            'classes': {
                'business': {
                    'found': True,
                    'search_settings': SEARCH_SETTINGS,
                    'estimated_time': 300,
                    'estimated_distance': 500,
                },
                'econom': {
                    'found': True,
                    'search_settings': SEARCH_SETTINGS,
                    'estimated_time': 200,
                    'estimated_distance': 600,
                    'candidates': [],
                },
                'comfortplus': {
                    'found': False,
                    'search_settings': SEARCH_SETTINGS,
                },
                'minivan': {
                    'found': True,
                    'search_settings': SEARCH_SETTINGS,
                    'estimated_time': 100,
                    'estimated_distance': 300,
                    'candidates': [
                        {
                            'dbid': 'dbid',
                            'uuid': 'uuid',
                            'status': 'free',
                            'grade': 4,
                            'position': [1, 2],
                            'chain_info': {'destination': [4, 5]},
                            'route_info': {
                                'time': 100,
                                'distance': 300,
                                'approximate': False,
                            },
                        },
                    ],
                },
            },
        }
        return mockserver.make_response(json.dumps(data), 200)

    @mockserver.json_handler('/mlaas/no_cars_order/v1')
    def mock_no_cars_order_mlaas(request):
        assert not use_umlaas
        for class_info in request.json['classes_info']:
            expected_info = copy.deepcopy(class_info)
            expected_info.update(
                {
                    'limit': SEARCH_SETTINGS['limit'],
                    'max_line_distance': SEARCH_SETTINGS['max_distance'],
                    'max_distance': SEARCH_SETTINGS['max_route_distance'],
                    'max_time': SEARCH_SETTINGS['max_route_time'],
                },
            )
            assert class_info == expected_info

        return load_json('no_cars_order_mlaas.json')

    @mockserver.json_handler('/umlaas/umlaas/v1/no-cars-order')
    def mock_no_cars_order_umlaas(request):
        assert use_umlaas
        for class_info in request.json['classes_info']:
            expected_info = copy.deepcopy(class_info)
            expected_info.update(
                {
                    'max_candidate_count': SEARCH_SETTINGS['limit'],
                    'max_line_distance': SEARCH_SETTINGS['max_distance'],
                    'max_distance': SEARCH_SETTINGS['max_route_distance'],
                    'max_time': SEARCH_SETTINGS['max_route_time'],
                },
            )
            assert class_info == expected_info
        return load_json('no_cars_order_mlaas.json')

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    data = response.json()

    expected = {'econom': 300, 'business': 600, 'minivan': 120}
    for service_level in data['service_levels']:
        if service_level['class'] not in expected:
            continue
        actual_eta = service_level['estimated_waiting']['seconds']
        assert actual_eta == expected[service_level['class']]


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(filename='experiments3.json')
def test_driver_eta_fallback(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        mockserver,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(
            request, 2, SurchargeParams(0.7, 0.3, 1000.5),
        )

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        return mockserver.make_response(500)

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    data = response.json()

    for service_level in data['service_levels']:
        assert 'tariff_unavailable' not in service_level


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='protocol_save_offer_via_service',
    consumers=['protocol/routestats'],
    clauses=[
        {
            'enabled': True,
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)
def test_order_offers_no_fallback(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        mockserver,
):
    @mockserver.handler('/order-offers/v1/save-offer')
    def _mock_save_offer(request):
        return mockserver.make_response('', 500)

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 500


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='protocol_save_offer_via_service',
    consumers=['protocol/routestats'],
    clauses=[
        {
            'enabled': True,
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)
@pytest.mark.config(PROTOCOL_GENERATE_OFFER_ID_BY_SERVICE='enabled')
def test_order_offers_generate_id(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        mockserver,
        mock_order_offers,
):
    generated_id = 'offer-id-from-service'

    @mockserver.json_handler('/order-offers/v1/generate-offer-id')
    def mock_generate_offer_id(request):
        return {'offer_id': generated_id}

    request = load_json('simple_request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    assert response.json().get('offer') == generated_id

    assert mock_generate_offer_id.times_called == 1

    assert mock_order_offers.get_offer(generated_id) is not None


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='protocol_save_offer_via_service',
    consumers=['protocol/routestats'],
    clauses=[
        {
            'enabled': True,
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)
@pytest.mark.config(PROTOCOL_GENERATE_OFFER_ID_BY_SERVICE='enabled')
def test_order_offers_generate_id_error(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        mockserver,
        mock_order_offers,
):
    @mockserver.json_handler('/order-offers/v1/generate-offer-id')
    def mock_generate_offer_id(request):
        return mockserver.make_response('', 500)

    request = load_json('simple_request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 500

    assert mock_generate_offer_id.times_called == 1


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='protocol_save_offer_via_service',
    consumers=['protocol/routestats'],
    clauses=[
        {
            'enabled': True,
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)
@pytest.mark.config(
    PROTOCOL_GENERATE_OFFER_ID_BY_SERVICE='enabled_with_fallback',
)
@pytest.mark.parametrize('generate_with_error', [False, True])
def test_order_offers_generate_id_fallback(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        mockserver,
        mock_order_offers,
        generate_with_error,
):
    generated_id = 'offer-id-from-service'

    @mockserver.json_handler('/order-offers/v1/generate-offer-id')
    def mock_generate_offer_id(request):
        if generate_with_error:
            return mockserver.make_response('', 500)
        return {'offer_id': generated_id}

    request = load_json('simple_request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200

    response_offer_id = response.json().get('offer')
    assert response_offer_id is not None
    if generate_with_error:
        assert response_offer_id != generated_id
    else:
        assert response_offer_id == generated_id

    assert mock_generate_offer_id.times_called == 1

    if generate_with_error:
        assert mock_order_offers.get_offer(generated_id) is None
        assert mock_order_offers.get_offer(response_offer_id) is not None
    else:
        assert mock_order_offers.get_offer(generated_id) is not None


@pytest.mark.config(
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {'econom': {'visible_by_default': False}},
        'moscow': {
            'econom': {
                'visible_by_default': False,
                'show_experiment': 'show_moscow',
                'use_legacy_experiments': True,
            },
        },
    },
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('show_moscow')
def test_legacy_tariff_visibility(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        mockserver,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    assert response.json() == expected_response

    offer = utils.get_saved_offer(db)
    assert offer is None


@pytest.mark.config(
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {
            'econom': {'visible_by_default': False},
            'business': {'visible_by_default': True},
        },
        'moscow': {
            'econom': {
                'visible_by_default': False,
                'show_experiment': 'show_moscow',
            },
            'business': {
                'visible_by_default': True,
                'hide_experiment': 'hide_moscow_business',
            },
        },
    },
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='show_moscow',
    consumers=['tariff_visibility_helper'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='hide_moscow_business',
    consumers=['tariff_visibility_helper'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {
                'init': {
                    'set': ['corp'],
                    'arg_name': 'payment_option',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        },
    ],
)
def test_exp3_tariff_visibility(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        db,
        load_json,
        mockserver,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    assert response.json() == expected_response

    offer = utils.get_saved_offer(db)
    assert offer is None


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'cargo'],
    APPLICATION_BRAND_CATEGORIES_SETS={'__default__': ['econom', 'cargo']},
    DEFAULT_REQUIREMENTS={'__default__': {'cargo': {'cargo_type': 'lcv_m'}}},
)
@pytest.mark.parametrize(
    ('selected_class', 'request_requirements', 'order_requirements'),
    [
        pytest.param('econom', {}, {}, id='requested_reqs_for_other_class'),
        pytest.param(
            'cargo',
            {'cargo_type': 'van'},
            {'cargo_type': 'van'},
            id='requested_reqs_for_config_class',
        ),
        pytest.param(
            'cargo',
            {},
            {'cargo_type': 'lcv_m'},
            id='default_reqs_for_config_class',
        ),
    ],
)
def test_default_requirements(
        local_services,
        taxi_protocol,
        db,
        load_json,
        selected_class,
        request_requirements,
        order_requirements,
        mockserver,
        pricing_data_preparer,
):
    pricing_data_preparer.set_trip_information(time=600, distance=3800)
    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_cost(
        user_cost=152, driver_cost=152, category='econom',
    )
    pricing_data_preparer.set_cost(
        user_cost=301, driver_cost=301, category='cargo',
    )

    request = load_json('simple_request.json')
    request['selected_class'] = selected_class
    request['requirements'] = request_requirements
    request['tariff_requirements'] = [
        {'class': selected_class, 'requirements': request_requirements},
    ]

    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200

    offer = utils.get_saved_offer(db)
    assert offer['classes_requirements'] == {
        selected_class: order_requirements,
    }


def build_rule(tariff, position_expression):
    return {'tariff': tariff, 'position_expression': position_expression}


def assert_response_tariffs(response, expected_tariffs):
    assert response.status_code == 200

    response_tariffs = list(
        map(
            lambda level: level['class'],
            filter(
                lambda level: level['is_hidden'] is not True,
                response.json()['service_levels'],
            ),
        ),
    )
    assert response_tariffs == expected_tariffs


@pytest.mark.config(ALL_CATEGORIES=['econom', 'business', 'cargo'])
@pytest.mark.parametrize(
    ('experiment_priority', 'expected_tariffs'),
    [
        pytest.param(
            [], ['econom', 'business', 'cargo'], id='default_priority',
        ),
        pytest.param(
            [build_rule('cargo', '0')],
            ['cargo', 'econom', 'business'],
            id='cargo_first',
        ),
        pytest.param(
            [build_rule('econom', '2'), build_rule('cargo', '0')],
            ['cargo', 'business', 'econom'],
            id='forward_then_backward',
        ),
        pytest.param(
            [build_rule('cargo', '0'), build_rule('econom', '2')],
            ['cargo', 'business', 'econom'],
            id='backward_then_forward',
        ),
        pytest.param(
            [build_rule('econom', '1'), build_rule('business', '2')],
            ['econom', 'cargo', 'business'],
            id='both_forward',
        ),
        pytest.param(
            [build_rule('business', '0'), build_rule('cargo', '1')],
            ['business', 'cargo', 'econom'],
            id='both_backward',
        ),
        pytest.param(
            [build_rule('cargo', '0'), build_rule('econom', 'invalid input')],
            ['econom', 'business', 'cargo'],
            id='invalid_expression',
        ),
        pytest.param(
            [build_rule('cargo', '2 - 0 - 3 + 1')],
            ['cargo', 'econom', 'business'],
            id='cargo_first_expression',
        ),
        pytest.param(
            [build_rule('cargo', 'selected_position')],
            ['econom', 'cargo', 'business'],
            id='cargo_instead_selected',
        ),
        pytest.param(
            [build_rule('econom', 'last_position - 1')],
            ['business', 'econom', 'cargo'],
            id='econom_before_last',
        ),
    ],
)
def test_tariffs_prioritization(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        experiments3,
        experiment_priority,
        expected_tariffs,
        mockserver,
):
    experiments3.add_experiment(
        name='prioritize_tariffs',
        consumers=['protocol/routestats'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'position_rules': experiment_priority},
    )

    request = load_json('simple_request.json')
    request['selected_class'] = 'business'
    response = taxi_protocol.post('3.0/routestats', request)
    assert_response_tariffs(response, expected_tariffs)


@pytest.mark.config(ALL_CATEGORIES=['econom', 'business'])
@pytest.mark.parametrize(
    ('selected_class', 'expected_tariffs'),
    [
        pytest.param(
            None, ['econom', 'business'], id='no_priority_without_selected',
        ),
        pytest.param(
            'bad', ['econom', 'business'], id='no_priority_bad_selected',
        ),
        pytest.param(
            'business', ['business', 'econom'], id='priority_for_selected',
        ),
    ],
)
def test_prioritization_by_selected_class(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        experiments3,
        selected_class,
        expected_tariffs,
        mockserver,
):
    experiments3.add_experiment(
        name='prioritize_tariffs',
        consumers=['protocol/routestats'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'position_rules': [build_rule('econom', 'selected_position')],
        },
    )

    request = load_json('simple_request.json')
    if selected_class:
        request['selected_class'] = selected_class
    response = taxi_protocol.post('3.0/routestats', request)
    assert_response_tariffs(response, expected_tariffs)


@pytest.mark.parametrize(
    ('selected_class', 'experiment_in_response'),
    [
        pytest.param(None, False, id='no_exp_without_selected_class'),
        pytest.param('econom', False, id='no_exp_for_wrong_class'),
        pytest.param('business', True, id='exp_for_right_class'),
    ],
)
def test_selected_class_experiment_parameter(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        experiments3,
        selected_class,
        experiment_in_response,
        mockserver,
):
    experiments3.add_experiment(
        name='test_selected_class',
        consumers=['client_protocol/routestats'],
        match={
            'predicate': {
                'init': {
                    'set': ['business'],
                    'arg_name': 'selected_class',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
            'enabled': True,
        },
        clauses=[],
        default_value={},
    )

    request = load_json('simple_request.json')
    if selected_class:
        request['selected_class'] = selected_class
    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200

    client_experiments = [
        exp['name'] for exp in response.json()['typed_experiments']['items']
    ]
    if experiment_in_response:
        assert 'test_selected_class' in client_experiments
    else:
        assert 'test_selected_class' not in client_experiments


@pytest.mark.parametrize(
    ('point_a', 'in_experiment'),
    [
        pytest.param([37.1, 55.9], True, id='point_a_inside_polygon'),
        pytest.param([37.7, 55.9], False, id='point_a_outside_polygon'),
    ],
)
def test_experiment_falls_inside_predicate(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        experiments3,
        point_a,
        in_experiment,
        mockserver,
):
    exp_name = 'test_falls_inside'
    experiments3.add_experiment(
        name=exp_name,
        consumers=['client_protocol/routestats'],
        match={
            'predicate': {
                'type': 'falls_inside',
                'init': {
                    'arg_name': 'point_a',
                    'arg_type': 'linear_ring',
                    'value': [
                        [37.038117609374986, 55.93553344495757],
                        [37.20565911328124, 55.937075097294915],
                        [37.20565911328124, 55.863006264633],
                        [37.03537102734374, 55.86377854710077],
                    ],
                },
            },
            'enabled': True,
        },
        clauses=[],
        default_value={},
    )

    request = load_json('simple_request.json')
    request['route'][0] = point_a
    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200

    client_experiments = [
        exp['name'] for exp in response.json()['typed_experiments']['items']
    ]
    if in_experiment:
        assert exp_name in client_experiments
    else:
        assert exp_name not in client_experiments


@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='skip_hidden_tariff_info',
    consumers=['protocol/routestats'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(
    ALL_CATEGORIES=['econom'],
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {'econom': {'visible_by_default': False}},
    },
)
@pytest.mark.parametrize(
    'prefiltration_enabled',
    [
        pytest.param(
            value,
            marks=pytest.mark.experiments3(
                is_config=True,
                name='routestats_tariffs_experimental_prefiltration',
                consumers=['protocol/routestats'],
                match={'predicate': {'type': 'true'}, 'enabled': True},
                clauses=[],
                default_value={'enabled': value},
            ),
        )
        for value in (False, True)
    ],
)
def test_hidden_tariff_response(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        mockserver,
        prefiltration_enabled,
):
    request = load_json('simple_request.json')
    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200

    response_json = response.json()
    levels = response_json.get('service_levels', [])
    expected_service_level = {
        'class': 'econom',
        'is_hidden': True,
        'name': 'Economy',
        'service_level': 50,
    }

    assert len(levels) > 0
    for service_level in levels:
        if service_level['class'] == 'econom':
            service_level.pop('offer', '')
            assert service_level == expected_service_level


@pytest.mark.config(
    NO_CARS_ORDER_MIN_VERSIONS={'android': {'version': [3, 15, 0]}},
    NO_CARS_ORDER_AVAILABLE_BY_ZONES=['moscow'],
    PROTOCOL_USE_SURGE_CALCULATOR=True,
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.user_experiments('no_cars_order_available')
@pytest.mark.experiments3(
    filename='paid_supply/exp3_request_umlaas_no_cars_verdict.json',
)
@pytest.mark.experiments3(
    filename='paid_supply/use_no_cars_verdict_from_umlaas.json',
)
def test_umlaas_no_cars_order_request(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        mockserver,
):
    pricing_data_preparer.set_fixed_price(enable=False)
    pricing_data_preparer.set_trip_information(time=0.0, distance=0.0)
    pricing_data_preparer.set_meta('min_price', 639)
    pricing_data_preparer.set_cost(user_cost=639, driver_cost=639)
    pricing_data_preparer.set_meta('min_price', 469, category='econom')
    pricing_data_preparer.set_cost(
        user_cost=469, driver_cost=469, category='econom',
    )
    pricing_data_preparer.set_user_surge(
        2, alpha=0.7, beta=0.3, surcharge=1000.5,
    )

    SEARCH_SETTINGS = {
        'limit': 10,
        'max_distance': 10000,
        'max_route_distance': 10000,
        'max_route_time': 720,
    }

    @mockserver.json_handler('/mlaas/eta')
    def mock_eta_mlaas(request):
        return load_json('eta_mlaas.json')

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        data = {
            'classes': {
                'business': {
                    'found': True,
                    'search_settings': SEARCH_SETTINGS,
                    'estimated_time': 300,
                    'estimated_distance': 500,
                },
                'econom': {
                    'found': True,
                    'search_settings': SEARCH_SETTINGS,
                    'estimated_time': 200,
                    'estimated_distance': 600,
                    'candidates': [],
                },
                'comfortplus': {
                    'found': False,
                    'search_settings': SEARCH_SETTINGS,
                },
                'minivan': {
                    'found': True,
                    'search_settings': SEARCH_SETTINGS,
                    'estimated_time': 100,
                    'estimated_distance': 300,
                    'candidates': [
                        {
                            'dbid': 'dbid',
                            'uuid': 'uuid',
                            'status': 'free',
                            'grade': 4,
                            'position': [1, 2],
                            'chain_info': {'destination': [4, 5]},
                            'route_info': {
                                'time': 100,
                                'distance': 300,
                                'approximate': False,
                            },
                        },
                    ],
                },
            },
        }
        return mockserver.make_response(json.dumps(data), 200)

    umlaas_json = {}

    @mockserver.json_handler('/umlaas/umlaas/v1/no-cars-order')
    def mock_no_cars_order_umlaas(request):
        nonlocal umlaas_json
        umlaas_json = request.json
        return load_json('no_cars_order_mlaas.json')

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert umlaas_json['currency'] == 'RUB'
    assert umlaas_json['route_distance'] == 0.0
    assert umlaas_json['route_duration'] == 0.0
    assert umlaas_json['route_points'] == [[37.6163408566, 55.7565896873]]
    assert umlaas_json['tariff_zone'] == 'moscow'
    assert sorted(
        umlaas_json['classes_info'], key=lambda v: v['tariff_class'],
    ) == load_json('expected_umlaas_classes_info.json')

    assert response.status_code == 200


@pytest.mark.parametrize(
    ('pdp_response_code', 'routestats_response_code'),
    [
        pytest.param(200, 200, id='pdp_code_200'),
        pytest.param(400, 400, id='pdp_code_400'),
        pytest.param(429, 429, id='pdp_code_429'),
        pytest.param(500, 500, id='pdp_code_500'),
    ],
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
def test_pdp_response_code(
        local_services,
        taxi_protocol,
        load_json,
        mockserver,
        experiments3,
        pdp_response_code,
        routestats_response_code,
):
    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def _mock_v2_prepare(request):
        if pdp_response_code == 400:
            response_json = {
                'message': 'error UNABLE_TO_MATCH_TARIFF',
                'code': 'UNABLE_TO_MATCH_TARIFF',
            }
            return mockserver.make_response(json.dumps(response_json), 400)

        if pdp_response_code == 200:
            return load_json('pdp_response.json')

        return mockserver.make_response('', pdp_response_code)

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == routestats_response_code


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.parametrize(
    'show_eta_v2_on_ui',
    [
        pytest.param(
            True,
            marks=pytest.mark.experiments3(filename='show_eta_v2_on_ui.json'),
            id='show_eta_v2',
        ),
        pytest.param(
            False,
            marks=pytest.mark.experiments3(filename='hide_eta_v2_on_ui.json'),
            id='hide_eta_v2',
        ),
    ],
)
@pytest.mark.parametrize(
    'prefiltration_enabled',
    [
        pytest.param(
            value,
            marks=pytest.mark.experiments3(
                is_config=True,
                name='routestats_tariffs_experimental_prefiltration',
                consumers=['protocol/routestats'],
                match={'predicate': {'type': 'true'}, 'enabled': True},
                clauses=[],
                default_value={'enabled': value},
            ),
        )
        for value in (False, True)
    ],
)
@pytest.mark.user_experiments('no_cars_order_available')
@pytest.mark.parametrize('order_allowed', [False, True])
def test_driver_eta_v2(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        mockserver,
        order_allowed,
        show_eta_v2_on_ui,
        prefiltration_enabled,
        db,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(
            request, 2, SurchargeParams(0.7, 0.3, 1000.5),
        )

    @mockserver.json_handler('/mlaas/eta')
    def mock_eta_mlaas(request):
        if order_allowed:
            return load_json('eta_mlaas.json')
        return {}

    @mockserver.json_handler('/driver-eta/driver-eta/v2/eta')
    def mock_driver_eta(request):
        response = load_json('driver_eta_v2.json')
        if not order_allowed:
            for _, tariff_class in response['classes'].items():
                tariff_class['order_allowed'] = False
        return response

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    assert mock_driver_eta.times_called == 1
    if show_eta_v2_on_ui:
        assert mock_eta_mlaas.times_called == 0
    else:
        assert mock_eta_mlaas.times_called == 1

    data = response.json()

    expected = (
        {'econom': 120, 'vip': 120}
        if show_eta_v2_on_ui
        else {'econom': 180, 'vip': 300}
    )
    expected_no_cars = ['business']

    for service_level in data['service_levels']:
        if service_level['class'] not in expected:
            continue
        if order_allowed:
            if service_level['class'] not in expected_no_cars:
                actual_eta = service_level['estimated_waiting']['seconds']
                assert actual_eta == expected[service_level['class']]
            else:
                assert 'estimated_waiting' not in service_level
                assert service_level['no_cars_order_enabled']
        else:
            'tariff_unavailable' in service_level


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(filename='show_eta_v2_on_ui.json')
@pytest.mark.user_experiments('no_cars_order_available')
@pytest.mark.parametrize('no_point_b', [False, True])
@pytest.mark.config(
    PAID_SUPPLY_LONG_TRIP_CRITERIA={
        'moscow': {
            '__default__': {'apply': 'either', 'distance': 1, 'duration': 1},
        },
    },
)
def test_paid_supply_no_b(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        mockserver,
        no_point_b,
):
    @mockserver.json_handler('/surger/get_surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_response(
            request, 2, SurchargeParams(0.7, 0.3, 1000.5),
        )

    @mockserver.json_handler('/driver-eta/driver-eta/v2/eta')
    def mock_driver_eta(request):
        return load_json('driver_eta_v2.json')

    pricing_data_preparer.set_fixed_price(category='comfortplus', enable=True)
    request = load_json('request.json')
    if no_point_b:
        request['route'] = request['route'][0:1]
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    assert mock_driver_eta.times_called == 1

    data = response.json()
    is_comfortplus_exists = False
    for service_level in data['service_levels']:
        if service_level['class'] == 'comfortplus':
            assert 'tariff_unavailable' in service_level
            assert 'estimated_waiting' not in service_level
            if no_point_b:
                assert (
                    service_level['tariff_unavailable']['code']
                    == 'paid_supply_no_b'
                )
            else:
                assert (
                    service_level['tariff_unavailable']['code']
                    == 'no_free_cars_nearby'
                )
            is_comfortplus_exists = True
    assert is_comfortplus_exists


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(filename='show_eta_v2_on_ui.json')
@pytest.mark.user_experiments('no_cars_order_available')
@pytest.mark.config(
    PAID_SUPPLY_LONG_TRIP_CRITERIA={
        'moscow': {
            '__default__': {'apply': 'either', 'distance': 1, 'duration': 1},
        },
    },
)
def test_hide_eta_for_cash_payment(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        load_json,
        mockserver,
):
    @mockserver.json_handler('/surger/get_surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_response(
            request, 2, SurchargeParams(0.7, 0.3, 1000.5),
        )

    @mockserver.json_handler('/driver-eta/driver-eta/v2/eta')
    def mock_driver_eta(request):
        return load_json('driver_eta_v2.json')

    request = load_json('request.json')
    request['payment']['type'] = 'cash'
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    assert mock_driver_eta.times_called == 1

    data = response.json()
    for service_level in data['service_levels']:
        if service_level['class'] == 'comfortplus':
            assert 'tariff_unavailable' in service_level
            assert service_level['tariff_unavailable'] == {
                'message': 'Paid supply does not support cash',
                'code': 'paid_supply_no_cash',
            }
            assert 'estimated_waiting' not in service_level


@pytest.mark.now('2022-06-25T11:30:00+0300')
@pytest.mark.experiments3(filename='show_eta_v2_on_ui.json')
@pytest.mark.user_experiments('no_cars_order_available')
@pytest.mark.config(
    PAID_SUPPLY_LONG_TRIP_CRITERIA={
        'moscow': {
            '__default__': {'apply': 'either', 'distance': 1, 'duration': 1},
        },
    },
)
@pytest.mark.experiments3(filename='paid_supply_restrictions_exp3.json')
def test_paid_supply_restrictions(
        config,
        local_services,
        taxi_protocol,
        db,
        load_json,
        now,
        mockserver,
        experiments3,
        pricing_data_preparer,
):
    pricing_data_preparer.set_cost(
        category='econom', user_cost=317, driver_cost=317,
    )
    pricing_data_preparer.set_user_category_prices_id(
        category='econom',
        category_prices_id='c/b7c4d5f6aa3b40a3807bb74b3bc042af',
        category_id='b7c4d5f6aa3b40a3807bb74b3bc042af',
    )

    pricing_data_preparer.set_paid_supply(
        category='econom', price={'price': 146},
    )

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(request, 1)

    @mockserver.json_handler('/driver-eta/driver-eta/v2/eta')
    def mock_driver_eta(request):
        return load_json('driver_eta_response.json')

    config.set_values(BASE_PAID_SUPPLY_CONFIG)

    experiments3.add_experiments_json(load_json('experiments3_01.json'))

    taxi_protocol.tests_control(now=now, invalidate_caches=True)

    request = load_json('request.json')

    response = taxi_protocol.post(
        '3.0/routestats',
        request,
        headers={
            'User-Agent': 'yandex-taxi/3.82.0.7675 Android/7.0 (test client)',
        },
    )

    assert response.status_code == 200
    data = response.json()

    data = response.json()

    expected_offer_prices = [
        {
            'price': 317.0,
            'driver_price': 317.0,
            'cls': 'econom',
            'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
            'cat_type': 'application',
            'sp': 1.0,
            'is_fixed_price': True,
            'using_new_pricing': True,
            'paid_supply_price': 146.0,
            'paid_supply_info': {'distance': 10000, 'time': 900},
        },
    ]

    offer = utils.get_saved_offer(db)
    del offer['prices'][0]['pricing_data']
    assert offer['prices'] == expected_offer_prices

    assert len(data['service_levels']) == 1
    service_level = data['service_levels'][0]
    assert service_level['class'] == 'econom'
    service_level['estimated_waiting']['seconds'] == 1200
