import bson
import pytest

from tests_payment_methods import common


@pytest.mark.parametrize(
    ('payment_type', 'invoice_state', 'moved_to_cash'),
    (
        pytest.param(
            'card',
            common.InvoiceState(),  # doesn't matter here
            False,
            id='Incorrect order: payment_type',
        ),
        pytest.param(
            'sbp',
            common.InvoiceState(status='cleared'),
            False,
            id='Successfull payment',
        ),
        pytest.param(
            'sbp',
            common.InvoiceState(status='hold-failed'),
            True,
            id='moved_to_cash. Failed invoice status',
        ),
        pytest.param(
            'sbp',
            common.InvoiceState(
                status='cleared', is_operations_in_progress=True,
            ),
            True,
            id='moved_to_cash. Operations in progress',
        ),
        pytest.param(
            'sbp',
            common.InvoiceState(
                status='cleared', is_transactions_in_progress=True,
            ),
            True,
            id='moved_to_cash. Transactions in progress',
        ),
        pytest.param(
            'sbp',
            common.InvoiceState(is_not_found=True),
            True,
            id='moved_to_cash. Invoice not found',
        ),
    ),
)
@pytest.mark.config(
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
async def test_spb_widget_retrieve(
        taxi_payment_methods,
        mockserver,
        load_json,
        payment_type: str,
        invoice_state: common.InvoiceState,
        moved_to_cash,
):

    order_id = 'b8b6152f9da92921b1edf8061af63376'

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
                        'status': 'transporting',
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

    response = await taxi_payment_methods.post(
        '/v1/sbp/complete_order_check_move_to_cash',
        json={'order_id': order_id},
    )
    assert response.status == 200
    assert {'moved_to_cash': moved_to_cash} == response.json()
