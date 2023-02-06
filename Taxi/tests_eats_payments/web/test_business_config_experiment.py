import pytest

from tests_eats_payments import consts
from tests_eats_payments import helpers


NOW = '2020-08-12T07:20:00+00:00'


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'service,'
    'billing_service,'
    'additional_request_part,'
    'pass_params,'
    'response_status,'
    'payment_timeout, ',
    (
        pytest.param(
            'eats',
            'food_payment',
            {'business': {'type': 'restaurant', 'specification': []}},
            {
                'terminal_route_data': {
                    'merchant': 'eda',
                    'business': 'restaurant',
                    'force_3ds': False,
                    '3ds_supported': False,
                },
            },
            200,
            None,
            id='Test eats/restaurant',
        ),
        pytest.param(
            'eats',
            'food_payment',
            {'business': {'type': 'shop', 'specification': []}},
            {
                'terminal_route_data': {
                    'merchant': 'eda',
                    'business': 'retail',
                    'force_3ds': False,
                    '3ds_supported': False,
                },
            },
            200,
            None,
            id='Test eats/shop',
        ),
        pytest.param(
            'eats',
            'food_payment',
            {'business': {'type': 'store', 'specification': []}},
            {
                'terminal_route_data': {
                    'merchant': 'eda',
                    'business': 'retail',
                    'force_3ds': False,
                    '3ds_supported': False,
                },
            },
            200,
            None,
            id='Test eats/store',
        ),
        pytest.param(
            'eats',
            'food_payment_test',
            {'business': {'type': 'test', 'specification': []}},
            {
                'terminal_route_data': {
                    'merchant': 'eda',
                    'business': 'retail',
                    'force_3ds': False,
                    '3ds_supported': False,
                },
            },
            200,
            None,
            id='Test not default billing service',
        ),
        pytest.param(
            'eats',
            'food_payment',
            {'business': {'type': 'store2', 'specification': []}},
            {
                'terminal_route_data': {
                    'merchant': 'eda',
                    'business': 'retail',
                    'force_3ds': False,
                    '3ds_supported': False,
                },
            },
            400,
            None,
            id='Test unknown business',
        ),
        pytest.param(
            'eats',
            'food_payment',
            {},
            {},
            200,
            None,
            id='Test create without business in request',
        ),
        pytest.param(
            'eats',
            'food_payment',
            {'business': {'type': 'zapravki', 'specification': []}},
            {},
            200,
            None,
            id='Test eats/zapravki',
        ),
    ),
)
async def test_create_order_with_business_config_experiment(
        check_create_order,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        service,
        billing_service,
        additional_request_part,
        pass_params,
        response_status,
        payment_timeout,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment(True),
    )
    experiments3.add_config(**helpers.make_business_experiment())

    invoice_create_mock = mock_transactions_invoice_create(
        payment_type=consts.CARD_PAYMENT_TYPE,
        billing_service=billing_service,
        service=service,
        pass_params=pass_params,
    )

    transactions_items = helpers.make_transactions_payment_items(
        payment_type=consts.CARD_PAYMENT_TYPE,
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )

    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items],
        operation_id='create:abcd',
        version=1,
        payment_timeout=payment_timeout,
    )
    save_last_payment_mock = mock_user_state_save_last_payment(
        payment_type=consts.CARD_PAYMENT_TYPE,
    )
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]

    await check_create_order(
        payment_type=consts.CARD_PAYMENT_TYPE,
        items=items,
        service=service,
        additional_request_part=additional_request_part,
        response_status=response_status,
    )
    if response_status == 200:
        assert invoice_create_mock.times_called == 1
        assert invoice_update_mock.times_called == 1
        assert save_last_payment_mock.times_called == 1
