import json

import pytest

OPERATION_ID = 'create:100500'
REFUND_OPERATION_ID = 'refund:13022-1234'
PERSONAL_WALLET_TYPE = 'personal_wallet'
NOW = '2020-03-31T07:20:00+00:00'
PERSONAL_TIN_ID = '477782c29a004ca98314ee2505833755'


@pytest.fixture(name='mock_transactions_invoice_retrieve')
def _mock_transactions_invoice_retrieve(mockserver, load_json, request):
    order_id = None
    if isinstance(request.param, list):
        response = load_json(request.param[0])
        order_id = request.param[1]
    else:
        response = load_json(request.param)

    @mockserver.json_handler('/transactions-eda/v2/invoice/retrieve')
    def _transactions_invoice_retrieve(request):
        if order_id is not None:
            assert order_id == request.json['id']
        return mockserver.make_response(json.dumps(response), 200)


def make_order(order_nr='test_order'):
    return {
        'country_code': 'RU',
        'order_nr': order_nr,
        'payment_method': 'card',
    }


def make_user_info():
    return {'personal_email_id': 'mail_id', 'personal_phone_id': 'phone_id'}


URL = '/v1/receipts/retrieve'


@pytest.mark.pgsql('eats_simple_payments', files=['insert_order_info.sql'])
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    ['document_id', 'expected_status'],
    [
        pytest.param('test_order/products//', 200, id='200'),
        pytest.param('220531-062886/error//', 404, id='404'),
    ],
)
@pytest.mark.parametrize(
    'mock_transactions_invoice_retrieve',
    ['transaction_client_response.json'],
    indirect=True,
)
async def test_just_test(
        document_id,
        expected_status,
        taxi_eats_simple_payments,
        mock_transactions_invoice_retrieve,
        insert_items,
):
    response = await taxi_eats_simple_payments.post(
        URL, json={'document_id': document_id},
    )
    assert response.status == expected_status


@pytest.mark.parametrize(
    ['document_id', 'expected_status'],
    [pytest.param('220531-062886/delivery//', 403, id='403')],
)
@pytest.mark.parametrize(
    'mock_transactions_invoice_retrieve',
    ['case_invoice_with_corp_primary_method.json'],
    indirect=True,
)
async def test_bad_403_endpoint(
        document_id,
        expected_status,
        taxi_eats_simple_payments,
        mock_transactions_invoice_retrieve,
):
    response = await taxi_eats_simple_payments.post(
        URL, json={'document_id': document_id},
    )
    assert response.status == expected_status


@pytest.mark.parametrize(
    ['document_id', 'expected_status'],
    [pytest.param('220531-062886/delivery//', 500, id='500')],
)
@pytest.mark.parametrize(
    'mock_transactions_invoice_bad_retrieve', [500], indirect=True,
)
async def test_bad_500_endpoints(
        document_id,
        expected_status,
        taxi_eats_simple_payments,
        mock_transactions_invoice_bad_retrieve,
):
    response = await taxi_eats_simple_payments.post(
        URL, json={'document_id': document_id},
    )
    assert response.status == expected_status


@pytest.mark.parametrize(
    ['document_id', 'expected_status'],
    [pytest.param('220531-062886/delivery//', 404, id='404')],
)
@pytest.mark.parametrize(
    'mock_transactions_invoice_bad_retrieve', [404], indirect=True,
)
async def test_bad_404_endpoint(
        document_id,
        expected_status,
        taxi_eats_simple_payments,
        mock_transactions_invoice_bad_retrieve,
):
    response = await taxi_eats_simple_payments.post(
        URL, json={'document_id': document_id},
    )
    assert response.status == expected_status
    assert response.json() == {'code': '404', 'message': 'error message'}


@pytest.mark.pgsql('eats_simple_payments', files=['insert_order_info.sql'])
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'mock_transactions_invoice_retrieve',
    ['transaction_client_refund_response.json'],
    indirect=True,
)
async def test_handle_retrieve_refund_receipt_return_inn(
        taxi_eats_simple_payments, mock_transactions_invoice_retrieve,
):
    response = await taxi_eats_simple_payments.post(
        URL,
        json={
            'document_id': (
                'test_order/products/refund/' + REFUND_OPERATION_ID
            ),
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'is_refund': True,
        'order': make_order(),
        'products': [
            {
                'id': 'pizza_1',
                'parent': None,
                'price': '340.99',
                'supplier_inn': '',
                'supplier_inn_id': '477782c29a004ca98314ee2505833755',
                'tax': '-1',
                'title': 'Pepperoni (33 cm)',
            },
        ],
        'user_info': make_user_info(),
    }


@pytest.mark.pgsql('eats_simple_payments', files=['insert_order_info.sql'])
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'mock_transactions_invoice_retrieve',
    ['transaction_client_refund_response.json'],
    indirect=True,
)
async def test_handle_retrieve_refund_receipt(
        taxi_eats_simple_payments, mock_transactions_invoice_retrieve,
):
    response = await taxi_eats_simple_payments.post(
        URL,
        json={
            'document_id': (
                'test_order/products/refund/' + REFUND_OPERATION_ID
            ),
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'is_refund': True,
        'order': make_order(),
        'products': [
            {
                'id': 'pizza_1',
                'parent': None,
                'price': '340.99',
                'supplier_inn': '',
                'supplier_inn_id': PERSONAL_TIN_ID,
                'tax': '-1',
                'title': 'Pepperoni (33 cm)',
            },
        ],
        'user_info': make_user_info(),
    }


@pytest.mark.pgsql('eats_simple_payments', files=['insert_order_info.sql'])
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'mock_transactions_invoice_retrieve',
    ['transaction_client_refund_service_fee_response.json'],
    indirect=True,
)
async def test_handle_retrieve_refund_service_fee_receipt(
        taxi_eats_simple_payments, mock_transactions_invoice_retrieve,
):
    response = await taxi_eats_simple_payments.post(
        URL,
        json={
            'document_id': (
                'test_order/service_fee/refund/' + REFUND_OPERATION_ID
            ),
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'is_refund': True,
        'order': make_order(),
        'products': [
            {
                'id': 'service-fee',
                'parent': None,
                'price': '9.00',
                'supplier_inn': '',
                'supplier_inn_id': PERSONAL_TIN_ID,
                'tax': '20',
                'title': 'Сервисный сбор',
            },
        ],
        'user_info': make_user_info(),
    }


@pytest.mark.pgsql('eats_simple_payments', files=['insert_order_info.sql'])
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'mock_transactions_invoice_retrieve',
    ['transaction_client_refund_double_payment_response.json'],
    indirect=True,
)
async def test_handle_retrieve_refund_double_payment_receipt(
        taxi_eats_simple_payments, mock_transactions_invoice_retrieve,
):
    response = await taxi_eats_simple_payments.post(
        URL,
        json={
            'document_id': (
                'test_order_cashback/products/refund/' + REFUND_OPERATION_ID
            ),
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'is_refund': True,
        'order': make_order('test_order_cashback'),
        'products': [
            {
                'id': 'pizza_1',
                'parent': None,
                'price': '100',
                'supplier_inn': '',
                'supplier_inn_id': PERSONAL_TIN_ID,
                'tax': '-1',
                'title': 'Pepperoni (33 cm)',
            },
        ],
        'user_info': make_user_info(),
    }


@pytest.mark.pgsql('eats_simple_payments', files=['insert_order_info.sql'])
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'mock_transactions_invoice_retrieve',
    [['transaction_client_response.json', 'test_order']],
    indirect=True,
)
async def test_handle_retrieve_receipt(
        taxi_eats_simple_payments,
        mock_transactions_invoice_retrieve,
        insert_items,
):
    response = await taxi_eats_simple_payments.post(
        URL, json={'document_id': 'test_order/products//'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'is_refund': False,
        'order': make_order(),
        'products': [
            {
                'id': 'test-1',
                'parent': None,
                'price': '100.00',
                'supplier_inn': '',
                'supplier_inn_id': PERSONAL_TIN_ID,
                'tax': '-1',
                'title': 'test-1',
            },
            {
                'id': 'test-2',
                'parent': None,
                'price': '349.99',
                'supplier_inn': '',
                'supplier_inn_id': PERSONAL_TIN_ID,
                'tax': '-1',
                'title': 'test-2',
            },
        ],
        'user_info': make_user_info(),
    }


@pytest.mark.pgsql('eats_simple_payments', files=['insert_order_info.sql'])
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'mock_transactions_invoice_retrieve',
    ['transaction_client_retail_double.json'],
    indirect=True,
)
async def test_handle_personal_wallet_retail(
        taxi_eats_simple_payments,
        mock_transactions_invoice_retrieve,
        insert_items,
):
    response = await taxi_eats_simple_payments.post(
        URL,
        json={
            'document_id': (
                'test_order_cashback/products/not_refund/' + OPERATION_ID
            ),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'is_refund': False,
        'order': make_order(order_nr='test_order_cashback'),
        'products': [
            {
                'id': 'retail-product',
                'parent': None,
                'price': '374.00',
                'supplier_inn': '',
                'supplier_inn_id': PERSONAL_TIN_ID,
                'tax': '-1',
                'title': 'Расходы на исполнение поручений по заказу',
            },
        ],
        'user_info': make_user_info(),
    }


@pytest.mark.pgsql('eats_simple_payments', files=['insert_order_info.sql'])
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'mock_transactions_invoice_retrieve',
    ['transaction_client_retail_double.json'],
    indirect=True,
)
async def test_handle_for_orders_without_revision(
        taxi_eats_simple_payments,
        mock_transactions_invoice_retrieve,
        mockserver,
        insert_items,
):
    response = await taxi_eats_simple_payments.post(
        URL, json={'document_id': 'test_order_cashback/products//'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'is_refund': False,
        'order': make_order(order_nr='test_order_cashback'),
        'products': [
            {
                'id': 'retail-product',
                'parent': None,
                'price': '374.00',
                'supplier_inn': '',
                'supplier_inn_id': PERSONAL_TIN_ID,
                'tax': '-1',
                'title': 'Расходы на исполнение поручений по заказу',
            },
        ],
        'user_info': make_user_info(),
    }


@pytest.mark.pgsql('eats_simple_payments', files=['insert_order_info.sql'])
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'mock_transactions_invoice_retrieve',
    ['transaction_client_refund_response_v1.json'],
    indirect=True,
)
async def test_handle_refund_without_revision(
        taxi_eats_simple_payments,
        mock_transactions_invoice_retrieve,
        mockserver,
        insert_items,
):
    response = await taxi_eats_simple_payments.post(
        URL,
        json={
            'document_id': (
                'test_order_cashback/products/refund/refund:13022-1234'
            ),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'is_refund': True,
        'order': make_order(order_nr='test_order_cashback'),
        'products': [
            {
                'id': 'salad-1',
                'parent': None,
                'price': '340.99',
                'supplier_inn': '',
                'supplier_inn_id': PERSONAL_TIN_ID,
                'tax': '-1',
                'title': 'Салат-1',
            },
        ],
        'user_info': make_user_info(),
    }
