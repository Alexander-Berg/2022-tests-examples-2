# pylint: disable=E0401
import copy
import decimal

from grocery_mocks.models import country
from metrics_aggregations import helpers as metrics_helpers
import pytest

from tests_grocery_payments_methods import consts
from tests_grocery_payments_methods.plugins import mock_api_proxy

SENSOR_METHOD_FALLBACK = 'grocery_payments_methods_method_fallback_metrics'

COUNTRY = country.Country.Russia
CURRENCY = COUNTRY.currency
COUNTRY_ISO2 = COUNTRY.country_iso2
REGION_ID = COUNTRY.geobase_country_id

CARD: dict = {
    key: value
    for key, value in mock_api_proxy.CARD.items()
    if key != 'available'
}

APPLE_PAY: dict = {
    **mock_api_proxy.APPLE_PAY,
    'availability': {'available': True},
    'id': 'applepay',
}

GOOGLE_PAY: dict = {
    **mock_api_proxy.GOOGLE_PAY,
    'availability': {'available': True},
    'id': 'googlepay',
}

BADGE: dict = {**mock_api_proxy.BADGE}

CORP: dict = {**mock_api_proxy.CORP}

CIBUS: dict = {
    **mock_api_proxy.CIBUS,
    'availability': {'available': True},
    'id': 'cibus',
}

SBP: dict = {**mock_api_proxy.SBP, 'availability': {'available': True}}

PAYMENT_METHODS = [CARD, APPLE_PAY, GOOGLE_PAY, BADGE, CORP, CIBUS, SBP]


@pytest.fixture(name='list_payment_methods')
def _grocery_available_payment_methods(
        taxi_grocery_payments_methods, api_proxy,
):
    async def _inner():
        return await taxi_grocery_payments_methods.post(
            '/lavka/v1/payments-methods/v1/list-payment-methods',
            json={'location': mock_api_proxy.LOCATION, 'country_iso3': 'RUS'},
            headers=consts.DEFAULT_HEADERS,
        )

    return _inner


async def test_basic(
        list_payment_methods, api_proxy, grocery_payments_methods_configs,
):
    response = await list_payment_methods()
    response_json = response.json()

    response_payment_methods = response_json['payment_methods']

    assert len(PAYMENT_METHODS) == len(response_payment_methods)

    assert all(
        [
            payment_method in response_payment_methods
            for payment_method in PAYMENT_METHODS
        ],
    )

    assert (
        response_json['default_payment_method']
        == mock_api_proxy.LAST_PAYMENT_METHOD
    )

    additional_data = response_json['additional_data']

    assert additional_data == {
        'merchants': consts.MERCHANTS,
        'service_token': consts.SERVICE_TOKEN,
        'country_region_id': REGION_ID,
        'country_iso2': COUNTRY_ISO2,
        'currency': CURRENCY,
        'sbp_banks_info': [
            consts.BANKS[2].to_raw_response(),
            consts.BANKS[1].to_raw_response(),
            consts.BANKS[3].to_raw_response(),
            consts.BANKS[0].to_raw_response(),
        ],
    }

    assert (
        response_json['last_used_payment_method']
        == mock_api_proxy.LAST_PAYMENT_METHOD
    )
    assert response_json['service_token'] == consts.SERVICE_TOKEN
    assert response_json['merchant_id_list'] == consts.MERCHANTS
    assert response_json['location_info'] == {
        'country_code': COUNTRY_ISO2,
        'currency_code': CURRENCY,
        'region_id': REGION_ID,
    }

    assert api_proxy.lpm_times_called() == 1


@pytest.mark.config(
    STATISTICS_FALLBACK_OVERRIDES=[
        {
            'enabled': True,
            'fallbacks': [consts.METHODS_FALLBACK_NAME],
            'service': 'grocery-payments',
        },
    ],
)
async def test_methods_fallbacks(
        list_payment_methods,
        grocery_payments_methods_configs,
        taxi_grocery_payments_methods_monitor,
):
    grocery_payments_methods_configs.methods_fallbacks()

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_payments_methods_monitor,
            sensor=SENSOR_METHOD_FALLBACK,
    ) as collector:
        await list_payment_methods()

    payment_types = {}

    for method in PAYMENT_METHODS:
        if method['type'] in payment_types:
            payment_types[method['type']] += decimal.Decimal(1)
        else:
            payment_types[method['type']] = decimal.Decimal(1)

    metrics = collector.collected_metrics

    for metric in metrics:
        payment_type = metric.labels['payment_type']
        assert metric.value == payment_types[payment_type]
        assert metric.labels['sensor'] == SENSOR_METHOD_FALLBACK
        assert metric.labels['country'] == COUNTRY.name


@pytest.mark.parametrize('available', [True, False])
async def test_filter_unavailable_card(
        list_payment_methods,
        grocery_payments_methods_configs,
        api_proxy,
        available,
):
    card = copy.deepcopy(mock_api_proxy.CARD)
    card['availability']['available'] = available
    api_proxy.card_data = card

    grocery_payments_methods_configs.filter_unavailable_methods(enabled=True)

    response = await list_payment_methods()
    response_json = response.json()

    expected_payment_methods = copy.deepcopy(PAYMENT_METHODS)
    if not available:
        expected_payment_methods.remove(CARD)

    response_payment_methods = response_json['payment_methods']

    assert len(expected_payment_methods) == len(response_payment_methods)


@pytest.mark.parametrize('enabled', [True, False])
async def test_can_pay_unverified_cards(
        list_payment_methods,
        grocery_payments_methods_configs,
        api_proxy,
        enabled,
):
    card = copy.deepcopy(mock_api_proxy.CARD)
    card['availability']['available'] = False
    card['verify_strategy'] = 'card_antifraud'
    api_proxy.card_data = card

    grocery_payments_methods_configs.can_pay_unverified_cards(enabled=enabled)

    response = await list_payment_methods()
    response_json = response.json()

    response_card = list(
        filter(
            lambda x: x['type'] == 'card', response_json['payment_methods'],
        ),
    )[0]

    assert response_card['availability']['available'] == enabled
