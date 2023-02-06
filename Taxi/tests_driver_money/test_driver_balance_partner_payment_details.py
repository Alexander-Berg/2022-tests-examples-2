import pytest


HEADERS = {
    'User-Agent': 'Taximeter 9.20 (1234)',
    'Accept-Language': 'ru',
    'X-Driver-Session': 'driver_session',
    'X-Request-Application-Version': '9.20',
    'X-YaTaxi-Park-Id': 'park_id_0',
    'X-YaTaxi-Driver-Profile-Id': 'driver',
}
PARAMS = {'park_id': 'park_id_0'}
URL = 'driver/balance/partner-payment-details'

PP_DETAILS_HEADER = (
    'TRUST_REFUND_ID\t'
    'TRUST_PAYMENT_ID\t'
    'SERVICE_ORDER_ID\t'
    'SUM\t'
    'CURRENCY\t'
    'PAYMENT_TYPE\t'
    'TRANSACTION_TYPE\t'
    'HANDLINGTIME\t'
    'PAYMENTTIME\t'
    'CONTRACT_ID\t'
    'PAYLOAD\t'
    'YANDEX_REWARD\n'
)

PAY_1 = (
    '\t'
    'pay1\t'
    'order1\t'
    '153\t'
    'RUR\t'
    'card\t'
    'payment\t'
    '20190510090010\t'
    '20190510110010\t'
    '664441\t'
    '\t'
    '0\n'
)

PAY_2 = (
    '\t'
    'pay2\t'
    'order2\t'
    '217\t'
    'RUR\t'
    'card\t'
    'payment\t'
    '20190510100010\t'
    '20190510110010\t'
    '664441\t'
    '\t'
    '0\n'
)

PAY_3 = (
    'refund1\t'
    '\t'
    '\t'
    '175\t'
    'RUR\t'
    'correction_commission\t'
    'refund\t'
    '20190511110010\t'
    '20190511120010\t'
    '664441\t'
    '\t'
    '0\n'
)

PAY_4 = (
    'refund2\t'
    '\t'
    'order2\t'
    '17\t'
    'RUR\t'
    'flskjdhflskdjg\t'
    'refund\t'
    '20190512170010\t'
    '20190512190010\t'
    '664441\t'
    '\t'
    '0\n'
)

PAY_5 = (
    '\t'
    '\t'
    'order1\t'
    '31\t'
    'RUR\t'
    'tips\t'
    'payment\t'
    '20190512220010\t'
    '20190512230710\t'
    '664441\t'
    '\t'
    '0\n'
)

PP_DETAILS = PP_DETAILS_HEADER + PAY_1 + PAY_2 + PAY_3 + PAY_4 + PAY_5


async def test_pp_details(
        taxi_driver_money,
        driver_authorizer,
        driver_orders,
        mockserver,
        load_json,
        load,
):
    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')

    @mockserver.json_handler('/billing_payments/get_payment_batch_details')
    def _pp_list(request):
        return mockserver.make_response(PP_DETAILS, status=200)

    response = await taxi_driver_money.post(
        URL,
        headers=HEADERS,
        params=PARAMS,
        json={'payment_batch_id': '10', 'date': '2019-06-05T12:00:00.000Z'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('pp_details_screen_old.json')


@pytest.mark.parametrize(
    'expected_payments, expected_response',
    [
        ('new_payments.json', 'pp_details_screen_new.json'),
        (
            'new_payments_no_orders.json',
            'pp_details_screen_new_no_orders.json',
        ),
    ],
)
async def test_pp_new_details(
        taxi_driver_money,
        driver_authorizer,
        driver_orders,
        mockserver,
        expected_payments,
        expected_response,
        load_json,
        load,
):
    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/details')
    def _pp_list(request):
        if 'cursor' in request.json:
            return {'payment_id': 'xxx', 'transactions': [], 'cursor': ''}

        return mockserver.make_response(load(expected_payments), status=200)

    response = await taxi_driver_money.post(
        URL,
        headers=HEADERS,
        params=PARAMS,
        json={
            'payment_batch_id': 'payment_id||10',
            'date': '2020-04-22T23:57:00.00Z',
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


async def test_pp_new_details_no_transactions(
        taxi_driver_money,
        driver_authorizer,
        driver_orders,
        mockserver,
        load_json,
):
    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/details')
    def _pp_list(request):
        return {'payment_id': 'xxx', 'transactions': [], 'cursor': ''}

    response = await taxi_driver_money.post(
        URL,
        headers=HEADERS,
        params=PARAMS,
        json={
            'payment_batch_id': 'payment_id||10',
            'date': '2020-04-22T23:57:00.00Z',
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'pp_details_screen_new_no_transactions.json',
    )


@pytest.mark.parametrize(
    'status_code,is_response_with_msg', [(429, False), (429, True)],
)
async def test_pp_new_details_billing_429(
        taxi_driver_money,
        driver_authorizer,
        driver_orders,
        mockserver,
        status_code,
        is_response_with_msg,
        load_json,
):
    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')

    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/details')
    def _pp_list(request):
        if is_response_with_msg:
            return mockserver.make_response('Too many requests', status=429)
        return mockserver.make_response(status=429)

    response = await taxi_driver_money.post(
        URL,
        headers=HEADERS,
        params=PARAMS,
        json={
            'payment_batch_id': 'payment_id||10',
            'date': '2020-04-22T23:57:00.00Z',
        },
    )
    assert response.status_code == status_code
