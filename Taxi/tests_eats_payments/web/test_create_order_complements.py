import decimal
import typing

import pytest

from tests_eats_payments import configs
from tests_eats_payments import consts
from tests_eats_payments import db_order
from tests_eats_payments import helpers
from tests_eats_payments import models

NOW = '2020-08-12T07:20:00+00:00'

TEST_PAYMENT_TYPE = 'card'
CURRENCY = 'RUB'

UNIFORM_DISCOUNT_RULES_DEFAULT = pytest.mark.experiments3(
    name='eats_payments_uniform_discount_rules',
    consumers=['eats-payments/uniform-discount'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'min_item_price': '1',
                'min_total_amount': '1',
                'precision': 0,
            },
        },
    ],
    is_config=True,
)


UNIFORM_DISCOUNT_RULES_SPECIAL = pytest.mark.experiments3(
    name='eats_payments_uniform_discount_rules',
    consumers=['eats-payments/uniform-discount'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {
                'min_item_price': '10',
                'min_total_amount': '15',
                'precision': 1,
            },
        },
    ],
    is_config=True,
)


GROCERY_EAYS_CASHBACK_SERVICE_ID = pytest.mark.parametrize(
    'service_id',
    [
        pytest.param(
            consts.GROCERY_CASHBACK_SERVICE_ID,
            marks=pytest.mark.config(
                EATS_BILLING_PROCESSOR_LAVKA_FEATURES={
                    'lavka_cashback_service_id_enabled': True,
                },
            ),
        ),
        pytest.param(
            consts.EATS_CASHBACK_SERVICE_ID,
            marks=pytest.mark.config(EATS_BILLING_PROCESSOR_LAVKA_FEATURES={}),
        ),
    ],
)


@UNIFORM_DISCOUNT_RULES_DEFAULT
@configs.PERSONAL_WALLET_FIRM_BY_SERVICE
@configs.CASHBACK_CONFIG
@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'request_items, complement_amount_to_pay, cashback_service',
    [
        # pytest.param(
        #     [
        #         {'amount': '100.00', 'by_complement': '17.00'},
        #         {'amount': '200.00', 'by_complement': '33.00'},
        #         {
        #             'price': '300.00',
        #             'quantity': '1.000',
        #             'by_complement': '50.00',
        #         },
        #     ],
        #     '100.00',
        #     'eats',
        #     id='Test with items with price&quantity + amount',
        # ),
        # pytest.param(
        #     [
        #         {'amount': '100.00', 'by_complement': '1.00'},
        #         {'amount': '200.00'},
        #         {'amount': '100.00'},
        #     ],
        #     '1.00',
        #     'grocery',
        #     id='Split 1 amount of cashback',
        # ),
        # (
        #     [
        #         {'amount': '10.00', 'by_complement': '2.00'},
        #         {'amount': '20.00', 'by_complement': '3.00'},
        #         {'amount': '30.00', 'by_complement': '5.00'},
        #     ],
        #     '10.00',
        #     'eats',
        # ),
        # (
        #     [
        #         {'amount': '100.00', 'by_complement': '22.00'},
        #         {'amount': '200.00', 'by_complement': '42.00'},
        #         {'amount': '30.00', 'by_complement': '6.00'},
        #     ],
        #     '70.00',
        #     'grocery',
        # ),
        # pytest.param(
        #     [
        #         {'amount': '100.00', 'by_complement': '1.00'},
        #         {'amount': '200.00', 'by_complement': '1.00'},
        #         {'amount': '300.00', 'by_complement': '1.00'},
        #     ],
        #     '3.00',
        #     'eats',
        #     id='Equal split for small cashback',
        # ),
        # pytest.param(
        #     [
        #         {'amount': '1.00'},
        #         {'amount': '2.00', 'by_complement': '1.00'},
        #         {'amount': '3.00', 'by_complement': '2.00'},
        #     ],
        #     '3.00',
        #     'grocery',
        #     id='Test min_item_price, no cashback for 1 item',
        # ),
        # pytest.param(
        #     [
        #         {'amount': '1.01', 'by_complement': '0.01'},
        #         {'amount': '2.00', 'by_complement': '1.00'},
        #         {'amount': '3.00', 'by_complement': '1.99'},
        #     ],
        #     '3.00',
        #     'eats',
        #     id='Test min_item_price, small prices',
        # ),
        # (
        #     [
        #         {'amount': '10.34', 'by_complement': '5.00'},
        #         {'amount': '20.99', 'by_complement': '7.00'},
        #         {'amount': '32.32', 'by_complement': '12.00'},
        #     ],
        #     '24.00',
        #     'grocery',
        # ),
        # (
        #     [
        #         {'amount': '10.00', 'by_complement': '9.00'},
        #         {'amount': '20.00', 'by_complement': '19.00'},
        #         {'amount': '30.00', 'by_complement': '29.00'},
        #     ],
        #     '57.00',
        #     'eats',
        # ),
        # (
        #     [
        #         {'amount': '151.00', 'by_complement': '150.00'},
        #         {'amount': '51.00', 'by_complement': '50.00'},
        #         {'amount': '136.00', 'by_complement': '135.00'},
        #     ],
        #     '335.00',
        #     'grocery',
        # ),
        # pytest.param(
        #     [
        #         {'amount': '270.00', 'by_complement': '3.00'},
        #         {'amount': '290.00', 'by_complement': '2.00'},
        #         {'amount': '420.00', 'by_complement': '2.00'},
        #         {'amount': '430.00', 'by_complement': '3.00'},
        #         {'amount': '0.00'},
        #     ],
        #     '10.00',
        #     'eats',
        #     id='Item with zero amount',
        # ),
        # TODO FIX IT
        pytest.param(
            [
                {'amount': '10.00', 'by_complement': '9.00'},
                {
                    'amount': '2.00',
                    'by_complement': '2.00',
                    'item_type': models.ItemType.option,
                },
            ],
            '11.00',
            'eats',
            id='No min price for option',
        ),
    ],
)
async def test_card_like_payment_methods_with_complement(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        request_items,
        complement_amount_to_pay,
        cashback_service,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )
    sum_complement = decimal.Decimal(0)
    for item in request_items:
        if 'by_complement' not in item:
            continue

        if 'amount' in item:
            sum_complement += decimal.Decimal(item['by_complement'])
        else:
            sum_complement += decimal.Decimal(
                item['by_complement'],
            ) * decimal.Decimal(item['quantity'])

    # Проверяем, что размазанный кэшбэк в сумме дает ровно то, что хотел
    # пользователь.
    assert sum_complement == decimal.Decimal(
        complement_amount_to_pay,
    ), 'Discount amount not equal of items discount'

    complement_payment = models.Complement(
        amount=complement_amount_to_pay, service=cashback_service,
    )

    invoice_create_mock = mock_transactions_invoice_create(
        complement_payment=complement_payment, service=cashback_service,
    )

    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card',
        items=_format_transactions_items(request_items, use_only_amount=True),
    )
    transactions_items_complement = helpers.make_transactions_payment_items(
        payment_type='personal_wallet',
        items=_format_items_complement(request_items, use_only_amount=True),
    )

    expected_wallet_payload = helpers.make_wallet_payload(
        cashback_service=helpers.map_service_to_wallet_service(
            cashback_service,
        ),
        order_id=consts.TEST_ORDER_ID,
        wallet_id=complement_payment.payment_id,
    )

    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items, transactions_items_complement],
        operation_id='create:abcd',
        version=1,
        wallet_payload=expected_wallet_payload,
    )

    mock_user_state_save_last_payment()

    items = _format_items(request_items, is_request=True, use_only_amount=True)

    await check_create_order(
        TEST_PAYMENT_TYPE,
        items=items,
        service=cashback_service,
        additional_request_part=helpers.to_complement_payload(
            complement_payment,
        ),
    )
    assert_db_order_payment(
        consts.TEST_ORDER_ID, consts.TEST_PAYMENT_ID, TEST_PAYMENT_TYPE,
    )
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1


@UNIFORM_DISCOUNT_RULES_DEFAULT
@configs.PERSONAL_WALLET_FIRM_BY_SERVICE
@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'request_items, complement_amount_to_pay, cashback_service',
    [
        pytest.param(
            [
                {'amount': '100.00', 'by_complement': '19.00'},
                {'amount': '200.00', 'by_complement': '33.00'},
                {
                    'price': '300.00',
                    'quantity': '1.000',
                    'by_complement': '48.00',
                },
            ],
            '100.00',
            'eats',
            id='Test with items with price&quantity + amount',
        ),
    ],
)
async def test_complement_is_disable_by_originator(
        check_create_order,
        mock_user_state_save_last_payment,
        request_items,
        complement_amount_to_pay,
        cashback_service,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )
    sum_complement = decimal.Decimal(0)
    for item in request_items:
        if 'by_complement' not in item:
            continue

        if 'amount' in item:
            sum_complement += decimal.Decimal(item['by_complement'])
        else:
            sum_complement += decimal.Decimal(
                item['by_complement'],
            ) * decimal.Decimal(item['quantity'])

    # Проверяем, что размазанный кэшбэк в сумме дает ровно то, что хотел
    # пользователь.
    assert sum_complement == decimal.Decimal(
        complement_amount_to_pay,
    ), 'Discount amount not equal of items discount'

    complement_payment = models.Complement(
        amount=complement_amount_to_pay, service=cashback_service,
    )

    mock_user_state_save_last_payment()

    items = _format_items(request_items, is_request=True)

    await check_create_order(
        TEST_PAYMENT_TYPE,
        items=items,
        additional_request_part=helpers.to_complement_payload(
            complement_payment,
        ),
        service=cashback_service,
        response_status=400,
    )


@configs.PERSONAL_WALLET_FIRM_BY_SERVICE
@configs.CASHBACK_CONFIG
@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.parametrize(
    'test_items, complement_to_pay',
    [
        pytest.param(
            [
                models.TestItem(amount='100.00', by_complement='50.00'),
                models.TestItem(amount='100.00', by_complement='50.00'),
                models.TestItem(
                    amount='99.00', item_type=models.ItemType.delivery,
                ),
            ],
            '100.00',
            id='Test ignore delivery item in splitting',
        ),
        pytest.param(
            [
                models.TestItem(amount='51.00', by_complement='50.00'),
                models.TestItem(amount='151.00', by_complement='150.00'),
                models.TestItem(amount='136.00', by_complement='135.00'),
                models.TestItem(
                    amount='0.00', item_type=models.ItemType.delivery,
                ),
            ],
            '335.00',
            id='Test zero delivery item in splitting',
        ),
    ],
)
@pytest.mark.now(NOW)
async def test_create_with_non_product_items(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        test_items,
        complement_to_pay,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    complement_payment = models.Complement(amount=complement_to_pay)

    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )

    invoice_create_mock = mock_transactions_invoice_create(
        complement_payment=complement_payment,
    )

    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card', items=helpers.make_transactions_items(test_items),
    )
    transactions_items_complement = helpers.make_transactions_payment_items(
        payment_type='personal_wallet',
        items=helpers.make_transactions_items_complement(test_items),
    )

    expected_wallet_payload = helpers.make_wallet_payload(
        cashback_service='eda',
        order_id=consts.TEST_ORDER_ID,
        wallet_id=complement_payment.payment_id,
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items, transactions_items_complement],
        operation_id='create:abcd',
        version=1,
        wallet_payload=expected_wallet_payload,
    )

    mock_user_state_save_last_payment()

    await check_create_order(
        TEST_PAYMENT_TYPE,
        items=helpers.make_request_items(test_items),
        additional_request_part=helpers.to_complement_payload(
            complement_payment,
        ),
    )
    assert_db_order_payment(
        consts.TEST_ORDER_ID, consts.TEST_PAYMENT_ID, TEST_PAYMENT_TYPE,
    )
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1


@configs.PERSONAL_WALLET_FIRM_BY_SERVICE
@configs.CASHBACK_CONFIG
@pytest.mark.tvm2_eats_corp_orders
@GROCERY_EAYS_CASHBACK_SERVICE_ID
@pytest.mark.parametrize(
    'test_items, complement_to_pay',
    [
        pytest.param(
            [
                models.TestItem(amount='100.00', by_complement='50.00'),
                models.TestItem(amount='100.00', by_complement='50.00'),
            ],
            '100.00',
        ),
    ],
)
@pytest.mark.now(NOW)
async def test_grocery_cashback_service_id(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        test_items,
        complement_to_pay,
        service_id,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    service = 'grocery'

    complement_payment = models.Complement(
        amount=complement_to_pay, service=service,
    )

    mock_transactions_invoice_create(
        complement_payment=complement_payment, service=service,
    )

    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card', items=helpers.make_transactions_items(test_items),
    )
    transactions_items_complement = helpers.make_transactions_payment_items(
        payment_type='personal_wallet',
        items=helpers.make_transactions_items_complement(test_items),
    )

    expected_wallet_payload = helpers.make_wallet_payload(
        cashback_service='lavka',
        order_id=consts.TEST_ORDER_ID,
        wallet_id=complement_payment.payment_id,
        service_id=service_id,
    )
    mock_transactions_invoice_update(
        items=[transactions_items, transactions_items_complement],
        operation_id='create:abcd',
        version=1,
        wallet_payload=expected_wallet_payload,
    )

    mock_user_state_save_last_payment()

    await check_create_order(
        TEST_PAYMENT_TYPE,
        items=helpers.make_request_items(test_items),
        additional_request_part=helpers.to_complement_payload(
            complement_payment,
        ),
        service=service,
    )


@UNIFORM_DISCOUNT_RULES_DEFAULT
@configs.PERSONAL_WALLET_FIRM_BY_SERVICE
@configs.CASHBACK_CONFIG
@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'request_items, complement_amount_to_pay',
    [
        # pytest.param(
        #     [{'amount': '1.00'}, {'amount': '2.00'}, {'amount': '3.00'}],
        #     '100.00000',
        #     id='Too much cashback error',
        # ),
        pytest.param(
            [
                {'price': '10.00', 'quantity': '2'},
                {'price': '10.00', 'quantity': '2'},
                {'price': '10.00', 'quantity': '2'},
            ],
            '40.00000',
            id='Unavailable to split because not `1` quantity',
        ),
        pytest.param(
            [{'price': '10.00'}], '40.00000', id='Only price without quantity',
        ),
        pytest.param(
            [{'quantity': '10.00'}],
            '40.00000',
            id='Only quantity without price',
        ),
    ],
)
async def test_unable_to_split(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        request_items,
        complement_amount_to_pay,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    complement_payment = models.Complement(amount=complement_amount_to_pay)
    items = _format_items(request_items, is_request=True)

    await check_create_order(
        TEST_PAYMENT_TYPE,
        items=items,
        additional_request_part=helpers.to_complement_payload(
            complement_payment,
        ),
        response_status=400,
    )
    assert_db_order_payment(consts.TEST_ORDER_ID, expect_no_payment=True)


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
async def test_no_complement_payment_id(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    await check_create_order(
        TEST_PAYMENT_TYPE,
        items=[],
        additional_request_part={
            'complements': [
                {
                    'payment_method': {'type': 'personal_wallet'},
                    'amount': '40.00000',
                },
            ],
        },
        response_status=400,
    )
    assert_db_order_payment(consts.TEST_ORDER_ID, expect_no_payment=True)


@configs.CASHBACK_CONFIG
@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'request_items, complement_amount_to_pay',
    [
        (
            [{'amount': '1.00'}, {'amount': '2.00'}, {'amount': '3.00'}],
            '1.00000',
        ),
    ],
)
@pytest.mark.parametrize('payment_type', ['card', 'applepay', 'googlepay'])
async def test_not_personal_wallet(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        request_items,
        complement_amount_to_pay,
        payment_type,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    assert payment_type != 'personal_wallet'

    complement_payment = models.Complement(
        amount=complement_amount_to_pay, payment_type=payment_type,
    )
    items = _format_items(request_items, is_request=True)

    await check_create_order(
        payment_type='card',
        items=items,
        additional_request_part=helpers.to_complement_payload(
            complement_payment,
        ),
        response_status=400,
    )
    assert_db_order_payment(consts.TEST_ORDER_ID, expect_no_payment=True)


@UNIFORM_DISCOUNT_RULES_SPECIAL
@configs.PERSONAL_WALLET_FIRM_BY_SERVICE
@configs.CASHBACK_CONFIG
@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'request_items, complement_amount_to_pay, expected_code',
    [
        pytest.param(
            [
                {'amount': '100.00', 'by_complement': '9.50'},
                {'amount': '200.00', 'by_complement': '19.00'},
                {'amount': '300.00', 'by_complement': '28.50'},
            ],
            '57.00000',
            200,
            id='Split with precision == 1',
        ),
        pytest.param(
            [
                {'amount': '10.00'},
                {'amount': '30.00', 'by_complement': '20.00'},
                {'amount': '40.00', 'by_complement': '20.00'},
            ],
            '40.00000',
            200,
            id='Split with min_item_price == 10',
        ),
        pytest.param(
            [{'amount': '1.00'}, {'amount': '21.00'}],
            '10.00000',
            400,
            id='Unable to split because min_total_amount is too big',
        ),
    ],
)
async def test_experiment_uniform_discounts(
        check_create_order,
        assert_db_order_payment,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        request_items,
        complement_amount_to_pay,
        expected_code,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )

    sum_complement = decimal.Decimal(0)
    for item in request_items:
        if 'by_complement' not in item:
            continue

        if 'amount' in item:
            sum_complement += decimal.Decimal(item['by_complement'])
        else:
            sum_complement += decimal.Decimal(
                item['by_complement'],
            ) * decimal.Decimal(item['quantity'])

    # Проверяем, что размазанный кэшбэк в сумме дает ровно то, что хотел
    # пользователь.
    diff = sum_complement - decimal.Decimal(complement_amount_to_pay)
    if expected_code == 200:
        assert diff == decimal.Decimal(0)

    complement_payment = models.Complement(amount=complement_amount_to_pay)

    invoice_create_mock = mock_transactions_invoice_create(
        complement_payment=complement_payment,
    )

    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card', items=_format_transactions_items(request_items),
    )
    transactions_items_complement = helpers.make_transactions_payment_items(
        payment_type='personal_wallet',
        items=_format_items_complement(request_items),
    )

    expected_wallet_payload = helpers.make_wallet_payload(
        cashback_service='eda',
        order_id=consts.TEST_ORDER_ID,
        wallet_id=complement_payment.payment_id,
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items, transactions_items_complement],
        operation_id='create:abcd',
        version=1,
        wallet_payload=expected_wallet_payload,
    )

    mock_user_state_save_last_payment()

    items = _format_items(request_items, is_request=True)

    await check_create_order(
        TEST_PAYMENT_TYPE,
        items=items,
        additional_request_part=helpers.to_complement_payload(
            complement_payment,
        ),
        response_status=expected_code,
    )
    if expected_code == 200:
        assert_db_order_payment(
            consts.TEST_ORDER_ID, consts.TEST_PAYMENT_ID, TEST_PAYMENT_TYPE,
        )
        assert invoice_create_mock.times_called == 1
        assert invoice_update_mock.times_called == 1
    else:
        assert_db_order_payment(consts.TEST_ORDER_ID, expect_no_payment=True)


@configs.PERSONAL_WALLET_FIRM_BY_SERVICE
@configs.CASHBACK_CONFIG
@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize('service', ['eats', 'grocery'])
async def test_db(
        check_create_order,
        assert_db_order_payment,
        mock_transactions,
        mock_user_state_save_last_payment,
        pgsql,
        service,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(False),
    )

    complement_amount_to_pay = decimal.Decimal('123.45')

    complement_payment = models.Complement(
        amount=str(complement_amount_to_pay), service=service,
    )

    request_items = [{'amount': '100.00'}, {'amount': '200.00'}]
    items = _format_items(request_items, is_request=True)

    mock_user_state_save_last_payment()

    await check_create_order(
        TEST_PAYMENT_TYPE,
        items=items,
        additional_request_part=helpers.to_complement_payload(
            complement_payment,
        ),
        service=service,
    )

    order = db_order.DBOrder.fetch(pgsql=pgsql, order_id=consts.TEST_ORDER_ID)

    expected_order = db_order.DBOrder(
        pgsql=pgsql,
        order_id=consts.TEST_ORDER_ID,
        service=service,
        currency=CURRENCY,
        originator=consts.CORP_ORDER_ORIGINATOR,
        complement_amount=complement_amount_to_pay,
        complement_payment_type=complement_payment.payment_type,
        complement_payment_id=complement_payment.payment_id,
    )
    assert order == expected_order
    assert_db_order_payment(
        consts.TEST_ORDER_ID, consts.TEST_PAYMENT_ID, TEST_PAYMENT_TYPE,
    )


def _get_item_id(idx):
    return f'item_id_{idx}'


def _format_items(
        request_items, is_request=False, use_only_amount=False,
) -> typing.List[dict]:
    result = []

    def _subtract_complement(item, key):
        if is_request:
            return item.get(key, None)
        value = decimal.Decimal(item[key])
        if 'by_complement' not in item:
            return str(value)
        value -= decimal.Decimal(item['by_complement'])
        return str(value)

    for idx, item in enumerate(request_items):
        if 'amount' in item:
            amount = _subtract_complement(item, 'amount')
            result.append(
                helpers.make_item(
                    item_id=_get_item_id(idx),
                    amount=amount,
                    item_type=item.get('item_type', models.ItemType.product),
                ),
            )
        else:
            price = _subtract_complement(item, 'price')
            if use_only_amount:
                result.append(
                    helpers.make_item(
                        item_id=_get_item_id(idx),
                        amount=price,
                        item_type=item.get(
                            'item_type', models.ItemType.product,
                        ),
                    ),
                )
            else:
                result.append(
                    helpers.make_item(
                        item_id=_get_item_id(idx),
                        price=price,
                        quantity=item.get('quantity', None),
                        item_type=item.get(
                            'item_type', models.ItemType.product,
                        ),
                    ),
                )
    return result


def _format_transactions_items(
        request_items, is_request=False, use_only_amount=False,
) -> typing.List[dict]:
    result = []

    def _subtract_complement(item, key):
        if is_request:
            return item.get(key, None)
        value = decimal.Decimal(item[key])
        if 'by_complement' not in item:
            return str(value)
        value -= decimal.Decimal(item['by_complement'])
        return str(value)

    for idx, item in enumerate(request_items):
        if 'amount' in item:
            amount = _subtract_complement(item, 'amount')
            result.append(
                helpers.make_transactions_item(
                    item_id=_get_item_id(idx), amount=amount,
                ),
            )
        else:
            price = _subtract_complement(item, 'price')
            if use_only_amount:
                result.append(
                    helpers.make_transactions_item(
                        item_id=_get_item_id(idx), amount=price,
                    ),
                )
            else:
                result.append(
                    helpers.make_transactions_item(
                        item_id=_get_item_id(idx),
                        price=price,
                        quantity=item.get('quantity', None),
                    ),
                )
    return result


def _format_items_complement(request_items, use_only_amount=False):
    result = []
    for idx, item in enumerate(request_items):
        if 'by_complement' not in item:
            continue

        if 'amount' in item:
            result.append(
                helpers.make_transactions_item(
                    item_id=_get_item_id(idx), amount=item['by_complement'],
                ),
            )
        else:
            if use_only_amount:
                result.append(
                    helpers.make_transactions_item(
                        item_id=_get_item_id(idx),
                        amount=item['by_complement'],
                    ),
                )
            else:
                result.append(
                    helpers.make_transactions_item(
                        item_id=_get_item_id(idx),
                        price=item['by_complement'],
                        quantity=item['quantity'],
                    ),
                )
    return result
