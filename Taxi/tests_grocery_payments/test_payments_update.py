import copy
import datetime
import decimal

import pytest

from . import consts
from . import headers
from . import helpers
from . import models
from . import pytest_marks
from .plugins import configs

PaymentType = models.PaymentType
# pylint: disable=invalid-name
Decimal = decimal.Decimal

COUNTRY = models.Country.Russia

ITEMS = [
    models.Item(item_id='item-id-1', price='10', quantity='2'),
    models.Item(
        item_id='item-id-2',
        price='20',
        quantity='1',
        receipt_info=models.ReceiptInfo(
            title='delivery-title',
            vat='20',
            personal_tin_id='personal-tin-id-x123',
        ),
    ),
    models.Item(
        item_id='item-id-3',
        price='123',
        quantity='1',
        item_type=models.ItemType.delivery,
    ),
]

PAYMENT_METHOD = models.PaymentMethod(
    payment_type=PaymentType.card, payment_id=consts.CARD_ID,
)

CASHBACK_PAYMENT_METHOD = models.PaymentMethod(
    payment_type=PaymentType.personal_wallet,
    payment_id=consts.PERSONAL_WALLET_ID,
)

OPERATION_SUM = models.OperationSum(ITEMS, PAYMENT_METHOD.payment_type)


@pytest.fixture(name='grocery_payments_update')
def _grocery_payments_update(taxi_grocery_payments):
    async def _inner(
            country=COUNTRY,
            items=None,
            payment_method=None,
            items_by_payment_types=None,
            **kwargs,
    ):
        if items_by_payment_types is None:
            items = items or ITEMS
            payment_method = payment_method or PAYMENT_METHOD
            items_by_payment_types = [
                {
                    'items': models.to_request_items(items),
                    'payment_method': payment_method.to_request(),
                },
            ]

        return await taxi_grocery_payments.post(
            '/payments/v1/update',
            json={
                'order_id': consts.ORDER_ID,
                'country_iso3': country.country_iso3,
                'items_by_payment_types': items_by_payment_types,
                'user_info': headers.DEFAULT_USER_INFO,
                **kwargs,
            },
        )

    return _inner


async def test_basic(grocery_payments_update, transactions):
    operation_id = '12345'
    operation_version = 123456

    trust_settings = configs.trust_settings_payload(COUNTRY)
    product_id = trust_settings['product_id']

    transactions.retrieve.mock_response(
        operation_info={'version': operation_version},
    )

    transactions.update.check(
        operation_type='update',
        operation_id=operation_id,
        id=consts.ORDER_ID,
        items_by_payment_type=[OPERATION_SUM.to_object(product_id=product_id)],
        originator=consts.TRANSACTIONS_ORIGINATOR,
        user_ip=headers.DEFAULT_IP,
        yandex_uid=headers.YANDEX_UID,
        disable_automatic_composite_refund=True,
        version=operation_version,
    )

    response = await grocery_payments_update(operation_id=operation_id)
    assert response.status_code == 200

    assert transactions.update.times_called == 1

    assert response.json() == {
        'invoice_id': consts.ORDER_ID,
        'operation_id': operation_id,
    }


@pytest_marks.INVOICE_ORIGINATORS
async def test_originator(grocery_payments_update, transactions, originator):
    invoice_id = originator.prefix + consts.ORDER_ID

    transactions.retrieve.mock_response(id=invoice_id)

    transactions.update.check(id=invoice_id)

    response = await grocery_payments_update(
        originator=originator.request_name,
    )
    assert response.status_code == 200

    assert transactions.update.times_called == 1

    assert response.json()['invoice_id'] == invoice_id


async def test_update_with_cashback(grocery_payments_update, transactions):
    trust_settings = configs.trust_settings_payload(COUNTRY)
    product_id = trust_settings['product_id']

    transactions.update.check(
        items_by_payment_type=[
            {
                'items': models.to_operation_items(
                    ITEMS, product_id=product_id,
                ),
                'payment_type': PAYMENT_METHOD.payment_type.value,
            },
            {
                'items': models.to_operation_items(
                    ITEMS, product_id=product_id,
                ),
                'payment_type': CASHBACK_PAYMENT_METHOD.payment_type.value,
            },
        ],
    )

    response = await grocery_payments_update(
        items_by_payment_types=[
            {
                'items': models.to_request_items(ITEMS),
                'payment_method': PAYMENT_METHOD.to_request(),
            },
            {
                'items': models.to_request_items(ITEMS),
                'payment_method': CASHBACK_PAYMENT_METHOD.to_request(),
            },
        ],
    )
    assert response.status_code == 200

    assert transactions.update.times_called == 1


@pytest.mark.parametrize(
    'desired_order',
    [None, ['card', 'personal_wallet'], ['personal_wallet', 'card']],
)
async def test_desired_payment_types_order(
        grocery_payments_update,
        transactions,
        grocery_payments_configs,
        desired_order,
):
    if desired_order is not None:
        grocery_payments_configs.grocery_payments_composite_payments_order(
            desired_order,
        )

    transactions.update.check(desired_payment_types_order=desired_order)

    response = await grocery_payments_update(
        items_by_payment_types=[
            {
                'items': models.to_request_items(ITEMS),
                'payment_method': PAYMENT_METHOD.to_request(),
            },
            {
                'items': models.to_request_items(ITEMS),
                'payment_method': CASHBACK_PAYMENT_METHOD.to_request(),
            },
        ],
    )

    assert response.status_code == 200

    assert transactions.update.times_called == 1


@pytest.mark.parametrize(
    'direct_wallet_id, request_wallet_id',
    [(True, False), (False, True), (False, False), (False, False)],
)
async def test_retrieve_wallet(
        grocery_payments_update,
        transactions,
        direct_wallet_id,
        request_wallet_id,
):
    payment_method = models.PaymentMethod(
        payment_type=PaymentType.personal_wallet,
        payment_id=consts.PERSONAL_WALLET_ID if request_wallet_id else '',
    )

    response = await grocery_payments_update(
        payment_method=payment_method,
        wallet_payload=(
            consts.DEFAULT_WALLET_PAYLOAD if direct_wallet_id else None
        ),
    )

    if direct_wallet_id or request_wallet_id:
        assert response.status_code == 200
    else:
        assert response.status_code == 400


@pytest.mark.parametrize('enable_modification', [True, False])
async def test_modification_policy(
        grocery_payments_update,
        grocery_payments_configs,
        transactions,
        enable_modification,
):
    grocery_payments_configs.invoice_modification_policy(
        enabled=enable_modification,
    )

    transactions.retrieve.mock_response(id=consts.ORDER_ID)

    response = await grocery_payments_update()

    if enable_modification:
        assert response.status_code == 200
        assert transactions.update.times_called == 1
    else:
        assert response.status_code == 400
        assert transactions.update.times_called == 0


@pytest.mark.parametrize(
    'deferred_task_status', [None, 'init', 'done', 'timeout'],
)
@pytest.mark.config(GROCERY_PAYMENTS_OPERATION_TTL_SECONDS=300)
async def test_deferred(
        grocery_payments_update,
        grocery_payments_configs,
        grocery_payments_db,
        transactions,
        deferred_task_status,
):
    invoice_id = consts.ORDER_ID
    operation_id = '12345'
    operation_id_full = f'update:{operation_id}'
    version = 5

    grocery_payments_configs.deferred_invoice_modification(enabled=True)

    payload = dict(
        type='update',
        country_iso3=COUNTRY.country_iso3,
        body=dict(
            operation_id=operation_id_full,
            id=invoice_id,
            items_by_payment_type=[],
            originator=consts.TRANSACTIONS_ORIGINATOR,
            user_ip=headers.DEFAULT_IP,
            yandex_uid=headers.YANDEX_UID,
            login_id=headers.LOGIN_ID,
            id_namespace=consts.SERVICE,
            ttl=300,
            disable_automatic_composite_refund=True,
            version=version,
            trust_afs_params={'force_3ds': False},
        ),
    )

    if deferred_task_status is not None:
        task = models.DeferredTask(
            invoice_id,
            operation_id_full,
            status=deferred_task_status,
            payload=payload,
        )
        grocery_payments_db.upsert_deferred(task)

    transactions.clear.check(id=invoice_id)

    transactions.retrieve.mock_response(
        id=invoice_id,
        operation_info={
            'originator': 'processing',
            'priority': 1,
            'version': version,
        },
    )

    response = await grocery_payments_update(
        operation_id=operation_id, items_by_payment_types=[],
    )

    if deferred_task_status is None:
        assert response.status_code == 200
        assert transactions.update.times_called == 0
        assert transactions.clear.times_called == 1

        task = grocery_payments_db.load_deferred(invoice_id, operation_id_full)
        assert task is not None
        assert task.status == 'init'
        assert task.payload == payload
    elif deferred_task_status != 'init':
        assert response.status_code == 200
        assert transactions.update.times_called == 1
        assert transactions.clear.times_called == 0
    else:
        assert response.status_code == 400
        assert transactions.update.times_called == 0
        assert transactions.clear.times_called == 0


@pytest.mark.now(consts.NOW)
async def test_deferred_timeout(
        grocery_payments_update,
        grocery_payments_configs,
        transactions,
        check_operation_timeout_stq_event,
):
    operation_type = 'update'
    operation_id = '12345'
    ttl_seconds = 123

    grocery_payments_configs.deferred_invoice_modification(enabled=True)
    grocery_payments_configs.set_operation_timeout(ttl_seconds=ttl_seconds)

    response = await grocery_payments_update(
        operation_id=operation_id, items_by_payment_types=[],
    )
    assert response.status_code == 200

    invoice_id = response.json()['invoice_id']
    operation_id_full = f'{operation_type}:{operation_id}'
    task_id = f'{invoice_id}_{operation_id_full}'
    eta = consts.NOW_DT + datetime.timedelta(seconds=ttl_seconds)

    check_operation_timeout_stq_event(
        stq_event_id=task_id,
        eta=eta,
        invoice_id=invoice_id,
        operation_id=operation_id_full,
        type='deferred_operation',
    )


@pytest_marks.INVOICE_ORIGINATORS
async def test_debt_update(
        grocery_payments_update, transactions, grocery_user_debts, originator,
):
    invoice_id = originator.prefix + consts.ORDER_ID
    trust_settings = configs.trust_settings_payload(COUNTRY)
    product_id = trust_settings['product_id']
    operation_id = 'operation_id123'

    items = [OPERATION_SUM.to_object(product_id=product_id)]

    invoice_operations = [
        helpers.make_operation(sum_to_pay=items, status='failed'),
        helpers.make_operation(sum_to_pay=items, status='failed'),
    ]

    grocery_user_debts.debt_available = True
    grocery_user_debts.retrieve.mock_response(debt_id=invoice_id, items=items)

    transactions.retrieve.mock_response(
        id=invoice_id, operations=invoice_operations,
    )

    grocery_user_debts.update.check(
        debt=dict(
            debt_id=invoice_id,
            idempotency_token=f'update/update:{operation_id}',
            items=items,
            reason_code='update',
        ),
        operation=dict(
            operation_type='update',
            operation_id=operation_id,
            priority=len(invoice_operations),
        ),
        order=dict(
            order_id=consts.ORDER_ID, country_iso3=COUNTRY.country_iso3,
        ),
    )

    response = await grocery_payments_update(
        operation_id=operation_id, originator=originator.request_name,
    )
    assert response.status_code == 200

    assert transactions.update.times_called == 1
    assert grocery_user_debts.retrieve.times_called == 1
    assert grocery_user_debts.update.times_called == 1


@pytest.mark.parametrize('debt_available', [True, False])
@pytest.mark.parametrize(
    'new_quantity, expect_request', [('6', True), ('5', False)],
)
async def test_debt_request(
        grocery_payments_update,
        transactions,
        grocery_user_debts,
        debt_available,
        new_quantity,
        expect_request,
):
    operation_sum_list = [copy.deepcopy(OPERATION_SUM) for _ in range(3)]
    operation_sum_list[0].items[0].quantity = '5'
    operation_sum_list[1].items[0].quantity = '10'
    operation_sum_list[2].items[0].quantity = new_quantity

    items_list = [[it.to_object()] for it in operation_sum_list]

    amount_0 = Decimal(operation_sum_list[0].amount())
    amount_2 = Decimal(operation_sum_list[2].amount())
    debt_amount = str(amount_2 - amount_0)

    grocery_user_debts.debt_available = debt_available
    grocery_user_debts.retrieve.mock_response(
        debt_id=consts.ORDER_ID, items=items_list[1],
    )

    transactions.retrieve.mock_response(
        id=consts.ORDER_ID,
        operations=[
            helpers.make_operation(sum_to_pay=items_list[0], status='done'),
            helpers.make_operation(sum_to_pay=items_list[1], status='failed'),
        ],
    )

    grocery_user_debts.request.check(
        debt_id=consts.ORDER_ID,
        user=dict(
            yandex_uid=headers.YANDEX_UID,
            personal_phone_id=headers.PERSONAL_PHONE_ID,
        ),
        order=dict(
            order_id=consts.ORDER_ID, country_iso3=COUNTRY.country_iso3,
        ),
        reason=None,
        originator=models.InvoiceOriginator.grocery.name,
        debt_amount=debt_amount,
    )

    response = await grocery_payments_update(items=operation_sum_list[2].items)
    assert response.status_code == 200

    assert transactions.update.times_called == 1
    assert grocery_user_debts.request.times_called == int(expect_request)


async def test_idempotency(
        grocery_payments_update, grocery_payments_db, transactions,
):
    invoice_id = consts.ORDER_ID
    operation_id = 'operation_id'

    for _ in range(2):
        response = await grocery_payments_update(operation_id=operation_id)
        assert response.status_code == 200

        assert grocery_payments_db.has_invoice_operation(
            invoice_id, f'update:{operation_id}',
        )

    assert transactions.update.times_called == 1


@pytest.mark.parametrize('operation_id', ['', ':', 'op:', ':op', 'o:p'])
async def test_wrong_operation_id(grocery_payments_update, operation_id):
    response = await grocery_payments_update(operation_id=operation_id)
    assert response.status_code == 400


async def test_trust_afs_params(grocery_payments_update, transactions):
    trust_afs_params = {'force_3ds': False}
    transactions.update.check(trust_afs_params=trust_afs_params)

    response = await grocery_payments_update()
    assert response.status_code == 200

    assert transactions.update.times_called == 1
