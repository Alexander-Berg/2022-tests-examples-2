import dataclasses
import decimal
import enum
import typing

import pytest

from . import consts
from . import models
from . import pytest_marks
from .plugins import configs
from .plugins import mock_billing_orders

Payment = mock_billing_orders.Payment
ReceiptType = models.ReceiptType
# pylint: disable=invalid-name
Decimal = decimal.Decimal


class PriceType(enum.Enum):
    full_price = 'full_price'
    discounts = 'discounts'
    paid_cashback = 'paid_cashback'
    paid_promocode = 'paid_promocode'


@dataclasses.dataclass
class SubItem:
    price: str
    quantity: str
    full_price: typing.Optional[str] = None
    paid_with_cashback: typing.Optional[str] = None
    paid_with_promocode: typing.Optional[str] = None


@dataclasses.dataclass
class ProductData:
    detailed_product: str
    payment_kind: str
    product: str
    price_type: PriceType


@pytest.fixture(autouse=True)
def _tlog_configs(grocery_payments_billing_configs):
    grocery_payments_billing_configs.tlog_enabled(True)
    grocery_payments_billing_configs.tlog_params()
    grocery_payments_billing_configs.service_id_mapping()
    grocery_payments_billing_configs.products_settings_default()


@pytest.fixture
def _update_courier_info(grocery_orders):
    def _do(**kwargs):
        grocery_orders.order['courier_info'].update(kwargs)

    return _do


@pytest.fixture
def _items_controller(grocery_cart):
    def _make_sub_item_id(item_id, item_type, index=0):
        if item_type == 'service_fee':
            return item_id
        return item_id + '_' + str(index)

    class Context:
        def __init__(self):
            self.cart_items: typing.List[models.GroceryCartItemV2] = []
            self.stq_items = []

        def _get_item_id(self, item_type: str):
            if item_type == 'service_fee':
                return 'service_fee'
            count = len(self.cart_items)
            return f'item_id-{count}'

        def cart_item_by_sub_item_id(self, sub_item_id):
            for cart_item in self.cart_items:
                for sub_item in cart_item.sub_items:
                    if sub_item.item_id == sub_item_id:
                        return sub_item, cart_item

            assert False, f'Cart sub item with id {sub_item_id} is not found'
            return None

        def add_item(
                self,
                *,
                vat,
                sub_items: typing.List[SubItem],
                item_type: str = 'product',
        ):
            item_id = self._get_item_id(item_type)

            cart_sub_items: typing.List[models.GroceryCartSubItem] = []

            for index, sub_item in enumerate(sub_items):
                sub_item.full_price = sub_item.full_price or sub_item.price
                sub_item_id = _make_sub_item_id(item_id, item_type, index)

                cart_sub_items.append(
                    models.GroceryCartSubItem(
                        item_id=sub_item_id,
                        price=sub_item.price,
                        full_price=sub_item.full_price,
                        quantity=sub_item.quantity,
                        paid_with_cashback=sub_item.paid_with_cashback,
                        paid_with_promocode=sub_item.paid_with_promocode,
                    ),
                )

                self.stq_items.append(
                    models.receipt_item(
                        item_id=sub_item_id,
                        price=sub_item.price,
                        quantity=sub_item.quantity,
                        item_type=item_type,
                    ),
                )

            item = models.GroceryCartItemV2(
                item_id=item_id, vat=vat, sub_items=cart_sub_items,
            )

            self.cart_items.append(item)

            grocery_cart.set_items_v2(self.cart_items)

            return [it.item_id for it in cart_sub_items]

        def get_stq_items(self):
            return self.stq_items

    context = Context()
    return context


def cart_sub_item_amount_by_price_type(
        sub_item: models.GroceryCartSubItem, price_type: PriceType,
):
    if price_type == PriceType.full_price:
        return sub_item.amount_full_price()
    if price_type == PriceType.discounts:
        return sub_item.amount_discounts()
    if price_type == PriceType.paid_cashback:
        return sub_item.amount_paid_with_cashback()
    if price_type == PriceType.paid_promocode:
        return sub_item.amount_paid_with_promocode()

    assert False, price_type
    return None


def create_payment(
        cart_item: models.GroceryCartItemV2,
        sub_item: models.GroceryCartSubItem,
        detailed_product,
        payment_kind,
        product,
        receipt_type,
        price_type: PriceType,
):

    return Payment(
        amount_with_vat=cart_sub_item_amount_by_price_type(
            sub_item, price_type,
        ),
        detailed_product=detailed_product,
        payment_kind=payment_kind,
        product=product,
        transaction_type=receipt_type,
        vat_rate=cart_item.vat,
        item_id=cart_item.item_id,
        quantity=sub_item.quantity,
    )


def append_payments(
        payments,
        cart_item: models.GroceryCartItemV2,
        sub_item: models.GroceryCartSubItem,
        detailed_product,
        payment_kind,
        product,
        receipt_type,
        price_type: PriceType,
):
    payment = create_payment(
        cart_item=cart_item,
        sub_item=sub_item,
        detailed_product=detailed_product,
        payment_kind=payment_kind,
        product=product,
        receipt_type=receipt_type,
        price_type=price_type,
    )

    if Decimal(payment.amount_with_vat) > 0:
        payments.append(payment)


def _format_tlog_item_by_product(
        payments_by_item_id,
        _items_controller,
        sub_item_ids: typing.List[str],
        products_data: typing.List[ProductData],
        receipt_type: ReceiptType,
):
    for sub_item_id in sub_item_ids:
        payment_of_sub_item: typing.List[Payment] = []

        sub_item, cart_item = _items_controller.cart_item_by_sub_item_id(
            sub_item_id,
        )
        for product_data in products_data:
            append_payments(
                payments=payment_of_sub_item,
                cart_item=cart_item,
                sub_item=sub_item,
                detailed_product=product_data.detailed_product,
                payment_kind=product_data.payment_kind,
                product=product_data.product,
                receipt_type=receipt_type.value,
                price_type=product_data.price_type,
            )

        if sub_item.item_id not in payments_by_item_id:
            payments_by_item_id[sub_item.item_id] = []

        payments_by_item_id[sub_item.item_id].extend(payment_of_sub_item)


@pytest.mark.now(consts.NOW)
@pytest_marks.DEPOT_COMPANY_TYPE
@pytest_marks.RECEIPT_TYPES
@pytest.mark.parametrize(
    'country', [models.Country.Russia, models.Country.Israel],
)
async def test_products(
        grocery_orders,
        grocery_cart,
        grocery_depots,
        billing_orders,
        eats_billing,
        run_grocery_payments_billing_tlog_callback,
        _items_controller,
        receipt_type,
        country,
        depot_company_type,
        oebs_depot_id,
):
    # sub items for item_id_0
    sub_item_ids_0 = _items_controller.add_item(
        vat='10',
        sub_items=[
            SubItem(price='10', quantity='1'),
            SubItem(price='13', quantity='4', full_price='35'),
            SubItem(
                price='14',
                quantity='5',
                full_price='56',
                paid_with_cashback='5',
            ),
        ],
    )

    # sub items for item_id_1
    sub_item_ids_1 = _items_controller.add_item(
        vat='20',
        sub_items=[
            SubItem(price='11', quantity='2'),
            SubItem(price='12', quantity='3'),
        ],
    )

    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID,
        oebs_depot_id=consts.OEBS_DEPOT_ID,
        company_type=depot_company_type,
        country_iso3=country.country_iso3,
    )

    grocery_orders.order.update(country=country.name)

    payments_by_item_id = {}

    _format_tlog_item_by_product(
        payments_by_item_id,
        _items_controller,
        sub_item_ids_0,
        products_data=[
            ProductData(
                detailed_product='gross_sales_b2c',
                payment_kind='grocery_gross_sales_b2c_agent',
                product='gross_sales_b2c',
                price_type=PriceType.full_price,
            ),
            ProductData(
                detailed_product='incentives_b2c_discount',
                payment_kind='grocery_incentives_b2c_discount_agent',
                product='incentives_b2c',
                price_type=PriceType.discounts,
            ),
            ProductData(
                detailed_product='grocery_coupon_plus',
                payment_kind='grocery_coupon_plus_agent',
                product='grocery_coupon_plus',
                price_type=PriceType.paid_cashback,
            ),
        ],
        receipt_type=receipt_type,
    )

    _format_tlog_item_by_product(
        payments_by_item_id,
        _items_controller,
        sub_item_ids_1,
        products_data=[
            ProductData(
                detailed_product='gross_sales_b2c',
                payment_kind='grocery_gross_sales_b2c_agent',
                product='gross_sales_b2c',
                price_type=PriceType.full_price,
            ),
        ],
        receipt_type=receipt_type,
    )

    billing_orders.check_request_v2(
        event_time=consts.PAYMENT_FINISHED,
        balance_client_id=configs.get_balance_client_id(country),
        payments_by_item_id=payments_by_item_id,
        oebs_depot_id=oebs_depot_id,
        country=country,
        payment_type='cibus',
    )

    await run_grocery_payments_billing_tlog_callback(
        items=_items_controller.get_stq_items(),
        country=country.name,
        receipt_type=receipt_type.value,
        payment_type='cibus',
    )

    assert billing_orders.process_async_times_called() == 1


@pytest.mark.now(consts.NOW)
@pytest_marks.RECEIPT_TYPES
async def test_service_fee(
        grocery_orders,
        grocery_depots,
        billing_orders,
        run_grocery_payments_billing_tlog_callback,
        _items_controller,
        eats_billing_processor,
        receipt_type,
):
    country = models.Country.Russia
    service_fee_amount = '29'

    sub_item_ids_0 = _items_controller.add_item(
        vat='10', sub_items=[SubItem(price='10', quantity='1')],
    )

    service_fee = _items_controller.add_item(
        vat='20',
        sub_items=[SubItem(price=service_fee_amount, quantity='1')],
        item_type='service_fee',
    )

    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID,
        oebs_depot_id=consts.OEBS_DEPOT_ID,
        company_type='yandex',
        country_iso3=country.country_iso3,
    )

    grocery_orders.order.update(country=country.name)

    payments_by_item_id = {}

    _format_tlog_item_by_product(
        payments_by_item_id,
        _items_controller,
        sub_item_ids_0,
        products_data=[
            ProductData(
                detailed_product='gross_sales_b2c',
                payment_kind='grocery_gross_sales_b2c_agent',
                product='gross_sales_b2c',
                price_type=PriceType.full_price,
            ),
        ],
        receipt_type=receipt_type,
    )

    _format_tlog_item_by_product(
        payments_by_item_id,
        _items_controller,
        service_fee,
        products_data=[
            ProductData(
                detailed_product='service_fee_b2c_agent',
                payment_kind='grocery_service_fee_b2c_agent',
                product='service_fee_b2c_agent',
                price_type=PriceType.full_price,
            ),
        ],
        receipt_type=receipt_type,
    )

    billing_orders.check_request_v2(
        event_time=consts.PAYMENT_FINISHED,
        balance_client_id=configs.get_balance_client_id(country),
        payments_by_item_id=payments_by_item_id,
        oebs_depot_id=consts.OEBS_DEPOT_ID,
        country=country,
        payment_type='card',
    )

    eats_billing_processor.v1_create.check(
        order_nr=consts.ORDER_ID,
        event_at=consts.NOW,
        kind='order_finished',
        rule_name='default',
        external_id=consts.EXTERNAL_PAYMENT_ID,
        data={
            'order_nr': consts.ORDER_ID,
            'client_id': configs.get_balance_client_id(country),
            'counteragent_id': consts.DEPOT_ID,
            'currency': country.currency,
            'product_type': 'service_fee',
            'product_id': 'service_fee',
            'service_fee_amount': service_fee_amount,
        },
    )

    await run_grocery_payments_billing_tlog_callback(
        items=_items_controller.get_stq_items(),
        country=country.name,
        receipt_type=receipt_type.value,
    )

    assert billing_orders.process_async_times_called() == 1
    assert eats_billing_processor.v1_create.times_called == 1


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'series_purpose', ['marketing', 'support', 'referral', 'referral_reward'],
)
async def test_products_with_promocode(
        grocery_orders,
        grocery_cart,
        grocery_depots,
        billing_orders,
        eats_billing,
        run_grocery_payments_billing_tlog_callback,
        _items_controller,
        series_purpose,
):
    receipt_type = models.ReceiptType.Payment
    country = models.Country.Russia

    # sub items for item_id_0
    sub_item_ids_0 = _items_controller.add_item(
        vat='10',
        sub_items=[
            SubItem(
                price='15',
                quantity='5',
                full_price='30',
                paid_with_promocode='5',
            ),
        ],
    )

    # sub items for item_id_1
    sub_item_ids_1 = _items_controller.add_item(
        vat='10',
        sub_items=[
            SubItem(
                price='15',
                quantity='5',
                full_price='20',
                paid_with_promocode='5',
            ),
        ],
    )

    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID,
        oebs_depot_id=consts.OEBS_DEPOT_ID,
        country_iso3=country.country_iso3,
    )
    grocery_orders.order.update(country=country.name)
    grocery_cart.set_promocode(
        code='promocode',
        valid=True,
        source='taxi',
        discount='100',
        series_purpose=series_purpose,
    )

    marketing_budget_purposes = {'marketing', 'referral', 'referral_reward'}

    if series_purpose in marketing_budget_purposes:
        promocode_product_data = ProductData(
            detailed_product='incentives_b2c_marketing_coupon',
            payment_kind='grocery_incentives_b2c_marketing_coupon_agent',
            product='incentives_b2c',
            price_type=PriceType.paid_promocode,
        )
    else:
        promocode_product_data = ProductData(
            detailed_product='incentives_b2c_support_coupon',
            payment_kind='grocery_incentives_b2c_support_coupon_agent',
            product='incentives_b2c',
            price_type=PriceType.paid_promocode,
        )

    payments_by_item_id = {}

    _format_tlog_item_by_product(
        payments_by_item_id,
        _items_controller,
        sub_item_ids_0,
        products_data=[
            ProductData(
                detailed_product='gross_sales_b2c',
                payment_kind='grocery_gross_sales_b2c_agent',
                product='gross_sales_b2c',
                price_type=PriceType.full_price,
            ),
            ProductData(
                detailed_product='incentives_b2c_discount',
                payment_kind='grocery_incentives_b2c_discount_agent',
                product='incentives_b2c',
                price_type=PriceType.discounts,
            ),
            promocode_product_data,
        ],
        receipt_type=receipt_type,
    )

    _format_tlog_item_by_product(
        payments_by_item_id,
        _items_controller,
        sub_item_ids_1,
        products_data=[
            ProductData(
                detailed_product='gross_sales_b2c',
                payment_kind='grocery_gross_sales_b2c_agent',
                product='gross_sales_b2c',
                price_type=PriceType.full_price,
            ),
            promocode_product_data,
        ],
        receipt_type=receipt_type,
    )

    billing_orders.check_request_v2(
        event_time=consts.PAYMENT_FINISHED,
        balance_client_id=configs.get_balance_client_id(country),
        payments_by_item_id=payments_by_item_id,
        payment_type='card',
    )

    await run_grocery_payments_billing_tlog_callback(
        items=_items_controller.get_stq_items(),
        country=country.name,
        receipt_type=receipt_type.value,
    )

    assert billing_orders.process_async_times_called() == 1


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'organization_name, vat',
    [
        pytest.param(None, '0', id='self employed'),
        pytest.param('123', consts.COURIER_VAT, id='not self employed'),
    ],
)
@pytest_marks.RECEIPT_TYPES
@pytest.mark.parametrize(
    'item_type, detailed_product, payment_kind, product',
    [
        (
            'delivery',
            'delivery_fee_b2c_agent',
            'grocery_delivery_fee_b2c_agent',
            'delivery_fee_b2c_agent',
        ),
        ('tips', 'tips_b2c_agent', 'grocery_tips_b2c_agent', 'tips_b2c_agent'),
    ],
)
async def test_courier_payments_russia(
        grocery_orders,
        grocery_cart,
        grocery_depots,
        billing_orders,
        eats_billing,
        run_grocery_payments_billing_tlog_callback,
        _update_courier_info,
        organization_name,
        vat,
        receipt_type,
        item_type,
        detailed_product,
        payment_kind,
        product,
):
    item_id = f'item_{item_type}'
    price = '100'
    courier_balance_client_id = 'courier_balance_client_id'

    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID, oebs_depot_id=consts.OEBS_DEPOT_ID,
    )

    _update_courier_info(
        organization_name=organization_name,
        balance_client_id=courier_balance_client_id,
    )

    billing_orders.check_request_v2(
        event_time=consts.PAYMENT_FINISHED,
        balance_client_id=courier_balance_client_id,
        payments_by_item_id={
            item_id: [
                Payment(
                    amount_with_vat=price,
                    detailed_product=detailed_product,
                    payment_kind=payment_kind,
                    product=product,
                    transaction_type=receipt_type.value,
                    vat_rate=vat,
                    item_id=item_id,
                    quantity='1',
                ),
            ],
        },
        payment_type='card',
    )

    await run_grocery_payments_billing_tlog_callback(
        items=[
            models.receipt_item(
                item_id=item_id,
                price=price,
                quantity='1',
                item_type=item_type,
            ),
        ],
        country=models.Country.Russia.name,
        receipt_type=receipt_type.value,
    )

    assert billing_orders.process_async_times_called() == 1


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'country, vat',
    [
        pytest.param(models.Country.Israel, consts.ISRAEL_COURIER_VAT),
        pytest.param(models.Country.France, consts.FRANCE_COURIER_VAT),
        pytest.param(
            models.Country.GreatBritain, consts.GREAT_BRITAIN_COURIER_VAT,
        ),
    ],
)
@pytest_marks.RECEIPT_TYPES
@pytest.mark.parametrize(
    'item_type, detailed_product, payment_kind, product',
    [
        (
            'delivery',
            'delivery_fee_b2c_agent',
            'grocery_delivery_fee_b2c_agent',
            'delivery_fee_b2c_agent',
        ),
        ('tips', 'tips_b2c_agent', 'grocery_tips_b2c_agent', 'tips_b2c_agent'),
    ],
)
async def test_courier_payments_israel_france(
        grocery_payments_billing_configs,
        grocery_orders,
        grocery_cart,
        grocery_depots,
        experiments3,
        billing_orders,
        eats_billing,
        run_grocery_payments_billing_tlog_callback,
        _update_courier_info,
        vat,
        receipt_type,
        item_type,
        detailed_product,
        payment_kind,
        product,
        country,
):
    item_id = f'item_{item_type}'
    price = '100'

    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID,
        oebs_depot_id=consts.OEBS_DEPOT_ID,
        country_iso3=country.country_iso3,
    )

    _update_courier_info(organization_name='yandex')

    grocery_orders.order['country'] = country.name

    courier_balance_client_id = configs.get_balance_client_id(country)
    grocery_payments_billing_configs.courier_balance_client_id(
        balance_client_id=courier_balance_client_id,
        modification_type='exchange',
    )

    billing_orders.check_request_v2(
        event_time=consts.PAYMENT_FINISHED,
        balance_client_id=courier_balance_client_id,
        country=country,
        payments_by_item_id={
            item_id: [
                Payment(
                    amount_with_vat=price,
                    detailed_product=detailed_product,
                    payment_kind=payment_kind,
                    product=product,
                    transaction_type=receipt_type.value,
                    vat_rate=vat,
                    item_id=item_id,
                    quantity='1',
                ),
            ],
        },
        payment_type='card',
    )

    await run_grocery_payments_billing_tlog_callback(
        items=[
            models.receipt_item(
                item_id=item_id,
                price=price,
                quantity='1',
                item_type=item_type,
            ),
        ],
        country=country.name,
        receipt_type=receipt_type.value,
    )

    assert billing_orders.process_async_times_called() == 1


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize('with_discount', [True, False])
@pytest.mark.parametrize(
    'country', [models.Country.Russia, models.Country.Israel],
)
async def test_skip_some_products(
        grocery_payments_billing_configs,
        grocery_orders,
        grocery_cart,
        grocery_depots,
        billing_orders,
        eats_billing,
        run_grocery_payments_billing_tlog_callback,
        _items_controller,
        experiments3,
        with_discount,
        country,
):
    receipt_type = ReceiptType.Payment

    vat = '10'
    sub_item_ids_0 = _items_controller.add_item(
        vat=vat, sub_items=[SubItem(price='10', quantity='1')],
    )
    sub_item_ids_1 = _items_controller.add_item(
        vat=vat,
        sub_items=[SubItem(price='13', quantity='4', full_price='35')],
    )

    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID,
        oebs_depot_id=consts.OEBS_DEPOT_ID,
        country_iso3=country.country_iso3,
    )
    grocery_orders.order.update(country=country.name)

    settings = [
        {
            'type': 'product_full_price',
            'detailed_product': 'gross_sales_b2c',
            'payment_kind': 'grocery_gross_sales_b2c_agent',
        },
    ]

    payments_by_item_id = {}

    for sub_item_ids in (sub_item_ids_0, sub_item_ids_1):
        _format_tlog_item_by_product(
            payments_by_item_id,
            _items_controller,
            sub_item_ids,
            products_data=[
                ProductData(
                    detailed_product='gross_sales_b2c',
                    payment_kind='grocery_gross_sales_b2c_agent',
                    product='gross_sales_b2c',
                    price_type=PriceType.full_price,
                ),
            ],
            receipt_type=receipt_type,
        )

    if with_discount:
        settings.append(
            {
                'type': 'discount',
                'detailed_product': 'incentives_b2c_discount',
                'payment_kind': 'grocery_incentives_b2c_discount_agent',
            },
        )

        for sub_item_ids in (sub_item_ids_0, sub_item_ids_1):
            _format_tlog_item_by_product(
                payments_by_item_id,
                _items_controller,
                sub_item_ids,
                products_data=[
                    ProductData(
                        detailed_product='incentives_b2c_discount',
                        payment_kind='grocery_incentives_b2c_discount_agent',
                        product='incentives_b2c',
                        price_type=PriceType.discounts,
                    ),
                ],
                receipt_type=receipt_type,
            )

    grocery_payments_billing_configs.products_settings(settings)

    billing_orders.check_request_v2(
        event_time=consts.PAYMENT_FINISHED,
        balance_client_id=configs.get_balance_client_id(country),
        payments_by_item_id=payments_by_item_id,
        country=country,
        payment_type='card',
    )

    await run_grocery_payments_billing_tlog_callback(
        items=_items_controller.get_stq_items(),
        country=country.name,
        receipt_type=receipt_type.value,
    )

    assert billing_orders.process_async_times_called() == 1


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'receipt_data_type',
    [models.ReceiptDataType.Delivery, models.ReceiptDataType.Order],
)
@pytest.mark.parametrize('item_type', ['product', 'delivery'])
async def test_empty_balance_client_id_fail(
        grocery_payments_billing_configs,
        grocery_orders,
        grocery_cart,
        experiments3,
        grocery_depots,
        eats_billing,
        run_grocery_payments_billing_tlog_callback,
        _update_courier_info,
        receipt_data_type,
        item_type,
):
    grocery_payments_billing_configs.balance_client_id(balance_client_id='')
    grocery_payments_billing_configs.courier_balance_client_id(
        balance_client_id='',
    )

    courier_balance_client_id = ''
    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID, oebs_depot_id=consts.OEBS_DEPOT_ID,
    )
    price = '100'

    _update_courier_info(
        organization_name='yandex',
        balance_client_id=courier_balance_client_id,
    )

    await run_grocery_payments_billing_tlog_callback(
        items=[{'item_id': item_type, 'price': price, 'quantity': '1'}],
        receipt_data_type=receipt_data_type.value,
        expect_fail=True,
    )


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'config_name,ensure_ntries,match_idx',
    [
        ('grocery_balance_client_id', 2, 1),
        ('grocery_courier_balance_client_id', 1, 0),
        ('grocery_service_id_mapping', 2, 0),
        ('grocery_tlog_enabled', 2, 0),
        ('grocery_tlog_params', 2, 0),
        ('grocery_tlog_products_settings', 1, 0),
    ],
)
async def test_kwargs(
        grocery_orders,
        grocery_cart,
        experiments3,
        grocery_depots,
        run_grocery_payments_billing_tlog_callback,
        _update_courier_info,
        config_name,
        ensure_ntries,
        match_idx,
):
    courier_balance_client_id = 'courier_balance_client_id-123'
    region_id = 999
    supplier_tin = 'some-tin'
    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID,
        oebs_depot_id=consts.OEBS_DEPOT_ID,
        region_id=region_id,
    )

    _update_courier_info(
        organization_name='yandex',
        balance_client_id=courier_balance_client_id,
    )

    exp3_recorder = experiments3.record_match_tries(config_name)

    payment_type = 'applepay'
    await run_grocery_payments_billing_tlog_callback(
        payment_type=payment_type, supplier_tin=supplier_tin,
    )

    exp3_matches = await exp3_recorder.get_match_tries(ensure_ntries)
    exp3_kwargs = exp3_matches[match_idx].kwargs

    assert exp3_kwargs['consumer'] == 'grocery-payments-billing/client_id'
    assert exp3_kwargs['company_type'] == 'yandex'
    assert exp3_kwargs['country_iso3'] == 'RUS'
    assert exp3_kwargs['courier_client_id'] == courier_balance_client_id
    assert exp3_kwargs['depot_id'] == consts.DEPOT_ID
    assert exp3_kwargs['order_created'].replace(
        '+0000', '',
    ) == consts.NOW.replace('+00:00', '')
    assert exp3_kwargs['order_cycle'] == 'grocery'
    assert exp3_kwargs['payment_type'] == payment_type
    assert exp3_kwargs['personal_phone_id'] == consts.PERSONAL_PHONE_ID
    assert exp3_kwargs['purpose'] == 'grocery_tlog'
    assert exp3_kwargs['region_id'] == region_id
    assert exp3_kwargs['yandex_uid'] == consts.YANDEX_UID
    assert exp3_kwargs['supplier_tin'] == supplier_tin
