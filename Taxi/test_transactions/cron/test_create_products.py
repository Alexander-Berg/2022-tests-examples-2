# pylint: disable=redefined-outer-name
import pytest

from transactions.clients.trust import settings as trust_settings
from transactions.generated.eda_cron import cron_context
from transactions.generated.eda_cron import run_cron as run_eda_cron
from transactions.generated.lavka_isr_cron import (
    run_cron as run_lavka_isr_cron,
)

RUNNERS_BY_APP = {'eda': run_eda_cron, 'lavka_isr': run_lavka_isr_cron}
PARTNER_PARAMS_BY_APP = {
    'eda': {
        'name': 'ООО «Яндекс.Еда»',
        'email': 'love@eda.yandex',
        'phone': '8 (800) 600-12-10',
        'region_id': 225,
    },
    'lavka_isr': None,
}

FOOD_PRODUCT = 'eda_107819207_ride'
MEDS_PRODUCT = 'eda_133158084_meds'
FUEL_PRODUCT = 'eda_133158084_fuel'
LAVKA_PRODUCT = 'lavka_courier'
LAVKA_ISR_PRODUCT = 'lavka_delivery'
EXPECTED_PRODUCT_NAMES = {
    FOOD_PRODUCT: 'Eda services',
    MEDS_PRODUCT: 'Eda.Pharmacy medications',
    FUEL_PRODUCT: 'Eda.Fuel services',
    LAVKA_PRODUCT: 'Lavka services',
    LAVKA_ISR_PRODUCT: 'Lavka services',
}


@pytest.fixture
def mock_trust_get_product(mockserver):
    def _do_mock(product_id, status):
        assert status in ('success', 'error')

        @mockserver.json_handler(f'/trust-payments/v2/products/{product_id}')
        def _handler(request):
            if status == 'success':
                return {'status': 'success'}
            return {'status': 'error', 'status_code': 'product_not_found'}

        return _handler

    return _do_mock


@pytest.mark.parametrize(
    'app, expected_get_product_calls',
    [
        (
            'eda',
            [
                (
                    FOOD_PRODUCT,
                    [{'service': trust_settings.BILLING_SERVICE_EDA}],
                ),
                (
                    MEDS_PRODUCT,
                    [
                        {
                            'service': (
                                trust_settings.BILLING_SERVICE_EDA_PHARMACY
                            ),
                        },
                    ],
                ),
                (
                    FUEL_PRODUCT,
                    [{'service': trust_settings.BILLING_SERVICE_EDA_FUEL}],
                ),
                (
                    LAVKA_PRODUCT,
                    [
                        {
                            'service': (
                                trust_settings.BILLING_SERVICE_LAVKA_COURIER
                            ),
                        },
                        {
                            'service': (
                                getattr(
                                    trust_settings,
                                    'BILLING_SERVICE_LAVKA_COURIER_ACCEPT_QTY',
                                )
                            ),
                        },
                    ],
                ),
            ],
        ),
        (
            'lavka_isr',
            [
                (
                    LAVKA_ISR_PRODUCT,
                    [
                        {
                            'service': (
                                trust_settings.BILLING_SERVICE_LAVKA_DELIVERY
                            ),
                        },
                    ],
                ),
            ],
        ),
    ],
)
async def test_already_exist(
        eda_cron_context: cron_context.Context,
        mock_trust_get_product,
        app,
        expected_get_product_calls,
):
    runner = RUNNERS_BY_APP[app]
    await _test_already_exist(
        eda_cron_context,
        mock_trust_get_product,
        runner,
        expected_get_product_calls,
    )


@pytest.mark.parametrize(
    'app, expected_create_product_calls',
    [
        (
            'eda',
            [
                (
                    FOOD_PRODUCT,
                    [{'service': trust_settings.BILLING_SERVICE_EDA}],
                ),
                (
                    MEDS_PRODUCT,
                    [{'service': trust_settings.BILLING_SERVICE_EDA_PHARMACY}],
                ),
                (
                    FUEL_PRODUCT,
                    [{'service': trust_settings.BILLING_SERVICE_EDA_FUEL}],
                ),
                (
                    LAVKA_PRODUCT,
                    [
                        {
                            'service': (
                                trust_settings.BILLING_SERVICE_LAVKA_COURIER
                            ),
                        },
                        {
                            'service': (
                                getattr(
                                    trust_settings,
                                    'BILLING_SERVICE_LAVKA_COURIER_ACCEPT_QTY',
                                )
                            ),
                        },
                    ],
                ),
            ],
        ),
        (
            'lavka_isr',
            [
                (
                    LAVKA_ISR_PRODUCT,
                    [
                        {
                            'service': (
                                trust_settings.BILLING_SERVICE_LAVKA_DELIVERY
                            ),
                        },
                    ],
                ),
            ],
        ),
    ],
)
async def test_create(
        eda_cron_context: cron_context.Context,
        mockserver,
        mock_trust_get_product,
        app,
        expected_create_product_calls,
):
    runner = RUNNERS_BY_APP[app]
    partner_params = PARTNER_PARAMS_BY_APP[app]
    await _test_create(
        eda_cron_context,
        mockserver,
        mock_trust_get_product,
        runner,
        expected_create_product_calls,
        partner_params,
    )


async def _test_already_exist(
        eda_cron_context,
        mock_trust_get_product,
        runner,
        expected_get_product_calls,
):
    product_to_mock = {
        product: mock_trust_get_product(product, 'success')
        for product, _ in expected_get_product_calls
    }
    await runner.main(['transactions.crontasks.create_products', '-t', '0'])
    for product, expected_calls in expected_get_product_calls:
        mock = product_to_mock[product]
        assert mock.times_called == len(expected_calls)
        for expected_call in expected_calls:
            call = mock.next_call()
            _assert_service_token_equal(
                call, expected_call['service'], eda_cron_context,
            )
        assert not mock.has_calls


async def _test_create(
        eda_cron_context,
        mockserver,
        mock_trust_get_product,
        runner,
        expected_create_product_calls,
        partner_params,
):
    product_to_get_mock = {
        product: mock_trust_get_product(product, 'error')
        for product, _ in expected_create_product_calls
    }

    @mockserver.json_handler('/trust-payments/v2/partners/')
    def mock_trust_create_partner(request):
        assert request.json == partner_params
        return {'status': 'success', 'partner_id': 'testsuite-partner'}

    @mockserver.json_handler('/trust-payments/v2/products/')
    def mock_trust_create_product(request):
        product_id = request.json['product_id']
        expected_product_name = EXPECTED_PRODUCT_NAMES[product_id]
        expected_request = {
            'product_id': product_id,
            'partner_id': 'testsuite-partner',
            'name': expected_product_name,
        }
        if partner_params is None:
            del expected_request['partner_id']
        assert request.json == expected_request
        return {'status': 'success'}

    await runner.main(['transactions.crontasks.create_products', '-t', '0'])

    for product, expected_calls in expected_create_product_calls:
        get_mock = product_to_get_mock[product]
        assert get_mock.times_called == len(expected_calls)
        for expected_call in expected_calls:
            actual_call = get_mock.next_call()
            _assert_service_token_equal(
                actual_call, expected_call['service'], eda_cron_context,
            )
    if partner_params is None:
        assert mock_trust_create_partner.times_called == 0
    else:
        for product, expected_calls in expected_create_product_calls:
            for expected_call in expected_calls:
                actual_call = mock_trust_create_partner.next_call()
                _assert_service_token_equal(
                    actual_call, expected_call['service'], eda_cron_context,
                )
                assert actual_call
        assert not mock_trust_create_partner.has_calls
    for product, expected_calls in expected_create_product_calls:
        for expected_call in expected_calls:
            actual_call = mock_trust_create_product.next_call()
            _assert_service_token_equal(
                actual_call, expected_call['service'], eda_cron_context,
            )
            actual_product_id = actual_call['request'].json['product_id']
            assert actual_product_id == product
    assert not mock_trust_create_product.has_calls


def _assert_service_token_equal(trust_call, service_name, eda_cron_context):
    actual_service_token = trust_call['request'].headers['X-Service-Token']
    expected_service_token = _get_service_token(service_name, eda_cron_context)
    assert actual_service_token == expected_service_token


def _get_service_token(service_name, eda_cron_context):
    key_name = trust_settings.BILLING_API_KEY
    service_tokens = (
        eda_cron_context.config.TRANSACTIONS_BILLING_SERVICE_TOKENS
    )
    service_settings = service_tokens.get(service_name)

    return service_settings[key_name]
