import datetime as dt
import decimal

import pytest
import pytz

from taxi.clients import stq_agent
from taxi.util import dates


@pytest.mark.config(TVM_RULES=[{'src': 'persey-payments', 'dst': 'stq-agent'}])
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.now('2019-11-11T07:00:00+0')
async def test_simple(
        stq,
        stq3_context,
        stq_runner,
        mockserver,
        trust_deliver_basket_success,
        mock_trust_check_basket,
        mock_balance,
        pgsql,
):
    check_mock = mock_trust_check_basket(
        {
            'payment_status': 'cleared',
            'orders': [
                {'order_id': 'some_order_test', 'paid_amount': '11.2'},
                {'order_id': 'some_order_delivery', 'paid_amount': '3.3'},
            ],
        },
    )
    deliver_mock = trust_deliver_basket_success('deliver_basket_simple.json')
    balance_mock = mock_balance(
        {'Balance2.UpdatePayment': 'update_payment_simple.xml'},
    )

    await stq_runner.persey_payments_deliver.call(
        task_id='some_order', args=('some_order', '123'),
    )

    assert deliver_mock.times_called == 1
    assert balance_mock.times_called == 1
    assert check_mock.times_called == 1

    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute(
        'SELECT status, hold_amount, payout_ready_dt '
        'FROM persey_payments.basket',
    )
    rows = list(cursor)
    assert rows == [
        (
            'delivered',
            decimal.Decimal('14.5'),
            dt.datetime(2019, 11, 11, 7, tzinfo=pytz.UTC),
        ),
    ]


@pytest.mark.config(TVM_RULES=[{'src': 'persey-payments', 'dst': 'stq-agent'}])
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.now('2019-11-11T12:00:00+0')
async def test_deliver_reschedule(
        stq,
        stq3_context,
        stq_runner,
        mockserver,
        mock_trust_check_basket,
        pgsql,
):
    check_mock = mock_trust_check_basket(
        {
            'payment_status': 'cleared',
            'orders': [
                {'order_id': 'some_order_test', 'paid_amount': '1'},
                {'order_id': 'some_order_delivery', 'paid_amount': '1'},
            ],
        },
    )

    @mockserver.json_handler(
        '/trust-payments/v2/payments/trust-basket-token/deliver/',
    )
    def _deliver_mock(request):
        resp_body = {
            'status': 'error',
            'status_code': 'not_postauthorized_yet',
        }
        return mockserver.make_response(status=200, json=resp_body)

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        eta = dates.utcnow() + dt.timedelta(seconds=20)

        assert request.json == {
            'queue_name': 'persey_payments_deliver',
            'eta': eta.strftime(stq_agent.ETA_FORMAT),
            'task_id': 'some_order',
        }

        return {}

    await stq_runner.persey_payments_deliver.call(
        task_id='some_order', args=('some_order', '123'),
    )

    assert _deliver_mock.times_called == 1
    assert check_mock.times_called == 1
    assert _stq_reschedule.times_called == 1

    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute('SELECT status FROM persey_payments.basket')
    rows = list(cursor)
    assert rows == [('clear_called',)]


@pytest.mark.config(TVM_RULES=[{'src': 'persey-payments', 'dst': 'stq-agent'}])
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.now('2019-11-11T12:00:00+0')
async def test_balance_reschedule(
        stq,
        stq3_context,
        stq_runner,
        mockserver,
        trust_deliver_basket_success,
        mock_trust_check_basket,
        mock_balance,
        pgsql,
):
    check_mock = mock_trust_check_basket(
        {
            'payment_status': 'cleared',
            'orders': [
                {'order_id': 'some_order_test', 'paid_amount': '1'},
                {'order_id': 'some_order_delivery', 'paid_amount': '0.0'},
            ],
        },
    )
    deliver_mock = trust_deliver_basket_success(
        'deliver_basket_one_order.json',
    )
    balance_mock = mock_balance(
        {'Balance2.UpdatePayment': 'update_payment_reschedule.xml'},
    )

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        eta = dates.utcnow() + dt.timedelta(seconds=20)

        assert request.json == {
            'queue_name': 'persey_payments_deliver',
            'eta': eta.strftime(stq_agent.ETA_FORMAT),
            'task_id': 'some_order',
        }

        return {}

    await stq_runner.persey_payments_deliver.call(
        task_id='some_order', args=('some_order', '123'),
    )

    assert deliver_mock.times_called == 1
    assert check_mock.times_called == 1
    assert balance_mock.times_called == 1
    assert _stq_reschedule.times_called == 1

    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute('SELECT status FROM persey_payments.basket')
    rows = list(cursor)
    assert rows == [('clear_called',)]


@pytest.mark.config(TVM_RULES=[{'src': 'persey-payments', 'dst': 'stq-agent'}])
@pytest.mark.pgsql('persey_payments', files=['refund.sql'])
@pytest.mark.now('2019-11-11T07:00:00+0')
@pytest.mark.parametrize(
    'refund_status, final_state, balance_called, reschedule_called, '
    'do_refund_called',
    [
        ('success', 'delivered', 1, 0, 0),
        ('failed', 'clear_called', 0, 1, 1),
        ('wait_for_notification', 'clear_called', 0, 1, 0),
    ],
)
async def test_refund(
        stq,
        stq3_context,
        stq_runner,
        mockserver,
        trust_deliver_basket_success,
        mock_trust_check_basket,
        mock_balance,
        mock_do_refund,
        mock_check_refund,
        pgsql,
        refund_status,
        final_state,
        balance_called,
        reschedule_called,
        do_refund_called,
):
    check_mock = mock_trust_check_basket(
        {
            'payment_status': 'cleared',
            'refunds': [{'trust_refund_id': 'trust-refund-id'}],
        },
    )
    balance_mock = mock_balance(
        {'Balance2.UpdatePayment': 'update_payment_simple.xml'},
    )
    check_refund_mock = mock_check_refund(refund_status)
    do_refund_mock = mock_do_refund('wait_for_notification')

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        eta = dates.utcnow() + dt.timedelta(seconds=20)

        assert request.json == {
            'queue_name': 'persey_payments_deliver',
            'eta': eta.strftime(stq_agent.ETA_FORMAT),
            'task_id': 'some_order',
        }

        return {}

    await stq_runner.persey_payments_deliver.call(
        task_id='some_order', args=('some_order', '123'),
    )

    assert balance_mock.times_called == balance_called
    assert check_mock.times_called == 1
    assert check_refund_mock.times_called == 1
    assert do_refund_mock.times_called == do_refund_called
    assert _stq_reschedule.times_called == reschedule_called

    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute('SELECT status FROM persey_payments.basket')
    rows = list(cursor)
    assert rows == [(final_state,)]


@pytest.mark.config(
    TVM_RULES=[{'src': 'persey-payments', 'dst': 'stq-agent'}],
    PERSEY_PAYMENTS_DELIVER_RECEIPT=True,
    PERSEY_COMMUNICATIONS={
        'persey_email': 'Помощь рядом &lt;covid@support.yandex.ru&gt;',
    },
)
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.now('2019-11-11T07:00:00+0')
async def test_deliver_receipt(
        stq,
        stq3_context,
        stq_runner,
        mockserver,
        load_json,
        trust_deliver_basket_success,
        mock_trust_check_basket,
        mock_balance,
        pgsql,
):
    check_mock = mock_trust_check_basket(
        {
            'payment_status': 'cleared',
            'user_email': 'my@ru',
            'orders': [
                {
                    'order_id': 'some_order_test',
                    'paid_amount': '11.2',
                    'delivery_id': '777',
                },
                {
                    'order_id': 'some_order_delivery',
                    'paid_amount': '3.3',
                    'delivery_id': '777',
                },
            ],
        },
    )
    deliver_mock = trust_deliver_basket_success('deliver_basket_simple.json')
    balance_mock = mock_balance(
        {'Balance2.UpdatePayment': 'update_payment_simple.xml'},
    )

    @mockserver.json_handler('/trust/checks/777/receipts/777/')
    def _get_receipt(request):
        return mockserver.make_response('some_html')

    @mockserver.json_handler('/sticker/send-raw/')
    def _send_raw(request):
        assert request.json == load_json('expected_sticker_request.json')

        return {}

    await stq_runner.persey_payments_deliver.call(
        task_id='some_order', args=('some_order', '123'),
    )

    assert deliver_mock.times_called == 1
    assert balance_mock.times_called == 1
    assert check_mock.times_called == 2
    assert _get_receipt.times_called == 1
    assert _send_raw.times_called == 1


@pytest.mark.config(
    TVM_RULES=[{'src': 'persey-payments', 'dst': 'stq-agent'}],
    PERSEY_PAYMENTS_DELIVER_RECEIPT=True,
    PERSEY_COMMUNICATIONS={
        'persey_email': 'Помощь рядом &lt;covid@support.yandex.ru&gt;',
    },
)
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.now('2019-11-11T07:00:00+0')
async def test_deliver_receipt_reschedule(
        stq,
        stq3_context,
        stq_runner,
        mockserver,
        load_json,
        trust_deliver_basket_success,
        mock_trust_check_basket,
        mock_balance,
        pgsql,
):
    check_mock = mock_trust_check_basket(
        {
            'payment_status': 'cleared',
            'user_email': 'my@ru',
            'orders': [
                {
                    'order_id': 'some_order_test',
                    'paid_amount': '11.2',
                    'delivery_id': '777',
                },
                {
                    'order_id': 'some_order_delivery',
                    'paid_amount': '3.3',
                    'delivery_id': '777',
                },
            ],
        },
    )

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        eta = dates.utcnow() + dt.timedelta(seconds=20)

        assert request.json == {
            'queue_name': 'persey_payments_deliver',
            'eta': eta.strftime(stq_agent.ETA_FORMAT),
            'task_id': 'some_order',
        }

        return {}

    deliver_mock = trust_deliver_basket_success('deliver_basket_simple.json')

    @mockserver.json_handler('/trust/checks/777/receipts/777/')
    def _get_receipt(request):
        return mockserver.make_response(status=404, json={})

    await stq_runner.persey_payments_deliver.call(
        task_id='some_order', args=('some_order', '123'),
    )

    assert deliver_mock.times_called == 1
    assert check_mock.times_called == 2
    assert _get_receipt.times_called == 1
    assert _stq_reschedule.times_called == 1
