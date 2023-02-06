# pylint: disable=too-many-lines
import decimal
import typing

import pytest

from tests_eats_payments import configs
from tests_eats_payments import consts
from tests_eats_payments import db_item_payment_type_plus
from tests_eats_payments import db_order
from tests_eats_payments import helpers
from tests_eats_payments import models

TEST_ORDER_ID = 'test_order'
TEST_PAYMENT_ID = '123'
URL = 'v2/orders/refund'
DELIVERY_ITEM = helpers.make_transactions_item(
    item_id='delivery',
    amount='100.00',
    product_id='delivery_trust_product_id',
)
DELIVERY_CUSTOMER_SERVICE = helpers.make_customer_service(
    customer_service_id='delivery',
    name='Delivery-1',
    cost_for_customer='100',
    currency='RUB',
    customer_service_type='delivery',
    vat='nds_20',
    trust_product_id='delivery_trust_product_id',
    place_id='place_1',
)


@pytest.fixture(name='check_refund_order_v2')
def check_refund_order_fixture(taxi_eats_payments, mockserver, load_json):
    async def _inner(response_status=200, response_body=None, ttl: int = None):
        request_payload = {
            'order_id': 'test_order',
            'version': 2,
            'revision': 'abcd-vfr',
        }

        payload: typing.Dict[str, typing.Any] = {**request_payload}
        response = await taxi_eats_payments.post(URL, json=payload)
        assert response.status == response_status
        if response_body is not None:
            assert response.json() == response_body

    return _inner


@configs.PERSONAL_WALLET_FIRM_BY_SERVICE
@pytest.mark.parametrize(
    'payment_type, complement_amount, init_db_items, '
    'invoice_retrieve_plus_items, items_paid, '
    'customer_services, customer_service_details, '
    'expected_plus_amount, expected_invoice_update_items, '
    'debts, invoice_update_expected_called, customer_services_expected_called',
    [
        pytest.param(
            # payment_type
            'card',
            # complement_amount
            '180.00',
            # init_db_items
            [
                {
                    'item_id': 'product-1',
                    'payment_type': 'trust',
                    'plus_amount': decimal.Decimal(107),
                    'customer_service_type': 'composition_products',
                },
                {
                    'item_id': 'option-1',
                    'payment_type': 'trust',
                    'plus_amount': decimal.Decimal(21),
                    'customer_service_type': 'composition_products',
                },
                {
                    'item_id': 'product-2',
                    'payment_type': 'trust',
                    'plus_amount': decimal.Decimal(31),
                    'customer_service_type': 'composition_products',
                },
                {
                    'item_id': 'delivery',
                    'payment_type': 'trust',
                    'plus_amount': decimal.Decimal(0),
                    'customer_service_type': 'delivery',
                },
                {
                    'item_id': 'retail-product-id',
                    'payment_type': 'trust',
                    'plus_amount': decimal.Decimal(21),
                    'customer_service_type': 'retail',
                },
            ],
            # invoice_retrieve_plus_items
            [
                helpers.make_transactions_item(
                    item_id='composition-products',
                    amount='159.00',
                    product_id='composition_products_trust_product_id',
                ),
                helpers.make_transactions_item(
                    item_id='retail-product-id',
                    amount='21.00',
                    product_id='retail_trust_product_id',
                ),
            ],
            # items_paid
            [
                helpers.make_transactions_item(
                    item_id='composition-products',
                    amount='1341.00',
                    product_id='composition_products_trust_product_id',
                ),
                helpers.make_transactions_item(
                    item_id='retail-product-id',
                    amount='159.00',
                    product_id='retail_trust_product_id',
                ),
                DELIVERY_ITEM,
            ],
            # customer_services
            [
                helpers.make_customer_service(
                    customer_service_id='composition-products',
                    name='big_mac',
                    cost_for_customer='1000.00',
                    currency='RUB',
                    customer_service_type='composition_products',
                    vat='nds_20',
                    trust_product_id='composition_products_trust_product_id',
                    place_id='place_1',
                ),
                helpers.make_customer_service(
                    customer_service_id='retail-product-id',
                    name='Retail',
                    cost_for_customer='0.00',
                    currency='RUB',
                    customer_service_type='retail',
                    vat='nds_none',
                    trust_product_id='retail_trust_product_id',
                    place_id='place_1',
                ),
                DELIVERY_CUSTOMER_SERVICE,
            ],
            # customer_service_details
            [
                helpers.make_customer_service(
                    customer_service_id='composition-products',
                    name='big_mac',
                    cost_for_customer='1000.00',
                    currency='RUB',
                    customer_service_type='composition_products',
                    trust_product_id='composition_products_trust_product_id',
                    place_id='place_1',
                    balance_client_id='123456789',
                    personal_tin_id='personal-tin-id',
                    details=helpers.make_customer_service_details(
                        composition_products=[
                            helpers.make_composition_product(
                                composition_product_id='product-1',
                                name='Product 1',
                                cost_for_customer='970.00',
                                composition_product_type='product',
                                vat='nds_20',
                            ),
                            helpers.make_composition_product(
                                composition_product_id='option-1',
                                name='Option 1',
                                cost_for_customer='30.00',
                                composition_product_type='product',
                                vat='nds_20',
                            ),
                        ],
                    ),
                ),
                helpers.make_customer_service(
                    customer_service_id='retail-product-id',
                    name='Retail',
                    cost_for_customer='0.00',
                    refunded_amount='500.00',
                    currency='RUB',
                    customer_service_type='retail',
                    vat='nds_none',
                    trust_product_id='retail_trust_product_id',
                    place_id='place_1',
                ),
                DELIVERY_CUSTOMER_SERVICE,
            ],
            # expected_plus_amount
            [('product-1', 'trust', '107'), ('option-1', 'trust', '21')],
            # expected_invoice_update_items
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products',
                            amount='872.00',
                            product_id='composition_products_trust_product_id',
                        ),
                        helpers.make_transactions_item(
                            item_id='retail-product-id',
                            amount='0.00',
                            product_id='retail_trust_product_id',
                        ),
                        DELIVERY_ITEM,
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='personal_wallet',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products',
                            amount='128.00',
                            product_id='composition_products_trust_product_id',
                        ),
                        helpers.make_transactions_item(
                            item_id='retail-product-id',
                            amount='0.00',
                            product_id='retail_trust_product_id',
                        ),
                        helpers.make_transactions_item(
                            item_id='delivery',
                            amount='0.00',
                            product_id='delivery_trust_product_id',
                        ),
                    ],
                ),
            ],
            # debts
            [],
            # invoice_update_expected_called
            1,
            # customer_services_expected_called
            1,
            id='Simple case',
        ),
        pytest.param(
            # payment_type
            'card',
            # complement_amount
            '880.00',
            # init_db_items
            [
                {
                    'item_id': 'product-1',
                    'payment_type': 'trust',
                    'plus_amount': decimal.Decimal(439),
                    'customer_service_type': 'composition_products',
                },
                {
                    'item_id': 'option-1',
                    'payment_type': 'trust',
                    'plus_amount': decimal.Decimal(0),
                    'customer_service_type': 'composition_products',
                },
                {
                    'item_id': 'product-2',
                    'payment_type': 'trust',
                    'plus_amount': decimal.Decimal(439),
                    'customer_service_type': 'composition_products',
                },
                {
                    'item_id': 'option-2',
                    'payment_type': 'trust',
                    'plus_amount': decimal.Decimal(0),
                    'customer_service_type': 'composition_products',
                },
                {
                    'item_id': 'delivery',
                    'payment_type': 'trust',
                    'plus_amount': decimal.Decimal(0),
                    'customer_service_type': 'delivery',
                },
            ],
            # invoice_retrieve_plus_items
            [
                helpers.make_transactions_item(
                    item_id='composition-products',
                    amount='878.00',
                    product_id='composition_products_trust_product_id',
                ),
            ],
            # items_paid
            [
                helpers.make_transactions_item(
                    item_id='composition-products',
                    amount='2.00',
                    product_id='composition_products_trust_product_id',
                ),
                DELIVERY_ITEM,
            ],
            # customer_services
            [
                helpers.make_customer_service(
                    customer_service_id='composition-products',
                    name='big_mac',
                    cost_for_customer='440.00',
                    currency='RUB',
                    customer_service_type='composition_products',
                    vat='nds_20',
                    trust_product_id='composition_products_trust_product_id',
                    place_id='place_1',
                ),
                DELIVERY_CUSTOMER_SERVICE,
            ],
            # customer_service_details
            [
                helpers.make_customer_service(
                    customer_service_id='composition-products',
                    name='big_mac',
                    cost_for_customer='440.00',
                    currency='RUB',
                    customer_service_type='composition_products',
                    trust_product_id='composition_products_trust_product_id',
                    place_id='place_1',
                    balance_client_id='123456789',
                    personal_tin_id='personal-tin-id',
                    refunded_amount='440.00',
                    details=helpers.make_customer_service_details(
                        composition_products=[
                            helpers.make_composition_product(
                                composition_product_id='product-1',
                                name='Product 1',
                                cost_for_customer='440.00',
                                composition_product_type='product',
                                vat='nds_20',
                            ),
                            helpers.make_composition_product(
                                composition_product_id='option-1',
                                name='Option 1',
                                cost_for_customer='0.00',
                                composition_product_type='option',
                                vat='nds_20',
                            ),
                            helpers.make_composition_product(
                                composition_product_id='product-2',
                                name='Product 2',
                                cost_for_customer='0.00',
                                composition_product_type='product',
                                vat='nds_20',
                            ),
                            helpers.make_composition_product(
                                composition_product_id='option-2',
                                name='Option 2',
                                cost_for_customer='0.00',
                                composition_product_type='option',
                                vat='nds_20',
                            ),
                        ],
                        refunds=[
                            helpers.make_composition_product_refund(
                                refund_revision_id='55555',
                                refund_products=[
                                    {
                                        'id': 'product-2',
                                        'refunded_amount': '440.00',
                                    },
                                    {
                                        'id': 'option-2',
                                        'refunded_amount': '0.00',
                                    },
                                ],
                            ),
                        ],
                    ),
                ),
                DELIVERY_CUSTOMER_SERVICE,
            ],
            # expected_plus_amount
            [('product-1', 'trust', '439'), ('option-1', 'trust', '0')],
            # expected_invoice_update_items
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products',
                            amount='1.00',
                            product_id='composition_products_trust_product_id',
                        ),
                        DELIVERY_ITEM,
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='personal_wallet',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products',
                            amount='439.00',
                            product_id='composition_products_trust_product_id',
                        ),
                        helpers.make_transactions_item(
                            item_id='delivery',
                            amount='0.00',
                            product_id='delivery_trust_product_id',
                        ),
                    ],
                ),
            ],
            # debts
            [],
            # invoice_update_expected_called
            1,
            # customer_services_expected_called
            1,
            id='Possible negative cost',
        ),
        pytest.param(
            # payment_type
            'card',
            # complement_amount
            '10',
            # init_db_items
            [
                {
                    'item_id': 'retail-product',
                    'payment_type': 'trust',
                    'plus_amount': decimal.Decimal(10),
                    'customer_service_type': 'retail',
                },
                {
                    'item_id': 'delivery',
                    'payment_type': 'trust',
                    'plus_amount': decimal.Decimal(0),
                    'customer_service_type': 'delivery',
                },
            ],
            # invoice_retrieve_plus_items
            [
                helpers.make_transactions_item(
                    item_id='retail-product',
                    amount='10.00',
                    product_id='retail_product',
                ),
            ],
            # items_paid
            [
                helpers.make_transactions_item(
                    item_id='retail-product',
                    amount='90.00',
                    product_id='retail_product',
                ),
                DELIVERY_ITEM,
            ],
            # customer_services
            [
                helpers.make_customer_service(
                    customer_service_id='retail-product',
                    name='big_mac',
                    cost_for_customer='100.00',
                    currency='RUB',
                    customer_service_type='retail',
                    vat='nds_20',
                    trust_product_id='retail_product',
                    place_id='place_1',
                ),
                DELIVERY_CUSTOMER_SERVICE,
            ],
            # customer_service_details
            [
                helpers.make_customer_service(
                    customer_service_id='retail-product',
                    name='zakaz',
                    cost_for_customer='60.00',
                    currency='RUB',
                    customer_service_type='retail',
                    trust_product_id='retail_products',
                    place_id='place_1',
                    balance_client_id='123456789',
                    personal_tin_id='personal-tin-id',
                    refunded_amount='40.00',
                    details=helpers.make_customer_service_details(
                        composition_products=[
                            helpers.make_composition_product(
                                composition_product_id='retail-product-1',
                                name='Product 1',
                                cost_for_customer='60.00',
                                composition_product_type='product',
                                vat='nds_20',
                            ),
                            helpers.make_composition_product(
                                composition_product_id='retail-product-2',
                                name='Product 2',
                                cost_for_customer='40.00',
                                composition_product_type='product',
                                vat='nds_20',
                            ),
                        ],
                        refunds=[
                            helpers.make_composition_product_refund(
                                refund_revision_id='55555',
                                refund_products=[
                                    {
                                        'id': 'retail-product',
                                        'refunded_amount': '40.00',
                                    },
                                ],
                            ),
                        ],
                    ),
                ),
                DELIVERY_CUSTOMER_SERVICE,
            ],
            # expected_plus_amount
            [('retail-product', 'trust', '10')],
            # expected_invoice_update_items
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='retail-product',
                            amount='50.00',
                            product_id='retail_products',
                        ),
                        DELIVERY_ITEM,
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='personal_wallet',
                    items=[
                        helpers.make_transactions_item(
                            item_id='retail-product',
                            amount='10.00',
                            product_id='retail_products',
                        ),
                        helpers.make_transactions_item(
                            item_id='delivery',
                            amount='0.00',
                            product_id='delivery_trust_product_id',
                        ),
                    ],
                ),
            ],
            # debts
            [],
            # invoice_update_expected_called
            1,
            # customer_services_expected_called
            1,
            id='Only retail',
        ),
    ],
)
async def test_basic(
        check_refund_order_v2,
        pgsql,
        assert_db_order,
        assert_db_item_payment_type,
        mock_debt_collector_by_ids,
        mock_debt_collector_update_invoice,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        mock_order_revision_list,
        payment_type,
        complement_amount,
        init_db_items,
        invoice_retrieve_plus_items,
        items_paid,
        customer_services,
        customer_service_details,
        expected_plus_amount,
        expected_invoice_update_items,
        debts,
        invoice_update_expected_called,
        customer_services_expected_called,
):
    order = db_order.DBOrder(
        pgsql=pgsql,
        order_id='test_order',
        api_version=2,
        complement_amount=complement_amount,
        complement_payment_type='personal_wallet',
        complement_payment_id='complement_payment_id',
        business_type=consts.BUSINESS,
    )
    order.upsert()

    for item in init_db_items:
        db_item_payment_type_plus.DBItemPaymentTypePlus(
            pgsql=pgsql,
            item_id=item['item_id'],
            order_id='test_order',
            payment_type=item['payment_type'],
            plus_amount=item['plus_amount'],
            customer_service_type=item['customer_service_type'],
            revision_id='abcd',
        ).insert()

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        cleared=[
            {
                'items': invoice_retrieve_plus_items,
                'payment_type': 'personal_wallet',
            },
        ],
        transactions=[
            helpers.make_transaction(
                payment_type='personal_wallet',
                operation_id='create:100500',
                status='clear_success',
                sum=invoice_retrieve_plus_items,
            ),
            helpers.make_transaction(
                payment_type=payment_type,
                operation_id='create:100500',
                status='hold_success',
                sum=items_paid,
            ),
        ],
        operations=[
            helpers.make_operation(
                sum_to_pay=[
                    {'items': items_paid, 'payment_type': payment_type},
                    {
                        'items': invoice_retrieve_plus_items,
                        'payment_type': 'personal_wallet',
                    },
                ],
            ),
        ],
        payment_types=[payment_type, 'personal_wallet'],
    )

    customer_services_mock = mock_order_revision_customer_services(
        customer_services=customer_services,
    )

    customer_service_details_mock = (
        mock_order_revision_customer_services_details(
            customer_services=customer_service_details,
        )
    )

    mock_debt_collector_by_ids(debts=debts)
    mock_debt_collector_update_invoice()
    mock_order_revision_list()

    wallet_payload = (
        helpers.make_wallet_payload(
            cashback_service='eda',
            order_id='test_order',
            wallet_id='complement_payment_id',
        )
        if complement_amount is not None
        else None
    )

    complement_payment = None
    if complement_amount is not None:
        complement_payment = models.Complement(
            amount=complement_amount, payment_id='complement_payment_id',
        )

    invoice_update_mock = mock_transactions_invoice_update(
        complement_payment=complement_payment,
        items=expected_invoice_update_items,
        payment_type=payment_type,
        version=2,
        wallet_payload=wallet_payload,
        operation_id='refund:abcd-vfr',
    )

    await check_refund_order_v2()
    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == invoice_update_expected_called
    assert (
        customer_services_mock.times_called
        == customer_services_expected_called
    )
    assert customer_service_details_mock.times_called == 1

    expected_complement_amount = (
        decimal.Decimal(complement_amount)
        if complement_amount is not None
        else None
    )

    assert_db_order(
        TEST_ORDER_ID,
        expected_service='eats',
        expected_api_version=2,
        expected_complement_payment_type='personal_wallet',
        expected_complement_payment_id='complement_payment_id',
        expected_complement_amount=expected_complement_amount,
        expected_business_type=consts.BUSINESS,
    )

    for product_id, payment_type_, plus in expected_plus_amount:
        assert_db_item_payment_type(
            product_id, TEST_ORDER_ID, payment_type_, decimal.Decimal(plus),
        )


@configs.PERSONAL_WALLET_FIRM_BY_SERVICE
@pytest.mark.parametrize(
    'payment_type, complement_amount, init_db_items, '
    'invoice_retrieve_plus_items, items_paid, '
    'customer_services, customer_service_details, '
    'expected_plus_amount, expected_invoice_update_items, '
    'debts, invoice_update_expected_called, customer_services_expected_called',
    [
        pytest.param(
            # payment_type
            'card',
            # complement_amount
            '180.00',
            # init_db_items
            [
                {
                    'item_id': 'product-1',
                    'payment_type': 'trust',
                    'plus_amount': decimal.Decimal(107),
                    'customer_service_type': 'composition_products',
                },
                {
                    'item_id': 'option-1',
                    'payment_type': 'trust',
                    'plus_amount': decimal.Decimal(21),
                    'customer_service_type': 'composition_products',
                },
                {
                    'item_id': 'product-2',
                    'payment_type': 'trust',
                    'plus_amount': decimal.Decimal(31),
                    'customer_service_type': 'composition_products',
                },
                {
                    'item_id': 'delivery',
                    'payment_type': 'trust',
                    'plus_amount': decimal.Decimal(0),
                    'customer_service_type': 'delivery',
                },
                {
                    'item_id': 'retail-product-id',
                    'payment_type': 'trust',
                    'plus_amount': decimal.Decimal(21),
                    'customer_service_type': 'retail',
                },
            ],
            # invoice_retrieve_plus_items
            [
                helpers.make_transactions_item(
                    item_id='composition-products',
                    amount='159.00',
                    product_id='composition_products_trust_product_id',
                ),
                helpers.make_transactions_item(
                    item_id='retail-product-id',
                    amount='21.00',
                    product_id='retail_trust_product_id',
                ),
            ],
            # items_paid
            [
                helpers.make_transactions_item(
                    item_id='composition-products',
                    amount='1341.00',
                    product_id='composition_products_trust_product_id',
                ),
                helpers.make_transactions_item(
                    item_id='retail-product-id',
                    amount='159.00',
                    product_id='retail_trust_product_id',
                ),
                DELIVERY_ITEM,
            ],
            # customer_services
            [
                helpers.make_customer_service(
                    customer_service_id='composition-products',
                    name='big_mac',
                    cost_for_customer='500.00',
                    currency='RUB',
                    customer_service_type='composition_products',
                    vat='nds_20',
                    trust_product_id='composition_products_trust_product_id',
                    place_id='place_1',
                    refunded_amount='1000.00',
                ),
                helpers.make_customer_service(
                    customer_service_id='retail-product-id',
                    name='Retail',
                    cost_for_customer='0.00',
                    currency='RUB',
                    customer_service_type='retail',
                    vat='nds_none',
                    trust_product_id='retail_trust_product_id',
                    place_id='place_1',
                    refunded_amount='159.00',
                ),
                DELIVERY_CUSTOMER_SERVICE,
            ],
            # customer_service_details
            [
                helpers.make_customer_service(
                    customer_service_id='composition-products',
                    name='big_mac',
                    cost_for_customer='500.00',
                    currency='RUB',
                    customer_service_type='composition_products',
                    trust_product_id='composition_products_trust_product_id',
                    place_id='place_1',
                    balance_client_id='123456789',
                    personal_tin_id='personal-tin-id',
                    details=helpers.make_customer_service_details(
                        composition_products=[
                            helpers.make_composition_product(
                                composition_product_id='product-1',
                                name='Product 1',
                                cost_for_customer='0.00',
                                composition_product_type='product',
                                vat='nds_20',
                            ),
                            helpers.make_composition_product(
                                composition_product_id='option-1',
                                name='Option 1',
                                cost_for_customer='0.00',
                                composition_product_type='product',
                                vat='nds_20',
                            ),
                            helpers.make_composition_product(
                                composition_product_id='product-2',
                                name='Product 2',
                                cost_for_customer='500.00',
                                composition_product_type='product',
                                vat='nds_20',
                            ),
                        ],
                        refunds=[
                            helpers.make_composition_product_refund(
                                refund_revision_id='55555',
                                refund_products=[
                                    {
                                        'id': 'product-1',
                                        'refunded_amount': '970.00',
                                    },
                                    {
                                        'id': 'option-1',
                                        'refunded_amount': '30.00',
                                    },
                                ],
                            ),
                        ],
                    ),
                ),
                helpers.make_customer_service(
                    customer_service_id='retail-product-id',
                    name='Retail',
                    cost_for_customer='0.00',
                    currency='RUB',
                    customer_service_type='retail',
                    vat='nds_none',
                    trust_product_id='retail_trust_product_id',
                    place_id='place_1',
                    refunded_amount='159.00',
                ),
                DELIVERY_CUSTOMER_SERVICE,
            ],
            # expected_plus_amount
            [('product-2', 'trust', '31'), ('delivery', 'trust', '0')],
            # expected_invoice_update_items
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products',
                            amount='469.00',
                            product_id='composition_products_trust_product_id',
                        ),
                        helpers.make_transactions_item(
                            item_id='retail-product-id',
                            amount='0.00',
                            product_id='retail_trust_product_id',
                        ),
                        DELIVERY_ITEM,
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='personal_wallet',
                    items=[
                        helpers.make_transactions_item(
                            item_id='composition-products',
                            amount='31.00',
                            product_id='composition_products_trust_product_id',
                        ),
                        helpers.make_transactions_item(
                            item_id='retail-product-id',
                            amount='0.00',
                            product_id='retail_trust_product_id',
                        ),
                        helpers.make_transactions_item(
                            item_id='delivery',
                            amount='0.00',
                            product_id='delivery_trust_product_id',
                        ),
                    ],
                ),
            ],
            # debts
            [],
            # invoice_update_expected_called
            1,
            # customer_services_expected_called
            1,
            id='composition_products_refunds',
        ),
    ],
)
async def test_update_detailing(
        check_refund_order_v2,
        pgsql,
        assert_db_order,
        assert_db_item_payment_type,
        get_db_items_payment_type_by_revision,
        mock_debt_collector_by_ids,
        mock_debt_collector_update_invoice,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        mock_order_revision_list,
        payment_type,
        complement_amount,
        init_db_items,
        invoice_retrieve_plus_items,
        items_paid,
        customer_services,
        customer_service_details,
        expected_plus_amount,
        expected_invoice_update_items,
        debts,
        invoice_update_expected_called,
        customer_services_expected_called,
):
    order = db_order.DBOrder(
        pgsql=pgsql,
        order_id='test_order',
        api_version=2,
        complement_amount=complement_amount,
        complement_payment_type='personal_wallet',
        complement_payment_id='complement_payment_id',
        business_type=consts.BUSINESS,
    )
    order.upsert()

    for item in init_db_items:
        db_item_payment_type_plus.DBItemPaymentTypePlus(
            pgsql=pgsql,
            item_id=item['item_id'],
            order_id='test_order',
            payment_type=item['payment_type'],
            plus_amount=item['plus_amount'],
            customer_service_type=item['customer_service_type'],
            revision_id='abcd',
        ).insert()

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        cleared=[
            {
                'items': invoice_retrieve_plus_items,
                'payment_type': 'personal_wallet',
            },
        ],
        transactions=[
            helpers.make_transaction(
                payment_type='personal_wallet',
                operation_id='create:100500',
                status='clear_success',
                sum=invoice_retrieve_plus_items,
            ),
            helpers.make_transaction(
                payment_type=payment_type,
                operation_id='create:100500',
                status='hold_success',
                sum=items_paid,
            ),
        ],
        operations=[
            helpers.make_operation(
                sum_to_pay=[
                    {'items': items_paid, 'payment_type': payment_type},
                    {
                        'items': invoice_retrieve_plus_items,
                        'payment_type': 'personal_wallet',
                    },
                ],
            ),
        ],
        payment_types=[payment_type, 'personal_wallet'],
    )

    customer_services_mock = mock_order_revision_customer_services(
        customer_services=customer_services,
    )

    customer_service_details_mock = (
        mock_order_revision_customer_services_details(
            customer_services=customer_service_details,
        )
    )

    mock_debt_collector_by_ids(debts=debts)
    mock_debt_collector_update_invoice()
    mock_order_revision_list()

    wallet_payload = (
        helpers.make_wallet_payload(
            cashback_service='eda',
            order_id='test_order',
            wallet_id='complement_payment_id',
        )
        if complement_amount is not None
        else None
    )

    complement_payment = None
    if complement_amount is not None:
        complement_payment = models.Complement(
            amount=complement_amount, payment_id='complement_payment_id',
        )

    invoice_update_mock = mock_transactions_invoice_update(
        complement_payment=complement_payment,
        items=expected_invoice_update_items,
        payment_type=payment_type,
        version=2,
        wallet_payload=wallet_payload,
        operation_id='refund:abcd-vfr',
    )

    await check_refund_order_v2()
    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == invoice_update_expected_called
    assert (
        customer_services_mock.times_called
        == customer_services_expected_called
    )
    assert customer_service_details_mock.times_called == 1

    expected_complement_amount = (
        decimal.Decimal(complement_amount)
        if complement_amount is not None
        else None
    )

    assert_db_order(
        TEST_ORDER_ID,
        expected_service='eats',
        expected_api_version=2,
        expected_complement_payment_type='personal_wallet',
        expected_complement_payment_id='complement_payment_id',
        expected_complement_amount=expected_complement_amount,
        expected_business_type=consts.BUSINESS,
    )

    items = get_db_items_payment_type_by_revision(TEST_ORDER_ID, 'abcd-vfr')

    assert len(items) == len(expected_plus_amount)
    for product_id, payment_type_, plus in expected_plus_amount:
        assert_db_item_payment_type(
            product_id, TEST_ORDER_ID, payment_type_, decimal.Decimal(plus),
        )
