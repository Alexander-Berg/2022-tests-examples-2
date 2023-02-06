import pytest

from tests_eats_payments import db_order
from tests_eats_payments import helpers

NOW = '2020-08-12T07:20:00+00:00'
TERMINAL_ID = '711'
TEST_PAYMENT_ID = '27affbc7-de68-4a79-abba-d9bdf48e6e09'
TEST_POSTPAYMENT_TERMINAL_ID = '2can'


def make_billing_experiment(send_enabled) -> dict:
    return {
        'name': 'eats_payments_billing_notifications',
        'consumers': ['eats-payments/billing-notifications'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': {'type': 'true'},
                'value': {'send_billing_notifications_enabled': send_enabled},
            },
        ],
    }


@pytest.fixture(name='mock_personal_tins_list')
def _mock_personal_tins_list(mockserver):
    def _inner(personal_tin_id):
        @mockserver.json_handler('/personal/v1/tins/retrieve')
        def mock_tins_personal(request):
            assert request.json['id'] == personal_tin_id
            return {'id': 'tin_id_1', 'value': 'tin'}

        return mock_tins_personal

    return _inner


def make_customer_service():
    return helpers.make_customer_service(
        customer_service_id='big_mac',
        name='big_mac',
        cost_for_customer='10.00',
        currency='RUB',
        customer_service_type='composition_products',
        trust_product_id='burger',
        place_id='some_place_id',
        balance_client_id='some_id',
        personal_tin_id='personal-tin-id',
        details={
            'composition_products': [
                {
                    'id': 'big_mac',
                    'name': 'Big Mac Burger',
                    'cost_for_customer': '2.00',
                    'type': 'product',
                    'vat': 'nds_20',
                },
            ],
            'discriminator_type': 'composition_products_details',
        },
    )


async def test_billing_notification_for_cleared(
        mock_transactions_invoice_retrieve,
        pgsql,
        experiments3,
        stq_runner,
        upsert_order_payment,
):
    order = db_order.DBOrder(
        pgsql=pgsql, order_id='test_order', currency='RUB',
    )
    order.upsert()

    upsert_order_payment(
        order_id='test_order',
        payment_id='test_payment_id',
        payment_type='card',
        currency='RUB',
    )

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        status='cleared',
        currency='RUB',
        transactions=[
            helpers.make_transaction(
                status='clear_success',
                operation_id='operation-1',
                external_payment_id='payment-1',
            ),
            helpers.make_transaction(
                status='clear_success',
                operation_id='operation-2',
                external_payment_id='payment-2',
            ),
        ],
    )

    experiments3.add_config(**make_billing_experiment(True))

    await stq_runner.eats_payments_check_no_payment.call(
        task_id='test_order', kwargs={'invoice_id': 'test_order'},
    )

    assert invoice_retrieve_mock.times_called == 1


@pytest.mark.parametrize('api_version', [1, 2])
@pytest.mark.now(NOW)
async def test_billing_notification_for_clear_failed(
        mock_transactions_invoice_retrieve,
        check_billing_callback,
        insert_items,
        pgsql,
        stq_runner,
        experiments3,
        mock_order_revision_customer_services_details,
        mock_personal_tins_list,
        api_version,
        upsert_order_payment,
):
    order = db_order.DBOrder(
        pgsql=pgsql,
        order_id='test_order',
        currency='RUB',
        service='eats',
        api_version=api_version,
    )
    order.upsert()
    upsert_order_payment(
        order_id='test_order',
        payment_id='test_payment_id',
        payment_type='card',
        currency='RUB',
    )

    insert_items(
        [
            helpers.make_db_row(
                order_id='test_order',
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        status='clear-failed',
        currency='RUB',
        transactions=[
            helpers.make_transaction(
                status='clear_fail',
                operation_id='create:operation-1',
                external_payment_id='payment-1',
                terminal_id=TERMINAL_ID,
            ),
            helpers.make_transaction(
                status='clear_success',
                operation_id='create:operation-2',
                external_payment_id='payment-2',
                terminal_id=TERMINAL_ID,
            ),
        ],
    )

    customer_services = [make_customer_service()]
    customer_service_details_mock = (
        mock_order_revision_customer_services_details(
            customer_services=customer_services,
            expected_revision_id='operation-1',
        )
    )

    experiments3.add_config(**make_billing_experiment(True))

    await stq_runner.eats_payments_check_no_payment.call(
        task_id='test_order', kwargs={'invoice_id': 'test_order'},
    )

    assert invoice_retrieve_mock.times_called == 1

    if api_version == 2:
        assert customer_service_details_mock.times_called == 1

    check_billing_callback(
        task_id='test_order/create:operation-1/no_payment/payment-1',
        **{
            'order_id': 'test_order',
            'external_payment_id': 'payment-1',
            'transaction_type': 'no_payment',
            'event_at': NOW,
            'payment_type': 'card',
            'currency': 'RUB',
            'terminal_id': TERMINAL_ID,
            'items': [
                helpers.make_billing_item(
                    item_id='big_mac',
                    amount='5.00',
                    place_id='some_place_id',
                    balance_client_id='some_id',
                    item_type='product',
                ),
            ],
        },
    )


@pytest.mark.parametrize('api_version', [1, 2])
@pytest.mark.now(NOW)
async def test_billing_notification_for_hold_failed(
        mock_transactions_invoice_retrieve,
        check_billing_callback,
        insert_items,
        pgsql,
        stq_runner,
        experiments3,
        mock_order_revision_customer_services_details,
        mock_personal_tins_list,
        api_version,
        upsert_order_payment,
):
    order = db_order.DBOrder(
        pgsql=pgsql,
        order_id='test_order',
        currency='RUB',
        service='eats',
        api_version=api_version,
    )
    order.upsert()
    upsert_order_payment(
        order_id='test_order',
        payment_id='test_payment_id',
        payment_type='card',
        currency='RUB',
    )
    insert_items(
        [
            helpers.make_db_row(
                order_id='test_order',
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        status='hold-failed',
        currency='RUB',
        transactions=[
            helpers.make_transaction(
                status='clear_success',
                operation_id='create:operation-1',
                external_payment_id='payment-1',
                terminal_id=TERMINAL_ID,
            ),
            helpers.make_transaction(
                status='hold_fail',
                operation_id='create:operation-2',
                external_payment_id='payment-2',
                terminal_id=TERMINAL_ID,
            ),
            helpers.make_transaction(
                status='hold_fail',
                operation_id='create:operation-3',
                external_payment_id='payment-3',
                terminal_id=TERMINAL_ID,
            ),
        ],
    )
    customer_services = [make_customer_service()]
    customer_service_details_mock = (
        mock_order_revision_customer_services_details(
            customer_services=customer_services,
            expected_revision_id='operation-3',
        )
    )

    experiments3.add_config(**make_billing_experiment(True))

    await stq_runner.eats_payments_check_no_payment.call(
        task_id='test_order',
        kwargs={'invoice_id': 'test_order', 'compensate_hold_fail': True},
    )

    assert invoice_retrieve_mock.times_called == 1

    if api_version == 2:
        assert customer_service_details_mock.times_called == 1

    check_billing_callback(
        task_id='test_order/create:operation-3/no_payment/payment-3',
        **{
            'order_id': 'test_order',
            'external_payment_id': 'payment-3',
            'transaction_type': 'no_payment',
            'event_at': NOW,
            'payment_type': 'card',
            'currency': 'RUB',
            'terminal_id': TERMINAL_ID,
            'items': [
                helpers.make_billing_item(
                    item_id='big_mac',
                    amount='5.00',
                    place_id='some_place_id',
                    balance_client_id='some_id',
                    item_type='product',
                ),
            ],
        },
    )


@pytest.mark.now(NOW)
async def test_without_billing_notification_for_hold_failed(
        mock_transactions_invoice_retrieve,
        check_billing_callback,
        insert_items,
        pgsql,
        stq_runner,
        experiments3,
        upsert_order_payment,
):
    order = db_order.DBOrder(
        pgsql=pgsql, order_id='test_order', currency='RUB', service='eats',
    )
    order.upsert()
    upsert_order_payment(
        order_id='test_order',
        payment_id='test_payment_id',
        payment_type='card',
        currency='RUB',
    )
    insert_items(
        [
            helpers.make_db_row(
                order_id='test_order',
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        status='hold-failed',
        currency='RUB',
        transactions=[
            helpers.make_transaction(
                status='clear_success',
                operation_id='operation-1',
                external_payment_id='payment-1',
                terminal_id=TERMINAL_ID,
            ),
            helpers.make_transaction(
                status='hold_fail',
                operation_id='operation-2',
                external_payment_id='payment-2',
                terminal_id=TERMINAL_ID,
            ),
        ],
    )

    experiments3.add_config(**make_billing_experiment(True))

    await stq_runner.eats_payments_check_no_payment.call(
        task_id='test_order',
        kwargs={'invoice_id': 'test_order', 'compensate_hold_fail': False},
    )

    assert invoice_retrieve_mock.times_called == 1
    check_billing_callback(times_called=0)


async def test_cashback_transaction(
        mock_transactions_invoice_retrieve,
        check_billing_callback,
        experiments3,
        pgsql,
        stq_runner,
        upsert_order_payment,
):
    order = db_order.DBOrder(
        pgsql=pgsql, order_id='test_order', currency='RUB', service='eats',
    )
    order.upsert()
    upsert_order_payment(
        order_id='test_order',
        payment_id='test_payment_id',
        payment_type='card',
        currency='RUB',
    )

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        status='clear-failed',
        currency='RUB',
        transactions=[
            helpers.make_transaction(
                status='clear_fail', payment_type='personal_wallet',
            ),
        ],
    )

    experiments3.add_config(**make_billing_experiment(True))

    await stq_runner.eats_payments_check_no_payment.call(
        task_id='test_order', kwargs={'invoice_id': 'test_order'},
    )

    assert invoice_retrieve_mock.times_called == 1

    check_billing_callback(times_called=0)


@pytest.mark.parametrize('api_version', [1, 2])
async def test_no_items(
        mock_transactions_invoice_retrieve,
        check_billing_callback,
        experiments3,
        pgsql,
        stq_runner,
        mock_order_revision_customer_services_details,
        mock_personal_tins_list,
        api_version,
        upsert_order_payment,
):
    order = db_order.DBOrder(
        pgsql=pgsql,
        order_id='test_order',
        currency='RUB',
        service='eats',
        api_version=api_version,
    )
    order.upsert()
    upsert_order_payment(
        order_id='test_order',
        payment_id='test_payment_id',
        payment_type='card',
        currency='RUB',
    )
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        operation_id='create:1234',
        status='clear-failed',
        currency='RUB',
        transactions=[
            helpers.make_transaction(
                operation_id='create:1234', status='clear_fail', sum=[],
            ),
        ],
    )
    customer_services = [make_customer_service()]
    customer_service_details_mock = (
        mock_order_revision_customer_services_details(
            customer_services=customer_services, expected_revision_id='1234',
        )
    )

    experiments3.add_config(**make_billing_experiment(True))

    await stq_runner.eats_payments_check_no_payment.call(
        task_id='test_order', kwargs={'invoice_id': 'test_order'},
    )

    assert invoice_retrieve_mock.times_called == 1
    if api_version == 2:
        assert customer_service_details_mock.times_called == 1

    check_billing_callback(times_called=0)


@pytest.mark.parametrize('api_version', [1, 2])
async def test_zero_amount_items(
        mock_transactions_invoice_retrieve,
        check_billing_callback,
        experiments3,
        pgsql,
        stq_runner,
        mock_order_revision_customer_services_details,
        mock_personal_tins_list,
        api_version,
        upsert_order_payment,
):
    order = db_order.DBOrder(
        pgsql=pgsql,
        order_id='test_order',
        service='eats',
        api_version=api_version,
    )
    order.upsert()
    upsert_order_payment(
        order_id='test_order',
        payment_id='test_payment_id',
        payment_type='card',
        currency='RUB',
    )

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        status='clear-failed',
        currency='RUB',
        transactions=[
            helpers.make_transaction(
                operation_id='create:1234',
                status='clear_fail',
                sum=[
                    {'amount': '0.00', 'item_id': 'big_mac'},
                    {'amount': '0.00', 'item_id': 'coca_cola'},
                    {'amount': '0.00', 'item_id': 'french_fries'},
                ],
            ),
        ],
    )
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        status='clear-failed',
        currency='RUB',
        transactions=[
            helpers.make_transaction(
                operation_id='create:1234', status='clear_fail', sum=[],
            ),
        ],
    )
    customer_services = [make_customer_service()]
    customer_service_details_mock = (
        mock_order_revision_customer_services_details(
            customer_services=customer_services, expected_revision_id='1234',
        )
    )

    experiments3.add_config(**make_billing_experiment(True))

    await stq_runner.eats_payments_check_no_payment.call(
        task_id='test_order', kwargs={'invoice_id': 'test_order'},
    )

    assert invoice_retrieve_mock.times_called == 1
    if api_version == 2:
        assert customer_service_details_mock.times_called == 1

    check_billing_callback(times_called=0)


async def test_no_payment_without_order_payment(stq_runner):
    await stq_runner.eats_payments_check_no_payment.call(
        task_id='test_order', kwargs={'invoice_id': 'test_order'},
    )
    # nothing happens
