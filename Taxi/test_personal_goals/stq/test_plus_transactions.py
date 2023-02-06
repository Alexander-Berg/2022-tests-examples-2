import pytest

from generated.models import cashback as cashback_models

from personal_goals.modules.cashback import models
from personal_goals.modules.cashback import plus_transactions

BILLING_INFO = {
    'billing_service': 'card',
    'billing_service_id': '124',
    'cashback_service': 'yataxi',
    'cashback_type': 'transaction',
    'issuer': 'taxi',
    'campaign_name': 'personal_goals_taxi',
    'product_id': 'personal_goals_cashback_bonus',
    'ticket': 'NEWSERVICE-000',
}


async def test_cashback_status(stq3_context, plus_transactions_fixt):
    resp = await plus_transactions.cashback_status(
        context=stq3_context, invoice_id='ext_ref_id_1',
    )
    assert resp.status == 'init'
    assert resp.amount == '0'
    assert resp.version == 1
    assert resp.operations == []


@pytest.mark.parametrize('race_condition', [True, False])
async def test_update_cashback(
        stq3_context, plus_transactions_fixt, race_condition,
):
    if race_condition:
        plus_transactions_fixt.update_cashback_exception = (
            plus_transactions.UpdateCashbackRaceCondition
        )

    update_cashback_args = {
        'context': stq3_context,
        'invoice_id': 'ext_ref_id_1',
        'yandex_uid': 'yandex_uid_1',
        'currency': 'RUB',
        'version': 1,
        'amount': '100',
        'billing_info': BILLING_INFO,
        'has_plus': True,
        'base_payload': cashback_models.TaxiOrderPayload(
            alias_id='alias_id',
            base_amount='356.0',
            country='RU',
            currency='RUB',
            oebs_mvp_id='MSKc',
            order_id='order_id_1',
            tariff_class='econom',
        ),
    }

    if race_condition:
        with pytest.raises(plus_transactions.UpdateCashbackRaceCondition):
            await plus_transactions.update_cashback(**update_cashback_args)
    else:
        await plus_transactions.update_cashback(**update_cashback_args)


@pytest.mark.parametrize(
    'cashback_status, expected_result',
    [
        ('in_progress', models.RewardStatus(is_done=False)),
        ('success', models.RewardStatus(is_done=True)),
        ('failed', plus_transactions.UpdateCashbackFailure),
        ('init', ValueError),
    ],
)
def test_process_cashback_status(
        stq3_context, cashback_status, expected_result,
):
    status = models.InvoiceCashbackStatus(cashback_status)
    if expected_result in (
            plus_transactions.UpdateCashbackFailure,
            ValueError,
    ):
        with pytest.raises(expected_result):
            plus_transactions.process_cashback_status(status)
    else:
        result = plus_transactions.process_cashback_status(status)
        assert result == expected_result
