# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
import copy

from grocery_mocks.models import country
from metrics_aggregations import helpers as metrics_helpers
import pytest

from tests_grocery_payments_methods import consts

SENSOR_BINDINGS_START = 'grocery_payments_methods_binding_start_metrics'
SENSOR_BINDINGS_EXTENDED_START = (
    'grocery_payments_methods_binding_start_extended_metrics'
)


COUNTRY_RUSSIA = country.Country.Russia
RUSSIA_CURRENCY = COUNTRY_RUSSIA.currency
COUNTRY_ISO2_RUS = COUNTRY_RUSSIA.country_iso2

COUNTRY_ISRAEL = country.Country.Israel
ISRAEL_CURRENCY = COUNTRY_ISRAEL.currency
COUNTRY_ISO2_ISR = COUNTRY_ISRAEL.country_iso2

CARD_BANK = 'some_bank'
SYSTEM = 'mastercard'
CARD_COUNTRY = 'RUS'

CARD_RESPONSE = {
    'billing_card_id': 'xb10sss57c12aaabe8345ac74',
    'bound': False,
    'busy': False,
    'busy_with': [],
    'card_id': 'card-xb10sss57c12aaabe8345ac74',
    'currency': 'RUB',
    'expiration_month': 2,
    'expiration_year': 22,
    'from_db': True,
    'number': '123456****1234',
    'owner': 'not used',
    'permanent_card_id': 'card-xb10sss57c12aaabe8345ac74',
    'possible_moneyless': False,
    'region_id': 'not used',
    'regions_checked': [],
    'system': SYSTEM,
    'unverified': False,
    'valid': True,
    'card_bank': CARD_BANK,
    'card_country': CARD_COUNTRY,
}

DEFAULT_CARD_INFO = {'bank': 'Sber Bank', 'country': 'RUS', 'system': 'visa'}


@pytest.fixture(name='binding')
def _binding(taxi_grocery_payments_methods):
    async def _inner(request=None, headers=None):
        if request is None:
            request = {'binding_id': 'binding_id', 'country_iso2': 'RU'}
        headers = headers or consts.DEFAULT_HEADERS
        return await taxi_grocery_payments_methods.post(
            '/lavka/v1/payments-methods/v1/binding',
            json=request,
            headers=headers,
        )

    return _inner


@pytest.mark.parametrize('billing_service', [None, 'some_service'])
async def test_cardstorage_request(
        binding,
        cardstorage,
        grocery_payments_methods_configs,
        billing_service,
):
    grocery_payments_methods_configs.grocery_binding_billing_service(
        service_name=billing_service,
    )

    card_info = {'bank': 'some_bank', 'country': 'RUS', 'system': 'visa'}

    request = {
        'binding_id': 'binding_id',
        'force_cache_invalidate': True,
        'region_id': 123,
        'country_iso2': COUNTRY_ISO2_RUS,
        'currency': RUSSIA_CURRENCY,
        'pass_params': {
            'avs_data': {
                'post_code': 'post_code',
                'street_address': 'street_address',
            },
            'preferred_processing_cc': 'preferred_processing_cc',
        },
        'card_info': card_info,
        'billing_service': billing_service,
    }

    headers = {
        **consts.DEFAULT_HEADERS,
        'X-YProxy-Header-Host': 'X-YProxy-Header-Host',
    }

    headers_check = {
        'X-AppMetrica-DeviceId': consts.APPMETRICA_DEVICE_ID,
        'X-YProxy-Header-Host': 'X-YProxy-Header-Host',
    }

    cardstorage.payment_verifications.mock_response(**consts.BINDING_RESPONSE)

    cardstorage_request = copy.deepcopy(request)
    cardstorage_request.pop('card_info')
    cardstorage.payment_verifications.check(
        headers=headers_check, **cardstorage_request,
    )

    response = await binding(request=request, headers=headers)

    assert response.json() == consts.BINDING_RESPONSE
    assert cardstorage.payment_verifications.times_called == 1


@pytest.mark.parametrize(
    'sensor_name, metric_value',
    [
        (
            SENSOR_BINDINGS_START,
            {'sensor': SENSOR_BINDINGS_START, 'country': COUNTRY_RUSSIA.name},
        ),
        (
            SENSOR_BINDINGS_EXTENDED_START,
            {
                'sensor': SENSOR_BINDINGS_EXTENDED_START,
                'country': COUNTRY_RUSSIA.name,
                'card_bank': DEFAULT_CARD_INFO['bank'],
                'card_system': DEFAULT_CARD_INFO['system'],
                'card_country': DEFAULT_CARD_INFO['country'],
                'app_name': 'Yango (android)',
                'currency': RUSSIA_CURRENCY,
            },
        ),
    ],
)
async def test_binding_start_metrics(
        binding,
        cardstorage,
        taxi_grocery_payments_methods_monitor,
        sensor_name,
        metric_value,
):
    request = {
        'binding_id': 'binding_id',
        'country_iso2': COUNTRY_ISO2_RUS,
        'currency': RUSSIA_CURRENCY,
        'card_info': DEFAULT_CARD_INFO,
    }

    cardstorage.payment_verifications.mock_response(**consts.BINDING_RESPONSE)

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_payments_methods_monitor, sensor=sensor_name,
    ) as collector:
        await binding(request=request)

    metric = collector.get_single_collected_metric()

    assert metric.value == 1
    assert metric.labels == metric_value


async def test_card_from_cardstorage(binding, cardstorage):
    request = {
        'binding_id': 'binding_id',
        'country_iso2': 'RU',
        'card_info': None,
    }

    cardstorage.payment_verifications.mock_response(**consts.BINDING_RESPONSE)
    cardstorage.card.mock_response(**CARD_RESPONSE)

    response = await binding(request=request)

    assert cardstorage.payment_verifications.times_called == 1
    assert cardstorage.card.times_called == 1
    assert response.status_code == 200


@pytest.mark.parametrize('status_code', [400, 404, 422])
async def test_cardstorage_errors(binding, cardstorage, status_code):
    cardstorage.payment_verifications.status_code = status_code
    response = await binding()

    assert cardstorage.payment_verifications.times_called == 1
    assert response.status_code == status_code


async def test_cardstorage_error_429(binding, cardstorage):
    status_code = 429
    retry_after = '1234'

    cardstorage.payment_verifications.mock_error(
        status_code=status_code, retry_after=retry_after,
    )
    response = await binding()

    assert cardstorage.payment_verifications.times_called == 1
    assert response.status_code == status_code
    assert response.headers['Retry-After'] == retry_after


@pytest.mark.parametrize(
    'exp_currency, country_iso2, expected_currency',
    [
        (RUSSIA_CURRENCY, COUNTRY_ISO2_ISR, RUSSIA_CURRENCY),
        (None, COUNTRY_ISO2_ISR, ISRAEL_CURRENCY),
    ],
)
async def test_currency(
        binding,
        cardstorage,
        grocery_payments_methods_configs,
        exp_currency,
        country_iso2,
        expected_currency,
):
    request = {'binding_id': 'binding_id', 'country_iso2': country_iso2}

    if exp_currency is not None:
        grocery_payments_methods_configs.grocery_binding_currency(
            currency=exp_currency,
        )

    cardstorage.payment_verifications.mock_response(**consts.BINDING_RESPONSE)
    cardstorage.payment_verifications.check(currency=expected_currency)
    await binding(request=request)

    assert cardstorage.payment_verifications.times_called == 1


@pytest.mark.parametrize(
    'request_card_info,cardstorage_card_times_called',
    [
        ({'bank': CARD_BANK, 'country': CARD_COUNTRY, 'system': SYSTEM}, 0),
        (None, 1),
    ],
)
async def test_currency_kwargs(
        binding,
        cardstorage,
        experiments3,
        grocery_payments_methods_configs,
        request_card_info,
        cardstorage_card_times_called,
):
    cardstorage.payment_verifications.mock_response(**consts.BINDING_RESPONSE)

    if request_card_info is None:
        cardstorage.card.mock_response(**CARD_RESPONSE)

    grocery_payments_methods_configs.grocery_binding_currency(currency='RUB')

    request = {
        'binding_id': 'binding_id',
        'country_iso2': 'IL',
        'card_info': request_card_info,
    }

    exp3_name = 'grocery_binding_currency'
    exp3_recorder = experiments3.record_match_tries(exp3_name)

    await binding(request=request)

    exp3_matches = await exp3_recorder.get_match_tries(1)
    exp3_kwargs = exp3_matches[0].kwargs
    assert exp3_kwargs['application'] == consts.APP_NAME

    assert exp3_kwargs['card_bank'] == CARD_BANK
    assert exp3_kwargs['card_country'] == CARD_COUNTRY
    assert exp3_kwargs['country_iso3'] == 'ISR'
    assert exp3_kwargs['personal_phone_id'] == consts.PERSONAL_PHONE_ID
    assert exp3_kwargs['system'] == SYSTEM
    assert exp3_kwargs['yandex_uid'] == consts.YANDEX_UID

    assert cardstorage.card.times_called == cardstorage_card_times_called
