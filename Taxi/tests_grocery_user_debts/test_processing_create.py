# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

from . import consts
from . import helpers
from . import models

ITEMS = [
    helpers.make_payment_items(
        [
            helpers.make_item('item-1', '100'),
            helpers.make_item('item-2', '200', product_id='product_id_2'),
        ],
    ),
]


@pytest.fixture(name='grocery_user_debts_create')
def _grocery_user_debts_create(taxi_grocery_user_debts):
    async def _inner(status_code=200, debt=None, **kwargs):
        response = await taxi_grocery_user_debts.post(
            '/processing/v1/debts/create',
            json={
                'debt': debt or _make_request_debt(),
                'order': consts.ORDER_INFO,
                'operation': helpers.make_operation(),
                **kwargs,
            },
        )

        assert response.status_code == status_code

    return _inner


async def test_debt_collector(grocery_user_debts_create, debt_collector):
    request_debt = _make_request_debt(debt_id=consts.DEBT_ID)

    debt_collector.create.check(
        id=consts.DEBT_ID,
        debtors=[f'yandex/uid/{consts.YANDEX_UID}'],
        currency=request_debt['currency'],
        invoice=request_debt['invoice'],
        items_by_payment_type=helpers.to_debt_collector_items(
            request_debt['items'],
        ),
        service=consts.SERVICE,
        reason=helpers.make_reason(),
        collection=dict(strategy=consts.DEBT_NULL_STRATEGY),
    )

    await grocery_user_debts_create(debt=request_debt)

    assert debt_collector.create.times_called == 1


@pytest.mark.parametrize('originator', models.InvoiceOriginator)
async def test_processing(grocery_user_debts_create, processing, originator):
    request_debt = _make_request_debt(debt_id=consts.DEBT_ID)
    request_debt['invoice']['id'] = originator.prefix + consts.ORDER_ID

    create_event = None

    if originator == models.InvoiceOriginator.grocery:
        create_event = processing.processing
    elif originator == models.InvoiceOriginator.tips:
        create_event = processing.tips

    state = 'hold_money'
    token = (
        f'{consts.ORDER_ID}-{state}-{consts.OPERATION_ID}-'
        f'{consts.OPERATION_TYPE}'
    )

    if create_event:
        create_event.check(
            order_id=consts.ORDER_ID,
            reason='setstate',
            state=state,
            payload=dict(
                operation_id=consts.OPERATION_ID,
                operation_type=consts.OPERATION_TYPE,
            ),
            headers={'X-Idempotency-Token': token},
        )

    await grocery_user_debts_create(debt=request_debt)

    if create_event:
        assert create_event.times_called == 1


async def test_pgsql(grocery_user_debts_create, grocery_user_debts_db):
    reason = models.debt_reason()
    request_debt = _make_request_debt(reason=reason)

    await grocery_user_debts_create(debt=request_debt)

    updated_debt = grocery_user_debts_db.get_debt(consts.DEBT_ID)
    assert updated_debt.priority == consts.OPERATION_PRIORITY
    assert updated_debt.payload == models.debt_payload(reason=reason)
    assert updated_debt.order_id == consts.ORDER_ID
    assert updated_debt.invoice_id == consts.INVOICE_ID


async def test_inited(grocery_user_debts_create, grocery_user_debts_db):
    debt = models.Debt(debt_id=consts.DEBT_ID, status='init')
    grocery_user_debts_db.upsert(debt)

    await grocery_user_debts_create()

    updated_debt = grocery_user_debts_db.get_debt(consts.DEBT_ID)
    assert updated_debt.priority == consts.OPERATION_PRIORITY


async def test_canceled(
        grocery_user_debts_create,
        grocery_user_debts_db,
        debt_collector,
        processing,
):
    grocery_user_debts_db.upsert(models.Debt(status='canceled'))

    await grocery_user_debts_create()

    assert debt_collector.create.times_called == 0
    assert processing.debts.times_called == 0


@pytest.mark.parametrize('priority', [1, 2, 3])
async def test_priority(
        grocery_user_debts_create,
        grocery_user_debts_db,
        debt_collector,
        processing,
        priority,
):
    debt = models.Debt(debt_id=consts.DEBT_ID, priority=2)
    grocery_user_debts_db.upsert(debt)

    early_exit = priority <= debt.priority

    await grocery_user_debts_create(
        operation=helpers.make_operation(priority=priority),
    )

    assert debt_collector.create.times_called == int(not early_exit)
    assert processing.processing.times_called == int(not early_exit)


async def test_debt_failed(
        grocery_user_debts_create, grocery_user_debts_db, debt_collector,
):
    debt_collector.create.status_code = 400

    await grocery_user_debts_create(status_code=400)

    assert grocery_user_debts_db.get_debt(consts.DEBT_ID) is None


@pytest.mark.parametrize('originator', models.InvoiceOriginator)
@pytest.mark.parametrize('payment_type', ['card', None])
@pytest.mark.parametrize('error_code', ['error_reason_code', None])
async def test_metric(
        grocery_user_debts_create,
        taxi_grocery_user_debts_monitor,
        originator,
        payment_type,
        error_code,
):
    sensor = 'grocery_user_debts_created_metrics'

    reason = models.debt_reason(
        payment_type=payment_type, error_reason_code=error_code,
    )
    request_debt = _make_request_debt(
        reason=reason, originator=originator.name,
    )

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_user_debts_monitor, sensor=sensor,
    ) as collector:
        await grocery_user_debts_create(debt=request_debt)

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'sensor': sensor,
        'originator': originator.name,
        'country': consts.COUNTRY,
        'payment_type': payment_type or 'none',
        'reason': error_code or 'none',
    }


def _make_request_debt(*, debt_id=consts.DEBT_ID, **kwargs):
    return {
        'debt_id': debt_id,
        'idempotency_token': consts.DEBT_IDEMPOTENCY_TOKEN,
        'user': consts.USER_INFO,
        'invoice': {**consts.INVOICE_INFO},
        'currency': consts.CURRENCY,
        'items': ITEMS,
        'reason_code': consts.DEBT_REASON_CODE,
        'reason': models.debt_reason(),
        'originator': 'grocery',
        **kwargs,
    }
