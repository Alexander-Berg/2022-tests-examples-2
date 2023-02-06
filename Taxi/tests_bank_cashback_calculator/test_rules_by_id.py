import pytest


@pytest.mark.config(BANK_CASHBACK_CALCULATOR_RULES={})
async def test_rule_not_found(taxi_bank_cashback_calculator):
    response = await taxi_bank_cashback_calculator.post(
        'cashback-calculator-support/v1/get_rule_by_id',
        json={'rule_id': 'rule_id_1'},
    )
    assert response.status == 404


@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_RULES={
        'rule_id_1': {
            'start_ts': '2020-01-06T16:00:00.372+03:00',
            'finish_ts': '2020-01-07T17:00:00.372+03:00',
            'percent': '5',
            'description': 'description',
            'is_money_rule': False,
            'execution_moment': 'NOW',
            'execution_trigger': 'NOW',
            'execution_status': 'HOLD',
            'transaction_status': 'CLEAR',
            'ticket': 'ticket',
            'campaign_name': 'campaign_name3',
            'issuer': 'issuer',
            'bank_commission_irf_rate': '1',
            'bank_commission_acquiring_rate': '2',
            'issued_in': 'non_ico',
            'mcc_list': ['1', '2'],
            'merchant_names': ['eda', 'taxi'],
            'only_ya_services': True,
            'product_id': 'pid_1',
            'required_tags': ['a'],
            'blocking_tags': ['b'],
        },
    },
)
async def test_existing_rule(taxi_bank_cashback_calculator):
    response = await taxi_bank_cashback_calculator.post(
        'cashback-calculator-support/v1/get_rule_by_id',
        json={'rule_id': 'rule_id_1'},
    )
    assert response.status == 200

    rule = response.json()['rule']
    if 'mcc_list' in rule:
        rule['mcc_list'].sort()
    if 'merchant_names' in rule:
        rule['merchant_names'].sort()
    assert rule == {
        'start_ts': '2020-01-06T13:00:00.372+00:00',
        'finish_ts': '2020-01-07T14:00:00.372+00:00',
        'percent': '5',
        'description': 'description',
        'is_money_rule': False,
        'execution_moment': 'NOW',
        'execution_trigger': 'NOW',
        'execution_status': 'HOLD',
        'transaction_status': 'CLEAR',
        'ticket': 'ticket',
        'campaign_name': 'campaign_name3',
        'issuer': 'issuer',
        'bank_commission_irf_rate': '1',
        'bank_commission_acquiring_rate': '2',
        'issued_in': 'non_ico',
        'mcc_list': ['1', '2'],
        'merchant_names': ['eda', 'taxi'],
        'only_ya_services': True,
        'product_id': 'pid_1',
        'required_tags': ['a'],
        'blocking_tags': ['b'],
    }
