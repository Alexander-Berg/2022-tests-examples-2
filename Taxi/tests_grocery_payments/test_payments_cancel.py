import pytest

from . import consts
from . import headers
from . import helpers
from . import models
from . import pytest_marks

PaymentType = models.PaymentType

COUNTRY = models.Country.Russia


@pytest.fixture(name='grocery_payments_cancel')
def _grocery_payments_cancel(taxi_grocery_payments):
    async def _inner(country=COUNTRY, **kwargs):
        return await taxi_grocery_payments.post(
            '/payments/v1/cancel',
            json={
                'order_id': consts.ORDER_ID,
                'country_iso3': country.country_iso3,
                'user_info': headers.DEFAULT_USER_INFO,
                **kwargs,
            },
        )

    return _inner


async def test_basic(grocery_payments_cancel, transactions):
    operation_id = '12345'

    transactions.retrieve.mock_response(status='held')

    transactions.update.check(
        operation_type='cancel',
        operation_id=operation_id,
        id=consts.ORDER_ID,
        items_by_payment_type=[],
    )

    response = await grocery_payments_cancel(operation_id=operation_id)
    assert response.status_code == 200

    assert transactions.update.times_called == 1
    assert transactions.clear.times_called == 1

    assert response.json() == {
        'invoice_id': consts.ORDER_ID,
        'operation_type': 'cancel',
        'operation_id': operation_id,
    }


@pytest_marks.INVOICE_ORIGINATORS
async def test_originator(grocery_payments_cancel, transactions, originator):
    invoice_id = originator.prefix + consts.ORDER_ID

    transactions.retrieve.mock_response(status='held')

    transactions.update.check(id=invoice_id)

    response = await grocery_payments_cancel(
        originator=originator.request_name,
    )
    assert response.status_code == 200

    assert transactions.update.times_called == 1
    assert transactions.clear.times_called == 1

    assert response.json()['invoice_id'] == invoice_id


@pytest_marks.INVOICE_STATUSES_WITH_CLEARED
async def test_invoice_status(
        grocery_payments_cancel, transactions, invoice_status, is_cleared,
):
    transactions.retrieve.mock_response(status=invoice_status)

    response = await grocery_payments_cancel()
    assert response.status_code == 200

    assert response.json()['operation_type'] == 'cancel'
    assert transactions.update.times_called == 1
    assert transactions.clear.times_called == 1


async def test_cancel_after_cancel(grocery_payments_cancel, transactions):
    operation_type = 'cancel'
    revision = '123123'
    cancel_operation_id = f'{operation_type}:{revision}'
    request_operation_id = 'cancel_request'

    assert cancel_operation_id != request_operation_id

    transactions.retrieve.mock_response(
        status='cleared',
        operations=[
            helpers.make_operation(id='create:1'),
            helpers.make_operation(id=cancel_operation_id, sum_to_pay=[]),
        ],
    )

    response = await grocery_payments_cancel(operation_id=request_operation_id)
    assert response.status_code == 200

    assert response.json()['operation_type'] == operation_type
    assert response.json()['operation_id'] == revision
    assert transactions.update.times_called == 0
    assert transactions.clear.times_called == 0


@pytest_marks.INVOICE_STATUSES_WITH_CLEARED
async def test_cancel_with_refund(
        grocery_payments_cancel, transactions, invoice_status, is_cleared,
):
    transactions.retrieve.mock_response(status=invoice_status)

    operation_type = 'cancel'

    transactions.update.check(
        operation_type=operation_type,
        id=consts.ORDER_ID,
        items_by_payment_type=[],
    )

    response = await grocery_payments_cancel(maybe_refund=True)
    assert response.status_code == 200

    assert response.json()['operation_type'] == operation_type
    assert transactions.update.times_called == 1
    assert transactions.clear.times_called == 1


@pytest_marks.INVOICE_STATUSES_WITH_CLEARED
async def test_404(
        grocery_payments_cancel, transactions, invoice_status, is_cleared,
):
    transactions.retrieve.mock_response(status=invoice_status)
    transactions.update.status_code = 404

    response = await grocery_payments_cancel(maybe_refund=True)
    assert response.status_code == 404


@pytest.mark.parametrize('operations', [None, []])
async def test_cancel_of_empty_invoice(
        grocery_payments_cancel, transactions, operations,
):
    transactions.retrieve.mock_response(
        status='cleared', operations=operations,
    )

    response = await grocery_payments_cancel(maybe_refund=True)
    assert response.status_code == 404


@pytest.mark.parametrize('enable_modification', [True, False])
async def test_modification_policy(
        grocery_payments_cancel,
        grocery_payments_configs,
        transactions,
        enable_modification,
):
    grocery_payments_configs.invoice_modification_policy(
        enabled=enable_modification,
    )

    transactions.retrieve.mock_response(id=consts.ORDER_ID)

    response = await grocery_payments_cancel()

    if enable_modification:
        assert response.status_code == 200
        assert transactions.update.times_called == 1
    else:
        assert response.status_code == 400
        assert transactions.update.times_called == 0


@pytest_marks.INVOICE_ORIGINATORS
async def test_debt_cancel(
        grocery_payments_cancel, transactions, grocery_user_debts, originator,
):
    invoice_id = originator.prefix + consts.ORDER_ID

    transactions.retrieve.mock_response(id=invoice_id)

    grocery_user_debts.set_pay_strategy.check(
        debt_id=invoice_id,
        idempotency_token='set_null_pay_strategy',
        order_id=consts.ORDER_ID,
        strategy=dict(type='null'),
    )

    grocery_user_debts.cancel.check(
        debt=dict(
            debt_id=invoice_id,
            idempotency_token='cancel',
            reason_code='cancel',
        ),
        order=dict(
            order_id=consts.ORDER_ID, country_iso3=COUNTRY.country_iso3,
        ),
    )

    response = await grocery_payments_cancel(
        originator=originator.request_name,
    )
    assert response.status_code == 200

    assert grocery_user_debts.cancel.times_called == 1
    assert grocery_user_debts.set_pay_strategy.times_called == 1


@pytest.mark.parametrize('deferred_task_status', ['init', 'done'])
async def test_deferred(
        grocery_payments_cancel,
        grocery_payments_configs,
        grocery_payments_db,
        transactions,
        deferred_task_status,
):
    grocery_payments_configs.deferred_invoice_modification(enabled=True)

    task = models.DeferredTask(
        consts.ORDER_ID,
        'operation_id',
        status=deferred_task_status,
        payload=dict(),
    )
    grocery_payments_db.upsert_deferred(task)

    response = await grocery_payments_cancel()

    if deferred_task_status == 'init':
        assert response.status_code == 400
        assert transactions.update.times_called == 0
    else:
        assert response.status_code == 200
        assert transactions.update.times_called == 1


async def test_idempotency(
        grocery_payments_cancel, grocery_payments_db, transactions,
):
    invoice_id = consts.ORDER_ID
    operation_id = 'operation_id'

    for _ in range(2):
        response = await grocery_payments_cancel(operation_id=operation_id)
        assert response.status_code == 200

        assert grocery_payments_db.has_invoice_operation(
            invoice_id, f'cancel:{operation_id}',
        )

    assert transactions.update.times_called == 1


@pytest.mark.parametrize('operation_id', ['', ':', 'op:', ':op', 'o:p'])
async def test_wrong_operation_id(grocery_payments_cancel, operation_id):
    response = await grocery_payments_cancel(operation_id=operation_id)
    assert response.status_code == 400
