import dataclasses
import decimal
import enum
import typing

import pytest

from . import consts
from . import models
from . import pytest_marks
from .plugins import mock_billing_orders

Payment = mock_billing_orders.Payment
ReceiptType = models.ReceiptType
# pylint: disable=invalid-name
Decimal = decimal.Decimal

EATS_STQ_TRANSACTION_DATE = '2021-03-12T12:40:00+00:00'
EATS_STQ_EVENT_AT = '2020-03-17T12:40:00+00:00'


class TlogPaymentType(enum.Enum):
    gross_sales = enum.auto()
    delivery = enum.auto()
    tips = enum.auto()


@dataclasses.dataclass
class SubItem:
    price: str
    quantity: str
    full_price: typing.Optional[str] = None
    id: typing.Optional[str] = None
    refunded: typing.Optional[str] = None

    @property
    def cost_for_customer(self) -> str:
        price = Decimal(self.price)
        quantity = Decimal(self.quantity)
        refunded = Decimal(self.refunded or '0')
        return str(price * (quantity - refunded))

    @property
    def refunded_amount(self) -> typing.Optional[str]:
        if self.refunded is None:
            return None

        price = Decimal(self.price)
        refunded = Decimal(self.refunded)
        return str(price * refunded)


@pytest.fixture(autouse=True)
def _tlog_configs(grocery_payments_billing_configs):
    grocery_payments_billing_configs.tlog_enabled(True)
    grocery_payments_billing_configs.tlog_params()
    grocery_payments_billing_configs.service_id_mapping()
    grocery_payments_billing_configs.products_settings_default()


@pytest.fixture
def _items_controller():
    def _make_sub_item_id(item_id, index=0):
        return item_id + '-' + str(index)

    def _split_items(items: typing.List[SubItem]) -> typing.List[SubItem]:
        result = []
        for item in items:
            refunded_total = Decimal(item.refunded or '0')
            for _ in range(int(Decimal(item.quantity))):
                result.append(
                    dataclasses.replace(
                        item,
                        quantity='1',
                        refunded='1' if refunded_total > 0 else None,
                    ),
                )
                refunded_total -= 1
        return result

    class Context:
        def __init__(self):
            self.stq_items = []
            self.eats_customer_services = []

        def _add_eats_item_product(self, item: SubItem, item_id, vat):
            for service_details in self.eats_customer_services:
                if service_details['id'] == 'composition-products':
                    break
            else:
                service_details = {
                    'id': 'composition-products',
                    'name': 'Продукты заказа',
                    'cost_for_customer': '0',
                    'currency': models.Country.Russia.currency,
                    'type': 'composition_products',
                    'trust_product_id': 'eda_107819207_ride',
                    'place_id': consts.DEPOT_ID,
                    'balance_client_id': consts.BALANCE_CLIENT_ID,
                    'details': {
                        'composition_products': [],
                        'discriminator_type': 'composition_products_details',
                    },
                }
                self.eats_customer_services.append(service_details)

            assert item.quantity == '1', 'subitems are not split?'
            service_details['details']['composition_products'].append(
                {
                    'id': item.id,
                    'name': 'item desc',
                    'partner_name': 'item_partner_name',
                    'cost_for_customer': item.cost_for_customer,
                    'type': 'product',
                    'vat': 'nds_' + vat,
                    'origin_id': item_id,
                },
            )

            if item.refunded is not None:
                if 'refunds' not in service_details['details']:
                    service_details['details']['refunds'] = [
                        {
                            'refund_revision_id': 'refund_revision_id',
                            'refund_products': [],
                        },
                    ]
                refund_products = service_details['details']['refunds'][0][
                    'refund_products'
                ]

                refund_products.append(
                    {'id': item.id, 'refunded_amount': item.refunded_amount},
                )

        def _add_eats_item_other(self, item: SubItem, item_type, vat):
            self.eats_customer_services.append(
                {
                    'id': item.id,
                    'name': 'name',
                    'cost_for_customer': item.cost_for_customer,
                    'currency': models.Country.Russia.currency,
                    'type': item_type,
                    'trust_product_id': 'trust_product_id',
                    'place_id': consts.DEPOT_ID,
                    'vat': 'nds_' + vat,
                    'balance_client_id': consts.BALANCE_CLIENT_ID,
                    'refunded_amount': item.refunded_amount,
                },
            )

        def _add_stq_item(self, item: SubItem, item_type):
            self.stq_items.append(
                {
                    'item_id': item.id,
                    'item_type': item_type,
                    'amount': item.price,
                    'balance_client_id': consts.BALANCE_CLIENT_ID,
                    'place_id': consts.DEPOT_ID,
                },
            )

        def add_item(
                self,
                *,
                item_id,
                item_type,
                vat,
                sub_items: typing.List[SubItem],
        ):
            sub_items = _split_items(sub_items)
            for index, sub_item in enumerate(sub_items):
                sub_item.full_price = sub_item.full_price or sub_item.price
                sub_item.id = sub_item.id or _make_sub_item_id(item_id, index)

                if item_type == 'product':
                    self._add_eats_item_product(sub_item, item_id, vat)
                else:
                    self._add_eats_item_other(sub_item, item_type, vat)

                self._add_stq_item(sub_item, item_type)

            return item_id

    context = Context()
    return context


@pytest.fixture(autouse=True)
def mock_eats_core_order_revision(eats_core_order_revision, _items_controller):
    revision_id = 'revision_id'

    eats_core_order_revision.mock_list(
        revisions=[dict(revision_id=revision_id)],
    )
    eats_core_order_revision.mock_customer_services(
        _items_controller.eats_customer_services,
    )

    eats_core_order_revision.check_list(order_id=consts.EATS_ORDER_ID)
    eats_core_order_revision.check_customer_services(
        order_id=consts.EATS_ORDER_ID, revision_id=revision_id,
    )


@pytest.mark.now(consts.NOW)
@pytest_marks.DEPOT_COMPANY_TYPE
@pytest.mark.parametrize(
    'receipt_type', [models.ReceiptType.Payment, models.ReceiptType.Refund],
)
async def test_products_from_eats(
        run_grocery_payments_billing_eats_orders,
        grocery_depots,
        billing_orders,
        transactions,
        _items_controller,
        receipt_type,
        depot_company_type,
        oebs_depot_id,
):
    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID,
        oebs_depot_id=consts.OEBS_DEPOT_ID,
        company_type=depot_company_type,
    )

    transactions.retrieve.status_code = 404

    item_id_0 = _items_controller.add_item(
        item_id='item_id_0',
        item_type='product',
        vat='10',
        sub_items=[
            SubItem(price='10', quantity='2'),
            SubItem(price='15', quantity='1', refunded='1'),
        ],
    )

    item_id_1 = _items_controller.add_item(
        item_id='item_id_1',
        item_type='product',
        vat='20',
        sub_items=[SubItem(price='10', quantity='2')],
    )

    gross_sales_payment_data = _get_payment_data(TlogPaymentType.gross_sales)

    payments_by_item_id = {
        f'payment/{item_id_0}-0': [
            Payment(
                item_id=item_id_0,
                amount_with_vat='20',
                vat_rate='10',
                quantity='2',
                transaction_type='payment',
                event_time=EATS_STQ_TRANSACTION_DATE,
                **gross_sales_payment_data,
            ),
        ],
        f'payment/{item_id_0}-2': [
            Payment(
                item_id=item_id_0,
                amount_with_vat='15',
                vat_rate='10',
                quantity='1',
                transaction_type='payment',
                event_time=EATS_STQ_TRANSACTION_DATE,
                **gross_sales_payment_data,
            ),
        ],
        f'refund/{item_id_0}-2': [
            Payment(
                item_id=item_id_0,
                amount_with_vat='15',
                vat_rate='10',
                quantity='1',
                transaction_type='refund',
                event_time=EATS_STQ_EVENT_AT,
                **gross_sales_payment_data,
            ),
        ],
        f'payment/{item_id_1}-0': [
            Payment(
                item_id=item_id_1,
                amount_with_vat='20',
                vat_rate='20',
                quantity='2',
                transaction_type='payment',
                event_time=EATS_STQ_TRANSACTION_DATE,
                **gross_sales_payment_data,
            ),
        ],
    }

    _billing_orders_check(
        billing_orders,
        payments_by_item_id=payments_by_item_id,
        oebs_depot_id=oebs_depot_id,
    )

    await run_grocery_payments_billing_eats_orders(
        items=_items_controller.stq_items,
        receipt_type=receipt_type.value,
        courier_id='courier_id',
        event_at=EATS_STQ_EVENT_AT,
        transaction_date=EATS_STQ_TRANSACTION_DATE,
    )

    assert billing_orders.process_async_times_called() == 1


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'receipt_type', [models.ReceiptType.Payment, models.ReceiptType.Refund],
)
@pytest.mark.parametrize('item_type', ['delivery', 'tips'])
async def test_delivery_tips_from_eats(
        run_grocery_payments_billing_eats_orders,
        grocery_depots,
        billing_orders,
        transactions,
        _items_controller,
        receipt_type,
        item_type,
):
    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID, oebs_depot_id=consts.OEBS_DEPOT_ID,
    )
    transactions.retrieve.status_code = 404

    item_id = _items_controller.add_item(
        item_id=f'item-{item_type}',
        item_type=item_type,
        vat='10',
        sub_items=[SubItem(price='15', quantity='1', refunded='1')],
    )

    courier_payment_data = _get_payment_data(TlogPaymentType[item_type])

    payments_by_item_id = {
        f'payment/{item_id}-0': [
            Payment(
                item_id=item_id,
                amount_with_vat='15',
                vat_rate='10',
                quantity='1',
                transaction_type='payment',
                event_time=EATS_STQ_TRANSACTION_DATE,
                **courier_payment_data,
            ),
        ],
        f'refund/{item_id}-0': [
            Payment(
                item_id=item_id,
                amount_with_vat='15',
                vat_rate='10',
                quantity='1',
                transaction_type='refund',
                event_time=EATS_STQ_EVENT_AT,
                **courier_payment_data,
            ),
        ],
    }

    _billing_orders_check(
        billing_orders, payments_by_item_id=payments_by_item_id,
    )

    await run_grocery_payments_billing_eats_orders(
        items=_items_controller.stq_items,
        receipt_type=receipt_type.value,
        courier_id='courier_id',
        event_at=EATS_STQ_EVENT_AT,
        transaction_date=EATS_STQ_TRANSACTION_DATE,
    )

    assert billing_orders.process_async_times_called() == 1


@pytest.mark.now(consts.NOW)
@pytest_marks.DEPOT_COMPANY_TYPE
@pytest.mark.parametrize(
    'receipt_type', [models.ReceiptType.Payment, models.ReceiptType.Refund],
)
async def test_products_from_payments_eda(
        run_grocery_payments_billing_eats_orders,
        grocery_payments_billing_configs,
        grocery_depots,
        billing_orders,
        transactions,
        experiments3,
        _items_controller,
        receipt_type,
        depot_company_type,
        oebs_depot_id,
):
    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID,
        oebs_depot_id=consts.OEBS_DEPOT_ID,
        company_type=depot_company_type,
    )

    grocery_payments_billing_configs.tlog_eats_settings(
        v2_flow_from=consts.EATS_ORDER_ID.split('-')[0],
    )

    transactions.retrieve.mock_response(
        sum_to_pay=[
            {
                'payment_type': 'card',
                'items': [{'item_id': 'food', 'amount': '69.00'}],
            },
        ],
    )

    item_id_0 = _items_controller.add_item(
        item_id='item_id_0',
        item_type='product',
        vat='10',
        sub_items=[
            SubItem(price='10', quantity='2'),
            SubItem(price='15', quantity='1', refunded='1'),
        ],
    )

    item_id_1 = _items_controller.add_item(
        item_id='item_id_1',
        item_type='product',
        vat='20',
        sub_items=[SubItem(price='10', quantity='2')],
    )

    gross_sales_payment_data = _get_payment_data(TlogPaymentType.gross_sales)

    payments_by_item_id = {
        f'payment/{item_id_0}-0': [
            Payment(
                item_id=item_id_0,
                amount_with_vat='20',
                vat_rate='10',
                quantity='2',
                transaction_type='payment',
                event_time=EATS_STQ_TRANSACTION_DATE,
                **gross_sales_payment_data,
            ),
        ],
        f'payment/{item_id_0}-2': [
            Payment(
                item_id=item_id_0,
                amount_with_vat='15',
                vat_rate='10',
                quantity='1',
                transaction_type='payment',
                event_time=EATS_STQ_TRANSACTION_DATE,
                **gross_sales_payment_data,
            ),
        ],
        f'refund/{item_id_0}-2': [
            Payment(
                item_id=item_id_0,
                amount_with_vat='15',
                vat_rate='10',
                quantity='1',
                transaction_type='refund',
                event_time=EATS_STQ_EVENT_AT,
                **gross_sales_payment_data,
            ),
        ],
        f'payment/{item_id_1}-0': [
            Payment(
                item_id=item_id_1,
                amount_with_vat='20',
                vat_rate='20',
                quantity='2',
                transaction_type='payment',
                event_time=EATS_STQ_TRANSACTION_DATE,
                **gross_sales_payment_data,
            ),
        ],
    }

    _billing_orders_check(
        billing_orders,
        payments_by_item_id=payments_by_item_id,
        oebs_depot_id=oebs_depot_id,
    )

    await run_grocery_payments_billing_eats_orders(
        items=_items_controller.stq_items,
        receipt_type=receipt_type.value,
        courier_id='courier_id',
        event_at=EATS_STQ_EVENT_AT,
        transaction_date=EATS_STQ_TRANSACTION_DATE,
    )

    assert billing_orders.process_async_times_called() == 1


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'receipt_type, account_date',
    [
        (models.ReceiptType.Payment, EATS_STQ_TRANSACTION_DATE),
        (models.ReceiptType.Refund, EATS_STQ_EVENT_AT),
    ],
)
async def test_products_from_callback(
        run_grocery_payments_billing_eats_orders,
        grocery_depots,
        billing_orders,
        transactions,
        _items_controller,
        receipt_type,
        account_date,
):
    item_prefix = f'{consts.EXTERNAL_PAYMENT_ID}/{receipt_type.value}'

    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID, oebs_depot_id=consts.OEBS_DEPOT_ID,
    )

    item_id_0 = _items_controller.add_item(
        item_id='item_id_0',
        item_type='product',
        vat='10',
        sub_items=[
            SubItem(price='10', quantity='2'),
            SubItem(price='15', quantity='1'),
        ],
    )

    item_id_1 = _items_controller.add_item(
        item_id='item_id_1',
        item_type='product',
        vat='20',
        sub_items=[SubItem(price='10', quantity='2')],
    )

    gross_sales_payment_data = _get_payment_data(TlogPaymentType.gross_sales)

    payments_by_item_id = {
        f'{item_prefix}/{item_id_0}-0': [
            Payment(
                item_id=item_id_0,
                amount_with_vat='20',
                vat_rate='10',
                quantity='2',
                transaction_type=receipt_type.value,
                **gross_sales_payment_data,
            ),
        ],
        f'{item_prefix}/{item_id_0}-2': [
            Payment(
                item_id=item_id_0,
                amount_with_vat='15',
                vat_rate='10',
                quantity='1',
                transaction_type=receipt_type.value,
                **gross_sales_payment_data,
            ),
        ],
        f'{item_prefix}/{item_id_1}-0': [
            Payment(
                item_id=item_id_1,
                amount_with_vat='20',
                vat_rate='20',
                quantity='2',
                transaction_type=receipt_type.value,
                **gross_sales_payment_data,
            ),
        ],
    }

    _billing_orders_check(
        billing_orders,
        payments_by_item_id=payments_by_item_id,
        event_time=account_date,
    )

    await run_grocery_payments_billing_eats_orders(
        items=_items_controller.stq_items,
        receipt_type=receipt_type.value,
        courier_id='courier_id',
        event_at=EATS_STQ_EVENT_AT,
        transaction_date=EATS_STQ_TRANSACTION_DATE,
    )

    assert billing_orders.process_async_times_called() == 1


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'receipt_type, account_date',
    [
        (models.ReceiptType.Payment, EATS_STQ_TRANSACTION_DATE),
        (models.ReceiptType.Refund, EATS_STQ_EVENT_AT),
    ],
)
@pytest.mark.parametrize('item_type', ['delivery', 'tips'])
async def test_delivery_tips_from_callback(
        run_grocery_payments_billing_eats_orders,
        grocery_depots,
        billing_orders,
        transactions,
        _items_controller,
        receipt_type,
        account_date,
        item_type,
):
    item_prefix = f'{consts.EXTERNAL_PAYMENT_ID}/{receipt_type.value}'

    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID, oebs_depot_id=consts.OEBS_DEPOT_ID,
    )

    item_id = _items_controller.add_item(
        item_id=f'item-{item_type}',
        item_type=item_type,
        vat='10',
        sub_items=[SubItem(price='15', quantity='1', refunded='1')],
    )

    courier_payment_data = _get_payment_data(TlogPaymentType[item_type])

    payments_by_item_id = {
        f'{item_prefix}/{item_id}-0': [
            Payment(
                item_id=item_id,
                amount_with_vat='15',
                vat_rate='10',
                quantity='1',
                transaction_type=receipt_type.value,
                **courier_payment_data,
            ),
        ],
    }

    _billing_orders_check(
        billing_orders,
        payments_by_item_id=payments_by_item_id,
        event_time=account_date,
    )

    await run_grocery_payments_billing_eats_orders(
        items=_items_controller.stq_items,
        receipt_type=receipt_type.value,
        courier_id='courier_id',
        event_at=EATS_STQ_EVENT_AT,
        transaction_date=EATS_STQ_TRANSACTION_DATE,
    )

    assert billing_orders.process_async_times_called() == 1


def _billing_orders_check(billing_orders, **kwargs):
    billing_orders.check_request_v2(
        order_id=consts.EATS_ORDER_ID,
        balance_client_id=consts.BALANCE_CLIENT_ID,
        receipt_id=consts.EXTERNAL_PAYMENT_ID,
        courier=dict(id='courier_id', type=''),
        order_cycle='eats',
        original_event_time=EATS_STQ_TRANSACTION_DATE,
        topic_begin_at=EATS_STQ_TRANSACTION_DATE,
        **kwargs,
    )


def _get_payment_data(payment_type: TlogPaymentType):
    if payment_type == TlogPaymentType.gross_sales:
        return dict(
            detailed_product='gross_sales_b2c',
            payment_kind='grocery_gross_sales_b2c_agent',
            product='gross_sales_b2c',
        )
    if payment_type == TlogPaymentType.delivery:
        return dict(
            detailed_product='delivery_fee_b2c_agent',
            payment_kind='grocery_delivery_fee_b2c_agent',
            product='delivery_fee_b2c_agent',
        )
    if payment_type == TlogPaymentType.tips:
        return dict(
            detailed_product='tips_b2c_agent',
            payment_kind='grocery_tips_b2c_agent',
            product='tips_b2c_agent',
        )

    assert False, f'unimplemented {payment_type.name}'
    return {}
