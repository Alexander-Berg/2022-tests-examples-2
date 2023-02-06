import pytest

from test_taxi_corp_integration_api import utils


BASE_ORDER_INFO = {'order_sum': '200', 'currency': 'RUB'}

DEFAULT_SERVICE_POSITION = {'position': [37.5, 55.7]}

BASE_PAYMENT_METHOD = {
    'id': 'corp:user_id_1:RUB',
    'type': 'corp',
    'name': 'Yandex.Uber team',
    'currency': 'RUB',
    'availability': {'available': True, 'disabled_reason': ''},
    'description': '',
    'user_id': 'user_id_1',
    'client_id': 'client_id_1',
}

BASE_PAYMENT_METHOD_WITH_EATS_COST_CENTERS = {
    'id': 'corp:user_with_eats_cost_center:RUB',
    'type': 'corp',
    'name': 'Yandex.Uber team',
    'currency': 'RUB',
    'availability': {'available': True, 'disabled_reason': ''},
    'description': '',
    'user_id': 'user_with_eats_cost_center',
    'client_id': 'client_id_1',
    'cost_center_fields': [
        {
            'format': 'mixed',
            'id': 'cost center',
            'order_flows': [],
            'required': True,
            'services': ['eats2'],
            'title': 'Центр затрат',
            'values': ['домой', 'в офис', 'в другой офис'],
        },
        {
            'format': 'mixed',
            'id': 'was_tasty',
            'order_flows': [],
            'required': True,
            'services': ['eats2'],
            'title': 'Было ли вкусно?',
            'values': ['Да', 'Нет'],
        },
    ],
}

DB_FIELDS_WITH_EATS = pytest.mark.filldb(corp_cost_center_options='with_eats')


@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.parametrize(
    [
        'personal_phone_id',
        'request_body',
        'expected_result',
        'expected_balance_ncalls',
    ],
    [
        pytest.param(
            'not_existing_user',
            {},
            [],
            0,
            id='not existing user',
            marks=[pytest.mark.now('2020-01-02T10:00:00+03:00')],
        ),
        pytest.param(
            'phone_id_6',
            {},
            [],
            0,
            id='deleted user',
            marks=[pytest.mark.now('2020-01-02T10:00:00+03:00')],
        ),
        pytest.param(
            'phone_id_1',
            {},
            [
                {
                    **BASE_PAYMENT_METHOD,
                    **{
                        'description': 'Осталось 4166.67 из 4166.67 ₽',
                        'balance_left': '4166.67',
                    },
                },
            ],
            1,
            id='simple can order',
            marks=[pytest.mark.now('2020-01-02T10:00:00+03:00')],
        ),
        pytest.param(
            'phone_id_1',
            BASE_ORDER_INFO,
            [
                {
                    **BASE_PAYMENT_METHOD,
                    **{
                        'description': 'Осталось 4166.67 из 4166.67 ₽',
                        'balance_left': '4166.67',
                    },
                },
            ],
            1,
            id='can order with order_info',
            marks=[pytest.mark.now('2020-01-02T10:00:00+03:00')],
        ),
        pytest.param(
            'phone_id_1',
            {**BASE_ORDER_INFO, **{'currency': 'KZT'}},
            [
                {
                    **BASE_PAYMENT_METHOD,
                    **{
                        'availability': {
                            'available': False,
                            'disabled_reason': (
                                'В этой стране корпоративная оплата не '
                                'поддерживается'
                            ),
                        },
                        'description': 'Осталось 4166.67 из 4166.67 ₽',
                        'balance_left': '4166.67',
                    },
                },
            ],
            1,
            id='empty methods for other countries',
            marks=[pytest.mark.now('2020-01-02T10:00:00+03:00')],
        ),
        pytest.param('phone_id_2', {}, [], 1, id='user without eats limit'),
        pytest.param(
            'phone_id_3',
            {**BASE_ORDER_INFO, **{'order_sum': '175'}},
            [
                {
                    **BASE_PAYMENT_METHOD,
                    **{
                        'id': 'corp:user_with_eats_spending:RUB',
                        'user_id': 'user_with_eats_spending',
                        'description': 'Осталось 175 из 4166.67 ₽',
                        'balance_left': '175',
                    },
                },
            ],
            1,
            id='with spending',
            marks=[pytest.mark.now('2020-01-02T10:00:00+03:00')],
        ),
        pytest.param(
            'phone_id_3',
            BASE_ORDER_INFO,
            [
                {
                    **BASE_PAYMENT_METHOD,
                    **{
                        'id': 'corp:user_with_eats_spending:RUB',
                        'user_id': 'user_with_eats_spending',
                        'availability': {
                            'available': False,
                            'disabled_reason': (
                                'Сумма заказа превышает доступный лимит'
                            ),
                        },
                        'description': 'Осталось 175 из 4166.67 ₽',
                        'balance_left': '175',
                    },
                },
            ],
            1,
            id='insufficient funds',
            marks=[pytest.mark.now('2020-01-02T10:00:00+03:00')],
        ),
        pytest.param(
            'phone_id_4',
            {},
            [
                {
                    **BASE_PAYMENT_METHOD,
                    **{
                        'id': 'corp:unlimited_user:RUB',
                        'user_id': 'unlimited_user',
                        'description': '',
                    },
                },
            ],
            1,
            id='unlimited, without description',
            marks=[pytest.mark.now('2020-01-02T10:00:00+03:00')],
        ),
        pytest.param(
            'with_eats_cost_center',
            {},
            [BASE_PAYMENT_METHOD_WITH_EATS_COST_CENTERS],
            1,
            id='with eats cost center',
            marks=[
                DB_FIELDS_WITH_EATS,
                pytest.mark.now('2020-01-02T10:00:00+03:00'),
            ],
        ),
        pytest.param(
            'phone_id_3',
            BASE_ORDER_INFO,
            [
                {
                    **BASE_PAYMENT_METHOD,
                    **{
                        'id': 'corp:user_with_eats_spending:RUB',
                        'user_id': 'user_with_eats_spending',
                        'availability': {
                            'available': True,
                            'disabled_reason': '',
                        },
                        'description': 'Осталось 4166.67 из 4166.67 ₽',
                        'balance_left': '4166.67',
                    },
                },
            ],
            1,
            id='can order with tz Moscow',
            marks=[pytest.mark.now('2020-02-01T02:00:00+03:00')],
        ),
    ],
)
@pytest.mark.config(
    CORP_INTEGRATION_API_USE_CLIENT_BALANCE=True,
    CORP_COUNTRIES_SUPPORTED={
        'rus': {'currency': 'RUB', 'currency_sign': '₽', 'vat': 0.2},
        'kzt': {'currency': 'KZT', 'currency_sign': '₸', 'vat': 0.2},
    },
)
async def test_payment_methods_eats(
        mockserver,
        taxi_corp_integration_api,
        load_json,
        personal_phone_id,
        request_body,
        expected_result,
        expected_balance_ncalls,
):
    @mockserver.json_handler('/billing-reports/v1/balances/select')
    def _mock_balances(request):
        return load_json('billing_reports_get_balances.json')

    headers = {'X-YaTaxi-User': ('personal_phone_id=' + personal_phone_id)}
    response = await taxi_corp_integration_api.post(
        '/v1/payment-methods/eats', headers=headers, json=request_body,
    )

    response_json = await response.json()
    assert response.status == 200
    assert response_json['payment_methods'] == expected_result
    assert _mock_balances.times_called == expected_balance_ncalls


@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.parametrize(
    ['additional_data', 'geo_restrictions', 'method'],
    [
        pytest.param(
            dict(
                place_of_service_location=DEFAULT_SERVICE_POSITION,
                place_of_user_location={'position': [37.60, 55.74]},
            ),
            [{'destination': 'geo_id_2'}],
            [
                {
                    **BASE_PAYMENT_METHOD,
                    **{
                        'description': 'Осталось 4166.67 из 4166.67 ₽',
                        'balance_left': '4166.67',
                    },
                },
            ],
            id='available zone',
        ),
    ],
)
@pytest.mark.config(
    CORP_INTEGRATION_API_USE_CLIENT_BALANCE=True,
    CORP_COUNTRIES_SUPPORTED={
        'rus': {'currency': 'RUB', 'currency_sign': '₽', 'vat': 0.2},
    },
)
async def test_payment_methods_eats_geo_restrictions(
        db,
        mockserver,
        mock_billing,
        taxi_corp_integration_api,
        load_json,
        additional_data,
        geo_restrictions,
        method,
):
    @mockserver.json_handler('/protocol/3.0/nearestzone')
    def _mock_nearestzone(request):
        return {'nearest_zone': 'moscow'}

    await db.corp_limits.update_one(
        {'_id': 'eats2_limit_id'},
        {'$set': {'geo_restrictions': geo_restrictions}},
    )

    request_body = dict(BASE_ORDER_INFO, **additional_data)
    personal_phone_id = 'phone_id_1'
    headers = {'X-YaTaxi-User': ('personal_phone_id=' + personal_phone_id)}
    response = await taxi_corp_integration_api.post(
        '/v1/payment-methods/eats', headers=headers, json=request_body,
    )
    response_json = await response.json()
    assert response.status == 200
    assert response_json['payment_methods'] == method


@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.parametrize(
    ['method', 'departments'],
    [
        pytest.param(
            {
                'availability': {
                    'available': False,
                    'disabled_reason': (
                        'Превышен лимит подразделения, '
                        'обратитесь в свою компанию'
                    ),
                },
            },
            [
                {
                    '_id': 'department_id_1',
                    'ancestors': [],
                    'limits': {
                        'taxi': {'budget': 100.00},
                        'eats2': {'budget': 100.00},
                    },
                },
            ],
        ),
    ],
)
@pytest.mark.config(
    CORP_INTEGRATION_API_USE_CLIENT_BALANCE=True,
    CORP_INTEGRATION_API_USE_DEPARTMENT_BALANCE=True,
    CORP_COUNTRIES_SUPPORTED={
        'rus': {'currency': 'RUB', 'currency_sign': '₽', 'vat': 0.2},
    },
)
@pytest.mark.now('2020-01-02T10:00:00+03:00')
async def test_payment_methods_eats_ride_limits_department_balance(
        db,
        taxi_config,
        mockserver,
        load_json,
        exp3_decoupling_mock,
        taxi_corp_integration_api,
        method,
        departments,
):
    @mockserver.json_handler('/billing-reports/v1/balances/select')
    def _mock_balances(request):
        return load_json('billing_reports_get_balances.json')

    await db.corp_limits.update_one(
        {'_id': 'eats2_limit_id'}, {'$set': {'limits.orders_cost': None}},
    )
    await db.corp_departments.insert_many(departments)

    request_body = BASE_ORDER_INFO
    personal_phone_id = 'phone_id_1'
    headers = {'X-YaTaxi-User': ('personal_phone_id=' + personal_phone_id)}
    response = await taxi_corp_integration_api.post(
        '/v1/payment-methods/eats', headers=headers, json=request_body,
    )

    expected_method = dict(BASE_PAYMENT_METHOD, **method)
    response_json = await response.json()
    assert response.status == 200
    assert response_json['payment_methods'] == [expected_method]
