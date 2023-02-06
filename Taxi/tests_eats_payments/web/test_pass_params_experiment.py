import typing

import pytest

from tests_eats_payments import configs
from tests_eats_payments import consts
from tests_eats_payments import helpers

DEFAULT_PASS_PARAMS = {
    'terminal_route_data': {
        'merchant': 'default',
        'business': 'default',
        'force_3ds': False,
        '3ds_supported': False,
    },
}


NOW = '2020-08-12T07:20:00+00:00'


@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'service,'
    'additional_request_part,'
    'pass_params,'
    'terminal_params_enabled',
    (
        pytest.param(
            'eats',
            {'business': {'type': 'restaurant', 'specification': []}},
            {
                'terminal_route_data': {
                    'merchant': 'eda',
                    'business': 'restaurant',
                    'force_3ds': False,
                    '3ds_supported': False,
                },
            },
            True,
            id='Test eats/restaurant matched experiment with true result',
        ),
        pytest.param(
            'eats',
            {'business': {'type': 'lavka', 'specification': []}},
            DEFAULT_PASS_PARAMS,
            True,
            id='Test eats/lavka not matched experiment',
        ),
        pytest.param(
            'eats',
            {'business': {'type': 'restaurant', 'specification': []}},
            DEFAULT_PASS_PARAMS,
            False,
            id='Test eats/restaurant matched experiment with false result',
        ),
    ),
)
async def test_create_order(
        check_create_order,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        service,
        additional_request_part,
        pass_params,
        terminal_params_enabled,
        experiments3,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_experiment(
        **helpers.make_terminal_pass_params_experiment2(
            terminal_params_enabled,
        ),
    )

    invoice_create_mock = mock_transactions_invoice_create(
        payment_type=consts.CARD_PAYMENT_TYPE,
        billing_service='food_payment',
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
        items=[transactions_items], operation_id='create:abcd', version=1,
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
    )
    assert invoice_create_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
    assert save_last_payment_mock.times_called == 1
