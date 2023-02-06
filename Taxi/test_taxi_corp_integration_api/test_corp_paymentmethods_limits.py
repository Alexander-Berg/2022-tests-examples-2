import datetime

import pytest

from taxi.util import dates

from test_taxi_corp_integration_api import utils


TEST_CORP_PAYMENTMETHODS_RIDE_LIMITS_PARAMS = dict(
    argnames='limit, method',
    argvalues=[
        pytest.param(
            {'limits': {'orders_cost': {'value': '101', 'period': 'day'}}},
            {'description': 'Осталось 1 из 101 руб.'},
            id='can_order=True with spending',
        ),
        pytest.param(
            {'limits': {'orders_cost': {'value': '99', 'period': 'day'}}},
            {
                'description': 'Осталось -1 из 99 руб.',
                'can_order': False,
                'order_disable_reason': 'Недостаточно денег на счёте',
            },
            id='can_order=False with spending',
        ),
    ],
)


@pytest.mark.config(
    ALL_CATEGORIES=['econom'],
    APPLICATION_TO_CORP_SOURCE_MAP={'cargo': 'cargo'},
    CORP_SOURCES_NO_USER=['cargo'],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.parametrize(**TEST_CORP_PAYMENTMETHODS_RIDE_LIMITS_PARAMS)
@pytest.mark.now('2020-01-02T10:00:00+03:00')
async def test_corp_pamentmethods_ride_limits(
        db,
        taxi_config,
        mockserver,
        load_json,
        exp3_decoupling_mock,
        taxi_corp_integration_api,
        limit,
        method,
):
    @mockserver.json_handler('/billing-reports/v1/balances/select')
    def _mock_balances(request):
        return load_json('billing_reports_get_balances.json')

    request_data = {
        'class': 'econom',
        'identity': {
            'uid': '12345678',
            'phone_id': '1a1a1a1a1a1a1a1a1a1a1a1a',
        },
    }

    await db.corp_clients.update_one(
        {'_id': 'client_id_1'}, {'$push': {'features': 'ride_limits'}},
    )

    await db.corp_limits.update_one({'_id': 'limit_id_1'}, {'$set': limit})

    response = await utils.request_corp_paymentmethods(
        taxi_corp_integration_api, mockserver, request_data, 'moscow', False,
    )

    method = dict(
        {
            'type': 'corp',
            'id': 'corp-client_id_1',
            'label': 'Yandex.Uber team',
            'cost_center': 'cost center',
            'cost_centers': utils.OLD_COST_CENTER_VALUE,
            'cost_center_fields': utils.OLD_COST_CENTER_NEW_FORMAT,
            'can_order': True,
            'zone_available': True,
            'hide_user_cost': False,
            'user_id': 'user_id_1',
            'client_comment': 'comment',
            'currency': 'RUB',
            'classes_available': ['econom', 'express'],
            'without_vat_contract': False,
        },
        **method,
    )

    assert await response.json() == {'methods': [method] if method else []}
    assert response.status == 200


@pytest.mark.config(
    ALL_CATEGORIES=['econom'],
    APPLICATION_TO_CORP_SOURCE_MAP={'cargo': 'cargo'},
    CORP_SOURCES_NO_USER=['cargo'],
    CORP_INTEGRATION_API_BILLING_FALLBACK={
        'fallback-mode': 'skip_billing_errors',
        'select_balance_from_billing': {
            'attempts': 2,
            'timeout-ms': 250,
            'total-timeout-ms': 350,
        },
    },
)
@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.parametrize(**TEST_CORP_PAYMENTMETHODS_RIDE_LIMITS_PARAMS)
@pytest.mark.now('2020-01-02T10:00:00+03:00')
async def test_corp_pamentmethods_with_billing_fallback(
        db,
        taxi_config,
        mockserver,
        load_json,
        exp3_decoupling_mock,
        taxi_corp_integration_api,
        limit,
        method,
):
    @mockserver.json_handler('/billing-reports/v1/balances/select')
    def _mock_balances(request):
        return mockserver.make_response(status=500, json={})

    request_data = {
        'class': 'econom',
        'identity': {
            'uid': '12345678',
            'phone_id': '1a1a1a1a1a1a1a1a1a1a1a1a',
        },
    }

    await db.corp_clients.update_one(
        {'_id': 'client_id_1'}, {'$push': {'features': 'ride_limits'}},
    )

    await db.corp_limits.update_one({'_id': 'limit_id_1'}, {'$set': limit})

    response = await utils.request_corp_paymentmethods(
        taxi_corp_integration_api, mockserver, request_data, 'moscow', False,
    )

    method = dict(
        {
            'type': 'corp',
            'id': 'corp-client_id_1',
            'label': 'Yandex.Uber team',
            'cost_center': 'cost center',
            'cost_centers': utils.OLD_COST_CENTER_VALUE,
            'cost_center_fields': utils.OLD_COST_CENTER_NEW_FORMAT,
            'can_order': True,
            'zone_available': True,
            'hide_user_cost': False,
            'user_id': 'user_id_1',
            'client_comment': 'comment',
            'currency': 'RUB',
            'classes_available': ['econom', 'express'],
            'description': '',
            'without_vat_contract': False,
        },
    )

    assert await response.json() == {'methods': [method] if method else []}
    assert response.status == 200


TEST_CORP_PAYMENTMETHODS_RIDE_LIMITS_CLIENT_BALANCE_PARAMS = dict(
    argnames=['method', 'contract_upd', 'order_price'],
    argvalues=[
        pytest.param(
            {},
            {
                'balance.operational_balance': '1202',
                'balance.balance_dt': dates.localize(
                    datetime.datetime(2019, 12, 31, 21, 0, 0),
                ),
                'settings.prepaid_deactivate_threshold': '1000',
            },
            '1.0',
            id='can_order=True with spending',
        ),
        pytest.param(
            {
                'can_order': False,
                'order_disable_reason': (
                    'Баланс клиента ниже значения порога отключения'
                ),
            },
            {
                'balance.operational_balance': '1200',
                'balance.balance_dt': dates.localize(
                    datetime.datetime(2019, 12, 31, 21, 0, 0),
                ),
                'settings.prepaid_deactivate_threshold': '1000',
            },
            '1.0',
            id='can_order=False with spending',
        ),
    ],
)


@pytest.mark.config(
    ALL_CATEGORIES=['econom'], CORP_INTEGRATION_API_USE_CLIENT_BALANCE=True,
)
@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.now('2020-01-02T10:00:00+03:00')
@pytest.mark.parametrize(
    **TEST_CORP_PAYMENTMETHODS_RIDE_LIMITS_CLIENT_BALANCE_PARAMS,
)
async def test_corp_pamentmethods_ride_limits_client_balance(
        db,
        taxi_config,
        mockserver,
        load_json,
        exp3_decoupling_mock,
        taxi_corp_integration_api,
        method,
        contract_upd,
        order_price,
):
    @mockserver.json_handler('/billing-reports/v1/balances/select')
    def _mock_balances(request):
        return load_json('billing_reports_get_balances.json')

    request_data = {
        'class': 'econom',
        'identity': {
            'uid': '12345678',
            'phone_id': '1a1a1a1a1a1a1a1a1a1a1a1a',
        },
        'order_price': order_price,
    }

    await db.corp_limits.update_one(
        {'_id': 'limit_id_1'}, {'$set': {'limits.orders_cost': None}},
    )

    if contract_upd:
        await db.corp_contracts.update_one(
            {'billing_client_id': '2000101'}, {'$set': contract_upd},
        )

    response = await utils.request_corp_paymentmethods(
        taxi_corp_integration_api, mockserver, request_data, 'moscow', False,
    )

    method = dict(
        {
            'type': 'corp',
            'id': 'corp-client_id_1',
            'label': 'Yandex.Uber team',
            'description': '',
            'cost_center': 'cost center',
            'cost_centers': utils.OLD_COST_CENTER_VALUE,
            'cost_center_fields': utils.OLD_COST_CENTER_NEW_FORMAT,
            'can_order': True,
            'zone_available': True,
            'hide_user_cost': False,
            'user_id': 'user_id_1',
            'client_comment': 'comment',
            'currency': 'RUB',
            'classes_available': ['econom', 'express'],
            'without_vat_contract': False,
        },
        **method,
    )

    assert await response.json() == {'methods': [method] if method else []}
    assert response.status == 200


TEST_CORP_PAYMENTMETHODS_RIDE_LIMITS_DEPARTMENT_BALANCE_PARAMS = dict(
    argnames=['method', 'departments'],
    argvalues=[
        pytest.param(
            {},
            [{'_id': 'department_id_1', 'ancestors': []}],
            id='can_order=True with spending',
        ),
        pytest.param(
            {
                'can_order': False,
                'order_disable_reason': 'Недостаточно денег на счёте',
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
            id='can_order=False with spending',
        ),
    ],
)


@pytest.mark.config(
    ALL_CATEGORIES=['econom'],
    APPLICATION_TO_CORP_SOURCE_MAP={'cargo': 'cargo'},
    CORP_SOURCES_NO_USER=['cargo'],
    CORP_INTEGRATION_API_USE_DEPARTMENT_BALANCE=True,
    CORP_INTEGRATION_API_USE_CLIENT_BALANCE=True,
)
@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.now('2020-01-02T10:00:00+03:00')
@pytest.mark.parametrize(
    **TEST_CORP_PAYMENTMETHODS_RIDE_LIMITS_DEPARTMENT_BALANCE_PARAMS,
)
async def test_corp_pamentmethods_ride_limits_department_balance(
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

    request_data = {
        'class': 'econom',
        'identity': {
            'uid': '12345678',
            'phone_id': '1a1a1a1a1a1a1a1a1a1a1a1a',
        },
    }

    await db.corp_limits.update_one(
        {'_id': 'limit_id_1'}, {'$set': {'limits.orders_cost': None}},
    )
    await db.corp_departments.insert_many(departments)

    response = await utils.request_corp_paymentmethods(
        taxi_corp_integration_api, mockserver, request_data, 'moscow', False,
    )

    method = dict(
        {
            'type': 'corp',
            'id': 'corp-client_id_1',
            'label': 'Yandex.Uber team',
            'cost_center': 'cost center',
            'cost_centers': utils.OLD_COST_CENTER_VALUE,
            'cost_center_fields': utils.OLD_COST_CENTER_NEW_FORMAT,
            'can_order': True,
            'description': '',
            'zone_available': True,
            'hide_user_cost': False,
            'user_id': 'user_id_1',
            'client_comment': 'comment',
            'currency': 'RUB',
            'classes_available': ['econom', 'express'],
            'without_vat_contract': False,
        },
        **method,
    )

    assert await response.json() == {'methods': [method] if method else []}
    assert response.status == 200
