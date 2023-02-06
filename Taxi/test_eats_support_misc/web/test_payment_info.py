import pytest


ORDER_NR = '123456-123456'
MAX_ATTEMPTS = 3

EATS_PICKER_ORDERS_URL = '/eats-picker-orders/api/v1/order/payments'

EATS_PICKER_ORDERS_RESPONSE_200 = {
    'receipt_loaded': False,
    'pickedup_total': '10000',
    'payment_limit': '15000',
    'current_limit': '5000',
    'spent': '10000',
}

EATS_PICKER_ORDERS_RESPONSE_NOT_SPENT = {
    'receipt_loaded': False,
    'pickedup_total': '10000',
    'payment_limit': '15000',
}

EATS_PICKER_ORDERS_RESPONSE_401 = {
    'errors': [{'code': 401, 'description': 'Authorization failed'}],
}
EATS_PICKER_ORDERS_RESPONSE_404 = {
    'errors': [{'code': 404, 'description': 'Order not found'}],
}
EATS_PICKER_ORDERS_RESPONSE_500 = {
    'errors': [{'code': 500, 'description': 'Internal server error'}],
}
EATS_PICKER_ORDERS_RESPONSE_503 = {
    'code': 'db_timeout',
    'message': 'DB timeout',
}

EXPECTED_RESPONSE_RU = {'spent_text': 'Списанная сумма денег: 10000'}
EXPECTED_RESPONSE_EN = {'spent_text': 'Money spent: 10000'}

EXPECTED_CORNER_RESPONSE_RU = {'spent_text': 'Деньги пока не списаны'}
EXPECTED_CORNER_RESPONSE_EN = {'spent_text': 'Money not spent yet'}

TRANSLATIONS = {
    'money_spent.text': {
        'ru': 'Списанная сумма денег: %(money_spent)s',
        'en': 'Money spent: %(money_spent)s',
    },
    'money_not_spent.text': {
        'ru': 'Деньги пока не списаны',
        'en': 'Money not spent yet',
    },
}


@pytest.mark.now('2020-04-28T12:10:00+03:00')
@pytest.mark.translations(eats_support_misc=TRANSLATIONS)
@pytest.mark.pgsql('eats_support_misc', files=['init_meta.sql'])
async def test_green_flow(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
):
    @mockserver.json_handler(EATS_PICKER_ORDERS_URL)
    async def _handler(request):
        return mockserver.make_response(
            status=200, json=EATS_PICKER_ORDERS_RESPONSE_200,
        )

    response = await taxi_eats_support_misc_web.get(
        '/v1/payment-info', params={'order_nr': ORDER_NR},
    )

    assert response.status == 200
    data = await response.json()
    assert data == EXPECTED_RESPONSE_RU


@pytest.mark.now('2020-04-28T12:10:00+03:00')
@pytest.mark.config(
    EATS_PICKER_ORDERS_CLIENT_QOS={
        '/api/v1/order/payments': {
            'attempts': MAX_ATTEMPTS,
            'timeout-ms': 200,
        },
        '__default__': {'attempts': 1, 'timeout-ms': 200},
    },
)
@pytest.mark.translations(eats_support_misc=TRANSLATIONS)
@pytest.mark.pgsql('eats_support_misc', files=['init_meta.sql'])
@pytest.mark.parametrize(
    """picker_orders_code, picker_orders_response""",
    [
        (401, EATS_PICKER_ORDERS_RESPONSE_401),
        (404, EATS_PICKER_ORDERS_RESPONSE_404),
        (500, EATS_PICKER_ORDERS_RESPONSE_500),
        (503, EATS_PICKER_ORDERS_RESPONSE_503),
    ],
)
async def test_error_picker_orders(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        picker_orders_code,
        picker_orders_response,
):
    @mockserver.json_handler(EATS_PICKER_ORDERS_URL)
    async def _handler(request):
        return mockserver.make_response(
            status=picker_orders_code, json=picker_orders_response,
        )

    response = await taxi_eats_support_misc_web.get(
        '/v1/payment-info', params={'order_nr': ORDER_NR},
    )

    assert response.status == 404
    if picker_orders_code in [401, 404]:
        assert _handler.times_called == 1
    elif picker_orders_code in [500, 503]:
        assert _handler.times_called == MAX_ATTEMPTS


@pytest.mark.now('2020-04-28T12:10:00+03:00')
@pytest.mark.translations(eats_support_misc=TRANSLATIONS)
@pytest.mark.pgsql('eats_support_misc', files=['init_meta.sql'])
@pytest.mark.parametrize(
    """spent_present,language,expected_response""",
    [
        (True, 'ru', EXPECTED_RESPONSE_RU),
        (True, 'en', EXPECTED_RESPONSE_EN),
        (False, 'ru', EXPECTED_CORNER_RESPONSE_RU),
        (False, 'en', EXPECTED_CORNER_RESPONSE_EN),
    ],
)
async def test_translations_and_not_spent(
        # ---- fixtures ----
        mockserver,
        taxi_eats_support_misc_web,
        # ---- parameters ----
        spent_present,
        language,
        expected_response,
):
    @mockserver.json_handler(EATS_PICKER_ORDERS_URL)
    async def _handler(request):
        return mockserver.make_response(
            status=200,
            json=(
                EATS_PICKER_ORDERS_RESPONSE_200
                if spent_present
                else EATS_PICKER_ORDERS_RESPONSE_NOT_SPENT
            ),
        )

    response = await taxi_eats_support_misc_web.get(
        '/v1/payment-info',
        params={'order_nr': ORDER_NR},
        headers={'Accept-Language': language},
    )

    assert response.status == 200
    data = await response.json()
    assert data == expected_response
