import pytest

from tests_eats_payments import consts
from tests_eats_payments import helpers

URL = 'v1/orders/retrieve'

BASE_REQUEST = {'id': 'test_order'}
TEST_RESPONSE_TYPE = 'retrieve_order_response'

BASE_RESPONSE = {
    'cleared': [],
    'currency': 'RUB',
    'debt': [],
    'held': [],
    'id': 'test_order',
    'payment_types': ['card'],
    'payments': [
        {
            'cleared': '2020-08-14T14:49:49.641+00:00',
            'created': '2020-08-14T14:39:50.265+00:00',
            'external_payment_id': 'c964a582b3b4b3dcd514ab1914a7d2a8',
            'held': '2020-08-14T14:40:01.053+00:00',
            'payment_method_id': '123',
            'payment_type': 'card',
            'status': 'clear_success',
            'sum': [{'amount': '5.00', 'item_id': 'big_mac'}],
            'updated': '2020-08-14T14:40:01.053+00:00',
            'terminal_id': '57000176',
        },
    ],
    'status': 'held',
    'sum_to_pay': [],
    'type': TEST_RESPONSE_TYPE,
    'version': 2,
    'yandex_uid': '25211664',
}


@pytest.fixture(name='check_retrieve_order')
def check_retrieve_order_fixture(taxi_eats_payments, mockserver, load_json):
    async def _inner(response_status=200, response_body=None):
        response = await taxi_eats_payments.post(
            URL, json=BASE_REQUEST, headers=consts.BASE_HEADERS,
        )
        assert response.status == response_status
        if response_body is not None:
            assert response.json() == response_body

    return _inner


@pytest.mark.parametrize('payment_type', consts.PAYMENT_TYPES)
async def test_payment_type(
        check_retrieve_order, mock_retrieve_invoice_retrieve, payment_type,
):
    invoice_retrieve_mock = mock_retrieve_invoice_retrieve(
        payment_types=[payment_type],
    )
    response_body = {**BASE_RESPONSE, **{'payment_types': [payment_type]}}
    await check_retrieve_order(response_body=response_body)

    assert invoice_retrieve_mock.times_called == 1


@pytest.mark.parametrize('key', ['sum_to_pay', 'held', 'cleared', 'debt'])
async def test_items(
        check_retrieve_order, mock_retrieve_invoice_retrieve, key,
):
    extra = {
        key: [
            helpers.make_transactions_payment_items(
                payment_type='card',
                items=[
                    helpers.make_transactions_item(
                        item_id='big_mac', amount='2.00',
                    ),
                ],
            ),
        ],
    }
    invoice_retrieve_mock = mock_retrieve_invoice_retrieve(**extra)
    response_body = {**BASE_RESPONSE, **extra}
    await check_retrieve_order(response_body=response_body)

    assert invoice_retrieve_mock.times_called == 1


async def test_no_version_in_invoice(
        check_retrieve_order, mock_retrieve_invoice_retrieve,
):
    invoice_retrieve_mock = mock_retrieve_invoice_retrieve(operation_info={})
    await check_retrieve_order(response_status=500)

    assert invoice_retrieve_mock.times_called == 1


@pytest.mark.parametrize(
    ('invoice_retrieve_response,' 'response_status,' 'response_body'),
    [
        (
            {
                'status': 404,
                'json': {'code': 'not-found', 'message': 'invoice not found'},
            },
            404,
            {
                'code': 'not-found',
                'message': (
                    'Transactions error while retrieving invoice. '
                    'Error: `invoice not found`'
                ),
            },
        ),
        (
            {
                'status': 500,
                'json': {
                    'code': 'internal-server-error',
                    'message': 'exception',
                },
            },
            500,
            None,
        ),
    ],
)
async def test_retrieve_invoice_errors(
        check_retrieve_order,
        mock_retrieve_invoice_retrieve,
        invoice_retrieve_response,
        response_status,
        response_body,
):
    invoice_retrieve_mock = mock_retrieve_invoice_retrieve(
        invoice_retrieve_response=invoice_retrieve_response,
    )

    await check_retrieve_order(
        response_status=response_status, response_body=response_body,
    )

    assert invoice_retrieve_mock.times_called == 1


@pytest.mark.parametrize(
    ('operation_type', 'invoice_status'),
    [
        ('create', 'init'),
        ('update', 'init'),
        ('cancel', 'cleared'),
        ('close', 'cleared'),
    ],
)
async def test_retrieve_cash(
        upsert_order,
        upsert_order_payment,
        insert_operation,
        taxi_eats_payments,
        experiments3,
        operation_type,
        invoice_status,
):
    order_id = 'test_order'
    payment_type = consts.CASH_PAYMENT_TYPE
    payment_method_id = 'cash_test_id'
    previous_revision = 'ab'
    currency = 'RUB'

    experiments3.add_config(**helpers.make_operations_config())

    upsert_order(order_id=order_id, api_version=2)
    upsert_order_payment(
        order_id=order_id,
        payment_id=payment_method_id,
        payment_type=payment_type,
        currency=currency,
    )
    insert_operation(
        order_id=order_id,
        revision=previous_revision,
        prev_revision=previous_revision,
        op_type=operation_type,
        status='done',
        fails_count=0,
    )

    response = await taxi_eats_payments.post(URL, json={'id': order_id})
    assert response.status == 200
    assert response.json() == {
        'id': order_id,
        'currency': currency,
        'status': invoice_status,
        'payment_types': ['cash'],
        'version': 1,
        'type': 'retrieve_order_response',
        'sum_to_pay': [],
        'held': [],
        'cleared': [],
        'debt': [],
        'yandex_uid': '',
        'payments': [],
    }
