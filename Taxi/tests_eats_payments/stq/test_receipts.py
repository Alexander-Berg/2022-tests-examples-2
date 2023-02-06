# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
# pylint: disable=too-many-lines
from metrics_aggregations import helpers as metrics_helpers
import pytest

from tests_eats_payments import consts
from tests_eats_payments import db_order
from tests_eats_payments import helpers


@pytest.fixture(autouse=True)
def _feature_flag_setter(taxi_config):
    taxi_config.set_values(
        {
            'EATS_PAYMENTS_FEATURE_FLAGS': {
                'response_with_inn_id_instead_of_inn': {
                    'description': '',
                    'enabled': True,
                },
            },
        },
    )


def _get_refund_transaction(
        operation_id: str,
        external_payment_id=None,
        payment_type: str = 'card',
        item_id: str = 'big_mac',
):
    refund_data = helpers.make_refund(
        refund_sum=[
            helpers.make_transactions_item(
                item_id=item_id,
                amount='1.00',
                fiscal_receipt_info={
                    'personal_tin_id': 'personal-tin-id',
                    'title': 'Big Mac Burger',
                    'vat': 'nds_20',
                },
            ),
        ],
        operation_id=operation_id,
    )

    if external_payment_id:
        refund_data['external_payment_id'] = external_payment_id

    return helpers.make_transaction(
        status='clear_success',
        operation_id=operation_id,
        payment_type=payment_type,
        terminal_id='456',
        sum=[helpers.make_transactions_item(item_id=item_id, amount='2.00')],
        refunds=[refund_data],
    )


def make_order():
    return {
        'countryCode': 'RU',
        'orderNr': 'test_order',
        'orderType': 'native',
        'paymentMethod': 'card',
    }


def make_user_info():
    return {'userEmail': 'user@example.com'}


def make_product(
        product_id: str,
        price: str,
        inn: str,
        title: str = 'Big Mac Burger',
        supplier_inn_id: str = 'personal-tin-id',
):
    return {
        'id': product_id,
        'parent': None,
        'price': price,
        'supplier_inn': inn,
        'tax': '20',
        'title': title,
        'supplier_inn_id': supplier_inn_id,
    }


@pytest.mark.parametrize(
    ['operation_id', 'operation_type'], [('create:100500', 'create')],
)
@pytest.mark.parametrize('service', ['grocery', 'eats'])
async def test_purchase_receipt(
        check_transactions_callback_task,
        check_send_receipt,
        taxi_eats_payments_monitor,
        mock_transactions_invoice_retrieve,
        insert_items,
        mock_personal_retrieve_tins,
        operation_id,
        operation_type,
        service,
        stq,
        taxi_eats_payments,
        upsert_order,
):
    upsert_order('test_order')
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    transactions_items = [
        helpers.make_transactions_item(
            item_id='big_mac',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': 'personal-tin-id',
                'title': 'Big Mac Burger',
                'vat': 'nds_20',
            },
        ),
    ]
    payment_items_list = [
        helpers.make_transactions_payment_items(
            payment_type='card', items=transactions_items,
        ),
    ]
    mock_transactions_invoice_retrieve(
        status='cleared',
        operations=[
            helpers.make_operation(
                id=operation_id, sum_to_pay=payment_items_list,
            ),
        ],
        service=service,
        cleared=payment_items_list,
        transactions=[
            helpers.make_transaction(
                status='clear_success',
                operation_id=operation_id,
                payment_type='card',
                terminal_id='456',
                sum=transactions_items,
            ),
        ],
        personal_email_id='personal-email-id',
    )
    personal_tins_mock = mock_personal_retrieve_tins()

    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(status='clear_success'),
        ],
        notification_type='transaction_clear',
    )

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='eats_payments_receipts_metrics',
            labels={'receipt_type': 'products'},
    ) as collector:
        await check_send_receipt(1)

    assert personal_tins_mock.times_called == 1
    assert stq.eats_send_receipts_requests.times_called == 1
    document_id = stq.eats_send_receipts_requests.next_call()['kwargs'][
        'document_id'
    ]
    response = await taxi_eats_payments.post(
        '/v1/receipts/retrieve/', json={'document_id': f'{document_id}'},
    )
    assert response.status_code == 200
    assert response.json()['products'] == [
        make_product(product_id='big_mac', price='2.00', inn=''),
    ]

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'sensor': 'eats_payments_receipts_metrics',
        'receipt_type': 'products',
        'operation_type': operation_type,
        'currency': 'RUB',
        'payment_type': 'card',
        'service_name': service,
    }


@pytest.mark.parametrize(
    ['operation_id', 'operation_type'], [('create:100500', 'create')],
)
@pytest.mark.parametrize('service', ['grocery', 'eats'])
async def test_purchase_receipt_service_fee(
        check_transactions_callback_task,
        check_send_receipt,
        taxi_eats_payments_monitor,
        mock_transactions_invoice_retrieve,
        insert_items,
        mock_personal_retrieve_tins,
        operation_id,
        operation_type,
        service,
        stq,
        taxi_eats_payments,
        upsert_order,
):
    upsert_order('test_order')
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
            helpers.make_db_row(
                item_id='service_fee',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='service_fee',
            ),
        ],
    )

    transactions_items = [
        helpers.make_transactions_item(
            item_id='big_mac',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': 'personal-tin-id',
                'title': 'Big Mac Burger',
                'vat': 'nds_20',
            },
        ),
        helpers.make_transactions_item(
            item_id='service_fee',
            amount='9.00',
            fiscal_receipt_info={
                'personal_tin_id': 'personal-tin-id',
                'title': 'Service Fee',
                'vat': 'nds_20',
            },
        ),
    ]
    payment_items_list = [
        helpers.make_transactions_payment_items(
            payment_type='card', items=transactions_items,
        ),
    ]
    mock_transactions_invoice_retrieve(
        status='cleared',
        operations=[
            helpers.make_operation(
                id=operation_id, sum_to_pay=payment_items_list,
            ),
        ],
        service=service,
        cleared=payment_items_list,
        transactions=[
            helpers.make_transaction(
                status='clear_success',
                operation_id=operation_id,
                payment_type='card',
                terminal_id='456',
                sum=transactions_items,
            ),
        ],
        personal_email_id='personal-email-id',
    )
    personal_tins_mock = mock_personal_retrieve_tins()

    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(status='clear_success'),
        ],
        notification_type='transaction_clear',
    )

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='eats_payments_receipts_metrics',
            labels={'receipt_type': 'products'},
    ) as collector:
        await check_send_receipt(1)

    assert personal_tins_mock.times_called == 1

    assert stq.eats_send_receipts_requests.times_called == 2
    document_id = stq.eats_send_receipts_requests.next_call()['kwargs'][
        'document_id'
    ]
    response = await taxi_eats_payments.post(
        '/v1/receipts/retrieve/', json={'document_id': f'{document_id}'},
    )
    assert response.status_code == 200
    assert response.json()['products'] == [
        make_product(
            product_id='service_fee',
            price='9.00',
            inn='',
            title='Service Fee',
        ),
    ]

    document_id = stq.eats_send_receipts_requests.next_call()['kwargs'][
        'document_id'
    ]
    response = await taxi_eats_payments.post(
        '/v1/receipts/retrieve/', json={'document_id': f'{document_id}'},
    )
    assert response.status_code == 200
    assert response.json()['products'] == [
        make_product(product_id='big_mac', price='2.00', inn=''),
    ]

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'sensor': 'eats_payments_receipts_metrics',
        'receipt_type': 'products',
        'operation_type': operation_type,
        'currency': 'RUB',
        'payment_type': 'card',
        'service_name': service,
    }


async def check_response(taxi_eats_payments, eats_send_receipts_requests):
    document_id = eats_send_receipts_requests.next_call()['kwargs'][
        'document_id'
    ]
    response = await taxi_eats_payments.post(
        '/v1/receipts/retrieve/', json={'document_id': f'{document_id}'},
    )
    assert response.status_code == 200

    if 'service_fee' in document_id:
        assert response.json()['products'] == [
            make_product(
                product_id='service_fee',
                price='100.00',
                inn='',
                title='service_fee',
            ),
        ]

    if 'product' in document_id:
        assert response.json()['products'] == [
            make_product(
                product_id='product-1',
                price='10.00',
                inn='',
                title='Product 1',
            ),
        ]

    assert response.json()['is_refund']


@pytest.mark.parametrize(
    ['operation_id', 'operation_type'], [('create:100500', 'create')],
)
@pytest.mark.parametrize('service', ['grocery', 'eats'])
@pytest.mark.parametrize(
    ['task_args_items', 'expect_fail', 'receipts_mock_times_called'],
    [
        [[{'item_id': 'big_mac'}, {'item_id': 'big_mac_excluded'}], False, 1],
        [[{'item_id': 'big_mac', 'price': '100'}], True, 0],
    ],
)
async def test_purchase_receipt_items_in_args(
        stq_runner,
        mock_transactions_invoice_retrieve,
        insert_items,
        mock_personal_retrieve_tins,
        operation_id,
        operation_type,
        service,
        task_args_items,
        expect_fail,
        receipts_mock_times_called,
        stq,
        taxi_eats_payments,
        upsert_order,
):
    upsert_order('test_order')
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
            helpers.make_db_row(
                item_id='big_mac_2',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    transactions_items = [
        helpers.make_transactions_item(
            item_id='big_mac',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': 'personal-tin-id',
                'title': 'Big Mac Burger',
                'vat': 'nds_20',
            },
        ),
        helpers.make_transactions_item(
            item_id='big_mac_2',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': 'personal-tin-id',
                'title': 'Big Mac Burger',
                'vat': 'nds_20',
            },
        ),
    ]
    payment_items_list = [
        helpers.make_transactions_payment_items(
            payment_type='card', items=transactions_items,
        ),
    ]
    mock_transactions_invoice_retrieve(
        status='cleared',
        operations=[
            helpers.make_operation(
                id=operation_id, sum_to_pay=payment_items_list,
            ),
        ],
        service=service,
        cleared=payment_items_list,
        transactions=[
            helpers.make_transaction(
                status='clear_success',
                operation_id=operation_id,
                payment_type='card',
                terminal_id='456',
                sum=transactions_items,
            ),
        ],
        personal_email_id='personal-email-id',
    )
    mock_personal_retrieve_tins()

    kwargs = {
        'invoice_id': 'test_order',
        'operation_id': 'create:100500',
        'receipt_processing_type': 'purchase',
        'items': task_args_items,
    }
    await stq_runner.eats_payments_send_receipt.call(
        task_id='test_task_id',
        kwargs=kwargs,
        exec_tries=0,
        expect_fail=expect_fail,
    )

    assert (
        stq.eats_send_receipts_requests.times_called
        == receipts_mock_times_called
    )
    if receipts_mock_times_called > 0:
        document_id = stq.eats_send_receipts_requests.next_call()['kwargs'][
            'document_id'
        ]
        response = await taxi_eats_payments.post(
            '/v1/receipts/retrieve/', json={'document_id': f'{document_id}'},
        )
        assert response.status_code == 200
        assert response.json()['products'] == [
            make_product(product_id='big_mac', price='2.00', inn=''),
            make_product(product_id='big_mac_2', price='2.00', inn=''),
        ]


# TODO: test for two receipts for the same order
@pytest.mark.parametrize(
    ['receipt_type', 'item_type'],
    [
        ('products', 'product'),
        ('delivery', 'delivery'),
        ('tips', 'tips'),
        ('restaurant_tips', 'restaurant_tips'),
    ],
)
async def test_purchase_receipt_receipt_type(
        check_transactions_callback_task,
        check_send_receipt,
        mock_transactions_invoice_retrieve,
        insert_items,
        mock_personal_retrieve_tins,
        receipt_type,
        item_type,
        stq,
        taxi_eats_payments,
        upsert_order,
):
    upsert_order('test_order')
    operation_id = 'create:100500'
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type=item_type,
            ),
        ],
    )
    transactions_items = [
        helpers.make_transactions_item(
            item_id='big_mac',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': 'personal-tin-id',
                'title': 'Big Mac Burger',
                'vat': 'nds_20',
            },
        ),
    ]
    # pylint: disable=invalid-name
    personal_wallet_transactions_items = [
        helpers.make_transactions_item(
            item_id='big_mac',
            amount='1.00',
            fiscal_receipt_info={
                'personal_tin_id': 'personal-tin-id',
                'title': 'Big Mac Burger',
                'vat': 'nds_20',
            },
        ),
    ]
    payment_items_list = [
        helpers.make_transactions_payment_items(
            payment_type='card', items=transactions_items,
        ),
        helpers.make_transactions_payment_items(
            payment_type='personal_wallet',
            items=personal_wallet_transactions_items,
        ),
    ]
    mock_transactions_invoice_retrieve(
        status='cleared',
        operations=[
            helpers.make_operation(
                id=operation_id, sum_to_pay=payment_items_list,
            ),
        ],
        cleared=payment_items_list,
        transactions=[
            helpers.make_transaction(
                status='clear_success',
                operation_id=operation_id,
                payment_type='card',
                terminal_id='456',
                sum=transactions_items,
            ),
            helpers.make_transaction(
                external_payment_id='456789',
                status='clear_success',
                operation_id=operation_id,
                payment_type='personal_wallet',
                terminal_id='456',
                sum=personal_wallet_transactions_items,
            ),
        ],
        personal_email_id='personal-email-id',
    )
    mock_personal_retrieve_tins()
    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(status='clear_success'),
        ],
        notification_type='transaction_clear',
    )
    await check_send_receipt(1)

    assert stq.eats_send_receipts_requests.times_called == 1
    document_id = stq.eats_send_receipts_requests.next_call()['kwargs'][
        'document_id'
    ]
    response = await taxi_eats_payments.post(
        '/v1/receipts/retrieve/', json={'document_id': f'{document_id}'},
    )
    assert response.status_code == 200
    assert response.json()['products'] == [
        make_product(product_id='big_mac', price='2.00', inn=''),
    ]


async def test_service_uses_eats_receipts(
        check_transactions_callback_task,
        check_send_receipt,
        mock_transactions_invoice_retrieve,
        insert_items,
        pgsql,
        mock_personal_retrieve_tins,
        mock_order_revision_list,
        stq,
        experiments3,
        taxi_eats_payments,
        stq_runner,
        mockserver,
):
    operation_id = 'create:100500'
    order = db_order.DBOrder(
        pgsql=pgsql,
        order_id='test_order',
        currency='RUB',
        service='eats',
        originator=consts.EDA_CORE_ORIGINATOR,
    )
    order.upsert()
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    transactions_items = [
        helpers.make_transactions_item(
            item_id='big_mac',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': 'personal-tin-id',
                'title': 'Big Mac Burger',
                'vat': 'nds_20',
            },
        ),
    ]
    payment_items_list = [
        helpers.make_transactions_payment_items(
            payment_type='card', items=transactions_items,
        ),
    ]
    mock_transactions_invoice_retrieve(
        id='test_order',
        status='cleared',
        currency='RUB',
        operations=[
            helpers.make_operation(
                id=operation_id, sum_to_pay=payment_items_list,
            ),
        ],
        cleared=payment_items_list,
        transactions=[
            helpers.make_transaction(
                status='clear_success',
                operation_id=operation_id,
                payment_type='card',
                terminal_id='456',
                sum=transactions_items,
            ),
        ],
        personal_email_id='personal-email-id',
    )
    mock_personal_retrieve_tins()
    mock_order_revision_list()

    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(status='clear_success'),
        ],
        notification_type='transaction_clear',
    )

    await check_send_receipt(1)
    assert stq.eats_send_receipts_requests.times_called == 1

    document_id = stq.eats_send_receipts_requests.next_call()['kwargs'][
        'document_id'
    ]
    print(f'document_id is {document_id}')
    response = await taxi_eats_payments.post(
        '/v1/receipts/retrieve/', json={'document_id': f'{document_id}'},
    )
    print(response)
    assert response.status_code == 200
    assert response.json()['products'] == [
        make_product(product_id='big_mac', price='2.00', inn=''),
    ]


@pytest.mark.parametrize(
    'payment_type, times_called', [('card', 1), (consts.PERSONAL_WALLET, 0)],
)
async def test_ignore_personal_wallet(
        check_transactions_callback_task,
        check_send_receipt,
        mock_transactions_invoice_retrieve,
        insert_items,
        mock_personal_retrieve_tins,
        payment_type,
        times_called,
        stq,
        taxi_eats_payments,
        upsert_order,
):
    upsert_order('test_order')
    operation_id = 'create:1234'

    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    transactions_items = [
        helpers.make_transactions_item(
            item_id='big_mac',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': 'personal-tin-id',
                'title': 'Big Mac Burger',
                'vat': 'nds_20',
            },
        ),
    ]
    payment_items_list = [
        helpers.make_transactions_payment_items(
            payment_type=payment_type, items=transactions_items,
        ),
    ]
    mock_transactions_invoice_retrieve(
        status='cleared',
        operations=[
            helpers.make_operation(
                id=operation_id, sum_to_pay=payment_items_list,
            ),
        ],
        service=consts.DEFAULT_SERVICE,
        cleared=payment_items_list,
        transactions=[
            helpers.make_transaction(
                status='clear_success',
                operation_id=operation_id,
                payment_type=payment_type,
                terminal_id='456',
                sum=transactions_items,
            ),
        ],
        personal_email_id='personal-email-id',
    )

    mock_personal_retrieve_tins()

    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(
                status='clear_success', payment_type=payment_type,
            ),
        ],
        notification_type='transaction_clear',
    )

    await check_send_receipt(1)

    assert stq.eats_send_receipts_requests.times_called == times_called
    if times_called > 0:
        document_id = stq.eats_send_receipts_requests.next_call()['kwargs'][
            'document_id'
        ]
        response = await taxi_eats_payments.post(
            '/v1/receipts/retrieve/', json={'document_id': f'{document_id}'},
        )
        assert response.status_code == 200
        assert response.json()['products'] == [
            make_product(product_id='big_mac', price='2.00', inn=''),
        ]


async def test_no_purchase_receipt_metrics_on_repeated_task_execution(
        check_transactions_callback_task,
        check_send_receipt,
        taxi_eats_payments_monitor,
        mock_transactions_invoice_retrieve,
        insert_items,
        mock_personal_retrieve_tins,
        testpoint,
        stq,
        upsert_order,
):
    upsert_order('test_order')
    operation_id = 'create:100500'
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    transactions_items = [
        helpers.make_transactions_item(
            item_id='big_mac',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': 'personal-tin-id',
                'title': 'Big Mac Burger',
                'vat': 'nds_20',
            },
        ),
    ]
    payment_items_list = [
        helpers.make_transactions_payment_items(
            payment_type='card', items=transactions_items,
        ),
    ]
    mock_transactions_invoice_retrieve(
        status='cleared',
        operations=[
            helpers.make_operation(
                id=operation_id, sum_to_pay=payment_items_list,
            ),
        ],
        service='eats',
        cleared=payment_items_list,
        transactions=[
            helpers.make_transaction(
                status='clear_success',
                operation_id=operation_id,
                payment_type='card',
                terminal_id='456',
                sum=transactions_items,
            ),
        ],
        personal_email_id='personal-email-id',
    )
    mock_personal_retrieve_tins()

    @testpoint('receipts_purchase_repeated_task_execution')
    def repeated_task_execution_tp(data):
        pass

    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(status='clear_success'),
        ],
        notification_type='transaction_clear',
        exec_tries=1,
    )

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='eats_payments_receipts_metrics',
            labels={'receipt_type': 'purchase'},
    ) as collector:
        await check_send_receipt(1, exec_tries=1)

    metric = collector.get_single_collected_metric()
    assert metric is None
    assert repeated_task_execution_tp.times_called == 1
    assert stq.eats_send_receipts_requests.times_called == 1


async def test_fiscal_receipt_info_only_in_update_operation(
        check_transactions_callback_task,
        check_send_receipt,
        taxi_eats_payments_monitor,
        mock_transactions_invoice_retrieve,
        insert_items,
        mock_personal_retrieve_tins,
        stq,
        taxi_eats_payments,
        upsert_order,
):
    upsert_order('test_order')
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    # pylint: disable=invalid-name
    transactions_items_with_fiscal_receipt_info = [
        helpers.make_transactions_item(
            item_id='big_mac',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': 'personal-tin-id',
                'title': 'Big Mac Burger',
                'vat': 'nds_20',
            },
        ),
    ]
    transactions_items = [
        helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
    ]
    # pylint: disable=invalid-name
    payment_items_list_with_fiscal_receipt_info = [
        helpers.make_transactions_payment_items(
            payment_type='card',
            items=transactions_items_with_fiscal_receipt_info,
        ),
    ]
    payment_items_list = [
        helpers.make_transactions_payment_items(
            payment_type='card', items=transactions_items,
        ),
    ]
    operation_id = 'create:100500'
    mock_transactions_invoice_retrieve(
        status='cleared',
        operations=[
            helpers.make_operation(
                id=operation_id, sum_to_pay=payment_items_list,
            ),
            helpers.make_operation(
                id='update:123456',
                sum_to_pay=payment_items_list_with_fiscal_receipt_info,
            ),
        ],
        cleared=payment_items_list,
        transactions=[
            helpers.make_transaction(
                status='clear_success',
                operation_id=operation_id,
                payment_type='card',
                terminal_id='456',
                sum=transactions_items,
            ),
        ],
        personal_email_id='personal-email-id',
    )
    personal_tins_mock = mock_personal_retrieve_tins()

    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(status='clear_success'),
        ],
        notification_type='transaction_clear',
    )

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='eats_payments_receipts_metrics',
            labels={'receipt_type': 'products'},
    ) as collector:
        await check_send_receipt(1)

    assert personal_tins_mock.times_called == 1
    assert stq.eats_send_receipts_requests.times_called == 1
    document_id = stq.eats_send_receipts_requests.next_call()['kwargs'][
        'document_id'
    ]
    response = await taxi_eats_payments.post(
        '/v1/receipts/retrieve/', json={'document_id': f'{document_id}'},
    )
    assert response.status_code == 200
    assert response.json()['products'] == [
        make_product(product_id='big_mac', price='2.00', inn=''),
    ]

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'sensor': 'eats_payments_receipts_metrics',
        'receipt_type': 'products',
        'operation_type': 'create',
        'currency': 'RUB',
        'payment_type': 'card',
        'service_name': 'eats',
    }


@pytest.mark.parametrize(
    'payment_type, times_called', [('card', 1), (consts.PERSONAL_WALLET, 0)],
)
async def test_ignore_personal_wallet_refund_receipt(
        check_transactions_callback_task,
        check_send_receipt,
        mock_transactions_invoice_retrieve,
        insert_items,
        mock_personal_retrieve_tins,
        payment_type,
        times_called,
        stq,
        upsert_order,
):
    upsert_order('test_order')
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    operation_id = 'refund:123'
    transactions_items = [
        helpers.make_transactions_item(
            item_id='big_mac',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': 'personal-tin-id',
                'title': 'Big Mac Burger',
                'vat': 'nds_20',
            },
        ),
    ]
    payment_items_list = [
        helpers.make_transactions_payment_items(
            payment_type=payment_type, items=transactions_items,
        ),
    ]
    mock_transactions_invoice_retrieve(
        status='cleared',
        operations=[
            helpers.make_operation(
                id=operation_id, sum_to_pay=payment_items_list,
            ),
        ],
        cleared=payment_items_list,
        transactions=[
            _get_refund_transaction(
                operation_id=operation_id, payment_type=payment_type,
            ),
        ],
        personal_email_id='personal-email-id',
    )

    mock_personal_retrieve_tins()

    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(
                status='clear_success', payment_type=payment_type,
            ),
        ],
        notification_type='operation_finish',
    )
    await check_send_receipt(1)
    assert stq.eats_send_receipts_requests.times_called == times_called


async def test_refund_receipt(
        check_transactions_callback_task,
        check_send_receipt,
        mock_transactions_invoice_retrieve,
        taxi_eats_payments_monitor,
        insert_items,
        mock_personal_retrieve_tins,
        stq,
        upsert_order,
):
    upsert_order('test_order')
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    operation_id = 'refund:123'
    transactions_items = [
        helpers.make_transactions_item(
            item_id='big_mac',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': 'personal-tin-id',
                'title': 'Big Mac Burger',
                'vat': 'nds_20',
            },
        ),
    ]
    payment_items_list = [
        helpers.make_transactions_payment_items(
            payment_type='card', items=transactions_items,
        ),
    ]
    mock_transactions_invoice_retrieve(
        status='cleared',
        operations=[
            helpers.make_operation(
                id=operation_id, sum_to_pay=payment_items_list,
            ),
        ],
        cleared=payment_items_list,
        transactions=[_get_refund_transaction(operation_id=operation_id)],
        personal_email_id='personal-email-id',
    )
    personal_tins_mock = mock_personal_retrieve_tins()

    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(status='clear_success'),
        ],
        notification_type='operation_finish',
    )

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='eats_payments_receipts_metrics',
            labels={'receipt_type': 'refund'},
    ) as collector:
        await check_send_receipt(1)

    assert personal_tins_mock.times_called == 1
    assert stq.eats_send_receipts_requests.times_called == 1

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'sensor': 'eats_payments_receipts_metrics',
        'receipt_type': 'refund',
        'operation_type': 'refund',
        'currency': 'RUB',
        'payment_type': 'card',
        'service_name': consts.DEFAULT_SERVICE,
    }


async def test_refund_receipt_service_fee(
        check_transactions_callback_task,
        check_send_receipt,
        mock_transactions_invoice_retrieve,
        taxi_eats_payments_monitor,
        insert_items,
        mock_personal_retrieve_tins,
        stq,
        upsert_order,
):
    upsert_order('test_order')
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
            helpers.make_db_row(
                item_id='service_fee',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='service_fee',
            ),
        ],
    )
    operation_id = 'refund:123'
    transactions_items = [
        helpers.make_transactions_item(
            item_id='big_mac',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': 'personal-tin-id',
                'title': 'Big Mac Burger',
                'vat': 'nds_20',
            },
        ),
        helpers.make_transactions_item(
            item_id='service_fee',
            amount='9.00',
            fiscal_receipt_info={
                'personal_tin_id': 'personal-tin-id',
                'title': 'Service Fee',
                'vat': 'nds_20',
            },
        ),
    ]
    payment_items_list = [
        helpers.make_transactions_payment_items(
            payment_type='card', items=transactions_items,
        ),
    ]
    mock_transactions_invoice_retrieve(
        status='cleared',
        operations=[
            helpers.make_operation(
                id=operation_id, sum_to_pay=payment_items_list,
            ),
        ],
        cleared=payment_items_list,
        transactions=[_get_refund_transaction(operation_id=operation_id)],
        personal_email_id='personal-email-id',
    )
    personal_tins_mock = mock_personal_retrieve_tins()

    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(status='clear_success'),
        ],
        notification_type='operation_finish',
    )

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='eats_payments_receipts_metrics',
            labels={'receipt_type': 'refund'},
    ) as collector:
        await check_send_receipt(1)

    assert personal_tins_mock.times_called == 1
    assert stq.eats_send_receipts_requests.times_called == 1

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'sensor': 'eats_payments_receipts_metrics',
        'receipt_type': 'refund',
        'operation_type': 'refund',
        'currency': 'RUB',
        'payment_type': 'card',
        'service_name': consts.DEFAULT_SERVICE,
    }


@pytest.mark.parametrize(
    ['task_args_items', 'refund_amount'],
    [
        [[{'item_id': 'big_mac'}, {'item_id': 'big_mac_excluded'}], '1.00'],
        [[{'item_id': 'big_mac', 'price': '5.00'}], '5.00'],
    ],
)
async def test_refund_receipt_items_in_args(
        stq_runner,
        mock_transactions_invoice_retrieve,
        insert_items,
        mock_personal_retrieve_tins,
        task_args_items,
        refund_amount,
        stq,
        upsert_order,
):
    upsert_order('test_order')
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    operation_id = 'refund:123'
    transactions_items = [
        helpers.make_transactions_item(
            item_id='big_mac',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': 'personal-tin-id',
                'title': 'Big Mac Burger',
                'vat': 'nds_20',
            },
        ),
    ]
    payment_items_list = [
        helpers.make_transactions_payment_items(
            payment_type='card', items=transactions_items,
        ),
    ]
    mock_transactions_invoice_retrieve(
        status='cleared',
        operations=[
            helpers.make_operation(
                id=operation_id, sum_to_pay=payment_items_list,
            ),
        ],
        cleared=payment_items_list,
        transactions=[_get_refund_transaction(operation_id=operation_id)],
        personal_email_id='personal-email-id',
    )
    mock_personal_retrieve_tins()
    kwargs = {
        'invoice_id': 'test_order',
        'operation_id': 'refund:123',
        'receipt_processing_type': 'refund',
        'items': task_args_items,
    }
    await stq_runner.eats_payments_send_receipt.call(
        task_id='test_task_id', kwargs=kwargs, exec_tries=0,
    )

    assert stq.eats_send_receipts_requests.times_called == 1


async def test_no_refund_receipt_metrics_on_repeated_task_execution(
        check_transactions_callback_task,
        check_send_receipt,
        mock_transactions_invoice_retrieve,
        taxi_eats_payments_monitor,
        insert_items,
        mock_personal_retrieve_tins,
        testpoint,
        upsert_order,
):
    upsert_order('test_order')
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    operation_id = 'refund:123'
    transactions_items = [
        helpers.make_transactions_item(
            item_id='big_mac',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': 'personal-tin-id',
                'title': 'Big Mac Burger',
                'vat': 'nds_20',
            },
        ),
    ]
    payment_items_list = [
        helpers.make_transactions_payment_items(
            payment_type='card', items=transactions_items,
        ),
    ]
    mock_transactions_invoice_retrieve(
        status='cleared',
        operations=[
            helpers.make_operation(
                id=operation_id, sum_to_pay=payment_items_list,
            ),
        ],
        cleared=payment_items_list,
        transactions=[_get_refund_transaction(operation_id=operation_id)],
        personal_email_id='personal-email-id',
    )
    mock_personal_retrieve_tins()

    @testpoint('receipts_refund_repeated_task_execution')
    def repeated_task_execution_tp(data):
        pass

    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(status='clear_success'),
        ],
        notification_type='operation_finish',
        exec_tries=1,
    )

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='eats_payments_receipts_metrics',
            labels={'receipt_type': 'refund'},
    ) as collector:
        await check_send_receipt(1, exec_tries=1)

    metric = collector.get_single_collected_metric()
    assert metric is None
    assert repeated_task_execution_tp.times_called == 1


async def test_no_refund_no_receipt(
        check_transactions_callback_task,
        check_send_receipt,
        taxi_eats_payments_monitor,
        mock_transactions_invoice_retrieve,
        insert_items,
        mock_personal_retrieve_tins,
        stq,
        upsert_order,
):
    upsert_order('test_order')
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    operation_id = 'refund:123'
    mock_transactions_invoice_retrieve(
        cleared=[
            helpers.make_transactions_payment_items(
                payment_type='card',
                items=[
                    helpers.make_transactions_item(
                        item_id='big_mac',
                        amount='2.00',
                        fiscal_receipt_info={
                            'personal_tin_id': 'personal-tin-id',
                            'title': 'Big Mac Burger',
                            'vat': 'nds_20',
                        },
                    ),
                ],
            ),
        ],
        transactions=[
            helpers.make_transaction(
                status='clear_success',
                operation_id=operation_id,
                payment_type='card',
                terminal_id='456',
                sum=[
                    helpers.make_transactions_item(
                        item_id='big_mac', amount='2.00',
                    ),
                ],
            ),
        ],
        personal_email_id='personal-email-id',
    )
    personal_tins_mock = mock_personal_retrieve_tins()
    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(status='clear_success'),
        ],
    )

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='eats_payments_receipts_metrics',
            labels={'receipt_type': 'refund'},
    ) as collector:
        await check_send_receipt(1)

    assert personal_tins_mock.times_called == 0
    assert stq.eats_send_receipts_requests.times_called == 0
    assert collector.get_single_collected_metric() is None


async def test_operation_finish_no_receipt(
        check_transactions_callback_task,
        check_send_receipt,
        taxi_eats_payments_monitor,
        mock_transactions_invoice_retrieve,
        insert_items,
        testpoint,
        stq,
        upsert_order,
):
    upsert_order('test_order')
    insert_items([helpers.make_db_row(item_id='big_mac')])
    mock_transactions_invoice_retrieve(status='cleared')

    @testpoint('receipts_notification_type_not_transaction_clear')
    def notification_type_tp(data):
        pass

    await check_transactions_callback_task(
        operation_id='create:123',
        transactions=[
            helpers.make_callback_transaction(status='clear_success'),
        ],
        notification_type='operation_finish',
    )

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='eats_payments_receipts_metrics',
            labels={'receipt_type': 'purchase'},
    ) as collector:
        await check_send_receipt(0)

    assert collector.get_single_collected_metric() is None
    assert notification_type_tp.times_called == 1
    assert stq.eats_send_receipts_requests.times_called == 0


async def test_canceled_invoice_no_receipt(
        check_transactions_callback_task,
        check_send_receipt,
        taxi_eats_payments_monitor,
        mock_transactions_invoice_retrieve,
        insert_items,
        testpoint,
        stq,
        upsert_order,
):
    upsert_order('test_order')
    insert_items([helpers.make_db_row(item_id='big_mac')])
    mock_transactions_invoice_retrieve(
        status='cleared',
        transactions=[
            helpers.make_transaction(
                operation_id='create:100500', status='clear_success',
            ),
            helpers.make_transaction(
                operation_id='cancel:100500', status='clear_success',
            ),
        ],
        operations=[
            helpers.make_operation(id='create:100500'),
            helpers.make_operation(id='cancel:100500'),
        ],
    )

    @testpoint('receipts_canceled_invoice')
    def canceled_invoice_tp(data):
        pass

    await check_transactions_callback_task(
        operation_id='create:123',
        transactions=[
            helpers.make_callback_transaction(status='clear_success'),
        ],
        notification_type='transaction_clear',
    )

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='eats_payments_receipts_metrics',
            labels={'receipt_type': 'purchase'},
    ) as collector:
        await check_send_receipt(0)

    assert collector.get_single_collected_metric() is None
    assert canceled_invoice_tp.times_called == 1
    assert stq.eats_send_receipts_requests.times_called == 0


async def test_no_personal_email_id(
        check_transactions_callback_task,
        check_send_receipt,
        mock_transactions_invoice_retrieve,
        insert_items,
        taxi_eats_payments_monitor,
        mock_personal_retrieve_tins,
        stq,
        taxi_eats_payments,
        upsert_order,
):
    upsert_order('test_order')
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    transactions_items = [
        helpers.make_transactions_item(
            item_id='big_mac',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': 'personal-tin-id',
                'title': 'Big Mac Burger',
                'vat': 'nds_20',
            },
        ),
    ]
    payment_items_list = [
        helpers.make_transactions_payment_items(
            payment_type='card', items=transactions_items,
        ),
    ]
    mock_transactions_invoice_retrieve(
        status='cleared',
        operations=[
            helpers.make_operation(
                id='create:100500', sum_to_pay=payment_items_list,
            ),
        ],
        service='eats',
        cleared=payment_items_list,
        transactions=[
            helpers.make_transaction(
                status='clear_success',
                operation_id='create:100500',
                payment_type='card',
                terminal_id='456',
                sum=transactions_items,
            ),
        ],
        personal_email_id=None,
        personal_phone_id='personal-phone-id',
    )
    personal_tins_mock = mock_personal_retrieve_tins()

    await check_transactions_callback_task(
        operation_id='create:100500',
        transactions=[
            helpers.make_callback_transaction(status='clear_success'),
        ],
        notification_type='transaction_clear',
    )

    async with metrics_helpers.MetricsCollector(
            taxi_eats_payments_monitor,
            sensor='eats_payments_receipts_metrics',
            labels={'receipt_type': 'products'},
    ) as collector:
        await check_send_receipt(1)

    assert personal_tins_mock.times_called == 1

    assert stq.eats_send_receipts_requests.times_called == 1

    document_id = stq.eats_send_receipts_requests.next_call()['kwargs'][
        'document_id'
    ]
    response = await taxi_eats_payments.post(
        '/v1/receipts/retrieve/', json={'document_id': f'{document_id}'},
    )
    assert response.status_code == 200
    assert response.json()['products'] == [
        make_product(product_id='big_mac', price='2.00', inn=''),
    ]
    assert response.json()['user_info']['personal_email_id'] == ''
    assert (
        response.json()['user_info']['personal_phone_id']
        == 'personal-phone-id'
    )

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'sensor': 'eats_payments_receipts_metrics',
        'receipt_type': 'products',
        'operation_type': 'create',
        'currency': 'RUB',
        'payment_type': 'card',
        'service_name': 'eats',
    }


async def test_zero_amount_items_not_in_receipt(
        check_transactions_callback_task,
        check_send_receipt,
        mock_transactions_invoice_retrieve,
        insert_items,
        mock_personal_retrieve_tins,
        stq,
        taxi_eats_payments,
        upsert_order,
):
    upsert_order('test_order')
    insert_items([helpers.make_db_row(item_id='big_mac')])
    transactions_payment_items = (
        helpers.make_transactions_payment_items(
            payment_type='card',
            items=[
                helpers.make_transactions_item(
                    item_id='big_mac',
                    amount='2.00',
                    fiscal_receipt_info={
                        'personal_tin_id': 'personal-tin-id',
                        'title': 'Big Mac Burger',
                        'vat': 'nds_20',
                    },
                ),
                # deliberately not adding fiscal receipt info
                # as this item should be skipped earlier
                helpers.make_transactions_item(
                    item_id='big_mac', amount='0.00',
                ),
            ],
        ),
    )
    transaction1 = helpers.make_transaction(
        operation_id='create:123', status='clear_success',
    )
    mock_transactions_invoice_retrieve(
        status='cleared',
        cleared=transactions_payment_items,
        operations=[
            helpers.make_operation(
                sum_to_pay=transactions_payment_items, id='create:123',
            ),
        ],
        transactions=[transaction1],
    )
    mock_personal_retrieve_tins()
    await check_transactions_callback_task(
        operation_id='create:123',
        transactions=[
            helpers.make_callback_transaction(status='clear_success'),
        ],
        notification_type='transaction_clear',
    )
    await check_send_receipt(1)
    assert stq.eats_send_receipts_requests.times_called == 1
    document_id = stq.eats_send_receipts_requests.next_call()['kwargs'][
        'document_id'
    ]
    response = await taxi_eats_payments.post(
        '/v1/receipts/retrieve/', json={'document_id': f'{document_id}'},
    )
    assert response.status_code == 200
    assert response.json()['products'] == [
        make_product(product_id='big_mac', price='2.00', inn=''),
    ]


@pytest.mark.parametrize(
    [
        'transactions',
        'cleared',
        'db_items',
        'products',
        'stq_receipts_times_called',
        'tp_times_called',
        'send_receipt_times_called',
    ],
    [
        pytest.param(
            [
                helpers.make_transaction(
                    status='clear_success',
                    operation_id='create:123',
                    payment_type='card',
                    terminal_id='456',
                    sum=[
                        helpers.make_transactions_item(
                            item_id='big_mac_1',
                            amount='1.00',
                            fiscal_receipt_info={
                                'personal_tin_id': 'personal-tin-id',
                                'title': 'Big Mac Burger 1',
                                'vat': 'nds_20',
                            },
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac_1',
                            amount='1.00',
                            fiscal_receipt_info={
                                'personal_tin_id': 'personal-tin-id',
                                'title': 'Big Mac Burger 1',
                                'vat': 'nds_20',
                            },
                        ),
                    ],
                ),
            ],
            [
                helpers.make_db_row(
                    item_id='big_mac_1',
                    place_id='some_place_id',
                    balance_client_id='some_id',
                    item_type='product',
                ),
            ],
            [
                make_product(
                    product_id='big_mac_1',
                    price='1.00',
                    inn='',
                    title='Big Mac Burger 1',
                ),
            ],
            1,
            0,
            1,
            id='Only one create cleared transaction',
        ),
        pytest.param(
            [
                helpers.make_transaction(
                    status='clear_success',
                    operation_id='create:123',
                    payment_type='card',
                    terminal_id='456',
                    sum=[
                        helpers.make_transactions_item(
                            item_id='big_mac_1',
                            amount='1.00',
                            fiscal_receipt_info={
                                'personal_tin_id': 'personal-tin-id',
                                'title': 'Big Mac Burger 1',
                                'vat': 'nds_20',
                            },
                        ),
                    ],
                ),
                helpers.make_transaction(
                    status='clear_success',
                    operation_id='update:123',
                    payment_type='card',
                    terminal_id='456',
                    sum=[
                        helpers.make_transactions_item(
                            item_id='big_mac_2',
                            amount='2.00',
                            fiscal_receipt_info={
                                'personal_tin_id': 'personal-tin-id',
                                'title': 'Big Mac Burger 2',
                                'vat': 'nds_20',
                            },
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac_1',
                            amount='1.00',
                            fiscal_receipt_info={
                                'personal_tin_id': 'personal-tin-id',
                                'title': 'Big Mac Burger 1',
                                'vat': 'nds_20',
                            },
                        ),
                        helpers.make_transactions_item(
                            item_id='big_mac_2',
                            amount='2.00',
                            fiscal_receipt_info={
                                'personal_tin_id': 'personal-tin-id',
                                'title': 'Big Mac Burger 2',
                                'vat': 'nds_20',
                            },
                        ),
                    ],
                ),
            ],
            [
                helpers.make_db_row(
                    item_id='big_mac_1',
                    place_id='some_place_id',
                    balance_client_id='some_id',
                    item_type='product',
                ),
                helpers.make_db_row(
                    item_id='big_mac_2',
                    place_id='some_place_id',
                    balance_client_id='some_id',
                    item_type='product',
                ),
            ],
            [
                make_product(
                    product_id='big_mac_1',
                    price='1.00',
                    inn='',
                    title='Big Mac Burger 1',
                ),
                make_product(
                    product_id='big_mac_2',
                    price='2.00',
                    inn='',
                    title='Big Mac Burger 2',
                ),
            ],
            1,
            0,
            1,
            id='Create and update cleared transactions',
        ),
        pytest.param(
            [
                helpers.make_transaction(
                    status='clear_success',
                    operation_id='create:123',
                    payment_type='card',
                    terminal_id='456',
                    sum=[
                        helpers.make_transactions_item(
                            item_id='big_mac_1',
                            amount='1.00',
                            fiscal_receipt_info={
                                'personal_tin_id': 'personal-tin-id',
                                'title': 'Big Mac Burger 1',
                                'vat': 'nds_20',
                            },
                        ),
                    ],
                ),
                helpers.make_transaction(
                    status='clear_success',
                    operation_id='update:123',
                    payment_type='card',
                    terminal_id='456',
                    sum=[
                        helpers.make_transactions_item(
                            item_id='big_mac_2',
                            amount='2.00',
                            fiscal_receipt_info={
                                'personal_tin_id': 'personal-tin-id',
                                'title': 'Big Mac Burger 2',
                                'vat': 'nds_20',
                            },
                        ),
                    ],
                ),
                helpers.make_transaction(
                    status='hold_success',
                    operation_id='add_item:123',
                    payment_type='card',
                    terminal_id='456',
                    sum=[
                        helpers.make_transactions_item(
                            item_id='big_mac_3',
                            amount='3.00',
                            fiscal_receipt_info={
                                'personal_tin_id': 'personal-tin-id',
                                'title': 'Big Mac Burger 3',
                                'vat': 'nds_20',
                            },
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac_1',
                            amount='1.00',
                            fiscal_receipt_info={
                                'personal_tin_id': 'personal-tin-id',
                                'title': 'Big Mac Burger 1',
                                'vat': 'nds_20',
                            },
                        ),
                        helpers.make_transactions_item(
                            item_id='big_mac_2',
                            amount='2.00',
                            fiscal_receipt_info={
                                'personal_tin_id': 'personal-tin-id',
                                'title': 'Big Mac Burger 2',
                                'vat': 'nds_20',
                            },
                        ),
                    ],
                ),
            ],
            [
                helpers.make_db_row(
                    item_id='big_mac_1',
                    place_id='some_place_id',
                    balance_client_id='some_id',
                    item_type='product',
                ),
                helpers.make_db_row(
                    item_id='big_mac_2',
                    place_id='some_place_id',
                    balance_client_id='some_id',
                    item_type='product',
                ),
                helpers.make_db_row(
                    item_id='big_mac_3',
                    place_id='some_place_id',
                    balance_client_id='some_id',
                    item_type='product',
                ),
            ],
            [
                make_product(
                    product_id='big_mac_1',
                    price='1.00',
                    inn='',
                    title='Big Mac Burger 1',
                ),
                make_product(
                    product_id='big_mac_2',
                    price='2.00',
                    inn='',
                    title='Big Mac Burger 2',
                ),
            ],
            1,
            0,
            1,
            id='Create, update, add_item transactions',
        ),
        pytest.param(
            [
                helpers.make_transaction(
                    status='clear_success',
                    operation_id='create:123',
                    payment_type='card',
                    terminal_id='456',
                    sum=[
                        helpers.make_transactions_item(
                            item_id='big_mac_1',
                            amount='1.00',
                            fiscal_receipt_info={
                                'personal_tin_id': 'personal-tin-id',
                                'title': 'Big Mac Burger 1',
                                'vat': 'nds_20',
                            },
                        ),
                    ],
                ),
                helpers.make_transaction(
                    status='hold_success',
                    operation_id='create:123',
                    payment_type='personal_wallet',
                    terminal_id='456',
                    sum=[
                        helpers.make_transactions_item(
                            item_id='big_mac_2',
                            amount='2.00',
                            fiscal_receipt_info={
                                'personal_tin_id': 'personal-tin-id',
                                'title': 'Big Mac Burger 2',
                                'vat': 'nds_20',
                            },
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac_1',
                            amount='1.00',
                            fiscal_receipt_info={
                                'personal_tin_id': 'personal-tin-id',
                                'title': 'Big Mac Burger 1',
                                'vat': 'nds_20',
                            },
                        ),
                        helpers.make_transactions_item(
                            item_id='big_mac_2',
                            amount='2.00',
                            fiscal_receipt_info={
                                'personal_tin_id': 'personal-tin-id',
                                'title': 'Big Mac Burger 2',
                                'vat': 'nds_20',
                            },
                        ),
                    ],
                ),
            ],
            [
                helpers.make_db_row(
                    item_id='big_mac_1',
                    place_id='some_place_id',
                    balance_client_id='some_id',
                    item_type='product',
                ),
                helpers.make_db_row(
                    item_id='big_mac_2',
                    place_id='some_place_id',
                    balance_client_id='some_id',
                    item_type='product',
                ),
            ],
            [
                make_product(
                    product_id='big_mac_1',
                    price='1.00',
                    inn='',
                    title='Big Mac Burger 1',
                ),
                make_product(
                    product_id='big_mac_2',
                    price='2.00',
                    inn='',
                    title='Big Mac Burger 2',
                ),
            ],
            0,
            1,
            0,
            id='Create and update transactions. '
            'One of transaction not finalized',
        ),
    ],
)
@pytest.mark.parametrize('service', ['grocery', 'eats'])
async def test_concurrently_transactions_clear(
        check_transactions_callback_task,
        check_send_receipt,
        mock_transactions_invoice_retrieve,
        insert_items,
        mock_personal_retrieve_tins,
        pgsql,
        testpoint,
        transactions,
        cleared,
        db_items,
        products,
        stq_receipts_times_called,
        stq,
        taxi_eats_payments,
        tp_times_called,
        send_receipt_times_called,
        service,
):
    order = db_order.DBOrder(
        pgsql=pgsql,
        order_id='test_order',
        currency='RUB',
        service='eats',
        originator=consts.EDA_CORE_ORIGINATOR,
    )
    order.upsert()
    insert_items(db_items)
    mock_transactions_invoice_retrieve(
        status='cleared',
        service=service,
        cleared=cleared,
        operations=[
            helpers.make_operation(id='create:123', sum_to_pay=cleared),
        ],
        transactions=transactions,
        personal_email_id='personal-email-id',
    )
    mock_personal_retrieve_tins()

    @testpoint('purchase_receipt_cleared_transaction')
    def receipt_test_point(data):
        pass

    await check_transactions_callback_task(
        operation_id='create:123', notification_type='transaction_clear',
    )
    await check_send_receipt(send_receipt_times_called)
    assert receipt_test_point.times_called == tp_times_called
    assert (
        stq.eats_send_receipts_requests.times_called
        == stq_receipts_times_called
    )
    if stq_receipts_times_called > 0:
        document_id = stq.eats_send_receipts_requests.next_call()['kwargs'][
            'document_id'
        ]
        response = await taxi_eats_payments.post(
            '/v1/receipts/retrieve/', json={'document_id': f'{document_id}'},
        )
        assert response.status_code == 200
        assert response.json()['products'] == products


async def test_badge_only_receipt_request(
        check_transactions_callback_task,
        check_send_receipt,
        mock_transactions_invoice_retrieve,
        insert_items,
        stq,
        upsert_order,
):
    upsert_order('test_order')
    insert_items([helpers.make_db_row(item_id='big_mac')])
    transactions_payment_items = (
        helpers.make_transactions_payment_items(
            payment_type='badge',
            items=[
                helpers.make_transactions_item(
                    item_id='big_mac',
                    amount='2.00',
                    fiscal_receipt_info={
                        'personal_tin_id': 'personal-tin-id',
                        'title': 'Big Mac Burger',
                        'vat': 'nds_20',
                    },
                ),
                helpers.make_transactions_item(
                    item_id='big_mac', amount='0.00',
                ),
            ],
        ),
    )
    transaction1 = helpers.make_transaction(
        operation_id='create:123', status='clear_success',
    )
    mock_transactions_invoice_retrieve(
        status='cleared',
        cleared=transactions_payment_items,
        payment_types=['badge'],
        operations=[
            helpers.make_operation(
                sum_to_pay=transactions_payment_items, id='create:123',
            ),
        ],
        transactions=[transaction1],
    )

    await check_transactions_callback_task(
        operation_id='create:123',
        transactions=[
            helpers.make_callback_transaction(status='clear_success'),
        ],
        notification_type='transaction_clear',
    )
    await check_send_receipt(1)
    assert stq.eats_send_receipts_requests.times_called == 0
