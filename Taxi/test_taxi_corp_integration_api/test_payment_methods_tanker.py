import pytest


from test_taxi_corp_integration_api import utils


BASE_ORDER_INFO = {'order_sum': '220', 'currency': 'RUB', 'fuel_type': 'a95'}

BASE_PAYMENT_METHOD = {
    'id': 'corp:user_id_1:tanker/RUB',
    'user_id': 'user_id_1',
    'client_id': 'client_id_1',
    'billing_id': '2000101',
    'type': 'corp',
    'name': 'Yandex.Uber team',
    'currency': 'RUB',
    'availability': {'available': True, 'disabled_reason': ''},
    'description': 'Осталось 5000 из 5000 ₽',
}

BASE_PAYMENT_METHOD_WITH_TANKER_COST_CENTERS = {
    'id': 'corp:user_with_tanker_cost_center:tanker/RUB',
    'user_id': 'user_with_tanker_cost_center',
    'client_id': 'client_id_1',
    'billing_id': '2000101',
    'type': 'corp',
    'name': 'Yandex.Uber team',
    'currency': 'RUB',
    'availability': {'available': True, 'disabled_reason': ''},
    'description': 'Осталось 5000 из 5000 ₽',
    'cost_center_fields': [
        {
            'format': 'mixed',
            'id': 'cost center',
            'order_flows': [],
            'required': True,
            'services': ['tanker'],
            'title': 'Центр затрат',
            'values': ['домой', 'в офис', 'в другой офис'],
        },
        {
            'format': 'mixed',
            'id': 'hidden_field_uuid_id',
            'order_flows': ['taxi'],
            'required': True,
            'services': ['taxi', 'drive', 'tanker'],
            'title': 'Сколько километров',
            'values': ['100', '200'],
        },
    ],
}

DB_FIELDS_WITH_TANKER = pytest.mark.filldb(
    corp_cost_center_options='with_tanker',
)


@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.parametrize(
    ['personal_phone_id', 'request_body', 'expected_result'],
    [
        pytest.param('not_existing_user', {}, [], id='not existing user'),
        pytest.param(
            'phone_id_1', {}, [BASE_PAYMENT_METHOD], id='simple can order',
        ),
        pytest.param(
            'phone_id_1',
            BASE_ORDER_INFO,
            [BASE_PAYMENT_METHOD],
            id='can order with order_info',
        ),
        pytest.param('phone_id_2', {}, [], id='user without tanker limit'),
        pytest.param(
            'phone_id_3',
            {**BASE_ORDER_INFO, **{'order_sum': '175'}},
            [
                {
                    **BASE_PAYMENT_METHOD,
                    **{
                        'id': 'corp:user_with_tanker_spending:tanker/RUB',
                        'user_id': 'user_with_tanker_spending',
                        'description': 'Осталось 210 из 5000 ₽',
                    },
                },
            ],
            id='with spending',
        ),
        pytest.param(
            'phone_id_3',
            BASE_ORDER_INFO,
            [
                {
                    **BASE_PAYMENT_METHOD,
                    **{
                        'id': 'corp:user_with_tanker_spending:tanker/RUB',
                        'user_id': 'user_with_tanker_spending',
                        'availability': {
                            'available': False,
                            'disabled_reason': (
                                'Недостаточно средств для оплаты заказа'
                            ),
                        },
                        'description': 'Осталось 210 из 5000 ₽',
                    },
                },
            ],
            id='insufficient funds',
        ),
        pytest.param(
            'phone_id_4',
            {},
            [
                {
                    **BASE_PAYMENT_METHOD,
                    **{
                        'id': 'corp:unlimited_user:tanker/RUB',
                        'user_id': 'unlimited_user',
                        'description': '',
                    },
                },
            ],
            id='unlimited, without description',
        ),
        pytest.param(
            'phone_id_card',
            {},
            [
                {
                    **BASE_PAYMENT_METHOD,
                    **{
                        'id': 'corp:user_id_2:tanker/RUB',
                        'user_id': 'user_id_2',
                        'client_id': 'client_id_2',
                        'billing_id': '3000101',
                        'type': 'card',
                        'card_info': {
                            'card_id': 'card-123',
                            'account': '500000****1111',
                            'yandex_uid': '44348071',
                        },
                    },
                },
            ],
            id='normal order',
        ),
        pytest.param(
            'user_with_tanker_cost_center',
            {**BASE_ORDER_INFO, **{'order_sum': '175'}},
            [BASE_PAYMENT_METHOD_WITH_TANKER_COST_CENTERS],
            id='with tanker cost center',
            marks=[DB_FIELDS_WITH_TANKER],
        ),
    ],
)
@pytest.mark.config(
    CORP_INTEGRATION_API_USE_CLIENT_BALANCE=True,
    CORP_COUNTRIES_SUPPORTED={
        'rus': {'currency': 'RUB', 'currency_sign': '₽', 'vat': 0.2},
    },
)
@pytest.mark.now('2020-01-02T10:00:00+03:00')
async def test_payment_methods_tanker(
        mockserver,
        taxi_corp_integration_api,
        load_json,
        personal_phone_id,
        request_body,
        expected_result,
):
    @mockserver.json_handler('/billing-reports/v1/balances/select')
    def _mock_balances(request):
        return load_json('billing_reports_get_balances.json')

    @mockserver.json_handler('/corp-clients/v1/cards/main')
    def _mock_cards(request):
        return load_json('corp_clients_get_cards_main.json')

    headers = {'X-YaTaxi-User': f'personal_phone_id={personal_phone_id}'}
    response = await taxi_corp_integration_api.post(
        '/v1/payment-methods/tanker', headers=headers, json=request_body,
    )

    response_json = await response.json()
    assert response.status == 200
    assert response_json['payment_methods'] == expected_result
