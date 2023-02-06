# pylint: disable=import-error
import decimal

from grocery_mocks.utils import helpers as mock_helpers
import pytest

from . import consts
from . import helpers
from . import models
from . import pytest_marks

COUNTRY = models.Country.Russia
# pylint: disable=invalid-name
Decimal = decimal.Decimal

OPERATION_ID = 'create:123'
DEBT_VERSION = 11

PAYMENT_METHOD = models.PaymentMethod(models.PaymentType.card, consts.CARD_ID)
PAYMENT_METHOD_WALLET = models.PaymentMethod(
    models.PaymentType.personal_wallet, consts.PERSONAL_WALLET_ID,
)

OPERATION_SUM = models.OperationSum(
    items=[
        models.Item(item_id='333', price='500', quantity='1'),
        models.Item(
            item_id='444',
            price='100',
            quantity='2',
            item_type=models.ItemType.delivery,
        ),
    ],
    payment_type=PAYMENT_METHOD.payment_type,
)
OPERATION_SUM_WALLET = models.OperationSum(
    items=[models.Item(item_id='555', price='500', quantity='1')],
    payment_type=PAYMENT_METHOD_WALLET.payment_type,
)


@pytest_marks.INVOICE_ORIGINATORS
async def test_debt_request(
        grocery_orders,
        grocery_user_debts,
        transactions,
        run_transactions_callback,
        originator,
):
    invoice_id = originator.prefix + consts.ORDER_ID
    error_reason_code = 'error_reason_code'
    technical_error = True

    _mock_retrieve(
        transactions,
        invoice_id=invoice_id,
        operation_id=OPERATION_ID,
        error_reason_code=error_reason_code,
        technical_error=technical_error,
    )

    debt_amount = str(
        Decimal(OPERATION_SUM.amount())
        + Decimal(OPERATION_SUM_WALLET.amount()),
    )

    grocery_user_debts.request.check(
        debt_id=invoice_id,
        order=dict(
            order_id=consts.ORDER_ID, country_iso3=COUNTRY.country_iso3,
        ),
        user=_make_user_info(grocery_orders.order),
        reason=_make_debt_reason(
            error_reason_code=error_reason_code,
            is_technical_error=technical_error,
        ),
        originator=originator.name,
        debt_amount=debt_amount,
    )

    await run_transactions_callback(
        notification_type=consts.OPERATION_FINISH,
        operation_id=OPERATION_ID,
        operation_status=consts.OPERATION_FAILED,
        originator=originator,
    )

    assert grocery_user_debts.request.times_called == 1


async def test_debt_create(
        grocery_orders,
        grocery_user_debts,
        transactions,
        run_transactions_callback,
):
    operation_type = 'create'
    operation_id = f'{operation_type}:123'

    grocery_user_debts.debt_available = True

    _mock_retrieve(transactions, operation_id=operation_id)

    grocery_user_debts.create.check(
        debt=dict(
            debt_id=consts.ORDER_ID,
            idempotency_token=f'create/{operation_id}',
            user=_make_user_info(grocery_orders.order),
            invoice=dict(
                id=consts.ORDER_ID,
                id_namespace=consts.SERVICE,
                originator='grocery_user_debts',
                transactions_installation='eda',
            ),
            currency=COUNTRY.currency,
            items=[
                OPERATION_SUM.to_object(),
                OPERATION_SUM_WALLET.to_object(),
            ],
            reason_code='create',
            reason=_make_debt_reason(
                error_reason_code='error_reason_code',
                is_technical_error=False,
            ),
            originator=models.InvoiceOriginator.grocery.name,
        ),
        order=dict(
            order_id=consts.ORDER_ID, country_iso3=COUNTRY.country_iso3,
        ),
        operation=_make_operation_info(operation_id=operation_id, priority=0),
    )

    await run_transactions_callback(
        notification_type=consts.OPERATION_FINISH,
        operation_id=operation_id,
        operation_status=consts.OPERATION_FAILED,
    )

    assert grocery_user_debts.create.times_called == 1


async def test_debt_update(
        grocery_orders,
        grocery_user_debts,
        transactions,
        run_transactions_callback,
):
    operation_type = 'update'
    operation_id = f'{operation_type}:123'

    grocery_user_debts.debt_available = True

    before_operations = [helpers.make_operation()] * 2

    _mock_debt(grocery_user_debts)
    _mock_retrieve(
        transactions,
        operation_id=operation_id,
        before_operations=before_operations,
    )

    grocery_user_debts.update.check(
        debt=dict(
            debt_id=consts.ORDER_ID,
            idempotency_token=f'update/{operation_id}',
            items=[
                OPERATION_SUM.to_object(),
                OPERATION_SUM_WALLET.to_object(),
            ],
            reason_code='update',
        ),
        order=dict(
            order_id=consts.ORDER_ID, country_iso3=COUNTRY.country_iso3,
        ),
        operation=_make_operation_info(
            operation_id=operation_id, priority=len(before_operations),
        ),
    )

    await run_transactions_callback(
        notification_type=consts.OPERATION_FINISH,
        operation_id=operation_id,
        operation_status=consts.OPERATION_FAILED,
    )

    assert grocery_user_debts.update.times_called == 1


@pytest.mark.parametrize(
    'kwargs',
    [
        dict(
            notification_type=consts.OPERATION_FINISH,
            operation_status=consts.OPERATION_FAILED,
            transaction_status='hold_fail',
            expect_debt_create=True,
        ),
        dict(
            notification_type=consts.OPERATION_FINISH,
            operation_status=consts.OPERATION_DONE,
            transaction_status='hold_fail',
            expect_debt_create=False,
        ),
        dict(
            notification_type=consts.OPERATION_FINISH,
            operation_status=consts.OPERATION_FAILED,
            transaction_status='hold_success',
            expect_debt_create=True,
        ),
        dict(
            notification_type=consts.OPERATION_FINISH,
            operation_status=consts.OPERATION_FAILED,
            transaction_status='hold_fail',
            expect_debt_create=True,
        ),
        dict(
            notification_type=consts.OPERATION_FINISH,
            operation_status=consts.OPERATION_OBSOLETE,
            transaction_status='hold_fail',
            expect_debt_create=True,
        ),
        dict(
            notification_type=consts.TRANSACTION_CLEAR,
            operation_status=consts.OPERATION_FAILED,
            transaction_status='hold_fail',
            expect_debt_create=False,
        ),
        dict(
            notification_type=consts.OPERATION_FINISH,
            operation_status=consts.OPERATION_FAILED,
            transaction_status='hold_fail',
            debt_request=False,
            expect_debt_create=False,
        ),
    ],
)
async def test_debt_create_conditions(
        grocery_payments_configs,
        grocery_orders,
        grocery_user_debts,
        transactions,
        run_transactions_callback,
        kwargs,
):
    operation_type = 'create'
    operation_id = f'{operation_type}:123'

    grocery_payments_configs.debt_request(kwargs.get('debt_request', True))

    grocery_user_debts.debt_available = True

    _mock_retrieve(
        transactions,
        operation_id=operation_id,
        operation_status=kwargs['operation_status'],
        transaction_status=kwargs.get('transaction_status', 'hold_success'),
    )

    await run_transactions_callback(
        notification_type=kwargs['notification_type'],
        operation_id=operation_id,
        operation_status=kwargs['operation_status'],
    )

    expect_debt_create = int(kwargs.get('expect_debt_create', False))
    assert grocery_user_debts.create.times_called == expect_debt_create


@pytest.mark.parametrize(
    'kwargs',
    [
        dict(
            notification_type=consts.OPERATION_FINISH,
            operation_status=consts.OPERATION_FAILED,
            transaction_status='hold_fail',
            expect_debt_create=True,
        ),
        dict(
            notification_type=consts.OPERATION_FINISH,
            operation_status=consts.OPERATION_DONE,
            transaction_status='hold_fail',
            expect_debt_create=False,
        ),
        dict(
            notification_type=consts.OPERATION_FINISH,
            operation_status=consts.OPERATION_FAILED,
            transaction_status='hold_success',
            expect_debt_create=True,
        ),
        dict(
            notification_type=consts.OPERATION_FINISH,
            operation_status=consts.OPERATION_FAILED,
            transaction_status='hold_fail',
            expect_debt_create=True,
        ),
        dict(
            notification_type=consts.OPERATION_FINISH,
            operation_status=consts.OPERATION_OBSOLETE,
            transaction_status='hold_fail',
            expect_debt_create=True,
        ),
        dict(
            notification_type=consts.TRANSACTION_CLEAR,
            operation_status=consts.OPERATION_FAILED,
            transaction_status='hold_fail',
            expect_debt_create=False,
        ),
        dict(
            notification_type=consts.OPERATION_FINISH,
            operation_status=consts.OPERATION_FAILED,
            transaction_status='hold_fail',
            debt=dict(items=[OPERATION_SUM.to_object()]),
            expect_debt_create=False,
            expect_debt_update=True,
        ),
        dict(
            notification_type=consts.OPERATION_FINISH,
            operation_status=consts.OPERATION_FAILED,
            transaction_status='hold_fail',
            debt_request=False,
            expect_debt_update=False,
        ),
        dict(
            notification_type=consts.OPERATION_FINISH,
            operation_status=consts.OPERATION_DONE,
            transaction_status='hold_success',
            debt=dict(items=[OPERATION_SUM.to_object()]),
            expect_debt_update=True,
        ),
    ],
)
async def test_debt_update_conditions(
        grocery_payments_configs,
        grocery_orders,
        grocery_user_debts,
        transactions,
        run_transactions_callback,
        kwargs,
):
    operation_type = 'update'
    operation_id = f'{operation_type}:123'

    grocery_payments_configs.debt_request(kwargs.get('debt_request', True))

    grocery_user_debts.debt_available = True

    if 'debt' in kwargs:
        _mock_debt(grocery_user_debts, **kwargs['debt'])

    _mock_retrieve(
        transactions,
        operation_id=operation_id,
        operation_status=kwargs['operation_status'],
        transaction_status=kwargs.get('transaction_status', 'hold_success'),
    )

    await run_transactions_callback(
        notification_type=kwargs['notification_type'],
        operation_id=operation_id,
        operation_status=kwargs['operation_status'],
    )

    expect_debt_create = int(kwargs.get('expect_debt_create', False))
    assert grocery_user_debts.create.times_called == expect_debt_create

    expect_debt_update = int(kwargs.get('expect_debt_update', False))
    assert grocery_user_debts.update.times_called == expect_debt_update


async def test_debt_after_fallbacks(
        grocery_payments_configs,
        grocery_orders,
        grocery_user_debts,
        transactions,
        run_transactions_callback,
):
    operation_type = 'create'
    operation_id = f'{operation_type}:123'
    operation_id_attempt_1 = f'{operation_id}:attempt:1'

    transactions.retrieve.mock_response(
        operations=[
            helpers.make_operation(
                id=operation_id,
                status=consts.OPERATION_FAILED,
                sum_to_pay=[OPERATION_SUM.to_object()],
            ),
            helpers.make_operation(
                id=operation_id_attempt_1,
                status=consts.OPERATION_FAILED,
                sum_to_pay=[OPERATION_SUM.to_object()],
            ),
            helpers.make_operation(),
        ],
        transactions=[
            helpers.make_transaction(
                status='hold_fail',
                sum=OPERATION_SUM.to_transaction_sum(),
                external_payment_id=consts.EXTERNAL_PAYMENT_ID,
                payment_type=PAYMENT_METHOD.payment_type.value,
                payment_method_id=PAYMENT_METHOD.payment_id,
                error_reason_code='error_reason_code',
                technical_error=False,
                operation_id=operation_id,
            ),
            helpers.make_transaction(
                status='hold_fail',
                sum=OPERATION_SUM.to_transaction_sum(),
                external_payment_id=consts.EXTERNAL_PAYMENT_ID,
                payment_type=PAYMENT_METHOD.payment_type.value,
                payment_method_id=PAYMENT_METHOD.payment_id,
                error_reason_code='error_reason_code_tech',
                technical_error=True,
                operation_id=operation_id_attempt_1,
            ),
            helpers.make_transaction(),
        ],
    )

    grocery_user_debts.request.check(
        reason=mock_helpers.sub_dict(
            error_reason_code='error_reason_code',
            is_technical_error=False,
            errors=[
                dict(
                    error_reason_code='error_reason_code',
                    is_technical_error=False,
                ),
                dict(
                    error_reason_code='error_reason_code_tech',
                    is_technical_error=True,
                ),
            ],
        ),
    )

    await run_transactions_callback(
        notification_type=consts.OPERATION_FINISH,
        operation_id=OPERATION_ID,
        operation_status=consts.OPERATION_FAILED,
    )

    assert grocery_user_debts.request.times_called == 1


async def test_debt_clear_after_success(
        grocery_payments_configs,
        grocery_orders,
        grocery_user_debts,
        transactions,
        run_transactions_callback,
):
    _mock_debt(grocery_user_debts)
    _mock_retrieve(
        transactions,
        operation_id=OPERATION_ID,
        operation_status=consts.OPERATION_DONE,
        transaction_status='hold_success',
    )

    grocery_user_debts.clear.check(
        debt=dict(
            debt_id=consts.ORDER_ID,
            idempotency_token=f'clear/{OPERATION_ID}',
            reason_code='clear',
            strategy={'type': 'now'},
        ),
    )

    await run_transactions_callback(
        notification_type=consts.OPERATION_FINISH,
        operation_id=OPERATION_ID,
        operation_status=consts.OPERATION_DONE,
    )

    assert grocery_user_debts.clear.times_called == 1


@pytest.mark.parametrize(
    'notification_type', [consts.OPERATION_FINISH, consts.TRANSACTION_CLEAR],
)
@pytest.mark.parametrize(
    'operation_type',
    ['create', 'update', 'refund', 'cancel', 'append', 'remove'],
)
@pytest.mark.parametrize(
    'operation_status, transaction_status, is_fail_status',
    [
        (consts.OPERATION_FAILED, 'hold_fail', True),
        (consts.OPERATION_DONE, 'hold_success', False),
    ],
)
async def test_prediction_send(
        grocery_orders,
        transactions,
        grocery_user_debts,
        run_transactions_callback,
        operation_type,
        notification_type,
        operation_status,
        transaction_status,
        is_fail_status,
):
    operation_id = f'{operation_type}:123'

    _mock_retrieve(
        transactions,
        operation_id=operation_id,
        operation_status=operation_status,
        transaction_status=transaction_status,
    )

    debt_amount = str(
        Decimal(OPERATION_SUM.amount())
        + Decimal(OPERATION_SUM_WALLET.amount()),
    )

    if is_fail_status:
        debt_reason = _make_debt_reason(error_reason_code='error_reason_code')
    else:
        debt_reason = _make_debt_reason()

    grocery_user_debts.append_prediction.check(
        reason='append-prediction',
        debt=dict(
            debt_id=consts.ORDER_ID,
            user=_make_user_info(grocery_orders.order),
            actual_debt_pred_status='fail' if is_fail_status else 'paid',
            reason=debt_reason,
            originator=models.InvoiceOriginator.grocery.name,
            debt_amount=debt_amount,
        ),
        order=dict(
            order_id=consts.ORDER_ID, country_iso3=COUNTRY.country_iso3,
        ),
    )

    await run_transactions_callback(
        notification_type=notification_type,
        operation_id=operation_id,
        operation_status=operation_status,
    )

    prediction_called = int(
        notification_type == consts.OPERATION_FINISH
        and operation_type == 'create',
    )
    assert (
        grocery_user_debts.append_prediction.times_called == prediction_called
    )


def _make_user_info(order):
    return dict(
        personal_phone_id=order['user_info']['personal_phone_id'],
        yandex_uid=order['user_info']['yandex_uid'],
    )


def _make_operation_info(operation_id, priority):
    operation_type, operation_id = operation_id.split(':')
    return dict(
        operation_type=operation_type,
        operation_id=operation_id,
        priority=priority,
    )


def _make_debt_reason(**kwargs):
    if 'errors' not in kwargs and 'error_reason_code' in kwargs:
        kwargs['errors'] = [
            dict(
                error_reason_code=kwargs.get('error_reason_code'),
                is_technical_error=kwargs.get('is_technical_error', False),
            ),
        ]

    return {
        'payment_type': PAYMENT_METHOD.payment_type.value,
        'payment_id': PAYMENT_METHOD.payment_id,
        'composite_payment_type': PAYMENT_METHOD_WALLET.payment_type.value,
        'is_technical_error': False,
        **kwargs,
    }


def _mock_debt(
        grocery_user_debts, debt_id=consts.ORDER_ID, items=None, **kwargs,
):
    if items is None:
        items = [OPERATION_SUM.to_object()]

    grocery_user_debts.retrieve.mock_response(
        debt_id=debt_id,
        created=consts.NOW,
        items=items,
        version=DEBT_VERSION,
        **kwargs,
    )


def _mock_retrieve(
        transactions,
        *,
        operation_id,
        operation_status=consts.OPERATION_FAILED,
        invoice_id=consts.ORDER_ID,
        transaction_status='hold_fail',
        error_reason_code='error_reason_code',
        technical_error=None,
        before_operations=None,
):
    transactions.retrieve.mock_response(
        id=invoice_id,
        operations=[
            *(before_operations or []),
            helpers.make_operation(
                id=operation_id,
                status=operation_status,
                sum_to_pay=[
                    OPERATION_SUM.to_object(),
                    OPERATION_SUM_WALLET.to_object(),
                ],
            ),
            helpers.make_operation(),
        ],
        transactions=[
            helpers.make_transaction(
                status=transaction_status,
                sum=OPERATION_SUM.to_transaction_sum(),
                external_payment_id=consts.EXTERNAL_PAYMENT_ID,
                payment_type=PAYMENT_METHOD.payment_type.value,
                payment_method_id=PAYMENT_METHOD.payment_id,
                error_reason_code=error_reason_code,
                technical_error=technical_error,
                operation_id=operation_id,
            ),
            helpers.make_transaction(
                status='clear_success',
                sum=OPERATION_SUM_WALLET.to_transaction_sum(),
                external_payment_id=consts.EXTERNAL_PAYMENT_ID,
                payment_type=PAYMENT_METHOD_WALLET.payment_type.value,
                payment_method_id=PAYMENT_METHOD_WALLET.payment_id,
                operation_id=operation_id,
            ),
        ],
    )
