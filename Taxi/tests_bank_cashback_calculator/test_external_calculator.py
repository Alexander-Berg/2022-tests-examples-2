import pytest

from tests_bank_cashback_calculator import common

HEADERS = {'X-Yandex-UID': 'uid'}

RULES = common.make_rules()
SERVICES_INFO = common.make_service_info()


@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_USER_LIMIT='1234',
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
)
async def test_ok(taxi_bank_cashback_calculator, _userinfo_mock):

    body = {
        'timestamp': '2021-09-08T14:20:00.372+03:00',
        'currency': 'RUB',
        'service_name': 'EDA',
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator/v1/calculate', json=body, headers=HEADERS,
    )
    assert response.status == 200

    json = response.json()
    assert json.get('cashback_rule')

    cashback_rule = json.get('cashback_rule')

    assert cashback_rule['percent']['amount'] == '15'
    assert sorted(cashback_rule['rule_ids']) == sorted(
        ['14-15-5percent', '14:20-14:30-10percent'],
    )
    assert cashback_rule['max_amount'] == '1234'


@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_USER_LIMIT='1234',
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
)
async def test_userinfo_404(taxi_bank_cashback_calculator, mockserver):
    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_buid_info',
    )
    def buid_info(request):
        return mockserver.make_response(
            status=404, json={'code': 'NotFound', 'message': ''},
        )

    body = {
        'timestamp': '2021-09-08T14:20:00.372+03:00',
        'currency': 'RUB',
        'service_name': 'EDA',
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator/v1/calculate', json=body, headers=HEADERS,
    )
    assert response.status == 200

    json = response.json()
    assert len(json) == 1


@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
)
async def test_no_cashback(taxi_bank_cashback_calculator, _userinfo_mock):

    body = {
        'timestamp': '2021-09-08T10:00:00.372+03:00',
        'currency': 'RUB',
        'service_name': 'EDA',
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator/v1/calculate', json=body, headers=HEADERS,
    )
    assert response.status == 200

    json = response.json()
    assert not json.get('cashback_rule')


@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
)
async def test_specific_service(taxi_bank_cashback_calculator, _userinfo_mock):

    body = {
        'timestamp': '2021-09-08T14:20:00.372+03:00',
        'currency': 'RUB',
        'service_name': 'TAXI',
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator/v1/calculate', json=body, headers=HEADERS,
    )
    assert response.status == 200

    json = response.json()
    assert json.get('cashback_rule')

    cashback_rule = json['cashback_rule']
    assert cashback_rule['percent']['amount'] == '30'
    assert sorted(cashback_rule['rule_ids']) == sorted(
        ['14-15-5percent', '14:20-14:30-10percent', 'taxi_rule-15percent'],
    )


@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
)
async def test_border_timestamp(taxi_bank_cashback_calculator, _userinfo_mock):

    body = {
        'timestamp': '2021-09-08T15:00:00.372+03:00',
        'currency': 'RUB',
        'service_name': 'EDA',
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator/v1/calculate', json=body, headers=HEADERS,
    )
    assert response.status == 200

    cashback_rule = response.json()['cashback_rule']
    assert cashback_rule['percent']['amount'] == '3'


@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
)
async def test_unknown_service(taxi_bank_cashback_calculator, _userinfo_mock):

    body = {
        'timestamp': '2021-09-08T15:00:00.372+03:00',
        'currency': 'RUB',
        'service_name': 'WTF',
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator/v1/calculate', json=body, headers=HEADERS,
    )
    assert response.status == 400


@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
)
async def test_no_money_cashback(
        taxi_bank_cashback_calculator, _userinfo_mock,
):
    body = {
        'timestamp': '2022-01-02T14:01:00.372+03:00',
        'currency': 'RUB',
        'service_name': 'EDA',
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator/v1/calculate', json=body, headers=HEADERS,
    )
    assert response.status == 200
    assert response.json() == {}


@pytest.mark.parametrize('payment_method_id', ['ya_card', 'driver_card'])
@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
)
async def test_ok_ya_card_product_id_rule(
        taxi_bank_cashback_calculator,
        _userinfo_mock,
        _core_card_mock,
        payment_method_id,
):
    body = {
        'timestamp': '2022-01-04T14:01:00.372+03:00',
        'currency': 'RUB',
        'service_name': 'EDA',
        'payment_method_id': payment_method_id,
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator/v1/calculate', json=body, headers=HEADERS,
    )
    assert response.status == 200
    assert response.json() == {
        'cashback_rule': {
            'max_amount': '10000',
            'percent': {'amount': '5'},
            'rule_ids': ['new_rule_for_' + payment_method_id],
        },
    }


@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_USER_LIMIT='1234',
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
    BANK_CASHBACK_CALCULATOR_RULES=RULES,
)
async def test_has_payment_method_ok(
        taxi_bank_cashback_calculator, _userinfo_mock, _core_card_mock,
):

    body = {
        'timestamp': '2021-09-08T14:20:00.372+03:00',
        'currency': 'RUB',
        'service_name': 'EDA',
        'payment_method_id': 'some_payment_method_id',
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator/v1/calculate', json=body, headers=HEADERS,
    )
    assert response.status == 200

    json = response.json()
    cashback_rule = json.get('cashback_rule')
    assert sorted(cashback_rule['rule_ids']) == sorted(
        ['14-15-5percent', '14:20-14:30-10percent'],
    )


@pytest.mark.parametrize('has_payment_method_id', [True, False])
@pytest.mark.config(
    BANK_CASHBACK_CALCULATOR_USER_LIMIT='1234',
    BANK_CASHBACK_CALCULATOR_SERVICES_INFO=SERVICES_INFO,
    BANK_CASHBACK_CALCULATOR_RULES={
        'has_product_id': {
            'start_ts': '2021-09-08T14:00:00.372+03:00',
            'finish_ts': '2021-09-08T15:00:00.372+03:00',
            'ticket': 'ticket',
            'campaign_name': 'campaign_name',
            'issuer': 'issuer',
            'percent': '5',
            'description': 'description',
            'product_id': 'WALLET',
        },
        'no_product_id': {
            'start_ts': '2021-09-08T14:00:00.372+03:00',
            'finish_ts': '2021-09-08T15:00:00.372+03:00',
            'ticket': 'ticket',
            'campaign_name': 'campaign_name',
            'issuer': 'issuer',
            'percent': '5',
            'description': 'description',
        },
    },
)
async def test_has_payment_method_fallback(
        taxi_bank_cashback_calculator,
        _userinfo_mock,
        mockserver,
        has_payment_method_id,
):
    @mockserver.handler('/bank-core-card/v1/card/product/get-by-trust-card-id')
    def _mock_product_id(request):
        return mockserver.make_response(
            status=404, json={'code': 'NotFound', 'message': 'NotFound'},
        )

    body = {
        'timestamp': '2021-09-08T14:20:00.372+03:00',
        'currency': 'RUB',
        'service_name': 'EDA',
    }
    if has_payment_method_id:
        body['payment_method_id'] = 'unknown_payment_method_id'

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator/v1/calculate', json=body, headers=HEADERS,
    )
    assert response.status == 200

    json = response.json()
    cashback_rule = json.get('cashback_rule')
    assert sorted(cashback_rule['rule_ids']) == sorted(
        ['has_product_id', 'no_product_id'],
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
('buid', 'bank_uid', 'a', '2022-06-01 00:00:00', '2023-06-02 01:00:00'),
('buid', 'bank_uid', 'b', '2022-06-02 00:00:00', '2023-06-03 00:00:00'),
('buid', 'bank_uid_2', 'c', '2022-06-01 00:00:00', '2023-06-03 00:00:00')""",
    ],
)
async def test_tags(taxi_bank_cashback_calculator, _userinfo_mock):
    body = {
        'timestamp': '2022-06-01T03:00:00.000+03:00',
        'currency': 'RUB',
        'service_name': 'EDA',
    }

    response = await taxi_bank_cashback_calculator.post(
        '/cashback-calculator/v1/calculate', json=body, headers=HEADERS,
    )
    assert response.status == 200

    json = response.json()
    assert json.get('cashback_rule')

    cashback_rule = json.get('cashback_rule')

    assert cashback_rule['rule_ids'] == ['tags']
