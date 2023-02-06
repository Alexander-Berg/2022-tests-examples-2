import datetime

import pytest

_CLAIM_ID = '731d5f778c8b4ac9b5569d38357b92b2'
_INVOICE_ID = f'claims/agent/{_CLAIM_ID}'


@pytest.fixture(name='mock_py2_update_transactions')
def _mock_py2_update_transactions(mockserver, mock_with_context):
    return mock_with_context(
        decorator=mockserver.json_handler(
            '/py2-delivery/update-billing-transactions',
        ),
        response_data={'value_in_db': []},
    )


@pytest.fixture(name='mock_py2_update_sum_to_pay')
def _mock_py2_update_sum_to_pay(mockserver, mock_with_context):
    return mock_with_context(
        decorator=mockserver.json_handler('/py2-delivery/update-sum-to-pay'),
        response_data={'value_in_db': {'ride': 0}},
    )


@pytest.fixture(name='mock_py2_update_payments_stats')
def _mock_py2_update_payments_stats(mockserver, mock_with_context):
    return mock_with_context(
        decorator=mockserver.json_handler(
            '/py2-delivery/update-payments-stats',
        ),
        response_data={},
    )


@pytest.fixture(name='mock_cut_claim')
def _mock_cut_claim(mockserver, mock_with_context, taxi_order_id):
    return mock_with_context(
        decorator=mockserver.json_handler('/cargo-claims/v1/claims/cut'),
        response_data={
            'id': _CLAIM_ID,
            'status': 'new',
            'version': 1,
            'user_request_revision': '1',
            'skip_client_notify': False,
            'taxi_order_id': taxi_order_id,
        },
    )


@pytest.fixture(name='mock_v2_invoice_retrieve')
def _mock_v2_invoice_retrieve(mockserver, mock_with_context, load_json):
    return mock_with_context(
        decorator=mockserver.json_handler(
            '/transactions-ng/v2/invoice/retrieve',
        ),
        response_data=load_json('response_t-ng_v2_invoice_retrieve.json'),
    )


@pytest.fixture(name='mock_pay_order_applying_call')
def _mock_pay_order_applying_call(mockserver, mock_with_context):
    return mock_with_context(
        decorator=mockserver.json_handler(
            '/cargo-finance/internal/cargo-finance/pay/order/applying/call',
        ),
        response_data={},
    )


@pytest.fixture(name='mock_rebill_order')
def _mock_rebill_order(mockserver, mock_with_context, taxi_order_id):
    url = r'/billing-orders/v1/rebill_order'

    @mockserver.json_handler(url)
    def handler(request):
        request_json = request.json
        assert request_json.pop('idempotency_token')
        assert request_json == {
            'order': {
                'alias_id': 'alias_id_22222222222222222222222',
                'due': '2021-02-13T09:20:00+00:00',
                'id': taxi_order_id,
                'version': 5,
                'zone_name': 'moscow',
            },
            'reason': {'data': {}, 'kind': 'phoenix_patched_taxi_databases'},
        }
        return {}

    return handler


async def run_invoice_callback_stq(stq_runner):
    await stq_runner.cargo_finance_update_invoice_callback.call(
        task_id='test_stq',
        kwargs={
            'invoice_id': _INVOICE_ID,
            'operation_id': 'operation_id',
            'operation_status': 'done',
            'notification_type': 'operation_finish',
            'transactions': [],
        },
        expect_fail=False,
    )


async def run_patch_stq(stq_runner, expect_fail=False):
    await stq_runner.cargo_finance_patch_taxi_databases_with_invoice.call(
        task_id='_INVOICE_ID',
        kwargs={'invoice_id': _INVOICE_ID},
        expect_fail=expect_fail,
    )


@pytest.mark.parametrize(
    'allow_async_patch',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                CARGO_FINANCE_PATCH_TAXI_DATABASES_SETTINGS={
                    'allow_async_patch': True,
                },
            ),
        ),
        pytest.param(False),
    ],
)
async def test_sync_async_config(
        stq,
        stq_runner,
        mock_py2_update_transactions,
        mock_py2_update_sum_to_pay,
        mock_py2_update_payments_stats,
        mock_v2_invoice_retrieve,
        mock_cut_claim,
        mock_pay_order_applying_call,
        mock_rebill_order,
        order_proc,
        taxi_order_id,
        allow_async_patch,
):
    await run_invoice_callback_stq(stq_runner)

    if allow_async_patch:
        assert (
            stq.cargo_finance_patch_taxi_databases_with_invoice.times_called
            == 1
        )
        assert stq.cargo_finance_receipt_by_tng_data.times_called == 1
        assert mock_v2_invoice_retrieve.request is None
        assert mock_cut_claim.request is None
        assert mock_py2_update_sum_to_pay.request is None
        assert mock_py2_update_transactions.request is None
        assert mock_py2_update_payments_stats.request is None
    else:
        assert (
            stq.cargo_finance_patch_taxi_databases_with_invoice.times_called
            == 0
        )
        assert mock_v2_invoice_retrieve.request.json['id'] == _INVOICE_ID
        assert mock_cut_claim.request.query['claim_id'] == _CLAIM_ID
        assert (
            mock_py2_update_sum_to_pay.request.query['order_id']
            == taxi_order_id
        )
        assert (
            mock_py2_update_transactions.request.query['order_id']
            == taxi_order_id
        )
        assert (
            mock_py2_update_payments_stats.request.query['order_id']
            == taxi_order_id
        )
        assert mock_rebill_order.times_called == 0


@pytest.mark.config(
    CARGO_FINANCE_PATCH_TAXI_DATABASES_SETTINGS={
        'allow_async_patch': True,
        'patch_start_delay_ms': 60000,
    },
)
@pytest.mark.now('2021-12-16T12:00:00+00:00')
async def test_delayed_update(stq, stq_runner, mock_pay_order_applying_call):
    await run_invoice_callback_stq(stq_runner)
    assert (
        stq.cargo_finance_patch_taxi_databases_with_invoice.times_called == 1
    )
    assert stq.cargo_finance_patch_taxi_databases_with_invoice.next_call()[
        'eta'
    ] == datetime.datetime(2021, 12, 16, 12, 1)


async def test_patch_stq_happy_path(
        stq_runner,
        mock_py2_update_transactions,
        mock_py2_update_sum_to_pay,
        mock_py2_update_payments_stats,
        mock_v2_invoice_retrieve,
        mock_cut_claim,
        mock_pay_order_applying_call,
        mock_rebill_order,
        order_proc,
        taxi_order_id,
):
    await run_patch_stq(stq_runner)
    assert mock_v2_invoice_retrieve.request.json['id'] == _INVOICE_ID
    assert mock_cut_claim.request.query['claim_id'] == _CLAIM_ID
    assert (
        mock_py2_update_sum_to_pay.request.query['order_id'] == taxi_order_id
    )
    assert (
        mock_py2_update_transactions.request.query['order_id'] == taxi_order_id
    )
    assert (
        mock_py2_update_payments_stats.request.query['order_id']
        == taxi_order_id
    )
    assert mock_rebill_order.times_called == 1


async def test_sum_to_pay(
        stq_runner,
        mock_py2_update_transactions,
        mock_py2_update_sum_to_pay,
        mock_py2_update_payments_stats,
        mock_v2_invoice_retrieve,
        mock_cut_claim,
        mock_pay_order_applying_call,
        mock_rebill_order,
        order_proc,
):
    ride_cost = 100
    mock_v2_invoice_retrieve.response_data['sum_to_pay'] = [
        {
            'items': [
                {'amount': str(ride_cost), 'item_id': 'ride'},
                {'amount': '10', 'item_id': 'tips'},
            ],
            'payment_type': 'card',
        },
    ]

    await run_patch_stq(stq_runner)

    assert mock_py2_update_sum_to_pay.request.json['value'] == {
        'ride': ride_cost * 10000,
        'tips': 0,
    }

    assert mock_rebill_order.times_called == 1


async def test_update_transactions(
        stq_runner,
        mock_py2_update_transactions,
        mock_py2_update_sum_to_pay,
        mock_py2_update_payments_stats,
        mock_v2_invoice_retrieve,
        mock_cut_claim,
        mock_pay_order_applying_call,
        mock_rebill_order,
        order_proc,
):

    await run_patch_stq(stq_runner)

    transactions = [
        {
            'cleared': '2021-10-11T13:13:40.01+00:00',
            'created': '2021-10-11T10:13:27.76+00:00',
            'holded': '2021-10-11T10:13:39.556+00:00',
            'initial_sum': {'ride': 3310000, 'tips': 0},
            'payment_method_type': 'card',
            'purchase_token': '3f2d033a62d9961417410b9f1a57b079',
            'refunds': [],
            'status': 'clear_success',
            'sum': {'ride': 3310000, 'tips': 0},
            'terminal_id': 55013005,
            'trust_payment_id': '61640e4783b1f23c525386d1',
            'updated': '2021-10-11T13:14:40.425+00:00',
        },
    ]

    assert mock_py2_update_transactions.request.json['value'] == transactions
    assert (
        mock_py2_update_payments_stats.request.json['transactions']
        == transactions
    )

    assert mock_rebill_order.times_called == 1


async def test_update_transactions_error_no_order(
        mockserver,
        stq_runner,
        mock_py2_update_sum_to_pay,
        mock_py2_update_payments_stats,
        mock_v2_invoice_retrieve,
        mock_cut_claim,
        mock_rebill_order,
):
    @mockserver.json_handler('/py2-delivery/update-billing-transactions')
    def _handler(request):
        return mockserver.make_response(
            json={'status': '', 'message': '', 'code': ''}, status=404,
        )

    await run_patch_stq(stq_runner, expect_fail=True)
    assert mock_v2_invoice_retrieve.request.json['id'] == _INVOICE_ID
    assert mock_cut_claim.request.query['claim_id'] == _CLAIM_ID
    assert mock_rebill_order.times_called == 0


async def test_update_sum_to_pay_error_no_order(
        mockserver,
        stq_runner,
        mock_py2_update_transactions,
        mock_py2_update_payments_stats,
        mock_v2_invoice_retrieve,
        mock_cut_claim,
        mock_rebill_order,
):
    @mockserver.json_handler('/py2-delivery/update-sum-to-pay')
    def _handler(request):
        return mockserver.make_response(
            json={'status': '', 'message': '', 'code': ''}, status=404,
        )

    await run_patch_stq(stq_runner, expect_fail=True)
    assert mock_v2_invoice_retrieve.request.json['id'] == _INVOICE_ID
    assert mock_cut_claim.request.query['claim_id'] == _CLAIM_ID
    assert mock_rebill_order.times_called == 0
