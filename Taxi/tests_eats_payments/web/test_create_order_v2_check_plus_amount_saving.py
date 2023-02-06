# pylint: disable=too-many-lines

import copy
import decimal
import typing

import pytest

from tests_eats_payments import configs
from tests_eats_payments import consts
from tests_eats_payments import helpers
from tests_eats_payments import models


NOW = '2020-08-12T07:20:00+00:00'


@configs.PERSONAL_WALLET_FIRM_BY_SERVICE
@configs.CASHBACK_CONFIG
@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize('payment_type', ['card'])
@pytest.mark.parametrize('service', ['eats'])
@pytest.mark.parametrize(
    'test_items_personal_wallet, delivery_item, '
    'complement_amount, '
    'customer_service_details, expected_db_complement_amount, '
    'expected_db_item_payment_type',
    [
        pytest.param(
            # test_items_personal_wallet
            [
                models.TestItem(
                    amount='1500.00',
                    by_complement='159.00',
                    item_id='composition-products',
                    product_id='composition_products_trust_product_id',
                ),
                models.TestItem(
                    amount='200.00',
                    by_complement='21.00',
                    item_id='retail-product-id',
                    product_id='retail_trust_product_id',
                ),
            ],
            # delivery_item
            models.TestItem(
                amount='100.00',
                by_complement='0.00',
                item_id='delivery',
                product_id='delivery_trust_product_id',
            ),
            # complement_amount
            '180.00',
            # customer_service_details
            [
                helpers.make_customer_service(
                    customer_service_id='composition-products',
                    name='big_mac',
                    cost_for_customer='1500.00',
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
                                cost_for_customer='1000.00',
                                composition_product_type='product',
                                vat='nds_20',
                            ),
                            helpers.make_composition_product(
                                composition_product_id='option-1',
                                name='Option 1',
                                cost_for_customer='200.00',
                                composition_product_type='option',
                                vat='nds_20',
                            ),
                            helpers.make_composition_product(
                                composition_product_id='product-2',
                                name='Product 2',
                                cost_for_customer='300.00',
                                composition_product_type='product',
                                vat='nds_20',
                            ),
                        ],
                    ),
                ),
                helpers.make_customer_service(
                    customer_service_id='retail-product-id',
                    name='Retail',
                    cost_for_customer='200',
                    currency='RUB',
                    customer_service_type='retail',
                    vat='nds_none',
                    trust_product_id='retail_trust_product_id',
                    place_id='place_1',
                ),
                helpers.make_customer_service(
                    customer_service_id='delivery',
                    name='Delivery-1',
                    cost_for_customer='100',
                    currency='RUB',
                    customer_service_type='delivery',
                    vat='nds_20',
                    trust_product_id='delivery_trust_product_id',
                    place_id='place_1',
                ),
            ],
            # expected_db_complement_amount
            '180',
            # expected_db_item_payment_type
            [
                ('product-1', '107'),
                ('option-1', '21'),
                ('product-2', '31'),
                ('delivery', '0'),
                ('retail-product-id', '21'),
            ],
        ),
        pytest.param(
            # test_items_personal_wallet
            [
                models.TestItem(
                    amount='1830.00',
                    by_complement='1827.00',
                    item_id='composition-products',
                    product_id='composition_products_trust_product_id',
                ),
            ],
            # delivery_item
            models.TestItem(
                amount='0',
                by_complement='0.00',
                item_id='delivery',
                product_id='delivery_trust_product_id',
            ),
            # complement_amount
            '1837.00',
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
                                cost_for_customer='816.00',
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
                                composition_product_id='option-2',
                                name='Option 2',
                                cost_for_customer='29.00',
                                composition_product_type='option',
                                vat='nds_20',
                            ),
                            helpers.make_composition_product(
                                composition_product_id='option-3',
                                name='Option 3',
                                cost_for_customer='30.00',
                                composition_product_type='option',
                                vat='nds_20',
                            ),
                            helpers.make_composition_product(
                                composition_product_id='product-2',
                                name='Product 2',
                                cost_for_customer='438.00',
                                composition_product_type='product',
                                vat='nds_20',
                            ),
                            helpers.make_composition_product(
                                composition_product_id='option-4',
                                name='Option 4',
                                cost_for_customer='0.00',
                                composition_product_type='option',
                                vat='nds_20',
                            ),
                            helpers.make_composition_product(
                                composition_product_id='option-5',
                                name='Option 5',
                                cost_for_customer='29.00',
                                composition_product_type='option',
                                vat='nds_20',
                            ),
                            helpers.make_composition_product(
                                composition_product_id='product-3',
                                name='Product 3',
                                cost_for_customer='488.00',
                                composition_product_type='product',
                                vat='nds_20',
                            ),
                        ],
                    ),
                ),
                helpers.make_customer_service(
                    customer_service_id='delivery',
                    name='Delivery-1',
                    cost_for_customer='0',
                    currency='RUB',
                    customer_service_type='delivery',
                    vat='nds_20',
                    trust_product_id='delivery_trust_product_id',
                    place_id='place_1',
                ),
            ],
            # expected_db_complement_amount
            '1837',
            # expected_db_item_payment_type
            [
                ('product-1', '815'),
                ('option-1', '0'),
                ('product-2', '437'),
                ('option-2', '29'),
                ('delivery', '0'),
            ],
            # https://st.yandex-team.ru/EDAORDERS-6057
            id='Delivery by restaurant',
        ),
    ],
)
async def test_card_like_payment_methods(
        check_create_order_v2,
        assert_db_order,
        assert_db_order_payment,
        assert_db_item_payment_type,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        payment_type,
        service,
        experiments3,
        test_items_personal_wallet,
        delivery_item,
        complement_amount,
        customer_service_details,
        expected_db_complement_amount,
        expected_db_item_payment_type,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )

    test_items = copy.deepcopy(test_items_personal_wallet)
    test_items.append(delivery_item)

    complement = models.Complement(amount=complement_amount, service=service)

    invoice_create_mock = mock_transactions_invoice_create(
        payment_type=payment_type,
        complement_payment=complement,
        billing_service='food_payment',
        service=service,
    )

    transactions_items = helpers.make_transactions_payment_items(
        payment_type=payment_type,
        items=helpers.make_transactions_items(test_items),
    )
    personal_wallet_items = helpers.make_transactions_payment_items(
        payment_type=complement.payment_type,
        items=helpers.make_transactions_items_complement(
            test_items_personal_wallet,
        ),
    )

    expected_wallet_payload = helpers.make_wallet_payload(
        cashback_service=('lavka' if service == 'grocery' else 'eda'),
        order_id=consts.TEST_ORDER_ID,
        wallet_id=complement.payment_id,
    )

    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items, personal_wallet_items],
        operation_id='create:abcd',
        version=1,
        wallet_payload=expected_wallet_payload,
    )

    customer_service_details_mock = (
        mock_order_revision_customer_services_details(
            customer_services=customer_service_details,
        )
    )

    save_last_payment_mock = mock_user_state_save_last_payment(
        payment_type=payment_type,
    )

    await check_create_order_v2(
        consts.TEST_ORDER_ID,
        revision='abcd',
        payment_type=payment_type,
        service=service,
        additional_request_part=helpers.to_complement_payload(complement),
    )

    assert_db_order(
        order_id=consts.TEST_ORDER_ID,
        expected_service=service,
        expected_api_version=2,
        expected_complement_payment_type='personal_wallet',
        expected_complement_payment_id='complement-id',
        expected_complement_amount=decimal.Decimal(
            expected_db_complement_amount,
        ),
    )
    assert_db_order_payment(
        consts.TEST_ORDER_ID,
        consts.TEST_PAYMENT_ID,
        payment_type,
        expected_currency='RUB',
    )

    for product_id, plus in expected_db_item_payment_type:
        assert_db_item_payment_type(
            product_id, consts.TEST_ORDER_ID, 'trust', decimal.Decimal(plus),
        )

    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert customer_service_details_mock.times_called == 1
    assert save_last_payment_mock.times_called == 1


def make_product_items():
    return [
        helpers.make_customer_service(
            customer_service_id='composition-products',
            name='big_mac',
            cost_for_customer='1830.00',
            currency='RUB',
            customer_service_type='composition_products',
            vat='nds_20',
            trust_product_id='composition_products_trust_product_id',
            place_id='place_1',
        ),
    ]


def make_product_items_with_details():
    return [
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
                        cost_for_customer='816.00',
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
                        composition_product_id='option-2',
                        name='Option 2',
                        cost_for_customer='29.00',
                        composition_product_type='option',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='option-3',
                        name='Option 3',
                        cost_for_customer='30.00',
                        composition_product_type='option',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-2',
                        name='Product 2',
                        cost_for_customer='438.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='option-4',
                        name='Option 4',
                        cost_for_customer='0.00',
                        composition_product_type='option',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='option-5',
                        name='Option 5',
                        cost_for_customer='29.00',
                        composition_product_type='option',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='product-3',
                        name='Product 3',
                        cost_for_customer='488.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                ],
            ),
        ),
    ]


@configs.PERSONAL_WALLET_FIRM_BY_SERVICE
@configs.CASHBACK_CONFIG
@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize('payment_type', ['card'])
@pytest.mark.parametrize('service', ['eats'])
@pytest.mark.parametrize(
    'items_with_complement, items_without_complement, '
    'item_types_amount, additional_customer_services, '
    'expected_db_item_payment_type',
    [
        pytest.param(
            # items_with_complement
            [
                models.TestItem(
                    amount='1830.00',
                    by_complement='1812.00',
                    item_id='composition-products',
                    product_id='composition_products_trust_product_id',
                ),
                models.TestItem(
                    amount='9.00',
                    by_complement='7.00',
                    item_id='delivery',
                    product_id='delivery_trust_product_id',
                ),
                models.TestItem(
                    amount='18.00',
                    by_complement='16.00',
                    item_id='service_fee',
                    product_id='service_fee_trust_product_id',
                ),
            ],
            # items_without_complement
            [],
            # item_types_amount
            [
                {'amount': '10', 'item_type': 'delivery'},
                {'amount': '20', 'item_type': 'service_fee'},
            ],
            # additional_customer_services
            [
                helpers.make_customer_service(
                    customer_service_id='service_fee',
                    name='Service-Fee-1',
                    cost_for_customer='18',
                    currency='RUB',
                    customer_service_type='service_fee',
                    vat='nds_20',
                    trust_product_id='service_fee_trust_product_id',
                    place_id='place_1',
                ),
                helpers.make_customer_service(
                    customer_service_id='delivery',
                    name='Delivery-1',
                    cost_for_customer='9',
                    currency='RUB',
                    customer_service_type='delivery',
                    vat='nds_20',
                    trust_product_id='delivery_trust_product_id',
                    place_id='place_1',
                ),
            ],
            # expected_db_item_payment_type
            [
                ('product-1', '815'),
                ('option-1', '0'),
                ('product-2', '437'),
                ('option-2', '29'),
                ('delivery', '8'),
                ('service_fee', '17'),
            ],
            id='Plus for delivery and service_fee is grater then cost',
        ),
        pytest.param(
            # items_with_complement
            [
                models.TestItem(
                    amount='1830.00',
                    by_complement='1827.00',
                    item_id='composition-products',
                    product_id='composition_products_trust_product_id',
                ),
                models.TestItem(
                    amount='9.00',
                    by_complement='8.00',
                    item_id='delivery',
                    product_id='delivery_trust_product_id',
                ),
            ],
            # items_without_complement
            [],
            # item_types_amount
            [
                {'amount': '10', 'item_type': 'delivery'},
                {'amount': '20', 'item_type': 'service_fee'},
            ],
            # additional_customer_services
            [
                helpers.make_customer_service(
                    customer_service_id='delivery',
                    name='Delivery-1',
                    cost_for_customer='9',
                    currency='RUB',
                    customer_service_type='delivery',
                    vat='nds_20',
                    trust_product_id='delivery_trust_product_id',
                    place_id='place_1',
                ),
            ],
            # expected_db_item_payment_type
            [
                ('product-1', '815'),
                ('option-1', '0'),
                ('product-2', '437'),
                ('option-2', '29'),
                ('delivery', '8'),
            ],
            id='Check service_fee if available for plus, but not in items',
        ),
        pytest.param(
            # items_with_complement
            [
                models.TestItem(
                    amount='1830.00',
                    by_complement='1827.00',
                    item_id='composition-products',
                    product_id='composition_products_trust_product_id',
                ),
                models.TestItem(
                    amount='9.00',
                    by_complement='8.00',
                    item_id='delivery',
                    product_id='delivery_trust_product_id',
                ),
            ],
            # items_without_complement
            [
                models.TestItem(
                    amount='18.00',
                    by_complement='0.00',
                    item_id='service_fee',
                    product_id='service_fee_trust_product_id',
                ),
            ],
            # item_types_amount
            [{'amount': '10', 'item_type': 'delivery'}],
            # additional_customer_services
            [
                helpers.make_customer_service(
                    customer_service_id='service_fee',
                    name='Service-Fee-1',
                    cost_for_customer='18',
                    currency='RUB',
                    customer_service_type='service_fee',
                    vat='nds_20',
                    trust_product_id='service_fee_trust_product_id',
                    place_id='place_1',
                ),
                helpers.make_customer_service(
                    customer_service_id='delivery',
                    name='Delivery-1',
                    cost_for_customer='9',
                    currency='RUB',
                    customer_service_type='delivery',
                    vat='nds_20',
                    trust_product_id='delivery_trust_product_id',
                    place_id='place_1',
                ),
            ],
            # expected_db_item_payment_type
            [
                ('product-1', '815'),
                ('option-1', '0'),
                ('product-2', '437'),
                ('option-2', '29'),
                ('delivery', '8'),
                ('service_fee', '0'),
            ],
            id='Check service_fee is not available for plus',
        ),
        pytest.param(
            # items_with_complement
            [
                models.TestItem(
                    amount='1830.00',
                    by_complement='1827.00',
                    item_id='composition-products',
                    product_id='composition_products_trust_product_id',
                ),
                models.TestItem(
                    amount='9.00',
                    by_complement='8.00',
                    item_id='delivery',
                    product_id='delivery_trust_product_id',
                ),
            ],
            # items_without_complement
            [],
            # item_types_amount
            [
                {'amount': '10', 'item_type': 'delivery'},
                {'amount': '1838', 'item_type': 'product'},
            ],
            # additional_customer_services
            [
                helpers.make_customer_service(
                    customer_service_id='delivery',
                    name='Delivery-1',
                    cost_for_customer='9',
                    currency='RUB',
                    customer_service_type='delivery',
                    vat='nds_20',
                    trust_product_id='delivery_trust_product_id',
                    place_id='place_1',
                ),
            ],
            # expected_db_item_payment_type
            [
                ('product-1', '815'),
                ('option-1', '0'),
                ('product-2', '437'),
                ('option-2', '29'),
                ('delivery', '8'),
            ],
            id='Check plus for composition_products items',
        ),
        pytest.param(
            # items_with_complement
            [
                models.TestItem(
                    amount='1830.00',
                    by_complement='1827.00',
                    item_id='composition-products',
                    product_id='composition_products_trust_product_id',
                ),
                models.TestItem(
                    amount='9.00',
                    by_complement='8.00',
                    item_id='delivery',
                    product_id='delivery_trust_product_id',
                ),
            ],
            # items_without_complement
            [],
            # item_types_amount
            [{'amount': '9', 'item_type': 'delivery'}],
            # additional_customer_services
            [
                helpers.make_customer_service(
                    customer_service_id='delivery',
                    name='Delivery-1',
                    cost_for_customer='9',
                    currency='RUB',
                    customer_service_type='delivery',
                    vat='nds_20',
                    trust_product_id='delivery_trust_product_id',
                    place_id='place_1',
                ),
            ],
            # expected_db_item_payment_type
            [
                ('product-1', '815'),
                ('option-1', '0'),
                ('product-2', '437'),
                ('option-2', '29'),
                ('delivery', '8'),
            ],
            id='Plus is equals cost',
        ),
    ],
)
async def test_check_plus_for_delivery_and_service_fee(
        check_create_order_v2,
        assert_db_order,
        assert_db_order_payment,
        assert_db_item_payment_type,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        payment_type,
        service,
        experiments3,
        items_with_complement,
        items_without_complement,
        item_types_amount,
        additional_customer_services,
        expected_db_item_payment_type,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )

    test_items = copy.deepcopy(items_with_complement)
    test_items += items_without_complement

    customer_services = make_product_items()
    customer_services += additional_customer_services

    customer_service_details = make_product_items_with_details()
    customer_service_details += additional_customer_services

    complement = models.Complement(
        amount='1837.00', item_types_amount=item_types_amount, service=service,
    )

    invoice_create_mock = mock_transactions_invoice_create(
        payment_type=payment_type,
        complement_payment=complement,
        billing_service='food_payment',
        service=service,
    )

    transactions_items = helpers.make_transactions_payment_items(
        payment_type=payment_type,
        items=helpers.make_transactions_items(test_items),
    )
    personal_wallet_items = helpers.make_transactions_payment_items(
        payment_type=complement.payment_type,
        items=helpers.make_transactions_items_complement(
            items_with_complement,
        ),
    )

    expected_wallet_payload = helpers.make_wallet_payload(
        cashback_service=('lavka' if service == 'grocery' else 'eda'),
        order_id=consts.TEST_ORDER_ID,
        wallet_id=complement.payment_id,
    )

    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items, personal_wallet_items],
        operation_id='create:abcd',
        version=1,
        wallet_payload=expected_wallet_payload,
    )

    customer_service_details_mock = (
        mock_order_revision_customer_services_details(
            customer_services=customer_service_details,
        )
    )

    save_last_payment_mock = mock_user_state_save_last_payment(
        payment_type=payment_type,
    )

    await check_create_order_v2(
        consts.TEST_ORDER_ID,
        revision='abcd',
        payment_type=payment_type,
        service=service,
        additional_request_part=helpers.to_complement_payload(complement),
    )

    assert_db_order(
        order_id=consts.TEST_ORDER_ID,
        expected_service=service,
        expected_api_version=2,
        expected_complement_payment_type='personal_wallet',
        expected_complement_payment_id='complement-id',
        expected_complement_amount=decimal.Decimal('1837.00'),
    )
    assert_db_order_payment(
        consts.TEST_ORDER_ID,
        consts.TEST_PAYMENT_ID,
        payment_type,
        expected_currency='RUB',
    )

    for product_id, plus in expected_db_item_payment_type:
        assert_db_item_payment_type(
            product_id, consts.TEST_ORDER_ID, 'trust', decimal.Decimal(plus),
        )

    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert customer_service_details_mock.times_called == 1
    assert save_last_payment_mock.times_called == 1


@configs.PERSONAL_WALLET_FIRM_BY_SERVICE
@configs.COMPLEMENT_CONFIG
@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize('payment_type', ['card'])
@pytest.mark.parametrize('service', ['eats'])
@pytest.mark.parametrize(
    'items_with_complement, items_without_complement, '
    'item_types_amount, additional_customer_services, ',
    [
        pytest.param(
            # items_with_complement
            [
                models.TestItem(
                    amount='1',
                    by_complement='61.98',
                    item_id='delivery-1',
                    product_id='delivery_trust_product_id',
                ),
                models.TestItem(
                    amount='1.98',
                    by_complement='37.02',
                    item_id='service_fee',
                    product_id='service_fee_trust_product_id',
                ),
            ],
            [
                models.TestItem(
                    amount='0.00',
                    by_complement='0.00',
                    item_id='composition-products',
                    product_id='composition_products_trust_product_id',
                ),
                models.TestItem(
                    amount='1',
                    by_complement='0.00',
                    item_id='delivery-1',
                    product_id='delivery_trust_product_id',
                ),
                models.TestItem(
                    amount='1.98',
                    by_complement='0.00',
                    item_id='service_fee',
                    product_id='service_fee_trust_product_id',
                ),
            ],
            # item_types_amount
            [
                {'amount': '61.98', 'item_type': 'delivery'},
                {'amount': '37.02', 'item_type': 'service_fee'},
            ],
            # additional_customer_services
            [
                helpers.make_customer_service(
                    customer_service_id='service_fee',
                    name='Service-Fee-1',
                    cost_for_customer='39',
                    currency='RUB',
                    customer_service_type='service_fee',
                    vat='nds_20',
                    trust_product_id='service_fee_trust_product_id',
                    place_id='place_1',
                ),
                helpers.make_customer_service(
                    customer_service_id='delivery-1',
                    name='Delivery-1',
                    cost_for_customer='62.98',
                    currency='RUB',
                    customer_service_type='delivery',
                    vat='nds_20',
                    trust_product_id='delivery_trust_product_id',
                    place_id='place_1',
                ),
            ],
            id='test_devision_on_zero',
        ),
    ],
)
async def test_division_by_zero(
        check_create_order_v2,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        payment_type,
        service,
        experiments3,
        items_with_complement,
        items_without_complement,
        item_types_amount,
        additional_customer_services,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )

    customer_services = [
        helpers.make_customer_service(
            customer_service_id='composition-products',
            name='Продукты заказа',
            cost_for_customer='0',
            currency='RUB',
            customer_service_type='composition_products',
            vat='nds_20',
            trust_product_id='composition_products_trust_product_id',
            place_id='place_1',
        ),
    ]
    customer_services += additional_customer_services

    customer_service_details = [
        helpers.make_customer_service(
            customer_service_id='composition-products',
            name='Продукты заказа',
            cost_for_customer='0',
            currency='RUB',
            customer_service_type='composition_products',
            vat='nds_20',
            trust_product_id='composition_products_trust_product_id',
            place_id='place_1',
            details=helpers.make_customer_service_details(
                composition_products=[
                    helpers.make_composition_product(
                        composition_product_id='product-1',
                        name='Product 1',
                        cost_for_customer='0',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                    helpers.make_composition_product(
                        composition_product_id='option-1',
                        name='Option 1',
                        cost_for_customer='0',
                        composition_product_type='option',
                        vat='nds_20',
                    ),
                ],
            ),
        ),
    ]
    customer_service_details += additional_customer_services

    complement = models.Complement(
        amount='99.00', item_types_amount=item_types_amount, service=service,
    )

    invoice_create_mock = mock_transactions_invoice_create(
        payment_type=payment_type,
        complement_payment=complement,
        billing_service='food_payment',
        service=service,
    )

    transactions_items = helpers.make_transactions_payment_items(
        payment_type=payment_type,
        items=helpers.make_transactions_items(items_without_complement),
    )
    personal_wallet_items = helpers.make_transactions_payment_items(
        payment_type=complement.payment_type,
        items=helpers.make_transactions_items_complement(
            items_with_complement,
        ),
    )

    expected_wallet_payload = helpers.make_wallet_payload(
        cashback_service=('lavka' if service == 'grocery' else 'eda'),
        order_id=consts.TEST_ORDER_ID,
        wallet_id=complement.payment_id,
    )

    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items, personal_wallet_items],
        operation_id='create:abcd',
        version=1,
        wallet_payload=expected_wallet_payload,
    )

    customer_service_details_mock = (
        mock_order_revision_customer_services_details(
            customer_services=customer_service_details,
        )
    )

    save_last_payment_mock = mock_user_state_save_last_payment(
        payment_type=payment_type,
    )

    await check_create_order_v2(
        consts.TEST_ORDER_ID,
        revision='abcd',
        payment_type=payment_type,
        service=service,
        additional_request_part=helpers.to_complement_payload(complement),
    )

    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert customer_service_details_mock.times_called == 1
    assert save_last_payment_mock.times_called == 1
