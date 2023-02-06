import pytest

from tests_eats_payments import consts
from tests_eats_payments import helpers

URL = 'v1/orders/close'

NOW = '2020-08-12T07:20:00+00:00'

BASE_BODY = {'id': 'test_order'}


@pytest.mark.now(NOW)
async def test_ok(
        upsert_order,
        taxi_eats_payments,
        mockserver,
        mock_retrieve_invoice_retrieve,
):
    invoice_close_request_body = {**BASE_BODY, **{'clear_eta': NOW}}
    response_status = 200
    response_body = {}

    @mockserver.json_handler('/transactions-eda/invoice/clear')
    def _transactions_close_invoice_handler(request):
        assert request.json == invoice_close_request_body
        return mockserver.make_response(**{'status': 200, 'json': {}})

    extra = {'personal_phone_id': '123456'}

    mock_retrieve_invoice_retrieve(**extra)

    upsert_order('test_order')

    body = BASE_BODY
    headers = consts.BASE_HEADERS
    response = await taxi_eats_payments.post(URL, json=body, headers=headers)
    assert response.status == response_status
    assert response.json() == response_body
    assert _transactions_close_invoice_handler.times_called == 1


@pytest.mark.now(NOW)
async def test_ok_with_operation(
        upsert_order,
        taxi_eats_payments,
        mockserver,
        mock_retrieve_invoice_retrieve,
        mock_order_revision_list,
        experiments3,
        fetch_operation,
):
    experiments3.add_config(**helpers.make_operations_config())

    invoice_close_request_body = {**BASE_BODY, **{'clear_eta': NOW}}
    response_status = 200
    response_body = {}

    @mockserver.json_handler('/transactions-eda/invoice/clear')
    def _transactions_close_invoice_handler(request):
        assert request.json == invoice_close_request_body
        return mockserver.make_response(**{'status': 200, 'json': {}})

    mock_order_revision_list()

    extra = {'personal_phone_id': '123456'}

    mock_retrieve_invoice_retrieve(**extra)

    upsert_order('test_order', api_version=2)

    body = BASE_BODY
    headers = consts.BASE_HEADERS
    response = await taxi_eats_payments.post(URL, json=body, headers=headers)

    fetch_operation('test_order', 'abcd')

    assert response.status == response_status
    assert response.json() == response_body
    assert _transactions_close_invoice_handler.times_called == 1


@pytest.mark.now(NOW)
@pytest.mark.parametrize('is_need_new_revision_service', [True, False])
async def test_spb_ok_with_operations(
        upsert_order,
        upsert_order_payment,
        taxi_eats_payments,
        mockserver,
        mock_retrieve_invoice_retrieve,
        mock_order_revision_list,
        experiments3,
        fetch_operation,
        stq,
        mock_order_revision_customer_services_details,
        is_need_new_revision_service,
):
    experiments3.add_config(**helpers.make_operations_config())
    experiments3.add_config(
        **helpers.make_eats_payments_receipts_operations_switch_experiment(
            True,
        ),
    )
    experiments3.add_experiment(
        **helpers.make_new_service_revision(is_need_new_revision_service),
    )
    invoice_close_request_body = {**BASE_BODY, **{'clear_eta': NOW}}
    response_status = 200
    response_body = {}

    @mockserver.json_handler('/transactions-eda/invoice/clear')
    def _transactions_close_invoice_handler(request):
        assert request.json == invoice_close_request_body
        return mockserver.make_response(**{'status': 200, 'json': {}})

    mock_order_revision_list()
    customer_services = [
        helpers.make_customer_service(
            customer_service_id='composition-products',
            name='big_mac',
            cost_for_customer='10.00',
            currency='RUB',
            customer_service_type='composition_products',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
            balance_client_id='123456789',
            details=helpers.make_customer_service_details(
                composition_products=[
                    helpers.make_composition_product(
                        composition_product_id='product-1',
                        name='Product 1',
                        cost_for_customer='5.00',
                        composition_product_type='product',
                    ),
                ],
            ),
        ),
    ]
    mock_order_revision_customer_services_details(
        customer_services=customer_services,
    )
    extra = {'personal_phone_id': '123456'}

    mock_retrieve_invoice_retrieve(**extra)

    upsert_order('test_order', api_version=2)
    upsert_order_payment('test_order', 'postpayment', 'sbp', 'RUB')

    body = BASE_BODY
    headers = consts.BASE_HEADERS
    response = await taxi_eats_payments.post(URL, json=body, headers=headers)

    fetch_operation('test_order', 'abcd')
    assert response.status == response_status
    assert response.json() == response_body
    assert _transactions_close_invoice_handler.times_called == 1
    assert stq.eats_send_receipts_requests.times_called == 1


async def test_close_cash(
        upsert_order,
        upsert_order_payment,
        insert_operation,
        taxi_eats_payments,
        experiments3,
        fetch_operation,
):
    order_id = 'test_order'
    payment_type = consts.CASH_PAYMENT_TYPE
    payment_method_id = 'cash_test_id'
    previous_revision = 'ab'

    experiments3.add_config(**helpers.make_operations_config())

    upsert_order(order_id=order_id, api_version=2)
    upsert_order_payment(
        order_id=order_id,
        payment_id=payment_method_id,
        payment_type=payment_type,
    )
    insert_operation(
        order_id=order_id,
        revision=previous_revision,
        prev_revision=previous_revision,
        op_type='create',
        status='done',
        fails_count=0,
    )

    response = await taxi_eats_payments.post(URL, json={'id': order_id})
    assert response.status == 200
    assert response.json() == {}

    fetch_operation(order_id, revision='null', prev_revision='null')


@pytest.mark.parametrize(
    ('invoice_close_response,' 'response_status,' 'response_body'),
    [
        (
            {
                'status': 400,
                'json': {
                    'code': 'bad-request',
                    'message': 'something wrong was sent',
                },
            },
            400,
            {
                'code': 'bad-request',
                'message': (
                    'Transactions error while clearing invoice. '
                    'Error: `something wrong was sent`'
                ),
            },
        ),
        (
            {'status': 404, 'json': {}},
            404,
            {
                'code': 'invoice-not-found',
                'message': (
                    'Transactions error while clearing invoice. '
                    'Error: `invoice not found`'
                ),
            },
        ),
        (
            {
                'status': 409,
                'json': {'code': 'conflict', 'message': 'conflict happened'},
            },
            409,
            {
                'code': 'conflict',
                'message': (
                    'Transactions error while clearing invoice. '
                    'Error: `conflict happened`'
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
            {
                'code': 'unknown-error',
                'message': (
                    'Transactions error while clearing invoice. '
                    'Error: `Unexpected HTTP response code '
                    '\'500\' for \'POST /invoice/clear\'`'
                ),
            },
        ),
    ],
)
async def test_errors(
        upsert_order,
        taxi_eats_payments,
        mockserver,
        mock_retrieve_invoice_retrieve,
        invoice_close_response,
        response_status,
        response_body,
):
    @mockserver.json_handler('/transactions-eda/invoice/clear')
    def _transactions_close_invoice_handler(request):
        return mockserver.make_response(**invoice_close_response)

    extra = {'personal_phone_id': '123456'}

    mock_retrieve_invoice_retrieve(**extra)

    upsert_order('test_order')

    body = BASE_BODY
    headers = consts.BASE_HEADERS
    response = await taxi_eats_payments.post(URL, json=body, headers=headers)
    assert response.status == response_status
    assert response.json() == response_body
    assert _transactions_close_invoice_handler.times_called == 1


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    ('sum_to_pay', 'held', 'invoice_update_expected_times_called'),
    [
        (
            [helpers.make_transactions_item(item_id='big_mac', amount='2.00')],
            [helpers.make_transactions_item(item_id='big_mac', amount='3.00')],
            1,
        ),
        (
            [helpers.make_transactions_item(item_id='big_mac', amount='2.00')],
            [helpers.make_transactions_item(item_id='big_mac', amount='2.00')],
            0,
        ),
        (
            [helpers.make_transactions_item(item_id='big_mac', amount='2.00')],
            [helpers.make_transactions_item(item_id='big_mac', amount='2.10')],
            0,
        ),
    ],
)
async def test_hold_unhold(
        taxi_eats_payments,
        mockserver,
        upsert_order,
        upsert_order_payment,
        experiments3,
        mock_cardstorage,
        mock_order_revision_list,
        mock_retrieve_invoice_retrieve,
        mock_transactions_invoice_update,
        sum_to_pay,
        held,
        invoice_update_expected_times_called,
        mock_eats_debt_user_scoring_verdict,
):
    upsert_order(
        'test_order',
        api_version=2,
        business_type='restaurant',
        business_specification='{}',
    )
    upsert_order_payment(
        'test_order', 'card-x5a699b31f78dba7d27c4f7ab', 'card', 'RUB',
    )
    experiments3.add_experiment(**helpers.make_hold_unhold_experiment())

    cardstorage_mock = mock_cardstorage()

    mock_order_revision_list(revisions=[{'revision_id': '12345'}])

    extra = {
        'transactions': [
            helpers.make_transaction(
                **{'initial_sum': held, 'sum': sum_to_pay},
            ),
        ],
        'personal_phone_id': '123456',
    }

    invoice_retrieve_mock = mock_retrieve_invoice_retrieve(**extra)

    invoice_update_mock = mock_transactions_invoice_update(
        operation_id='update:unhold:test_order:12345',
    )

    invoice_close_request_body = {**BASE_BODY, **{'clear_eta': NOW}}

    @mockserver.json_handler('/transactions-eda/invoice/clear')
    def _transactions_clear_invoice_handler(request):
        assert request.json == invoice_close_request_body
        return mockserver.make_response(**{'status': 200, 'json': {}})

    mock_eats_debt_user_scoring_verdict(verdict='accept')

    response = await taxi_eats_payments.post(
        URL, json=BASE_BODY, headers=consts.BASE_HEADERS,
    )
    assert invoice_retrieve_mock.times_called == 1
    assert (
        invoice_update_mock.times_called
        == invoice_update_expected_times_called
    )
    assert cardstorage_mock.times_called == 2
    assert response.status == 200
    assert response.json() == {}
