# pylint: disable=too-many-lines

from __future__ import annotations

import dataclasses
import datetime
import decimal
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pytest

from taxi.billing.util import dates as billing_dates

from test_transactions import helpers
from transactions.generated.stq3 import stq_context
from transactions.stq import cashback_events_handler
from transactions.stq import plan_operation

_MISSING = object()
_NOW = '2020-02-02T00:00:00'
_QUEUES = {
    'eda': {
        'plan_operations': 'transactions_eda_plan_operation',
        'events': 'transactions_eda_cashback_events',
    },
    'taxi': {
        'plan_operations': 'transactions_plan_operation',
        'events': 'transactions_cashback_events',
    },
}
_EXPECTED_CASHBACK_SETTINGS = {
    'taxi': {
        'user': {
            'product_id': 'agent-cashback-product-id',
            'cashback_type': 'agent',
        },
        'service': {
            'product_id': 'marketing-cashback-product-id',
            'cashback_type': 'transaction',
        },
    },
    'eda': {
        'user': {
            'product_id': 'agent-cashback-product-id',
            'cashback_type': 'agent',
        },
        'service': {
            'product_id': 'marketing-cashback-product-id',
            'cashback_type': 'transaction',
        },
    },
}


@pytest.mark.parametrize(
    'scope, invoice_id, extra_update_params, initial_source, final_source',
    [
        ('taxi', 'invoice-id', {}, 'user', 'service'),
        (
            'taxi',
            'invoice-id-b2b',
            {
                'extra_payload': {'payment_type': 'corp'},
                'billing_service': 'card',
            },
            'user',
            'service',
        ),
        (
            'taxi',
            'invoice-id-cash',
            {
                'extra_payload': {'payment_type': 'cash'},
                'billing_service': 'card',
            },
            'user',
            'service',
        ),
        ('taxi', 'invoice-id', {'billing_service': 'card'}, 'user', 'service'),
        pytest.param(
            'eda',
            'invoice-id',
            {'billing_service': 'card'},
            'user',
            'service',
            marks=[pytest.mark.config()],
        ),
        (
            'eda',
            'invoice-id',
            {'billing_service': 'card', 'extra_payload': {'foo': 'bar'}},
            'user',
            'service',
        ),
        (
            'taxi',
            'invoice-id',
            {
                'sources': {
                    'user': {},
                    'service': {
                        'extra_payload': {'campign_name': 'mastercard'},
                        'cashback_type': 'some_cashback_type',
                        'product_id': 'some_product_id',
                    },
                },
            },
            'user',
            'service',
        ),
        (
            'taxi',
            'invoice-id',
            {
                'sources': {
                    'user': {},
                    'service': {
                        'extra_payload': {'campign_name': 'mastercard'},
                        'cashback_type': 'some_cashback_type',
                        'product_id': 'some_product_id',
                        'fiscal_nds': 'nds_none',
                        'fiscal_title': 'Кешбэк',
                    },
                },
            },
            'user',
            'service',
        ),
        (
            'taxi',
            'invoice-id',
            {
                'sources': {
                    'arbitrary_source_1': {
                        'extra_payload': {'source': 'arbitrary_source_1'},
                        'cashback_type': 'arbitrary_source_1_cashback_type',
                        'product_id': 'arbitrary_source_1_product_id',
                    },
                    'arbitrary_source_2': {
                        'extra_payload': {'source': 'arbitrary_source_2'},
                        'cashback_type': 'arbitrary_source_2_cashback_type',
                        'product_id': 'arbitrary_source_2_product_id',
                    },
                },
            },
            'arbitrary_source_1',
            'arbitrary_source_2',
        ),
    ],
)
@pytest.mark.config(
    TRANSACTIONS_SAVE_IS_HANDLED={'eda': 1, '__default__': 0},
    TRANSACTIONS_TOPUP_PRODUCTS=[
        {
            'billing_service': 'card',
            'cashback_type': 'agent',
            'product_id': 'agent-cashback-product-id',
            'source': 'user',
        },
        {
            'billing_service': 'card',
            'cashback_type': 'transaction',
            'product_id': 'marketing-cashback-product-id',
            'source': 'service',
        },
        {
            'billing_service': 'food_payment',
            'cashback_type': 'agent',
            'product_id': 'agent-cashback-product-id',
            'source': 'user',
        },
        {
            'billing_service': 'food_payment',
            'cashback_type': 'transaction',
            'product_id': 'marketing-cashback-product-id',
            'source': 'service',
        },
    ],
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.now(_NOW)
async def test_topup_and_refund(
        stq3_context: stq_context.Context,
        eda_stq3_context,
        stq,
        scope,
        invoice_id,
        extra_update_params,
        initial_source,
        final_source,
        web_app_client,
        eda_web_app_client,
        mock_experiments3,
        mock_trust_create_topup,
        mock_trust_start_topup,
        mock_trust_check_topup,
        trust_create_refund_success,
        mock_trust_start_refund,
        mock_check_refund,
        mock_taxi_agglomerations,
        simple_secdist,
):
    assert scope in ('taxi', 'eda', 'ng')
    if scope == 'taxi':
        context = stq3_context
        client = web_app_client
    elif scope == 'eda':
        context = eda_stq3_context
        client = eda_web_app_client

    @mock_taxi_agglomerations('/v1/geo_nodes/get_mvp_oebs_id')
    def get_mvp_oebs_id(request):
        # pylint: disable=unused-variable
        expected_dt = datetime.datetime(
            2020, 2, 2, tzinfo=datetime.timezone.utc,
        )
        assert request.args['tariff_zone'] == 'moscow'
        assert billing_dates.parse_datetime(request.args['dt']) == expected_dt
        return {'oebs_mvp_id': 'some_oebs_mvp_id'}

    expected_service_token = _get_expected_service_token(
        context, extra_update_params,
    )
    state = _State.empty(invoice_id, sources=[initial_source, final_source])
    await _check_state(client, context, state)
    operation_id = f'topup_{initial_source}'
    await _update_cashback(
        context=context,
        stq=stq,
        client=client,
        state=state,
        operation_id=operation_id,
        amounts_by_source={
            initial_source: decimal.Decimal(100),
            final_source: decimal.Decimal(0),
        },
        extra_params=extra_update_params,
    )
    mock_trust_create_topup(
        purchase_token='topup-1',
        pass_params=_get_expected_pass_params(
            invoice_id, extra_update_params, initial_source, scope,
        ),
        expected_product_id=_get_expected_cashback_setting(
            'product_id',
            scope=scope,
            source=initial_source,
            extra_update_params=extra_update_params,
        ),
        expected_fiscal_nds=_get_expected_cashback_setting_opt(
            'fiscal_nds',
            source=initial_source,
            extra_update_params=extra_update_params,
        ),
        expected_fiscal_title=_get_expected_cashback_setting_opt(
            'fiscal_title',
            source=initial_source,
            extra_update_params=extra_update_params,
        ),
        expected_service_token=expected_service_token,
    )
    state.add_topup(
        topup_id='topup-1',
        source=initial_source,
        amount=decimal.Decimal(100),
        status='hold_init',
        refunds=[],
    )
    state.operations.append(Operation('processing'))
    state.status = 'in-progress'
    if scope == 'eda':
        state.is_handled = None
    await _run_iter(stq, context, client, state)
    mock_trust_start_topup(
        purchase_token='topup-1',
        expected_service_token=expected_service_token,
        expect_headers={'X-Uid': '102030'},
    )
    state.topups[-1].status = 'hold_pending'
    await _run_iter(stq, context, client, state)
    mock_trust_check_topup(
        purchase_token='topup-1',
        expected_service_token=expected_service_token,
        expect_headers={'X-Uid': '102030'},
    )
    state.topups[-1].status = 'clear_success'
    state.amounts_by_source[initial_source] = decimal.Decimal(100)
    await _run_iter(stq, context, client, state)
    state.operations[-1].status = 'done'
    state.status = 'success'
    if scope == 'eda':
        state.is_handled = True
    await _run_iter(stq, context, client, state, final=True)
    operation_id = f'topup_{final_source}_instead'
    await _update_cashback(
        context=context,
        stq=stq,
        client=client,
        state=state,
        operation_id=operation_id,
        amounts_by_source={
            initial_source: decimal.Decimal(0),
            final_source: decimal.Decimal(100),
        },
        extra_params=extra_update_params,
    )
    trust_create_refund_success(
        expect_body=_get_expected_refund_request(
            invoice_id, extra_update_params, initial_source, scope,
        ),
        expected_service_token=expected_service_token,
    )
    state.amounts_by_source[initial_source] = decimal.Decimal(0)
    state.topups[-1].add_refund(
        refund_id='trust-refund-id',
        amount=decimal.Decimal(100),
        status='refund_pending',
    )
    state.operations.append(Operation('processing'))
    state.status = 'in-progress'
    if scope == 'eda':
        state.is_handled = False
    await _run_iter(stq, context, client, state)
    state.topups[-1].refunds[-1].status = 'refund_waiting'
    state.topups[-1].status = 'refund_waiting'
    mock_trust_start_refund(
        status='wait_for_notification',
        expected_service_token=expected_service_token,
        expect_headers={'X-Uid': '102030'},
    )
    mock_check_refund(status='success', expect_headers={'X-Uid': '102030'})
    await _run_iter(stq, context, client, state)
    state.topups[-1].refunds[-1].status = 'refund_success'
    state.topups[-1].status = 'clear_success'
    await _run_iter(stq, context, client, state)
    mock_trust_create_topup(
        purchase_token='topup-2',
        pass_params=_get_expected_pass_params(
            invoice_id, extra_update_params, final_source, scope,
        ),
        expected_product_id=_get_expected_cashback_setting(
            'product_id',
            scope=scope,
            source=final_source,
            extra_update_params=extra_update_params,
        ),
        expected_service_token=expected_service_token,
    )
    state.add_topup(
        topup_id='topup-2',
        source=final_source,
        amount=decimal.Decimal(100),
        status='hold_init',
        refunds=[],
    )
    await _run_iter(stq, context, client, state)
    mock_trust_start_topup(
        purchase_token='topup-2',
        expected_service_token=expected_service_token,
        expect_headers={'X-Uid': '102030'},
    )
    state.topups[-1].status = 'hold_pending'
    await _run_iter(stq, context, client, state)
    mock_trust_check_topup(
        purchase_token='topup-2',
        expected_service_token=expected_service_token,
        expect_headers={'X-Uid': '102030'},
    )
    state.topups[-1].status = 'clear_success'
    state.amounts_by_source[final_source] = decimal.Decimal(100)
    await _run_iter(stq, context, client, state)
    state.operations[-1].status = 'done'
    state.status = 'success'
    if scope == 'eda':
        state.is_handled = True
    await _run_iter(stq, context, client, state, final=True)


@pytest.mark.config(
    TRANSACTIONS_TOPUP_PRODUCTS=[
        {
            'billing_service': 'card',
            'cashback_type': 'transaction',
            'product_id': 'marketing-cashback-product-id',
            'source': 'service',
        },
    ],
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.now(_NOW)
async def test_pass_params_is_stored(
        stq3_context: stq_context.Context,
        db,
        stq,
        web_app_client,
        mock_experiments3,
        mock_trust_create_topup,
        mock_trust_start_topup,
        mock_trust_check_topup,
        trust_create_refund_success,
        mock_taxi_agglomerations,
        simple_secdist,
):
    context = stq3_context
    client = web_app_client
    invoice_id = 'invoice-id'

    @mock_taxi_agglomerations('/v1/geo_nodes/get_mvp_oebs_id')
    def get_mvp_oebs_id(request):
        # pylint: disable=unused-variable
        expected_dt = datetime.datetime(
            2020, 2, 2, tzinfo=datetime.timezone.utc,
        )
        assert request.args['tariff_zone'] == 'moscow'
        assert billing_dates.parse_datetime(request.args['dt']) == expected_dt
        return {'oebs_mvp_id': 'some_oebs_mvp_id'}

    state = _State.empty(invoice_id, sources=['service'])
    await _check_state(client, context, state)
    operation_id = 'topup'
    await _update_cashback(
        context=context,
        stq=stq,
        client=client,
        state=state,
        operation_id=operation_id,
        amounts_by_source={'service': decimal.Decimal(100)},
        extra_params={},
    )
    topup_pass_params = _get_expected_pass_params(
        invoice_id=invoice_id,
        extra_update_params={},
        source='service',
        scope='taxi',
    )
    mock_trust_create_topup(
        purchase_token='topup-1', pass_params=topup_pass_params,
    )
    state.add_topup(
        topup_id='topup-1',
        source='service',
        amount=decimal.Decimal(100),
        status='hold_init',
        refunds=[],
    )
    state.operations.append(Operation('processing'))
    state.status = 'in-progress'
    await _run_iter(stq, context, client, state)
    invoice = await db.orders.find_one({'_id': invoice_id})
    assert len(invoice['cashback_tech']['transactions']) == 1
    topup = invoice['cashback_tech']['transactions'][0]
    assert topup['pass_params'] == topup_pass_params
    mock_trust_start_topup(
        purchase_token='topup-1', expect_headers={'X-Uid': '102030'},
    )
    state.topups[-1].status = 'hold_pending'
    await _run_iter(stq, context, client, state)
    mock_trust_check_topup(
        purchase_token='topup-1', expect_headers={'X-Uid': '102030'},
    )
    state.topups[-1].status = 'clear_success'
    state.amounts_by_source['service'] = decimal.Decimal(100)
    await _run_iter(stq, context, client, state)
    state.operations[-1].status = 'done'
    state.status = 'success'
    await _run_iter(stq, context, client, state, final=True)

    operation_id = 'refund_topup'
    extra_refund_update_params = {
        'extra_payload': {'some_param_not_in_topup_payload': 'foo'},
    }
    await _update_cashback(
        context=context,
        stq=stq,
        client=client,
        state=state,
        operation_id=operation_id,
        amounts_by_source={'service': decimal.Decimal(0)},
        extra_params=extra_refund_update_params,
    )
    refund_pass_params = _get_expected_pass_params(
        invoice_id=invoice_id,
        extra_update_params=extra_refund_update_params,
        source='service',
        scope='taxi',
    )
    trust_create_refund_success(
        expect_body={'pass_params': refund_pass_params},
    )
    state.amounts_by_source['service'] = decimal.Decimal(0)
    state.topups[-1].add_refund(
        refund_id='trust-refund-id',
        amount=decimal.Decimal(100),
        status='refund_pending',
    )
    state.operations.append(Operation('processing'))
    state.status = 'in-progress'
    await _run_iter(stq, context, client, state)
    invoice = await db.orders.find_one({'_id': invoice_id})
    assert len(invoice['cashback_tech']['transactions']) == 1
    topup = invoice['cashback_tech']['transactions'][0]
    assert len(topup['refunds']) == 1
    assert topup['refunds'][0]['pass_params'] == refund_pass_params


@pytest.mark.config(
    TRANSACTIONS_TOPUP_PRODUCTS=[
        {
            'billing_service': 'card',
            'cashback_type': 'transaction',
            'product_id': 'marketing-cashback-product-id',
            'source': 'service',
        },
    ],
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.now(_NOW)
async def test_reschedule_on_no_op_operation(
        stq3_context: stq_context.Context,
        db,
        stq,
        web_app_client,
        mock_experiments3,
        mock_trust_create_topup,
        mock_trust_start_topup,
        mock_trust_check_topup,
        mock_taxi_agglomerations,
        simple_secdist,
):
    context = stq3_context
    client = web_app_client
    invoice_id = 'invoice-id'

    @mock_taxi_agglomerations('/v1/geo_nodes/get_mvp_oebs_id')
    def get_mvp_oebs_id(request):
        # pylint: disable=unused-variable
        expected_dt = datetime.datetime(
            2020, 2, 2, tzinfo=datetime.timezone.utc,
        )
        assert request.args['tariff_zone'] == 'moscow'
        assert billing_dates.parse_datetime(request.args['dt']) == expected_dt
        return {'oebs_mvp_id': 'some_oebs_mvp_id'}

    state = _State.empty(invoice_id, sources=['service'])
    await _check_state(client, context, state)
    operation_id = 'topup'
    await _update_cashback(
        context=context,
        stq=stq,
        client=client,
        state=state,
        operation_id=operation_id,
        amounts_by_source={'service': decimal.Decimal(100)},
        extra_params={},
    )
    state.operations.append(Operation('processing'))

    topup_pass_params = _get_expected_pass_params(
        invoice_id=invoice_id,
        extra_update_params={},
        source='service',
        scope='taxi',
    )
    mock_trust_create_topup(
        purchase_token='topup-1', pass_params=topup_pass_params,
    )
    state.add_topup(
        topup_id='topup-1',
        source='service',
        amount=decimal.Decimal(100),
        status='hold_init',
        refunds=[],
    )
    state.status = 'in-progress'
    await _run_iter(stq, context, client, state)
    invoice = await db.orders.find_one({'_id': invoice_id})
    assert len(invoice['cashback_tech']['transactions']) == 1
    mock_trust_start_topup(
        purchase_token='topup-1', expect_headers={'X-Uid': '102030'},
    )
    state.topups[-1].status = 'hold_pending'
    await _run_iter(stq, context, client, state)
    mock_trust_check_topup(
        purchase_token='topup-1', expect_headers={'X-Uid': '102030'},
    )
    state.topups[-1].status = 'clear_success'
    state.amounts_by_source['service'] = decimal.Decimal(100)
    await _run_iter(stq, context, client, state)
    state.status = 'success'
    state.operations[-1].status = 'done'
    await _run_iter(stq, context, client, state, final=True)
    no_op_operation_id = 'no-op-topup'
    await _update_cashback(
        context=context,
        stq=stq,
        client=client,
        state=state,
        operation_id=no_op_operation_id,
        amounts_by_source={'service': decimal.Decimal(100)},
        extra_params={},
    )
    state.operations.append(Operation('processing'))
    state.status = 'in-progress'
    await _run_iter(stq, context, client, state)
    state.operations[-1].status = 'done'
    state.status = 'success'
    await _run_iter(stq, context, client, state, final=True)


@pytest.mark.config(
    TRANSACTIONS_TOPUP_PRODUCTS=[
        {
            'billing_service': 'card',
            'cashback_type': 'transaction',
            'product_id': 'marketing-cashback-product-id',
            'source': 'service',
        },
    ],
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
)
@pytest.mark.now(_NOW)
async def test_topup_crutches(
        stq,
        stq3_context,
        db,
        web_app_client,
        mock_experiments3,
        mock_trust_create_topup,
        mock_trust_start_topup,
        mock_taxi_agglomerations,
):
    @mock_taxi_agglomerations('/v1/geo_nodes/get_mvp_oebs_id')
    def get_mvp_oebs_id(request):
        # pylint: disable=unused-variable
        expected_dt = datetime.datetime(
            2020, 2, 2, tzinfo=datetime.timezone.utc,
        )
        assert request.args['tariff_zone'] == 'moscow'
        assert billing_dates.parse_datetime(request.args['dt']) == expected_dt
        return {'oebs_mvp_id': 'some_oebs_mvp_id'}

    crutches = ['cashback-topup-fail']
    invoice_id = 'invoice-id'
    mock_experiments3.set_crutches(crutches)
    mock_experiments3.expected_uid = '102030'
    context = stq3_context
    client = web_app_client

    state = _State.empty(invoice_id, sources=['service'])
    await _check_state(client, context, state)
    operation_id = 'topup'
    await _update_cashback(
        context=context,
        stq=stq,
        client=client,
        state=state,
        operation_id=operation_id,
        amounts_by_source={'service': decimal.Decimal(100)},
        extra_params={},
    )
    topup_pass_params = _get_expected_pass_params(
        invoice_id=invoice_id,
        extra_update_params={},
        source='service',
        scope='taxi',
    )
    mock_trust_create_topup(
        purchase_token='topup-1', pass_params=topup_pass_params,
    )
    state.add_topup(
        topup_id='topup-1',
        source='service',
        amount=decimal.Decimal(100),
        status='hold_init',
        refunds=[],
    )
    state.operations.append(Operation('processing'))
    state.status = 'in-progress'
    await _run_iter(stq, context, client, state)

    invoice = await db.orders.find_one({'_id': invoice_id})
    assert len(invoice['cashback_tech']['transactions']) == 1

    mock_trust_start_topup(
        purchase_token='topup-1', expect_headers={'X-Uid': '102030'},
    )
    state.topups[-1].status = 'hold_pending'
    await _run_iter(stq, context, client, state)

    state.topups[-1].status = 'hold_fail'
    await _run_iter(stq, context, client, state)


@dataclasses.dataclass(frozen=False)
class _Refund:
    refund_id: str
    amount: decimal.Decimal
    status: str


@dataclasses.dataclass(frozen=False)
class _Topup:
    topup_id: str
    source: str
    amount: decimal.Decimal
    status: str
    refunds: List[_Refund]

    def add_refund(self, **kwargs):
        self.status = 'refund_pending'
        self.refunds.append(_Refund(**kwargs))


@dataclasses.dataclass(frozen=False)
class Operation:
    status: str


@dataclasses.dataclass(frozen=False)
class _State:
    invoice_id: str
    amounts_by_source: Dict[str, decimal.Decimal]
    status: str
    version: int
    topups: List[_Topup]
    operations: List[Operation]
    is_handled: Union[Optional[bool], object]

    def add_topup(self, **kwargs):
        self.topups.append(_Topup(**kwargs))

    @classmethod
    def empty(cls, invoice_id: str, sources: List[str]) -> _State:
        return _State(
            invoice_id=invoice_id,
            amounts_by_source={
                source: decimal.Decimal(0) for source in sources
            },
            status='init',
            version=1,
            topups=[],
            operations=[],
            is_handled=_MISSING,
        )


async def _check_state(client, context, expected_state):
    db_invoice = await context.transactions.invoices.find_one(
        {'_id': expected_state.invoice_id},
    )
    body = {'id': expected_state.invoice_id}
    response = await client.post('/v2/invoice/retrieve', json=body)
    assert response.status == 200
    content = await response.json()
    data = content['cashback']
    actual_state = _State(
        invoice_id=expected_state.invoice_id,
        amounts_by_source={
            item['source']: decimal.Decimal(item['amount'])
            for item in data['rewarded']
        },
        status=data['status'],
        version=data['version'],
        topups=[_parse_topup(topup) for topup in data['transactions']],
        operations=[
            _parse_operation(operation) for operation in data['operations']
        ],
        is_handled=db_invoice.get('invoice_request', {}).get('is_handled'),
    )
    actual_amounts_by_source = actual_state.amounts_by_source
    expected_amounts_by_source = expected_state.amounts_by_source
    actual_state = dataclasses.replace(actual_state, amounts_by_source={})
    if expected_state.is_handled is _MISSING:
        actual_state = dataclasses.replace(actual_state, is_handled=_MISSING)
    expected_state = dataclasses.replace(expected_state, amounts_by_source={})
    assert actual_state == expected_state
    _assert_amounts_by_source_match(
        actual_amounts_by_source, expected_amounts_by_source,
    )


def _assert_amounts_by_source_match(actual, expected):
    for source in actual.keys() | expected.keys():
        actual_amount = actual.get(source, decimal.Decimal(0))
        expected_amount = expected.get(source, decimal.Decimal(0))
        error_msg = (
            f'Source {source} has incorrect amount: '
            f'actual != expected ({actual_amount} != {expected_amount})'
        )
        assert actual_amount == expected_amount, error_msg


def _parse_operation(data) -> Operation:
    return Operation(status=data['status'])


def _parse_topup(data) -> _Topup:
    return _Topup(
        topup_id=data['external_payment_id'],
        source=data['source'],
        amount=decimal.Decimal(data['amount']),
        status=data['status'],
        refunds=[_parse_refund(refund) for refund in data['refunds']],
    )


def _parse_refund(data) -> _Refund:
    return _Refund(
        refund_id=data['external_payment_id'],
        amount=decimal.Decimal(data['amount']),
        status=data['status'],
    )


async def _update_cashback(
        context,
        stq,
        client,
        state,
        operation_id,
        amounts_by_source,
        extra_params,
):
    plan_operations_queue = _get_queue(
        stq, context, queue_type='plan_operations',
    )
    events_queue = _get_queue(stq, context, queue_type='events')
    invoice_id = state.invoice_id
    with stq.flushing():
        body = {
            'invoice_id': invoice_id,
            'operation_id': operation_id,
            'version': state.version,
            'yandex_uid': '102030',
            'user_ip': '127.0.0.1',
            'wallet_account': 'w/abcd1234-def',
            'reward': [
                {'source': source, 'amount': str(amount)}
                for source, amount in amounts_by_source.items()
            ],
        }
        body.update(extra_params)
        response = await client.post('/v2/cashback/update', json=body)
        assert response.status == 200
        state.version += 1
        assert plan_operations_queue.times_called == 2
        task = plan_operations_queue.next_call()
        assert task['id'] == f'{invoice_id}#{operation_id}'
        task = plan_operations_queue.next_call()
        assert task['id'] == f'{invoice_id}#{operation_id}'
        assert task['eta'] == datetime.datetime(1970, 1, 1)
        assert task['kwargs']['operation_id'] == operation_id
        assert task['kwargs']['operations_kind'] == 'cashback_operations'
        assert stq.is_empty
    with stq.flushing():
        plan_operations_queue_name = _get_queue_name(
            stq, context, queue_type='plan_operations',
        )
        await plan_operation.task(
            context,
            helpers.create_task_info(queue=plan_operations_queue_name),
            invoice_id=invoice_id,
            operation_id=operation_id,
            operations_kind='cashback_operations',
            created=datetime.datetime.utcnow(),
        )
        assert events_queue.times_called == 1
        task = events_queue.next_call()
        assert task['id'] == invoice_id
        assert task['eta'] == datetime.datetime(1970, 1, 1)
        assert task['args'] == [invoice_id]
        assert stq.is_empty


def _assert_next_iter_planned(stq, context, invoice_id: str):
    queue = _get_queue(stq, context, queue_type='events')
    assert queue.times_called == 1
    task = queue.next_call()
    assert task['id'] == invoice_id


def _get_expected_pass_params(invoice_id, extra_update_params, source, scope):
    cashback_type = _get_expected_cashback_setting(
        'cashback_type',
        source,
        scope,
        extra_update_params=extra_update_params,
    )
    if scope == 'eda':
        return _get_expected_eda_pass_params(
            invoice_id, extra_update_params, cashback_type,
        )
    assert scope == 'taxi'
    pass_params = {
        'payload': {
            'cashback_type': cashback_type,
            'service_id': '124',
            'tariff_class': 'econom',
            'order_id': invoice_id,
            'alias_id': '<alias_id>',
            'oebs_mvp_id': 'some_oebs_mvp_id',
        },
    }
    if 'sources' in extra_update_params:
        extra_cashback_type = (
            extra_update_params['sources'].get(source, {}).get('cashback_type')
        )
        if extra_cashback_type is not None:
            pass_params.setdefault('payload', {})[
                'cashback_type'
            ] = extra_cashback_type
        payload = (
            extra_update_params['sources']
            .get(source, {})
            .get('extra_payload', {})
        )
        pass_params.setdefault('payload', {}).update(payload)
    elif 'extra_payload' in extra_update_params:
        pass_params.setdefault('payload', {}).update(
            extra_update_params['extra_payload'],
        )
    return pass_params


def _get_expected_eda_pass_params(
        invoice_id, extra_update_params, cashback_type,
):
    if 'extra_payload' in extra_update_params:
        return {'payload': extra_update_params['extra_payload']}
    return None


def _get_expected_refund_request(
        invoice_id, extra_update_params, source, scope,
):
    return {
        'pass_params': _get_expected_pass_params(
            invoice_id, extra_update_params, source, scope,
        ),
    }


def _get_expected_service_token(context, extra_update_params):
    billing_service = extra_update_params.get('billing_service')
    if billing_service is None:
        return None

    billings = context.config.TRANSACTIONS_BILLING_SERVICE_TOKENS
    return billings[billing_service]['billing_api_key']


def _get_queue(stq, context, queue_type: str):
    return getattr(stq, _get_queue_name(stq, context, queue_type))


def _get_queue_name(stq, context, queue_type: str):
    settings = _QUEUES[context.transactions.transactions_scope]
    return settings[queue_type]


async def _run_iter(stq, context, client, state, final=False):
    with stq.flushing():
        await cashback_events_handler.task(context, state.invoice_id)
        if final:
            assert stq.is_empty
        else:
            _assert_next_iter_planned(stq, context, state.invoice_id)
        await _check_state(client, context, state)


def _get_expected_cashback_setting(
        setting: str,
        source: str,
        scope: str,
        extra_update_params: Optional[dict] = None,
) -> str:
    if extra_update_params is not None:
        source_settings = extra_update_params.get('sources', {}).get(
            source, {},
        )
        extra_setting_value = source_settings.get(setting)
        if extra_setting_value is not None:
            return extra_setting_value
    settings = _EXPECTED_CASHBACK_SETTINGS[scope][source]
    return settings[setting]


def _get_expected_cashback_setting_opt(
        setting: str, source: str, extra_update_params: Optional[dict] = None,
) -> Optional[str]:
    if extra_update_params is not None:
        source_settings = extra_update_params.get('sources', {}).get(
            source, {},
        )
        extra_setting_value = source_settings.get(setting)
        if extra_setting_value is not None:
            return extra_setting_value
    return None
