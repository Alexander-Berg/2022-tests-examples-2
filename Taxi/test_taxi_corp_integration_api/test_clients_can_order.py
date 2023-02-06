# pylint: disable=redefined-outer-name
import datetime

import pytest

from test_taxi_corp_integration_api import utils


SUCCESS_RESPONSE = {
    'can_order': True,
    'order_disable_reason': '',
    'zone_available': True,
    'zone_disable_reason': '',
}


async def _request_client_can_order(
        web_app_client,
        mockserver,
        service,
        request_data,
        zone_name,
        headers=None,
):
    @mockserver.json_handler('/protocol/3.0/nearestzone')
    def _mock_nearestzone(request):
        return {'nearest_zone': zone_name}

    return await web_app_client.post(
        '/v1/clients/can_order/{}'.format(service),
        headers=headers,
        json=request_data,
    )


@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.config(CORP_INTEGRATION_API_USE_CLIENT_BALANCE=True)
@pytest.mark.parametrize(
    argnames=['request_data', 'response_data', 'zone_name'],
    argvalues=[
        pytest.param(
            {'client_ids': ['client_happy_path_prepaid']},
            [dict(SUCCESS_RESPONSE, client_id='client_happy_path_prepaid')],
            'moscow',
            id='happy path prepaid',
        ),
        pytest.param(
            {
                'client_ids': [
                    'client_service_is_disabled',
                    'client_happy_path_prepaid',
                ],
            },
            [
                dict(
                    SUCCESS_RESPONSE,
                    client_id='client_service_is_disabled',
                    can_order=False,
                    order_disable_reason='Сервис отключен',
                ),
                dict(SUCCESS_RESPONSE, client_id='client_happy_path_prepaid'),
            ],
            'moscow',
            id='multiple clients',
        ),
        pytest.param(
            {'client_ids': ['client_contract_deactivated']},
            [
                dict(
                    SUCCESS_RESPONSE,
                    client_id='client_contract_deactivated',
                    can_order=False,
                    order_disable_reason='Корпоративный контракт отключен',
                ),
            ],
            'moscow',
            id='check contract is active',
        ),
    ],
)
async def test_clients_can_order_general_service(
        web_app_client,
        taxi_config,
        mockserver,
        mock_billing,
        request_data,
        response_data,
        zone_name,
):
    response = await _request_client_can_order(
        web_app_client, mockserver, 'eats2', request_data, zone_name,
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {'statuses': response_data}


@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.config(CORP_INTEGRATION_API_USE_CLIENT_BALANCE=True)
@pytest.mark.parametrize(
    argnames=['request_data', 'response_data', 'zone_name'],
    argvalues=[
        pytest.param(
            {
                'client_ids': ['taxi_client_happy_path_prepaid'],
                'order': {'order_price': '123.456', 'classes': ['business']},
            },
            dict(
                SUCCESS_RESPONSE,
                client_id='taxi_client_happy_path_prepaid',
                can_order=False,
                order_disable_reason='Комфорт недоступны',
            ),
            'moscow',
            id='check allowed classes',
        ),
        pytest.param(
            {
                'client_ids': ['taxi_client_happy_path_prepaid'],
                'order': {
                    'order_price': '123.456',
                    'classes': ['econom'],
                    'route': [{'geopoint': [37.59, 55.73]}],
                },
            },
            dict(
                SUCCESS_RESPONSE,
                client_id='taxi_client_happy_path_prepaid',
                zone_available=False,
                zone_disable_reason='Не задан тариф для зоны',
            ),
            'nvkz',
            id='decoupling tariff for zone not exists, fallback is off',
        ),
    ],
)
@pytest.mark.client_experiments3(
    file_with_default_response='exp3_decoupling_enabled.json',
)
async def test_clients_can_order_taxi(
        web_app_client,
        taxi_config,
        mockserver,
        mock_billing,
        request_data,
        response_data,
        zone_name,
):
    response = await _request_client_can_order(
        web_app_client, mockserver, 'taxi', request_data, zone_name,
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {'statuses': [response_data]}


@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.parametrize(
    argnames=['request_data', 'response_data', 'zone_name'],
    argvalues=[
        pytest.param(
            {
                'client_ids': ['taxi_client_happy_path_prepaid'],
                'order': {'order_price': '123.456', 'classes': ['business']},
            },
            dict(SUCCESS_RESPONSE, client_id='taxi_client_happy_path_prepaid'),
            'moscow',
            id='no check allowed classes, cause no taxi order',
        ),
        pytest.param(
            {
                'client_ids': ['taxi_client_happy_path_prepaid'],
                'order': {
                    'order_price': '123.456',
                    'classes': ['econom'],
                    'route': [{'geopoint': [37.59, 55.73]}],
                },
            },
            dict(SUCCESS_RESPONSE, client_id='taxi_client_happy_path_prepaid'),
            'nvkz',
            id='no check decoupling tariff for zone, cause no taxi order',
        ),
    ],
)
@pytest.mark.client_experiments3(
    file_with_default_response='exp3_decoupling_enabled.json',
)
async def test_clients_can_order_no_taxi_order_checks_for_next_day_delivery(
        web_app_client,
        taxi_config,
        mockserver,
        mock_billing,
        request_data,
        response_data,
        zone_name,
):
    response = await _request_client_can_order(
        web_app_client,
        mockserver,
        'next_day_delivery',
        request_data,
        zone_name,
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {'statuses': [response_data]}


@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.config(CORP_INTEGRATION_API_USE_CLIENT_BALANCE=True)
@pytest.mark.now('2020-01-02T10:00:00+03:00')
@pytest.mark.parametrize(
    argnames=['deactivate_threshold', 'contract_limit', 'response_data'],
    argvalues=[
        pytest.param(
            '0',
            '3000',
            [
                dict(
                    SUCCESS_RESPONSE,
                    client_id='client_happy_path_prepaid',
                    can_order=False,
                    order_disable_reason='Баланс клиента ниже значения '
                    'порога отключения',
                ),
            ],
            id='check contract low balance',
        ),
        pytest.param(
            '-200',
            '2000',
            [
                dict(
                    SUCCESS_RESPONSE,
                    client_id='client_happy_path_prepaid',
                    can_order=False,
                    order_disable_reason='Недостаточно денег на счёте',
                ),
            ],
            id='check contract over limit',
        ),
        pytest.param(
            '-50',
            '3000',
            [dict(SUCCESS_RESPONSE, client_id='client_happy_path_prepaid')],
            id='check contract success',
        ),
    ],
)
async def test_balance_with_spendings(
        db,
        web_app_client,
        mockserver,
        load_json,
        deactivate_threshold,
        contract_limit,
        response_data,
):
    @mockserver.json_handler('/billing-reports/v1/balances/select')
    def _mock_balances(request):
        return load_json('billing_reports_get_balances.json')

    await db.corp_contracts.update_one(
        {'billing_client_id': '2000105'},
        {
            '$set': {
                'settings.prepaid_deactivate_threshold': deactivate_threshold,
                'settings.contract_limit.limit': contract_limit,
            },
        },
    )

    response = await _request_client_can_order(
        web_app_client,
        mockserver,
        'eats2',
        {'client_ids': ['client_happy_path_prepaid']},
        'moscow',
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {'statuses': response_data}


# тест логики округления даты на основе
# конфига CORP_BALANCE_DATES_ROUNDING_DAYS_DELAY
@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.config(CORP_INTEGRATION_API_USE_CLIENT_BALANCE=True)
@pytest.mark.now('2020-01-10T10:00:00+03:00')
@pytest.mark.parametrize(
    argnames=['deactivate_threshold', 'contract_limit', 'response_data'],
    argvalues=[
        pytest.param(
            '0',
            '3000',
            [
                dict(
                    SUCCESS_RESPONSE,
                    client_id='client_happy_path_prepaid',
                    can_order=False,
                    order_disable_reason='Баланс клиента ниже значения '
                    'порога отключения',
                ),
            ],
            id='check contract low balance',
        ),
    ],
)
async def test_balance_with_spendings_rounding(
        db,
        web_app_client,
        mockserver,
        load_json,
        deactivate_threshold,
        contract_limit,
        response_data,
):
    @mockserver.json_handler('/billing-reports/v1/balances/select')
    def _mock_balances(request):
        return load_json('billing_reports_get_balances_with_rounding.json')

    await db.corp_contracts.update_one(
        {'billing_client_id': '2000105'},
        {
            '$set': {
                'settings.prepaid_deactivate_threshold': deactivate_threshold,
                'settings.contract_limit.limit': contract_limit,
                'balance.balance_dt': datetime.datetime(
                    year=2020, month=1, day=1, minute=35,
                ),
            },
        },
    )

    response = await _request_client_can_order(
        web_app_client,
        mockserver,
        'eats2',
        {'client_ids': ['client_happy_path_prepaid']},
        'moscow',
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {'statuses': response_data}


@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.config(CORP_INTEGRATION_API_USE_CLIENT_BALANCE=True)
@pytest.mark.now('2020-01-02T10:00:00+03:00')
@pytest.mark.parametrize(
    argnames=[
        'deactivate_threshold',
        'contract_limit',
        'order',
        'response_data',
    ],
    argvalues=[
        pytest.param(
            '200',
            '0',
            None,
            [dict(SUCCESS_RESPONSE, client_id='client_happy_path_prepaid')],
            id='check contract success - no order info',
        ),
        pytest.param(
            '201',
            '0',
            None,
            [
                dict(
                    SUCCESS_RESPONSE,
                    client_id='client_happy_path_prepaid',
                    can_order=False,
                    order_disable_reason='Баланс клиента ниже значения '
                    'порога отключения',
                ),
            ],
            id='check contract low balance - no order info',
        ),
        pytest.param(
            '100',
            '0',
            {'order_price': '100.000'},
            [dict(SUCCESS_RESPONSE, client_id='client_happy_path_prepaid')],
            id='check contract success - have order info',
        ),
        pytest.param(
            '101',
            '0',
            {'order_price': '100.000'},
            [
                dict(
                    SUCCESS_RESPONSE,
                    client_id='client_happy_path_prepaid',
                    can_order=False,
                    order_disable_reason='Баланс клиента ниже значения '
                    'порога отключения',
                ),
            ],
            id='check contract low balance - have order info',
        ),
        pytest.param(
            '200',
            '-999999',
            None,
            [dict(SUCCESS_RESPONSE, client_id='client_happy_path_prepaid')],
            id='no check contract over limit if no info about spendings',
        ),
    ],
)
async def test_balance_checks_for_next_day_delivery(
        db,
        web_app_client,
        mockserver,
        load_json,
        deactivate_threshold,
        contract_limit,
        order,
        response_data,
):
    await db.corp_contracts.update_one(
        {'billing_client_id': '2000105'},
        {
            '$set': {
                'settings.prepaid_deactivate_threshold': deactivate_threshold,
                'settings.contract_limit.limit': contract_limit,
            },
        },
    )

    request = {'client_ids': ['client_happy_path_prepaid']}
    if order:
        request['order'] = order
    response = await _request_client_can_order(
        web_app_client, mockserver, 'next_day_delivery', request, 'moscow',
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {'statuses': response_data}
