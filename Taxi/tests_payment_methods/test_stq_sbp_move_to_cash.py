import datetime

import bson
import dateutil
import pytest

from tests_payment_methods import common

EXPIRED_DELAY = 600
QUEUE_NAME = 'taxi_payments_sbp_move_to_cash'


@pytest.mark.parametrize(
    (
        'calculated_transporting_time',
        'reschedule_counter',
        'status',
        'payment_type',
        'invoice_state',
        'calls_count',
    ),
    (
        pytest.param(
            519.2,
            0,  # doesn't matter here
            'not_finished',  # doesn't matter here
            'sbp',  # doesn't matter here
            common.InvoiceState(status='cleared'),  # doesn't matter here
            common.CallsCount(),  # no calls
            id='Short ride, no calls',
        ),
        pytest.param(
            700,
            0,
            'not_finished',  # doesn't matter here
            'sbp',  # doesn't matter here
            common.InvoiceState(),  # doesn't matter here
            common.CallsCount(reschedule=1),
            id='Call for reschedule',
        ),
        pytest.param(
            700,
            1,
            'finished',
            'sbp',
            common.InvoiceState(),  # doesn't matter here
            common.CallsCount(get_fields=1),
            id='Incorrect order: finished',
        ),
        pytest.param(
            700,
            1,
            'not_finished',
            'card',
            common.InvoiceState(),  # doesn't matter here
            common.CallsCount(get_fields=1),
            id='Incorrect order: payment_type',
        ),
        pytest.param(
            700,
            1,
            'not_finished',
            'sbp',
            common.InvoiceState(status='cleared'),
            common.CallsCount(get_fields=1, transactions=1),
            id='Successfull payment',
        ),
        pytest.param(
            700,
            1,
            'not_finished',
            'sbp',
            common.InvoiceState(status='hold-failed'),
            common.CallsCount(get_fields=1, transactions=1, send_event=1),
            id='Send moved_to_cash. Faild invoice status',
        ),
        pytest.param(
            700,
            1,
            'not_finished',
            'sbp',
            common.InvoiceState(
                status='cleared', is_operations_in_progress=True,
            ),
            common.CallsCount(get_fields=1, transactions=1, send_event=1),
            id='Send moved_to_cash. Operations in progress',
        ),
        pytest.param(
            700,
            1,
            'not_finished',
            'sbp',
            common.InvoiceState(
                status='cleared', is_transactions_in_progress=True,
            ),
            common.CallsCount(get_fields=1, transactions=1, send_event=1),
            id='Send moved_to_cash. Transactions in progress',
        ),
        pytest.param(
            700,
            1,
            'not_finished',
            'sbp',
            common.InvoiceState(is_not_found=True),
            common.CallsCount(get_fields=1, transactions=1, send_event=1),
            id='Send moved_to_cash. Invoice not found',
        ),
    ),
)
@pytest.mark.config(
    TAXI_PAYMENTS_SBP_TRASACTION_EXPIRE_TIMEOUT=EXPIRED_DELAY,
    TAXI_PAYMENTS_INVOICE_STATUSES_MAP={
        'invoice_statuses': {
            'success': ['held', 'cleared'],
            'failure': ['hold-failed', 'clear-failed'],
            'in_progress': ['init', 'holding', 'clearing', 'refunding'],
        },
        'operation_statuses': {
            'success': ['done'],
            'failure': ['failed'],
            'in_progress': ['init', 'processing'],
        },
        'transaction_statuses': {
            'success': [
                'hold_success',
                'clear_success',
                'refund_success',
                'compensation_success',
            ],
            'failure': [
                'hold_fail',
                'clear_fail',
                'refund_fail',
                'compensation_fail',
            ],
            'in_progress': [
                'hold_init',
                'hold_pending',
                'hold_resize',
                'unhold_init',
                'unhold_pending',
                'clear_init',
                'clear_pending',
                'refund_pending',
                'refund_waiting',
                'compensation_init',
                'compensation_pending',
            ],
        },
    },
)
async def test_success(
        mockserver,
        load_json,
        stq_runner,
        calculated_transporting_time: float,
        reschedule_counter: int,
        status: str,
        payment_type: str,
        invoice_state: common.InvoiceState,
        calls_count: common.CallsCount,
):
    create_status_time = '2021-08-18T12:00:27.871+0000'
    order_id = 'b8b6152f9da92921b1edf8061af63376'

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def _mock_stq_reschedule(request):
        data = request.json
        assert data['queue_name'] == QUEUE_NAME

        eta = dateutil.parser.parse(data['eta']).replace(tzinfo=None)
        create_status_datetime = datetime.datetime.strptime(
            create_status_time, '%Y-%m-%dT%H:%M:%S.%f%z',
        ).replace(tzinfo=None)
        assert (eta - create_status_datetime).total_seconds() == EXPIRED_DELAY
        return {}

    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_core_get_fields(request):
        assert request.content_type == 'application/bson'
        assert request.query['order_id'] == order_id
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(
                {
                    'document': {
                        '_id': order_id,
                        'status': status,
                        'payment_tech': {'type': payment_type},
                    },
                    'revision': {'processing.version': 1, 'order.version': 1},
                },
            ),
        )

    @mockserver.json_handler('/transactions/v2/invoice/retrieve')
    def _mock_transactions_retrive(request):
        data = request.json
        assert data['id'] == order_id
        assert data['prefer_transactions_data']

        if invoice_state.is_not_found:
            return mockserver.make_response(
                status=404, json={'code': 'not_found', 'message': 'Not found'},
            )

        response = load_json('retrieve_response.json')
        response['status'] = invoice_state.status
        if not invoice_state.is_operations_in_progress:
            response['operations'] = []
        if not invoice_state.is_transactions_in_progress:
            response['transactions'] = []
        return response

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/moved_to_cash',
    )
    def _order_core_event(request):
        assert request.query['order_id'] == order_id
        assert (
            request.headers['X-Idempotency-Token']
            == f'{order_id}_sbp_moved_to_cash'
        )
        assert bson.BSON.decode(request.get_data()) == {
            'event_arg': {
                'reason_code': 'UNUSABLE_CARD',
                'with_coupon': False,
                'force_action': False,
                'invalidate_transactions': False,
            },
        }

        return mockserver.make_response('', status=200)

    await stq_runner.taxi_payments_sbp_move_to_cash.call(
        task_id=order_id,
        kwargs={
            'order_id': order_id,
            'create_status_time': create_status_time,
            'calculated_transporting_time': calculated_transporting_time,
        },
        reschedule_counter=reschedule_counter,
    )

    assert _mock_stq_reschedule.times_called == calls_count.reschedule
    assert _mock_order_core_get_fields.times_called == calls_count.get_fields
    assert _mock_transactions_retrive.times_called == calls_count.transactions
    assert _order_core_event.times_called == calls_count.send_event
