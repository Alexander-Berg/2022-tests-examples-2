import datetime as dt

import pytest

from tests_eats_payments import configs
from tests_eats_payments import helpers

NOW = '2020-03-31T07:20:00+00:00'


@configs.DEBT_CONFIG
@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.parametrize(
    [
        'debt_enabled',
        'score_request_granted',
        'score_times_called',
        'scoring_status',
    ],
    [(True, True, 1, 200), (True, False, 0, 200), (True, True, 1, 500)],
)
async def test_eats_debt_user_score_request(
        check_create_order,
        experiments3,
        stq,
        mock_eats_debt_user_scoring,
        mockserver,
        mock_user_state_save_last_payment,
        debt_enabled,
        score_request_granted,
        score_times_called,
        scoring_status,
):
    experiments3.add_config(
        **helpers.make_debts_experiment(debt_enabled, score_request_granted),
    )
    items = [
        helpers.make_item(
            item_id='big_mac_1',
            amount='2.21',
            billing_info={
                'place_id': '100500',
                'balance_client_id': '123456',
                'item_type': 'product',
            },
        ),
        helpers.make_item(
            item_id='big_mac_2',
            amount='3.30',
            billing_info={
                'place_id': '100500',
                'balance_client_id': '123456',
                'item_type': 'product',
            },
        ),
    ]

    check_score_request = {
        'amount': '5.51',
        'currency': 'RUB',
        'is_disaster': debt_enabled,
        'order_nr': 'test_order',
        'payment_method': 'card',
        'phone_id': '',
        'service': 'eats',
        'yandex_uid': '100500',
    }

    user_score = mock_eats_debt_user_scoring(
        allow_credit=True,
        check_request=check_score_request,
        status=scoring_status,
    )

    # pylint: disable=unused-variable
    # pylint: disable=invalid-name
    @mockserver.json_handler('/transactions-eda/v2/invoice/create')
    def transactions_create_invoice_handler(request):
        return mockserver.make_response(**{'status': 200, 'json': {}})

    # pylint: disable=unused-variable
    # pylint: disable=invalid-name
    @mockserver.json_handler('/transactions-eda/v2/invoice/update')
    def transactions_update_invoice_handler(request):
        return mockserver.make_response(**{'status': 200, 'json': {}})

    mock_user_state_save_last_payment(payment_type='card')

    await check_create_order(payment_type='card', items=items)
    if scoring_status == 200:
        helpers.check_callback_mock(
            callback_mock=stq.eda_order_processing_payment_events_callback,
            task_id='test_order:debt',
            queue='eda_order_processing_payment_events_callback',
            **{
                'order_id': 'test_order',
                'action': 'debt',
                'status': 'confirmed',
                'revision': 'test_order',
                'meta': [{'discriminator': 'debt_type', 'value': 'disaster'}],
            },
        )
    assert user_score.times_called == score_times_called


@configs.DEBT_CONFIG
@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    [
        'debt_enabled',
        'eats_debt_user_scoring_enabled',
        'auto_debt_enabled',
        'debt_check_invoice_status_times_called',
    ],
    [
        (True, False, False, 0),
        (True, False, True, 0),
        (True, True, False, 0),
        (True, True, True, 0),
        (False, False, False, 0),
        (False, False, True, 1),
        (False, True, False, 0),
        (False, True, True, 1),
    ],
)
async def test_eats_auto_debt(
        check_create_order,
        experiments3,
        stq,
        mock_eats_debt_user_scoring,
        mockserver,
        mock_user_state_save_last_payment,
        debt_enabled,
        eats_debt_user_scoring_enabled,
        auto_debt_enabled,
        debt_check_invoice_status_times_called,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    delay = 1000
    experiments3.add_config(
        **helpers.make_debts_experiment(
            debt_enabled,
            eats_debt_user_scoring_enabled,
            auto_debt_enabled,
            delay,
        ),
    )

    # pylint: disable=unused-variable
    # pylint: disable=invalid-name
    @mockserver.json_handler('/transactions-eda/v2/invoice/create')
    def transactions_create_invoice_handler(request):
        return mockserver.make_response(**{'status': 200, 'json': {}})

    # pylint: disable=unused-variable
    # pylint: disable=invalid-name
    @mockserver.json_handler('/transactions-eda/v2/invoice/update')
    def transactions_update_invoice_handler(request):
        return mockserver.make_response(**{'status': 200, 'json': {}})

    mock_user_state_save_last_payment(payment_type='card')

    items = [
        helpers.make_item(item_id='big_mac_1', amount='2.21'),
        helpers.make_item(item_id='big_mac_2', amount='3.30'),
    ]
    check_score_request = {
        'amount': '5.51',
        'currency': 'RUB',
        'is_disaster': debt_enabled,
        'order_nr': 'test_order',
        'payment_method': 'card',
        'phone_id': '',
        'service': 'eats',
        'yandex_uid': '100500',
    }

    mock_eats_debt_user_scoring(
        allow_credit=True, check_request=check_score_request,
    )
    await check_create_order(payment_type='card', items=items)
    helpers.check_callback_mock(
        times_called=debt_check_invoice_status_times_called,
        callback_mock=stq.eats_payments_debt_check_invoice_status,
        task_id='test_order',
        queue='eats_payments_debt_check_invoice_status',
        eta=dt.datetime.fromisoformat('2020-03-31T07:20:01+00:00').replace(
            tzinfo=None,
        ),
        **{'invoice_id': 'test_order', 'ttl': '2020-03-31T07:20:05+00:00'},
    )
