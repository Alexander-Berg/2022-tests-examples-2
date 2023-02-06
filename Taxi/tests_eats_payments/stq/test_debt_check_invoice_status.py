import pytest

from tests_eats_payments import consts
from tests_eats_payments import helpers

NOW = '2020-03-31T07:20:00+00:00'


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    ['invoice_status', 'core_stq_times_called', 'payment_available'],
    [
        ('init', 1, True),
        ('init', 1, None),
        ('init', 0, False),
        ('holding', 1, None),
        ('held', 0, None),
        ('hold-failed', 0, None),
        ('clearing', 0, None),
        ('cleared', 0, None),
        ('clear-failed', 0, None),
        ('refunding', 0, None),
    ],
)
async def test_check_invoice_status(
        stq_runner,
        stq,
        mock_transactions_invoice_retrieve,
        invoice_status,
        core_stq_times_called,
        upsert_order_payment,
        upsert_order,
        insert_items,
        payment_available,
):
    upsert_order_payment(
        'test_order',
        '27affbc7-de68-4a79-abba-d9bdf48e6e09',
        'card',
        'RUB',
        payment_available,
    )

    upsert_order(
        order_id='test_order', business_type=consts.BUSINESS, api_version=2,
    )
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
    mock_transactions_invoice_retrieve(status=invoice_status)
    await stq_runner.eats_payments_debt_check_invoice_status.call(
        task_id='test_order',
        kwargs={
            'invoice_id': 'test_order',
            'ttl': '2020-03-31T07:21:00+00:00',
        },
    )
    helpers.check_callback_mock(
        callback_mock=stq.eda_order_processing_payment_events_callback,
        times_called=core_stq_times_called,
        task_id='test_order:debt',
        queue='eda_order_processing_payment_events_callback',
        **{
            'order_id': 'test_order',
            'action': 'debt',
            'status': 'confirmed',
            'revision': 'test_order',
            'meta': [{'discriminator': 'debt_type', 'value': 'auto'}],
        },
    )


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    ['invoice_status', 'core_stq_times_called', 'allow_empty_transactions'],
    [('init', 1, True), ('init', 0, False)],
)
async def test_check_invoice_status_no_transactions(
        stq_runner,
        stq,
        mock_transactions_invoice_retrieve,
        invoice_status,
        core_stq_times_called,
        upsert_order,
        insert_items,
        taxi_config,
        allow_empty_transactions,
):
    taxi_config.set_values(
        {
            'EATS_PAYMENTS_FEATURE_FLAGS': {
                'invoice_with_empty_transactions_could_be_treated_as_debt': {
                    'description': '',
                    'enabled': allow_empty_transactions,
                },
            },
        },
    )
    upsert_order(
        order_id='test_order', business_type=consts.BUSINESS, api_version=2,
    )
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
    mock_transactions_invoice_retrieve(status=invoice_status, transactions=[])
    await stq_runner.eats_payments_debt_check_invoice_status.call(
        task_id='test_order',
        kwargs={
            'invoice_id': 'test_order',
            'ttl': '2020-03-31T07:21:00+00:00',
        },
    )
    helpers.check_callback_mock(
        callback_mock=stq.eda_order_processing_payment_events_callback,
        times_called=core_stq_times_called,
        task_id='test_order:debt',
        queue='eda_order_processing_payment_events_callback',
        **{
            'order_id': 'test_order',
            'action': 'debt',
            'status': 'confirmed',
            'revision': 'test_order',
            'meta': [{'discriminator': 'debt_type', 'value': 'auto'}],
        },
    )


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    ['ttl', 'test_point_times_called'],
    [
        ('2020-03-31T07:19:30+00:00', 1),
        ('2020-03-31T07:19:59+00:00', 1),
        ('2020-03-31T07:20:00+00:00', 0),
        ('2020-03-31T07:20:01+00:00', 0),
        ('2020-03-31T07:20:30+00:00', 0),
    ],
)
async def test_task_ttl(
        stq_runner,
        testpoint,
        mock_transactions_invoice_retrieve,
        ttl,
        test_point_times_called,
):
    mock_transactions_invoice_retrieve(status='cleared')

    @testpoint('debt_invoice_status_task_timeout')
    def timeout_testpoint(data):
        pass

    await stq_runner.eats_payments_debt_check_invoice_status.call(
        task_id='test_order', kwargs={'invoice_id': 'test_order', 'ttl': ttl},
    )
    assert timeout_testpoint.times_called == test_point_times_called


@pytest.mark.now(NOW)
async def test_invoice_retrieve_timeout(stq_runner, stq, mockserver):
    # pylint: disable=invalid-name
    @mockserver.json_handler('/transactions-eda/v2/invoice/retrieve')
    # pylint: disable=unused-variable
    def transactions_retrieve_invoice_handler(request):
        raise mockserver.TimeoutError()

    await stq_runner.eats_payments_debt_check_invoice_status.call(
        task_id='test_order',
        kwargs={
            'invoice_id': 'test_order',
            'ttl': '2020-03-31T07:20:30+00:00',
        },
    )
    helpers.check_callback_mock(
        callback_mock=stq.eda_order_processing_payment_events_callback,
        times_called=1,
        task_id='test_order:debt',
        queue='eda_order_processing_payment_events_callback',
        **{
            'order_id': 'test_order',
            'action': 'debt',
            'status': 'confirmed',
            'revision': 'test_order',
            'meta': [{'discriminator': 'debt_type', 'value': 'auto'}],
        },
    )
