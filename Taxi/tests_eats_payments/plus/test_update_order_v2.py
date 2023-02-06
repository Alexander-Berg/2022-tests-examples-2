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
REVISION = 'abcd'
URL = 'v2/orders/update'
DELIVERY_ITEM = helpers.make_transactions_item(
    item_id='delivery',
    amount='100.00',
    product_id='delivery_trust_product_id',
)
FREE_DELIVERY_ITEM = helpers.make_transactions_item(
    item_id='delivery-1',
    amount='0.00',
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
FREE_DELIVERY_CUSTOMER_SERVICE = helpers.make_customer_service(
    customer_service_id='delivery-1',
    name='Delivery-1',
    cost_for_customer='0',
    currency='RUB',
    customer_service_type='delivery',
    vat='nds_20',
    trust_product_id='delivery_trust_product_id',
    place_id='place_1',
)


@pytest.fixture(name='check_update_order_v2')
def check_update_order_fixture(taxi_eats_payments, mockserver, load_json):
    async def _inner(
            payment_type: typing.Optional[str] = 'card',
            payment_method_id: typing.Optional[str] = '123',
            response_status=200,
            response_body=None,
            ttl: int = None,
    ):
        request_payload = {
            'id': 'test_order',
            'version': 2,
            'revision': 'abcd',
        }
        if payment_type is not None:
            request_payload['payment_method'] = {
                'id': payment_method_id,
                'type': payment_type,
            }

        payload: typing.Dict[str, typing.Any] = {**request_payload}
        if ttl is not None:
            payload['ttl'] = ttl
        response = await taxi_eats_payments.post(URL, json=payload)
        assert response.status == response_status
        if response_body is not None:
            assert response.json() == response_body

    return _inner


TESTCASE_SIMPLE = pytest.param(
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
    # debt_status
    'created',
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
                        composition_product_id='product-1-updated',
                        name='Product 1',
                        cost_for_customer='1000.00',
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
            currency='RUB',
            customer_service_type='retail',
            vat='nds_none',
            trust_product_id='retail_trust_product_id',
            place_id='place_1',
        ),
        DELIVERY_CUSTOMER_SERVICE,
    ],
    # expected_plus_amount
    [('product-1-updated', 'trust', '180')],
    # expected_invoice_update_items
    [
        helpers.make_transactions_payment_items(
            payment_type='card',
            items=[
                helpers.make_transactions_item(
                    item_id='composition-products',
                    amount='820.00',
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
                    amount='180.00',
                    product_id='composition_products_trust_product_id',
                ),
            ],
        ),
    ],
    # debts
    [],
    # invoice_update_expected_called
    1,
    id='simple_case',
)


TESTCASE_MAX_PLUS_AMOUNT = pytest.param(
    # payment_type
    'card',
    # complement_amount
    '1348.00',
    # init_db_items
    [
        {
            'item_id': 'product-1',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(1200),
            'customer_service_type': 'composition_products',
            'revision_id': 'bbbb',
        },
        {
            'item_id': 'option-1',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(100),
            'customer_service_type': 'composition_products',
            'revision_id': 'bbbb',
        },
        {
            'item_id': 'product-2',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(48),
            'customer_service_type': 'composition_products',
            'revision_id': 'bbbb',
        },
        {
            'item_id': 'delivery',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(0),
            'customer_service_type': 'delivery',
            'revision_id': 'bbbb',
        },
    ],
    # debt_status
    'created',
    # invoice_retrieve_plus_items
    [
        helpers.make_transactions_item(
            item_id='composition-products',
            amount='1348.00',
            product_id='composition_products_trust_product_id',
        ),
    ],
    # items_paid
    [
        helpers.make_transactions_item(
            item_id='composition-products',
            amount='1348.00',
            product_id='composition_products_trust_product_id',
        ),
        DELIVERY_ITEM,
    ],
    # customer_service_details
    [
        helpers.make_customer_service(
            customer_service_id='composition-products',
            name='big_mac',
            cost_for_customer='880.00',
            currency='RUB',
            customer_service_type='composition_products',
            trust_product_id='composition_products_trust_product_id',
            place_id='place_1',
            balance_client_id='123456789',
            personal_tin_id='personal-tin-id',
            details=helpers.make_customer_service_details(
                composition_products=[
                    helpers.make_composition_product(
                        composition_product_id='product-1-updated',
                        name='Product 1',
                        cost_for_customer='480.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-2-updated',
                        name='Product 2',
                        cost_for_customer='400.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                ],
            ),
        ),
        DELIVERY_CUSTOMER_SERVICE,
    ],
    # expected_plus_amount
    [
        ('product-1-updated', 'trust', '479'),
        ('product-2-updated', 'trust', '399'),
    ],
    # expected_invoice_update_items
    [
        helpers.make_transactions_payment_items(
            payment_type='card',
            items=[
                helpers.make_transactions_item(
                    item_id='composition-products',
                    amount='2.00',
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
                    amount='878.00',
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
    id='Max plus amount',
)

TESTCASE_DEBT_COLLECTOR = pytest.param(
    # payment_type
    'card',
    # complement_amount
    '1837.00',
    # init_db_items
    [
        {
            'item_id': 'product-1',
            'payment_type': 'debt-collector',
            'plus_amount': decimal.Decimal(439),
            'customer_service_type': 'composition_products',
        },
        {
            'item_id': 'product-2',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(489),
            'customer_service_type': 'composition_products',
        },
        {
            'item_id': 'product-3',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(819),
            'customer_service_type': 'composition_products',
        },
        {
            'item_id': 'option-1',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(30),
            'customer_service_type': 'composition_products',
        },
        {
            'item_id': 'option-2',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(30),
            'customer_service_type': 'composition_products',
        },
        {
            'item_id': 'option-3',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(0),
            'customer_service_type': 'composition_products',
        },
        {
            'item_id': 'option-4',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(30),
            'customer_service_type': 'composition_products',
        },
        {
            'item_id': 'option-5',
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
    # debt_status
    'updated',
    # invoice_retrieve_plus_items
    [
        helpers.make_transactions_item(
            item_id='composition-products',
            amount='1837.00',
            product_id='composition_products_trust_product_id',
        ),
    ],
    # items_paid
    [
        helpers.make_transactions_item(
            item_id='composition-products',
            amount='1837.00',
            product_id='composition_products_trust_product_id',
        ),
        DELIVERY_ITEM,
    ],
    # customer_service_details
    [
        helpers.make_customer_service(
            customer_service_id='composition-products',
            name='big_mac',
            cost_for_customer='1830.00',
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
                        cost_for_customer='370.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-2',
                        name='Product 1',
                        cost_for_customer='490.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-3',
                        name='Product 1',
                        cost_for_customer='820.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='option-1',
                        name='Product 1',
                        cost_for_customer='30.00',
                        composition_product_type='option',
                        vat='nds_none',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='option-2',
                        name='Product 1',
                        cost_for_customer='30.00',
                        composition_product_type='option',
                        vat='nds_none',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='option-3',
                        name='Product 1',
                        cost_for_customer='0.00',
                        composition_product_type='option',
                        vat='nds_none',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='option-4',
                        name='Product 1',
                        cost_for_customer='30.00',
                        composition_product_type='option',
                        vat='nds_none',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='option-5',
                        name='Product 1',
                        cost_for_customer='0.00',
                        composition_product_type='option',
                        vat='nds_none',
                    ),
                ],
            ),
        ),
        DELIVERY_CUSTOMER_SERVICE,
    ],
    # expected_plus_amount
    [
        ('product-1', 'debt-collector', '369'),
        ('product-2', 'debt-collector', '489'),
        ('product-3', 'debt-collector', '819'),
    ],
    # expected_invoice_update_items
    [],
    # debts
    [helpers.make_debt(reason_code='technical_debt')],
    # invoice_update_expected_called
    0,
    id='Use debt-collector',
)

TESTCASE_DEBT_COLLECTOR_WITHOUT_PLUS = pytest.param(
    # payment_type
    'card',
    # complement_amount
    None,
    # init_db_items
    [
        {
            'item_id': 'product-1',
            'payment_type': 'debt-collector',
            'plus_amount': decimal.Decimal(0),
            'customer_service_type': 'composition_products',
        },
        {
            'item_id': 'product-2',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(0),
            'customer_service_type': 'composition_products',
        },
        {
            'item_id': 'option-1',
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
    # debt_status
    'updated',
    # invoice_retrieve_plus_items
    [
        helpers.make_transactions_item(
            item_id='composition-products',
            amount='1840.00',
            product_id='composition_products_trust_product_id',
        ),
    ],
    # items_paid
    [
        helpers.make_transactions_item(
            item_id='composition-products',
            amount='1840.00',
            product_id='composition_products_trust_product_id',
        ),
        DELIVERY_ITEM,
    ],
    # customer_service_details
    [
        helpers.make_customer_service(
            customer_service_id='composition-products',
            name='big_mac',
            cost_for_customer='1840.00',
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
                        cost_for_customer='370.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-2',
                        name='Product 1',
                        cost_for_customer='1400.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='option-1',
                        name='Product 1',
                        cost_for_customer='30.00',
                        composition_product_type='option',
                        vat='nds_none',
                    ),
                ],
            ),
        ),
        DELIVERY_CUSTOMER_SERVICE,
    ],
    # expected_plus_amount
    [
        ('product-1', 'debt-collector', '0'),
        ('product-2', 'debt-collector', '0'),
    ],
    # expected_invoice_update_items
    [],
    # debts
    [helpers.make_debt(reason_code='technical_debt')],
    # invoice_update_expected_called
    0,
    id='Without plus, debt-collector',
)

TESTCASE_WITHOUT_PLUS = pytest.param(
    # payment_type
    'card',
    # complement_amount
    None,
    # init_db_items
    [
        {
            'item_id': 'product-1',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(0),
            'customer_service_type': 'composition_products',
        },
        {
            'item_id': 'product-2',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(0),
            'customer_service_type': 'composition_products',
        },
        {
            'item_id': 'option-1',
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
    # debt_status
    'created',
    # invoice_retrieve_plus_items
    [
        helpers.make_transactions_item(
            item_id='composition-products',
            amount='1840.00',
            product_id='composition_products_trust_product_id',
        ),
        DELIVERY_ITEM,
    ],
    # items_paid
    [
        helpers.make_transactions_item(
            item_id='composition-products',
            amount='1840.00',
            product_id='composition_products_trust_product_id',
        ),
        DELIVERY_ITEM,
    ],
    # customer_service_details
    [
        helpers.make_customer_service(
            customer_service_id='composition-products',
            name='big_mac',
            cost_for_customer='1840.00',
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
                        cost_for_customer='370.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-2',
                        name='Product 1',
                        cost_for_customer='1400.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='option-1',
                        name='Product 1',
                        cost_for_customer='30.00',
                        composition_product_type='option',
                        vat='nds_none',
                    ),
                ],
            ),
        ),
        DELIVERY_CUSTOMER_SERVICE,
    ],
    # expected_plus_amount
    [('product-1', 'trust', '0'), ('product-2', 'trust', '0')],
    # expected_invoice_update_items
    [
        helpers.make_transactions_payment_items(
            payment_type='card',
            items=[
                helpers.make_transactions_item(
                    item_id='composition-products',
                    amount='1840.00',
                    product_id='composition_products_trust_product_id',
                ),
                DELIVERY_ITEM,
            ],
        ),
    ],
    # debts
    [],
    # invoice_update_expected_called
    1,
    id='Without plus',
)

TESTCASE_EDAORDERS_7548 = pytest.param(
    # payment_type
    'card',
    # complement_amount
    '409.00',
    # init_db_items
    [
        {
            'item_id': 'product-1',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(409),
            'customer_service_type': 'composition_products',
            'revision_id': 'bbbb',
        },
        {
            'item_id': 'option-1',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(0),
            'customer_service_type': 'composition_products',
            'revision_id': 'bbbb',
        },
    ],
    # debt_status
    'created',
    # invoice_retrieve_plus_items
    [
        helpers.make_transactions_item(
            item_id='composition-products',
            amount='409.00',
            product_id='composition_products_trust_product_id',
        ),
    ],
    # items_paid
    [
        helpers.make_transactions_item(
            item_id='composition-products',
            amount='409.00',
            product_id='composition_products_trust_product_id',
        ),
        DELIVERY_ITEM,
    ],
    # customer_service_details
    [
        helpers.make_customer_service(
            customer_service_id='composition-products',
            name='big_mac',
            cost_for_customer='410.00',
            currency='RUB',
            customer_service_type='composition_products',
            trust_product_id='composition_products_trust_product_id',
            place_id='place_1',
            balance_client_id='123456789',
            personal_tin_id='personal-tin-id',
            details=helpers.make_customer_service_details(
                composition_products=[
                    helpers.make_composition_product(
                        composition_product_id='product-2',
                        name='Product 2',
                        cost_for_customer='135.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='option-2',
                        name='Option 2',
                        cost_for_customer='70.00',
                        composition_product_type='option',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-3',
                        name='Product 3',
                        cost_for_customer='135.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='option-3',
                        name='Option 3',
                        cost_for_customer='70.00',
                        composition_product_type='option',
                        vat='nds_20',
                    ),
                ],
            ),
        ),
        DELIVERY_CUSTOMER_SERVICE,
    ],
    # expected_plus_amount
    [
        ('product-2', 'trust', '134'),
        ('option-2', 'trust', '70'),
        ('product-3', 'trust', '134'),
        ('option-3', 'trust', '70'),
    ],
    # expected_invoice_update_items
    [
        helpers.make_transactions_payment_items(
            payment_type='card',
            items=[
                helpers.make_transactions_item(
                    item_id='composition-products',
                    amount='2.00',
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
                    amount='408.00',
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
    id='EDAORDERS-7548',
)

TESTCASE_REVISION_IS_NOT_CHANGED = pytest.param(
    # payment_type
    'card',
    # complement_amount
    '502.00',
    # init_db_items
    [
        {
            'item_id': 'product-1',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(208.99),
            'customer_service_type': 'composition_products',
            'revision_id': REVISION,
        },
        {
            'item_id': 'option-1',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(39.99),
            'customer_service_type': 'composition_products',
            'revision_id': REVISION,
        },
        {
            'item_id': 'product-2',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(49.99),
            'customer_service_type': 'composition_products',
            'revision_id': REVISION,
        },
        {
            'item_id': 'product-3',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(128.05),
            'customer_service_type': 'composition_products',
            'revision_id': REVISION,
        },
        {
            'item_id': 'option-2',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(39.99),
            'customer_service_type': 'composition_products',
            'revision_id': REVISION,
        },
        {
            'item_id': 'option-3',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(34.99),
            'customer_service_type': 'composition_products',
            'revision_id': REVISION,
        },
    ],
    # debt_status
    'created',
    # invoice_retrieve_plus_items
    [
        helpers.make_transactions_item(
            item_id='composition-products',
            amount='502.00',
            product_id='composition_products_trust_product_id',
        ),
    ],
    # items_paid
    [
        helpers.make_transactions_item(
            item_id='composition-products',
            amount='3.94',
            product_id='composition_products_trust_product_id',
        ),
        helpers.make_transactions_item(
            item_id='delivery',
            amount='99.00',
            product_id='delivery_trust_product_id',
        ),
        helpers.make_transactions_item(
            item_id='service_fee',
            amount='39.00',
            product_id='service_fee_product_id',
        ),
    ],
    # customer_service_details
    [
        helpers.make_customer_service(
            customer_service_id='composition-products',
            name='big_mac',
            cost_for_customer='505.94',
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
                        cost_for_customer='209.99',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='option-1',
                        name='Option 1',
                        cost_for_customer='39.99',
                        composition_product_type='option',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='option-2',
                        name='Option 2',
                        cost_for_customer='39.99',
                        composition_product_type='option',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='option-3',
                        name='Option 3',
                        cost_for_customer='34.99',
                        composition_product_type='option',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-2',
                        name='Product 2',
                        cost_for_customer='50.99',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-3',
                        name='Product 3',
                        cost_for_customer='129.99',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                ],
            ),
        ),
        helpers.make_customer_service(
            customer_service_id='delivery',
            name='Delivery-1',
            cost_for_customer='99',
            currency='RUB',
            customer_service_type='delivery',
            vat='nds_20',
            trust_product_id='delivery_trust_product_id',
            place_id='place_1',
        ),
        helpers.make_customer_service(
            customer_service_id='service_fee',
            name='ServiceFee-1',
            cost_for_customer='39',
            currency='RUB',
            customer_service_type='service_fee',
            vat='nds_20',
            trust_product_id='eda_61664402_ride',
            place_id='place_1',
        ),
    ],
    # expected_plus_amount
    [
        ('product-1', 'trust', '208.99'),
        ('option-1', 'trust', '39.99'),
        ('product-2', 'trust', '49.99'),
        ('product-3', 'trust', '128.05'),
        ('option-2', 'trust', '39.99'),
        ('option-3', 'trust', '34.99'),
        ('delivery', 'trust', '0'),
    ],
    # expected_invoice_update_items
    [
        helpers.make_transactions_payment_items(
            payment_type='card',
            items=[
                helpers.make_transactions_item(
                    item_id='composition-products',
                    amount='3.94',
                    product_id='composition_products_trust_product_id',
                ),
                helpers.make_transactions_item(
                    item_id='delivery',
                    amount='99.00',
                    product_id='delivery_trust_product_id',
                ),
                helpers.make_transactions_item(
                    item_id='service_fee',
                    amount='39.00',
                    product_id='eda_61664402_ride',
                ),
            ],
        ),
        helpers.make_transactions_payment_items(
            payment_type='personal_wallet',
            items=[
                helpers.make_transactions_item(
                    item_id='composition-products',
                    amount='502.00',
                    product_id='composition_products_trust_product_id',
                ),
            ],
        ),
    ],
    # debts
    [],
    # invoice_update_expected_called
    1,
    id='EDAORDERS-7646',
)


TESTCASE_FREE_DELIVERY = pytest.param(
    # payment_type
    'card',
    # complement_amount
    '24.00',
    # init_db_items
    [
        {
            'item_id': 'product-1',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(3),
            'customer_service_type': 'composition_products',
            'revision_id': 'bbbb',
        },
        {
            'item_id': 'product-2',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(1),
            'customer_service_type': 'composition_products',
            'revision_id': 'bbbb',
        },
        {
            'item_id': 'product-3',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(1),
            'customer_service_type': 'composition_products',
            'revision_id': 'bbbb',
        },
        {
            'item_id': 'product-4',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(3),
            'customer_service_type': 'composition_products',
            'revision_id': 'bbbb',
        },
        {
            'item_id': 'product-5',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(3),
            'customer_service_type': 'composition_products',
            'revision_id': 'bbbb',
        },
        {
            'item_id': 'product-6',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(3),
            'customer_service_type': 'composition_products',
            'revision_id': 'bbbb',
        },
        {
            'item_id': 'product-7',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(4),
            'customer_service_type': 'composition_products',
            'revision_id': 'bbbb',
        },
        {
            'item_id': 'product-8',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(6),
            'customer_service_type': 'composition_products',
            'revision_id': 'bbbb',
        },
        {
            'item_id': 'delivery-1',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(0),
            'customer_service_type': 'delivery',
            'revision_id': 'bbbb',
        },
        {
            'item_id': 'service_fee-1',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(0),
            'customer_service_type': 'service_fee',
            'revision_id': 'bbbb',
        },
    ],
    # debt_status
    'created',
    # invoice_retrieve_plus_items
    [
        helpers.make_transactions_item(
            item_id='composition-products',
            amount='24.00',
            product_id='composition_products_trust_product_id',
        ),
    ],
    # items_paid
    [
        helpers.make_transactions_item(
            item_id='composition-products',
            amount='1687.00',
            product_id='composition_products_trust_product_id',
        ),
        FREE_DELIVERY_ITEM,
        helpers.make_transactions_item(
            item_id='sf-1',
            amount='39.00',
            product_id='service_fee_trust_product_id',
        ),
    ],
    # customer_service_details
    [
        helpers.make_customer_service(
            customer_service_id='composition-products',
            name='big_mac',
            cost_for_customer='1605.59',
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
                        cost_for_customer='97.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-2',
                        name='Product 2',
                        cost_for_customer='97.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-3',
                        name='Product 3',
                        cost_for_customer='97.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-4',
                        name='Product 4',
                        cost_for_customer='230.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-5',
                        name='Product 5',
                        cost_for_customer='230.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-6',
                        name='Product 6',
                        cost_for_customer='230.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-7',
                        name='Product 7',
                        cost_for_customer='298.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-8',
                        name='Product 8',
                        cost_for_customer='326.59',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                ],
            ),
        ),
        FREE_DELIVERY_CUSTOMER_SERVICE,
        helpers.make_customer_service(
            customer_service_id='service_fee-1',
            name='sf-1',
            cost_for_customer='39.00',
            currency='RUB',
            customer_service_type='service_fee',
            vat='nds_20',
            trust_product_id='service_fee_trust_product_id',
            place_id='place_1',
        ),
    ],
    # expected_plus_amount
    [
        ('product-1', 'trust', '5'),
        ('product-2', 'trust', '1'),
        ('product-3', 'trust', '1'),
        ('product-4', 'trust', '3'),
        ('product-5', 'trust', '3'),
        ('product-6', 'trust', '3'),
        ('product-7', 'trust', '4'),
        ('product-8', 'trust', '4'),
    ],
    # expected_invoice_update_items
    [
        helpers.make_transactions_payment_items(
            payment_type='card',
            items=[
                helpers.make_transactions_item(
                    item_id='composition-products',
                    amount='1581.59',
                    product_id='composition_products_trust_product_id',
                ),
                FREE_DELIVERY_ITEM,
                helpers.make_transactions_item(
                    item_id='service_fee-1',
                    amount='39.00',
                    product_id='service_fee_trust_product_id',
                ),
            ],
        ),
        helpers.make_transactions_payment_items(
            payment_type='personal_wallet',
            items=[
                helpers.make_transactions_item(
                    item_id='composition-products',
                    amount='24.00',
                    product_id='composition_products_trust_product_id',
                ),
                helpers.make_transactions_item(
                    item_id='delivery-1',
                    amount='0.00',
                    product_id='delivery_trust_product_id',
                ),
                helpers.make_transactions_item(
                    item_id='service_fee-1',
                    amount='0.00',
                    product_id='service_fee_trust_product_id',
                ),
            ],
        ),
    ],
    # debts
    [],
    # invoice_update_expected_called
    1,
    id='EDAORDERS-7675',
)


TESTCASE_SERVICE_FEE_BYN = pytest.param(
    # payment_type
    'card',
    # complement_amount
    '2.5',
    # init_db_items
    [
        {
            'item_id': 'product-1',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(1.5),
            'customer_service_type': 'composition_products',
            'revision_id': 'bbbb',
        },
        {
            'item_id': 'product-2',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(1),
            'customer_service_type': 'composition_products',
            'revision_id': 'bbbb',
        },
        {
            'item_id': 'delivery-1',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(0),
            'customer_service_type': 'delivery',
            'revision_id': 'bbbb',
        },
        {
            'item_id': 'service_fee-1',
            'payment_type': 'trust',
            'plus_amount': decimal.Decimal(0),
            'customer_service_type': 'service_fee',
            'revision_id': 'bbbb',
        },
    ],
    # debt_status
    'created',
    # invoice_retrieve_plus_items
    [
        helpers.make_transactions_item(
            item_id='composition-products',
            amount='24.00',
            product_id='composition_products_trust_product_id',
        ),
    ],
    # items_paid
    [
        helpers.make_transactions_item(
            item_id='composition-products',
            amount='33.40',
            product_id='composition_products_trust_product_id',
        ),
        helpers.make_transactions_item(
            item_id='delivery-1',
            amount='4.00',
            product_id='delivery_trust_product_id',
        ),
        helpers.make_transactions_item(
            item_id='sf-1',
            amount='0.89',
            product_id='service_fee_trust_product_id',
        ),
    ],
    # customer_service_details
    [
        helpers.make_customer_service(
            customer_service_id='composition-products',
            name='big_mac',
            cost_for_customer='33.40',
            currency='BYN',
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
                        cost_for_customer='19.90',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-2',
                        name='Product 2',
                        cost_for_customer='13.50',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                ],
            ),
        ),
        helpers.make_customer_service(
            customer_service_id='delivery-1',
            name='delivery-1',
            cost_for_customer='4.00',
            currency='BYN',
            customer_service_type='delivery',
            vat='nds_20',
            trust_product_id='delivery_trust_product_id',
            place_id='place_1',
        ),
        helpers.make_customer_service(
            customer_service_id='service_fee-1',
            name='sf-1',
            cost_for_customer='0.89',
            currency='BYN',
            customer_service_type='service_fee',
            vat='nds_20',
            trust_product_id='service_fee_trust_product_id',
            place_id='place_1',
        ),
    ],
    # expected_plus_amount
    [('product-1', 'trust', '1.5'), ('product-2', 'trust', '1')],
    # expected_invoice_update_items
    [
        helpers.make_transactions_payment_items(
            payment_type='card',
            items=[
                helpers.make_transactions_item(
                    item_id='composition-products',
                    amount='30.90',
                    product_id='composition_products_trust_product_id',
                ),
                helpers.make_transactions_item(
                    item_id='delivery-1',
                    amount='4.00',
                    product_id='delivery_trust_product_id',
                ),
                helpers.make_transactions_item(
                    item_id='service_fee-1',
                    amount='0.89',
                    product_id='service_fee_trust_product_id',
                ),
            ],
        ),
        helpers.make_transactions_payment_items(
            payment_type='personal_wallet',
            items=[
                helpers.make_transactions_item(
                    item_id='composition-products',
                    amount='2.50',
                    product_id='composition_products_trust_product_id',
                ),
                helpers.make_transactions_item(
                    item_id='delivery-1',
                    amount='0.00',
                    product_id='delivery_trust_product_id',
                ),
                helpers.make_transactions_item(
                    item_id='service_fee-1',
                    amount='0.00',
                    product_id='service_fee_trust_product_id',
                ),
            ],
        ),
    ],
    # debts
    [],
    # invoice_update_expected_called
    1,
    id='EDAORDERS-7791',
)


TESTCASE_DB_ITEMS_NOT_FOUND_REDUCE_PLUS = pytest.param(
    # payment_type
    'card',
    # complement_amount
    '1531.00',
    # init_db_items
    [],
    # debt_status
    'created',
    # invoice_retrieve_plus_items
    [
        helpers.make_transactions_item(
            item_id='composition-products',
            amount='1531.00',
            product_id='composition_products_trust_product_id',
        ),
    ],
    # items_paid
    [
        helpers.make_transactions_item(
            item_id='composition-products',
            amount='142.00',
            product_id='composition_products_trust_product_id',
        ),
        DELIVERY_ITEM,
    ],
    # customer_service_details
    [
        helpers.make_customer_service(
            customer_service_id='composition-products',
            name='big_mac',
            cost_for_customer='1405.00',
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
                        cost_for_customer='378.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-2',
                        name='Product 2',
                        cost_for_customer='164.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-4',
                        name='Product 2',
                        cost_for_customer='445.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-5',
                        name='Product 2',
                        cost_for_customer='418.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                ],
            ),
        ),
        DELIVERY_CUSTOMER_SERVICE,
    ],
    # expected_plus_amount
    [
        ('product-1', 'trust', '377'),
        ('product-2', 'trust', '163'),
        ('product-4', 'trust', '444'),
        ('product-5', 'trust', '417'),
    ],
    # expected_invoice_update_items
    [
        helpers.make_transactions_payment_items(
            payment_type='card',
            items=[
                helpers.make_transactions_item(
                    item_id='composition-products',
                    amount='4.00',
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
                    amount='1401.00',
                    product_id='composition_products_trust_product_id',
                ),
            ],
        ),
    ],
    # debts
    [],
    # invoice_update_expected_called
    1,
    id='EDAORDERS-7845',
)


@configs.PERSONAL_WALLET_FIRM_BY_SERVICE
@pytest.mark.parametrize(
    'payment_type, complement_amount, init_db_items, debt_status,'
    'invoice_retrieve_plus_items, items_paid, '
    'customer_service_details, '
    'expected_plus_amount, expected_invoice_update_items, '
    'debts, invoice_update_expected_called',
    [
        TESTCASE_SIMPLE,
        TESTCASE_MAX_PLUS_AMOUNT,
        TESTCASE_DEBT_COLLECTOR,
        TESTCASE_DEBT_COLLECTOR_WITHOUT_PLUS,
        TESTCASE_WITHOUT_PLUS,
        TESTCASE_EDAORDERS_7548,
        TESTCASE_REVISION_IS_NOT_CHANGED,
        TESTCASE_FREE_DELIVERY,
        TESTCASE_SERVICE_FEE_BYN,
        TESTCASE_DB_ITEMS_NOT_FOUND_REDUCE_PLUS,
    ],
)
async def test_basic(
        check_update_order_v2,
        pgsql,
        assert_db_order,
        assert_db_item_payment_type,
        upsert_debt_status,
        mock_debt_collector_by_ids,
        mock_debt_collector_update_invoice,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        mock_order_revision_list,
        payment_type,
        complement_amount,
        init_db_items,
        debt_status,
        invoice_retrieve_plus_items,
        items_paid,
        customer_service_details,
        expected_plus_amount,
        expected_invoice_update_items,
        debts,
        invoice_update_expected_called,
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
    upsert_debt_status(order_id='test_order', debt_status=debt_status)

    for item in init_db_items:
        db_item_payment_type_plus.DBItemPaymentTypePlus(
            pgsql=pgsql,
            item_id=item['item_id'],
            order_id='test_order',
            payment_type=item['payment_type'],
            plus_amount=item['plus_amount'],
            customer_service_type=item['customer_service_type'],
            revision_id=item['revision_id'] if 'revision_id' in item else '',
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
    )

    await check_update_order_v2(payment_type=payment_type)
    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == invoice_update_expected_called
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
            product_id,
            TEST_ORDER_ID,
            payment_type_,
            decimal.Decimal(plus),
            REVISION,
        )
