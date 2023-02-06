import pytest

from tests_bank_cashback_calculator import common

RULES = common.make_rules()
SERVICES_INFO = common.make_service_info()


@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
)
async def test_rule_ids(taxi_bank_cashback_calculator):

    body = {
        'yandex_uid': 'uid',
        'timestamp': '2021-09-08T14:20:00.372+03:00',
        'money': {'currency': 'RUB', 'amount': '49'},
        'mcc': '1234',
        'rule_ids': ['14-15-5percent', '14:20-14:30-10percent'],
        'merchant_name': 'merchant_name',
        'direction': 'DEBIT',
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator-internal/v1/calculate', json=body,
    )
    assert response.status == 200

    json = response.json()

    rules = json['rules']
    rule_dict = dict(
        map(lambda rule: (rule['rule_id'], rule['cashback']['amount']), rules),
    )
    assert rule_dict == {'14-15-5percent': '3', '14:20-14:30-10percent': '5'}


@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
    BANK_CASHBACK_CALCULATOR_MCC_DENY_LIST=['1234'],
)
async def test_mcc_blacklisted(taxi_bank_cashback_calculator):

    body = {
        'yandex_uid': 'uid',
        'timestamp': '2021-09-08T14:20:00.372+03:00',
        'money': {'currency': 'RUB', 'amount': '50'},
        'mcc': '1234',
        'rule_ids': ['14-15-5percent', '14:20-14:30-10percent'],
        'merchant_name': 'merchant_name',
        'direction': 'DEBIT',
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator-internal/v1/calculate', json=body,
    )
    assert response.status == 200

    json = response.json()
    assert not json.get('rules')


@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
)
async def test_external_trx(taxi_bank_cashback_calculator):

    body = {
        'yandex_uid': 'uid',
        'timestamp': '2021-09-08T15:35:00.372+03:00',
        'money': {'currency': 'RUB', 'amount': '1'},
        'mcc': '1234',
        'merchant_name': 'merchant_name',
        'direction': 'DEBIT',
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator-internal/v1/calculate', json=body,
    )
    assert response.status == 200

    json = response.json()

    rules = json['rules']
    rule_dict = dict(
        map(lambda rule: (rule['rule_id'], rule['cashback']['amount']), rules),
    )
    assert rule_dict == {'15-16-3percent': '1'}

    body['direction'] = 'CREDIT'
    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator-internal/v1/calculate', json=body,
    )
    json = response.json()
    assert not json.get('rules')


@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
)
async def test_ya_service(taxi_bank_cashback_calculator):

    body = {
        'yandex_uid': 'uid',
        'timestamp': '2021-09-08T15:35:00.372+03:00',
        'money': {'currency': 'RUB', 'amount': '100'},
        'mcc': '1234',
        'merchant_name': 'MERCHANT_EDA',
        'direction': 'DEBIT',
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator-internal/v1/calculate', json=body,
    )
    assert response.status == 200

    json = response.json()

    rules = json['rules']
    rule_dict = dict(
        map(lambda rule: (rule['rule_id'], rule['cashback']['amount']), rules),
    )
    assert rule_dict == {
        '15-16-3percent': '3',
        'ya_services_rule-1percent': '1',
    }


@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
)
async def test_mcc_list(taxi_bank_cashback_calculator):

    body = {
        'yandex_uid': 'uid',
        'timestamp': '2021-09-08T14:20:00.372+03:00',
        'money': {'currency': 'RUB', 'amount': '73'},
        'mcc': '3456',
        'merchant_name': 'merchant_name',
        'direction': 'DEBIT',
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator-internal/v1/calculate', json=body,
    )
    assert response.status == 200

    json = response.json()

    rules = json['rules']
    rule_dict = dict(
        map(lambda rule: (rule['rule_id'], rule['cashback']['amount']), rules),
    )
    assert rule_dict == {
        '14-15-5percent': '4',
        '14:20-14:30-10percent': '8',
        'specific_mcc_rule-5percent': '4',
    }


@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
)
async def test_mcc_list_credit(taxi_bank_cashback_calculator):

    body = {
        'yandex_uid': 'uid',
        'timestamp': '2021-09-08T14:20:00.372+03:00',
        'money': {'currency': 'RUB', 'amount': '73'},
        'mcc': '3456',
        'merchant_name': 'merchant_name',
        'direction': 'CREDIT',
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator-internal/v1/calculate', json=body,
    )
    assert response.status == 200

    json = response.json()

    rules = json['rules']
    rule_dict = dict(
        map(lambda rule: (rule['rule_id'], rule['cashback']['amount']), rules),
    )
    assert rule_dict == {
        '14-15-5percent': '3',
        '14:20-14:30-10percent': '7',
        'specific_mcc_rule-5percent': '3',
    }


@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
)
async def test_topup(taxi_bank_cashback_calculator):

    body = {
        'yandex_uid': 'uid',
        'timestamp': '2021-09-08T14:20:00.372+03:00',
        'money': {'currency': 'RUB', 'amount': '73'},
        'mcc': '3456',
        'merchant_name': 'merchant_name',
        'direction': 'CREDIT',
        'type': 'TOPUP',
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator-internal/v1/calculate', json=body,
    )
    assert response.status == 200

    json = response.json()
    assert not json.get('rules')


@pytest.mark.parametrize('field', ['merchant_name', 'mcc'])
@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
)
async def test_missing_merchant_info(taxi_bank_cashback_calculator, field):

    body = {
        'yandex_uid': 'uid',
        'timestamp': '2021-09-08T14:20:00.372+03:00',
        'money': {'currency': 'RUB', 'amount': '73'},
        'mcc': '3456',
        'merchant_name': 'merchant_name',
        'direction': 'CREDIT',
        'type': 'PURCHASE',
    }

    body.pop(field)

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator-internal/v1/calculate', json=body,
    )
    assert response.status == 400


@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
)
async def test_rub_cashback(taxi_bank_cashback_calculator):

    body = {
        'yandex_uid': 'uid',
        'timestamp': '2022-01-02T14:01:00.372+03:00',
        'money': {'currency': 'RUB', 'amount': '100'},
        'mcc': '3456',
        'merchant_name': 'merchant_name',
        'direction': 'DEBIT',
        'type': 'PURCHASE',
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator-internal/v1/calculate', json=body,
    )
    assert response.json() == {
        'rules': [
            {
                'campaign_name': 'campaign_name',
                'money': {'amount': '5', 'currency': 'RUB'},
                'issuer': 'issuer',
                'rule_id': 'first_rub_rule',
                'execution_moment': 'MONTH_END',
                'execution_trigger': 'DELIVERY',
                'execution_status': 'CLEAR',
                'ticket': 'ticket',
                'bank_commission_irf_rate': '0.0117',
                'bank_commission_acquiring_rate': '0.013',
                'issued_in': 'ico',
            },
        ],
    }


@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
)
async def test_product_id(taxi_bank_cashback_calculator):

    body = {
        'yandex_uid': 'uid',
        'timestamp': '2022-01-03T16:01:00.372+03:00',
        'money': {'currency': 'RUB', 'amount': '100'},
        'mcc': '3456',
        'merchant_name': 'merchant_name',
        'direction': 'DEBIT',
        'type': 'PURCHASE',
        'bank_product_id': 'product_id',
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator-internal/v1/calculate', json=body,
    )
    assert response.status_code == 200
    rules = response.json()['rules']
    rule_ids = set(map(lambda rule: rule['rule_id'], rules))
    assert rule_ids == {
        'first_product_id_rule',
        'same_rule_as_above_without_product_id',
    }


@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
)
@pytest.mark.parametrize('status', ['HOLD', 'CLEAR'])
async def test_only_clear_rule(taxi_bank_cashback_calculator, status):

    body = {
        'yandex_uid': 'uid',
        'timestamp': '2022-01-06T16:00:00.372+03:00',
        'money': {'currency': 'RUB', 'amount': '100'},
        'mcc': '3456',
        'merchant_name': 'merchant_name',
        'direction': 'DEBIT',
        'type': 'PURCHASE',
        'transaction_status': status,
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator-internal/v1/calculate', json=body,
    )
    if status == 'CLEAR':
        assert response.json() == {
            'rules': [
                {
                    'campaign_name': 'campaign_name',
                    'cashback': {'amount': '5', 'currency': 'RUB'},
                    'issuer': 'issuer',
                    'plus': {'amount': '5', 'currency': 'RUB'},
                    'rule_id': 'only_clear_rule',
                    'execution_moment': 'NOW',
                    'execution_trigger': 'NOW',
                    'execution_status': 'CLEAR',
                    'ticket': 'ticket',
                    'bank_commission_irf_rate': '0.0117',
                    'bank_commission_acquiring_rate': '0.013',
                    'issued_in': 'ico',
                },
                {
                    'campaign_name': 'campaign_name2',
                    'cashback': {'amount': '5', 'currency': 'RUB'},
                    'execution_moment': 'NOW',
                    'execution_status': 'CLEAR',
                    'execution_trigger': 'NOW',
                    'issuer': 'issuer',
                    'plus': {'amount': '5', 'currency': 'RUB'},
                    'rule_id': 'only_clear_rule_with_execute_status_clear',
                    'ticket': 'ticket',
                    'bank_commission_irf_rate': '0.0117',
                    'bank_commission_acquiring_rate': '0.013',
                    'issued_in': 'ico',
                },
            ],
        }
    else:
        assert response.json() == {}


@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
)
async def test_hold_execute_status(taxi_bank_cashback_calculator):

    body = {
        'yandex_uid': 'uid',
        'timestamp': '2020-01-06T16:00:00.372+03:00',
        'money': {'currency': 'RUB', 'amount': '100'},
        'mcc': '3456',
        'merchant_name': 'merchant_name',
        'direction': 'DEBIT',
        'type': 'PURCHASE',
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator-internal/v1/calculate', json=body,
    )
    assert response.json() == {
        'rules': [
            {
                'campaign_name': 'campaign_name3',
                'cashback': {'amount': '5', 'currency': 'RUB'},
                'execution_moment': 'NOW',
                'execution_status': 'HOLD',
                'execution_trigger': 'NOW',
                'issuer': 'issuer',
                'plus': {'amount': '5', 'currency': 'RUB'},
                'rule_id': 'only_clear_rule_with_execute_status_hold',
                'ticket': 'ticket',
                'bank_commission_irf_rate': '1',
                'bank_commission_acquiring_rate': '2',
                'issued_in': 'non_ico',
            },
        ],
    }


@pytest.mark.parametrize(
    'merchant_name, buid, expected_response',
    [
        (
            'merchant_name',
            '00112233-4455-6677-8899-aabbccddeeff',
            {
                'rules': [
                    {
                        'bank_commission_acquiring_rate': '0.013',
                        'bank_commission_irf_rate': '0.0117',
                        'campaign_name': 'campaign_name',
                        'cashback': {'amount': '5', 'currency': 'RUB'},
                        'execution_moment': 'NOW',
                        'execution_status': 'CLEAR',
                        'execution_trigger': 'NOW',
                        'issued_in': 'ico',
                        'issuer': 'issuer',
                        'plus': {'amount': '5', 'currency': 'RUB'},
                        'rule_id': 'tags',
                        'ticket': 'ticket',
                    },
                ],
            },
        ),
        ('MERCHANT_TAXI', '00112233-4455-6677-8899-aabbccdddddd', {}),
    ],
)
@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
    BANK_CASHBACK_CALCULATOR_RULES={
        'tags': {
            'start_ts': '2022-06-01T00:00:00+03:00',
            'finish_ts': '2022-06-02T00:00:00+03:00',
            'ticket': 'ticket',
            'campaign_name': 'campaign_name',
            'issuer': 'issuer',
            'percent': '5',
            'description': 'description',
            'required_tags': ['a'],
            'blocking_tags': ['b', 'c'],
        },
    },
)
@pytest.mark.pgsql(
    'core_cashback_rules@0',
    queries=[
        """insert into tags.tag_records
(entity_type, entity_id, name, starts_at, ends_at) values
('buid', '00112233-4455-6677-8899-aabbccddeeff',
    'a', '2022-06-01 00:00:00', '2023-06-02 01:00:00'),
('buid', '00112233-4455-6677-8899-aabbccddeeff',
    'b', '2022-06-02 00:00:00', '2023-06-03 00:00:00'),
('buid', '00112233-4455-6677-8899-aabbccddeeee',
    'c', '2022-06-01 00:00:00', '2023-06-03 00:00:00')""",
    ],
)
async def test_tags(
        taxi_bank_cashback_calculator,
        _userinfo_mock,
        merchant_name,
        buid,
        expected_response,
):
    body = {
        'yandex_uid': 'uid',
        'buid': buid,
        'timestamp': '2022-06-01T03:00:00.000+03:00',
        'money': {'currency': 'RUB', 'amount': '100'},
        'mcc': '3456',
        'merchant_name': merchant_name,
        'direction': 'DEBIT',
        'type': 'PURCHASE',
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator-internal/v1/calculate', json=body,
    )
    assert response.status == 200
    assert response.json() == expected_response
