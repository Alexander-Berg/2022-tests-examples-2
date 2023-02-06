# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
import copy

from grocery_mocks.models import country as country_models
from metrics_aggregations import helpers as metrics_helpers
import pytest

from tests_grocery_payments_methods import consts


SENSOR_BINDINGS_FINISH = 'grocery_payments_methods_binding_finish_metrics'
SENSOR_BINDINGS_EXTENDED_FINISH = (
    'grocery_payments_methods_binding_finish_extended_metrics'
)

COUNTRY = country_models.Country.Russia
ERROR_CODE = 'fail_3ds'
BINDING_CURRENCY = 'ILS'

SOME_BANK = 'some_bank!'
SOME_BANK_FORMATTED = 'somebank'

DEFUALT_CARD_INFO = {
    'bank': SOME_BANK,
    'country': COUNTRY.country_iso3,
    'system': 'visa',
}


@pytest.fixture(name='binding_status')
def _binding_status(taxi_grocery_payments_methods):
    async def _inner(request=None, headers=None):
        if request is None:
            request = {'binding_id': 'binding_id', 'country_iso2': 'RU'}
        headers = headers or consts.DEFAULT_HEADERS
        return await taxi_grocery_payments_methods.post(
            '/lavka/v1/payments-methods/v1/binding/status',
            json=request,
            headers=headers,
        )

    return _inner


@pytest.mark.parametrize('billing_service', [None, 'some_service'])
async def test_cardstorage_request(
        binding_status,
        cardstorage,
        grocery_payments_methods_configs,
        billing_service,
):
    grocery_payments_methods_configs.grocery_binding_billing_service(
        service_name=billing_service,
    )

    request = {
        'binding_id': 'binding_id',
        'verification_id': 'verification_id',
        'force_cache_invalidate': True,
        'country_iso2': 'RU',
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
    cardstorage.payment_verifications.check(headers=headers_check, **request)
    response = await binding_status(request=request, headers=headers)

    assert response.json() == consts.BINDING_RESPONSE

    assert cardstorage.payment_verifications.times_called == 1


@pytest.mark.parametrize('status_code', [400, 404, 422])
async def test_cardstorage_errors(binding_status, cardstorage, status_code):
    cardstorage.payment_verifications.status_code = status_code
    response = await binding_status()

    assert cardstorage.payment_verifications.times_called == 1
    assert response.status_code == status_code


async def test_cardstorage_error_429(binding_status, cardstorage):
    status_code = 429
    retry_after = '1234'

    cardstorage.payment_verifications.mock_error(
        status_code=status_code, retry_after=retry_after,
    )
    response = await binding_status()

    assert cardstorage.payment_verifications.times_called == 1
    assert response.status_code == status_code
    assert response.headers['Retry-After'] == retry_after


@pytest.mark.parametrize(
    'status, metric_count',
    [
        (consts.SUCCESS_BINDING_STATUS, 1),
        (consts.FAIL_BINDING_STATUS, 1),
        (consts.IN_PROGRESS_BINDING_STATUS, 0),
    ],
)
@pytest.mark.parametrize(
    'sensor_name, metric_value',
    [
        (
            SENSOR_BINDINGS_FINISH,
            {
                'sensor': SENSOR_BINDINGS_FINISH,
                'country': COUNTRY.name,
                'error_code': ERROR_CODE,
            },
        ),
        (
            SENSOR_BINDINGS_EXTENDED_FINISH,
            {
                'sensor': SENSOR_BINDINGS_EXTENDED_FINISH,
                'country': COUNTRY.name,
                'card_bank': SOME_BANK_FORMATTED,
                'card_system': DEFUALT_CARD_INFO['system'],
                'card_country': DEFUALT_CARD_INFO['country'],
                'app_name': 'Yango (android)',
                'currency': BINDING_CURRENCY,
                'error_code': ERROR_CODE,
            },
        ),
    ],
)
async def test_binding_finish_metrics(
        binding_status,
        cardstorage,
        taxi_grocery_payments_methods_monitor,
        status,
        metric_count,
        sensor_name,
        metric_value,
):
    request = {
        'binding_id': 'binding_id',
        'verification_id': 'verification_id',
        'force_cache_invalidate': True,
        'country_iso2': COUNTRY.country_iso2,
        'card_info': DEFUALT_CARD_INFO,
    }

    mock_response = copy.deepcopy(consts.BINDING_RESPONSE)
    mock_response['verification']['status'] = status
    mock_response['verification']['tech_error_code'] = ERROR_CODE
    mock_response['verification']['currency'] = BINDING_CURRENCY

    cardstorage.payment_verifications.mock_response(**mock_response)

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_payments_methods_monitor, sensor=sensor_name,
    ) as collector:
        await binding_status(request=request)

    metric = collector.get_single_collected_metric()

    if metric_count == 0:
        assert metric is None
        return

    assert metric.value == metric_count

    metric_value['status'] = status
    assert metric.labels == metric_value
