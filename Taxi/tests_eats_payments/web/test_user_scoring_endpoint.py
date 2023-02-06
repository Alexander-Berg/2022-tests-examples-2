import pytest

from tests_eats_payments import configs
from tests_eats_payments import helpers
from tests_eats_payments import models

NOW = '2020-08-12T07:20:00+00:00'


@configs.DEBT_CONFIG
@pytest.mark.tvm2_eats_corp_orders
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'eats_debt_user_scoring_enabled, user_scoring_verdict_enabled, '
    'user_scoring_times_called, user_verdict_times_called',
    [
        pytest.param(False, False, 0, 0, id='Disabled by experiment'),
        pytest.param(True, True, 0, 1, id='All enabled'),
        pytest.param(
            True, False, 1, 0, id='User scoring enabled, verdict disabled',
        ),
        pytest.param(
            False, True, 0, 1, id='User scoring disables, verdict enabled',
        ),
    ],
)
async def test_user_scoring_endpoint_v1(
        check_create_order,
        mock_transactions_invoice_create,
        mock_transactions_invoice_update,
        mock_user_state_save_last_payment,
        mock_eats_debt_user_scoring,
        mock_eats_debt_user_scoring_verdict,
        experiments3,
        eats_debt_user_scoring_enabled,
        user_scoring_verdict_enabled,
        user_scoring_times_called,
        user_verdict_times_called,
):
    experiments3.add_config(
        **helpers.make_debts_experiment(
            debt_enabled=False,
            auto_debt_enabled=True,
            eats_debt_user_scoring_enabled=eats_debt_user_scoring_enabled,
            request_to_user_scoring_verdict_enabled=(
                user_scoring_verdict_enabled
            ),
        ),
    )

    mock_transactions_invoice_create(payment_type='card')

    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card',
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
            helpers.make_transactions_item(
                item_id='service_fee', amount='9.00',
            ),
        ],
    )

    mock_transactions_invoice_update(
        items=[transactions_items], operation_id='create:abcd', version=1,
    )

    mock_user_state_save_last_payment(payment_type='card')

    items = [
        helpers.make_item(item_id='big_mac', amount='2.00'),
        helpers.make_item(
            item_id='service_fee',
            item_type=models.ItemType.service_fee,
            amount='9.00',
        ),
    ]

    debt_user_scoring = mock_eats_debt_user_scoring(allow_credit=True)
    debt_user_verdict = mock_eats_debt_user_scoring_verdict(verdict='accept')
    await check_create_order(
        payment_type='card',
        items=items,
        additional_request_part={
            'business': {'type': 'zapravki', 'specification': []},
        },
    )

    assert debt_user_scoring.times_called == user_scoring_times_called
    assert debt_user_verdict.times_called == user_verdict_times_called
