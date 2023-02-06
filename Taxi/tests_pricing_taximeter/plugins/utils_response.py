# pylint: disable=redefined-outer-name
import pytest


@pytest.fixture
def econom_category(load_json):
    return load_json('v2_prepare_econom_category.json')


@pytest.fixture
def econom_category_callcenter(load_json):
    return load_json('v2_prepare_econom_category_callcenter.json')


@pytest.fixture
def decoupling_response(load_json):
    return load_json('v2_prepare_decoupling_response.json')


@pytest.fixture
def business_category(load_json):
    return load_json('v2_prepare_business_category.json')


@pytest.fixture
def econom_tariff(econom_category):
    return econom_category['user']['data']['tariff']


@pytest.fixture
def business_tariff(business_category):
    return business_category['user']['data']['tariff']


@pytest.fixture
def callcenter_tariff(econom_category_callcenter):
    return econom_category_callcenter['user']['data']['tariff']


@pytest.fixture
def econom_with_additional_prices(load_json):
    return load_json('v2_prepare_econom_with_additional_prices.json')


@pytest.fixture
def econom_response(econom_category):
    return {
        'categories': {'econom': econom_category},
        'surge_calculation_id': '012345678901234567890123',
    }


@pytest.fixture
def business_response(business_category, econom_category):
    return {
        'categories': {
            'business': business_category,
            'econom': econom_category,
        },
        'surge_calculation_id': '012345678901234567890123',
    }


def calc_price(price):
    assert 'total' in price
    return float(price['total'])


def category_list(response):
    return list(cat for cat, _ in response['categories'].items())
