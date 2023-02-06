# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-lines

import pytest

from test_taxi_corp_integration_api import utils


METHOD_MAP = {
    '1a1a1a1a1a1a1a1a1a1a1a1a': {
        'type': 'corp',
        'id': 'corp-client_id_1',
        'label': 'Yandex.Uber team',
        'description': 'Осталось 4000 из 5000 руб.',
        'cost_center': 'cost center',
        'cost_centers': utils.OLD_COST_CENTER_VALUE,
        'cost_center_fields': utils.OLD_COST_CENTER_NEW_FORMAT,
        'can_order': True,
        'zone_available': True,
        'hide_user_cost': False,
        'user_id': 'user_id_1',
        'client_comment': 'comment',
        'currency': 'RUB',
        'classes_available': ['econom'],
        'without_vat_contract': False,
    },
    'no_user': {
        'type': 'corp',
        'id': 'corp-client_id_1',
        'label': 'Yandex.Uber team',
        'description': '',
        'cost_center': '',
        'cost_centers': utils.OLD_COST_CENTER_VALUE,
        'cost_center_fields': utils.OLD_COST_CENTER_NEW_FORMAT,
        'can_order': True,
        'zone_available': True,
        'hide_user_cost': False,
        'client_comment': 'comment',
        'currency': 'RUB',
        'classes_available': ['cargo', 'courier', 'express', 'cargocorp'],
    },
}

OLD_COST_CENTER_W_TEXT = {
    'required': True,
    'format': 'text',
    'values': ['123', '456'],
}
OLD_COST_CENTER_W_TEXT_NEW_FORMAT = utils.new_fields_from_old_value(
    OLD_COST_CENTER_W_TEXT,
)
OLD_COST_CENTER_W_SELECT = {
    'required': False,
    'format': 'select',
    'values': ['123', '456'],
}
OLD_COST_CENTER_W_SELECT_NEW_FORMAT = utils.new_fields_from_old_value(
    OLD_COST_CENTER_W_SELECT,
)
OLD_COST_CENTER_W_SELECT_TRUE = dict(OLD_COST_CENTER_W_SELECT, required=True)
OLD_COST_CENTER_W_SELECT_TRUE_NEW_FORMAT = utils.new_fields_from_old_value(
    OLD_COST_CENTER_W_SELECT_TRUE,
)


TEST_CORP_PAYMENTMETHODS_PARAMS = dict(
    argnames=['request_data', 'method', 'zone_name'],
    argvalues=[
        pytest.param(
            {
                'identity': {
                    'uid': '12345678',
                    'phone_id': '1a1a1a1a1a1a1a1a1a1a1a1a',
                },
                'class': 'econom',
                'order_price': '400',
            },
            METHOD_MAP['1a1a1a1a1a1a1a1a1a1a1a1a'],
            'moscow',
            id='0',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'identity': {
                    'uid': '12345678',
                    'phone_id': '1a1a1a1a1a1a1a1a1a1a1a1a',
                },
                'route': [{'geopoint': [37.59, 55.73]}],
                'cost_center': '123',
                'class': 'econom',
                'order_price': '400.00',
            },
            dict(
                METHOD_MAP['1a1a1a1a1a1a1a1a1a1a1a1a'],
                cost_center='123',
                zone_available=False,
                zone_disable_reason=(
                    'Страна клиента не совпадает со страной заказа'
                ),
            ),
            'almaty',
            id='1',
        ),
        pytest.param(
            {
                'identity': {
                    'uid': '12345678',
                    'phone_id': '1a1a1a1a1a1a1a1a1a1a1a1a',
                },
                'class': 'vip',
                'order_price': '400',
            },
            dict(
                METHOD_MAP['1a1a1a1a1a1a1a1a1a1a1a1a'],
                can_order=False,
                order_disable_reason='Бизнес недоступны',
            ),
            'moscow',
            id='2',
        ),
        pytest.param(
            {
                'identity': {
                    'uid': '12345678',
                    'phone_id': '1a1a1a1a1a1a1a1a1a1a1a1a',
                },
                'source': {'app': 'call_center'},
            },
            METHOD_MAP['1a1a1a1a1a1a1a1a1a1a1a1a'],
            'moscow',
            id='4',
        ),
        pytest.param(
            {
                'client_id': 'client_id_3',
                'identity': {
                    'uid': '12345678',
                    'phone_id': '4a1a1a1a1a1a1a1a1a1a1a1a',
                },
                'cost_center': '123',
                'source': {'app': 'corpweb'},
            },
            {
                'type': 'corp',
                'id': 'corp-client_id_3',
                'label': '3 name',
                'description': '',
                'cost_center': '123',
                'cost_centers': OLD_COST_CENTER_W_SELECT_TRUE,
                'cost_center_fields': OLD_COST_CENTER_W_SELECT_TRUE_NEW_FORMAT,
                'can_order': True,
                'zone_available': True,
                'hide_user_cost': False,
                'user_id': 'user_id_4',
                'client_comment': '',
                'currency': 'RUB',
                'classes_available': ['econom', 'vip'],
                'without_vat_contract': False,
            },
            'moscow',
            id='6',
        ),
        pytest.param(
            {
                'identity': {
                    'uid': '12345678',
                    'phone_id': '2a1a1a1a1a1a1a1a1a1a1a1a',
                },
                'source': {'app': 'call_center'},
            },
            None,
            'moscow',
            id='7',
        ),
        pytest.param(
            {
                'identity': {
                    'uid': '12345678',
                    'phone_id': '3a1a1a1a1a1a1a1a1a1a1a1a',
                },
                'source': {'app': 'yataxi_application'},
            },
            None,
            'moscow',
            id='8',
        ),
        pytest.param(
            {
                'identity': {
                    'uid': '12345678',
                    'phone_id': '1a1a1a1a1a1a1a1a1a1a1a1a',
                },
            },
            METHOD_MAP['1a1a1a1a1a1a1a1a1a1a1a1a'],
            'moscow',
            id='9',
        ),
        pytest.param(
            {
                'client_id': 'not_found',
                'identity': {
                    'uid': '12345678',
                    'phone_id': '1a1a1a1a1a1a1a1a1a1a1a1a',
                },
                'class': 'vip',
            },
            None,
            'moscow',
            id='14',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'identity': {
                    'uid': '12345678',
                    'phone_id': '8a1a1a1a1a1a1a1a1a1a1a1a',
                },
                'source': {'app': 'call_center'},
            },
            None,
            'moscow',
            id='17',
        ),
        pytest.param(
            {
                'identity': {
                    'uid': '12345678',
                    'phone_id': '1a1a1a1a1a1a1a1a1a1a1a1a',
                },
                'source': {'app': 'alice'},
                'class': 'econom',
                'order_price': '400',
            },
            METHOD_MAP['1a1a1a1a1a1a1a1a1a1a1a1a'],
            'moscow',
            id='20',
        ),
        pytest.param(
            {'source': {'app': 'cargo'}, 'client_id': 'client_id_1'},
            METHOD_MAP['no_user'],
            'moscow',
            id='no_user',
        ),
        pytest.param(
            {
                'identity': {
                    'uid': '12345678',
                    'phone_id': '20a1a1a1a1a1a1a1a1a1a1a1',
                },
                'source': {'app': 'corpweb'},
            },
            dict(
                METHOD_MAP['1a1a1a1a1a1a1a1a1a1a1a1a'],
                user_id='user_id_20',
                id='corp-client_id_12',
                classes_available=['econom', 'vip', 'start'],
                description='',
            ),
            'moscow',
            id='client_categories',
        ),
    ],
)


CORP_PAYMENTMETHODS_CONFIG = {
    'CORP_CARGO_CATEGORIES': {
        '__default__': {
            'cargo': 'name.cargo',
            'courier': 'name.courier',
            'express': 'name.express',
            'cargocorp': 'name.cargocorp',
        },
    },
    'CORP_CARGO_DEFAULT_CATEGORIES': {
        'rus': ['cargo', 'courier', 'express', 'cargocorp'],
    },
    'CORP_SOURCES_NO_USER': ['cargo'],
    'APPLICATION_TO_CORP_SOURCE_MAP': {'test': 'alice', 'cargo': 'cargo'},
    'CORP_INTEGRATION_API_SPLIT_TRANSLATIONS': True,
    'CORP_ORDERS_COUNT_LIMIT_ENABLED': True,
    'CORP_CLIENTS_ORDERS_COUNT_LIMIT': {'client_id_1': 1, 'client_id_11': 2},
    'CORP_CLIENTS_WITH_UNCHECKED_OFFER_ACCEPTED': ['client_id_15'],
    'CORP_INTEGRATION_API_USE_CLIENT_BALANCE': True,
}


@pytest.mark.config(**utils.CONFIG)
@pytest.mark.config(**CORP_PAYMENTMETHODS_CONFIG)
@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.parametrize(**TEST_CORP_PAYMENTMETHODS_PARAMS)
@pytest.mark.now('2019-11-02T10:02:03+0300')
async def test_corp_paymentmethods(
        db,
        taxi_config,
        mockserver,
        mock_billing,
        exp3_decoupling_mock,
        taxi_corp_integration_api,
        request_data,
        method,
        zone_name,
):
    response = await utils.request_corp_paymentmethods(
        taxi_corp_integration_api, mockserver, request_data, zone_name, None,
    )
    assert await response.json() == {'methods': [method] if method else []}
    assert response.status == 200


CORP_PAYMENTMETHODS_CONFIG = {
    'CORP_CARGO_CATEGORIES': {
        '__default__': {
            'cargo': 'name.cargo',
            'courier': 'name.courier',
            'express': 'name.express',
            'cargocorp': 'name.cargocorp',
        },
    },
    'CORP_CARGO_DEFAULT_CATEGORIES': {
        'rus': ['cargo', 'courier', 'express', 'cargocorp'],
    },
    'CORP_SOURCES_NO_USER': ['cargo'],
    'APPLICATION_TO_CORP_SOURCE_MAP': {'test': 'alice', 'cargo': 'cargo'},
    'CORP_INTEGRATION_API_SPLIT_TRANSLATIONS': True,
    'CORP_ORDERS_COUNT_LIMIT_ENABLED': True,
    'CORP_CLIENTS_ORDERS_COUNT_LIMIT': {'client_id_1': 1, 'client_id_11': 2},
    'CORP_CLIENTS_WITH_UNCHECKED_OFFER_ACCEPTED': ['client_id_15'],
    'CORP_INTEGRATION_API_USE_CLIENT_BALANCE': True,
}


@pytest.mark.config(**utils.CONFIG)
@pytest.mark.config(**CORP_PAYMENTMETHODS_CONFIG)
@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.parametrize(
    argnames=['request_data', 'contract_patch', 'method'],
    argvalues=[
        pytest.param(
            {
                'client_id': 'client_id_1',
                'identity': {'phone_id': '1a1a1a1a1a1a1a1a1a1a1a1a'},
                'class': 'econom',
                'order_price': '400',
            },
            {'service_ids': [650]},
            dict(
                METHOD_MAP['1a1a1a1a1a1a1a1a1a1a1a1a'],
                without_vat_contract=False,
            ),
            id='common_service',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'identity': {'phone_id': '1a1a1a1a1a1a1a1a1a1a1a1a'},
                'class': 'econom',
                'order_price': '400',
            },
            {'service_ids': [1181, 1183]},
            dict(
                METHOD_MAP['1a1a1a1a1a1a1a1a1a1a1a1a'],
                without_vat_contract=True,
            ),
            id='agent_services',
        ),
    ],
)
@pytest.mark.now('2019-11-02T10:02:03+0300')
async def test_corp_paymentmethods_without_vat(
        db,
        taxi_config,
        mockserver,
        mock_billing,
        exp3_decoupling_mock,
        taxi_corp_integration_api,
        request_data,
        contract_patch,
        method,
):
    if contract_patch is not None:
        client = await db.corp_clients.find_one({'_id': 'client_id_1'})
        await db.corp_contracts.update_one(
            {'billing_client_id': client['billing_id']},
            {'$set': contract_patch},
        )

    response = await utils.request_corp_paymentmethods(
        taxi_corp_integration_api, mockserver, request_data, 'moscow', None,
    )
    assert await response.json() == {'methods': [method] if method else []}
    assert response.status == 200


@pytest.mark.parametrize(
    ['request_data', 'expected_error'],
    [
        pytest.param(
            {
                'identity': {
                    'uid': '12345678',
                    'phone_id': '1a1a1a1a1a1a1a1a1a1a1a1a',
                },
                'source': {'app': 'wrong_alice'},
                'class': 'econom',
                'order_price': '400',
            },
            {
                'code': 'INVALID_INPUT',
                'details': {'identity.source_app': ['unknown source app']},
                'message': 'Invalid input',
            },
            id='unknown_source_app',
        ),
        pytest.param(
            {
                'client_id': 'client_id_3',
                'identity': {
                    'uid': '12345678',
                    'phone_id': '4a1a1a1a1a1a1a1a1a1a1a1a',
                },
                'cost_center': '1234' * 76,
                'source': {'app': 'corpweb'},
            },
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'reason': (
                        'Invalid value for cost_center: \''
                        + '1234' * 76
                        + '\' length must be less than or equal to 300'
                    ),
                },
                'message': 'Some parameters are invalid',
            },
            id='invalid_cost_center',
        ),
        pytest.param(
            {'client_id': 'client_id_3', 'source': {'app': 'corpweb'}},
            {
                'code': 'INVALID_INPUT',
                'details': {
                    'identity': [
                        'identity is required for source.app "corpweb"',
                    ],
                },
                'message': 'Invalid input',
            },
            id='no_user',
        ),
        pytest.param(
            {'client_id': 'client_id_3'},
            {
                'code': 'INVALID_INPUT',
                'details': {
                    'identity': [
                        'identity is required for requests without source.app',
                    ],
                },
                'message': 'Invalid input',
            },
            id='no_user_no_source',
        ),
    ],
)
@pytest.mark.config(
    APPLICATION_TO_CORP_SOURCE_MAP={'test': 'alice'},
    CORP_INTEGRATION_API_USE_CLIENT_BALANCE=True,
)
async def test_400(
        db,
        mockserver,
        taxi_config,
        mock_billing,
        exp3_decoupling_mock,
        taxi_corp_integration_api,
        request_data,
        expected_error,
):
    response = await utils.request_corp_paymentmethods(
        taxi_corp_integration_api, mockserver, request_data, 'moscow', None,
    )
    assert await response.json() == expected_error
    assert response.status == 400


@pytest.mark.config(**utils.CONFIG)
@pytest.mark.config(CORP_INTEGRATION_API_USE_CLIENT_BALANCE=True)
@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.parametrize(
    ['request_data', 'expected_response', 'nearestzone_error', 'status_code'],
    [
        (
            {
                'identity': {
                    'uid': '12345678',
                    'phone_id': '1a1a1a1a1a1a1a1a1a1a1a1a',
                },
                'class': 'vip',
                'route': [{'geopoint': [37.59, 55.73]}],
            },
            {
                'methods': [
                    dict(
                        METHOD_MAP['1a1a1a1a1a1a1a1a1a1a1a1a'],
                        can_order=False,
                        order_disable_reason='Бизнес недоступны',
                        zone_available=False,
                        zone_disable_reason='Зона недоступна',
                    ),
                ],
            },
            {
                'status': 404,
                'json': {
                    'code': 'NOT_FOUND',
                    'error': {'message': 'Not found'},
                },
            },
            200,
        ),
        (
            {
                'identity': {
                    'uid': '12345678',
                    'phone_id': '1a1a1a1a1a1a1a1a1a1a1a1a',
                },
                'class': 'vip',
                'route': [{'geopoint': [37.59, 55.73]}],
            },
            {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'failed to fetch nearestzone',
                'details': {
                    'internal-error': [
                        'protocol /3.0/nearestzone does not '
                        'respond to requests',
                    ],
                },
            },
            {
                'status': 500,
                'json': {
                    'code': 'INTERNAL_SERVER_ERROR',
                    'error': {'message': 'oh'},
                },
            },
            500,
        ),
    ],
)
@pytest.mark.now('2019-11-02T01:02:03')
async def test_corp_paymentmethods_raise_nearestzone(
        db,
        mockserver,
        taxi_config,
        mock_billing,
        exp3_decoupling_mock,
        taxi_corp_integration_api,
        request_data,
        expected_response,
        nearestzone_error,
        status_code,
):
    response = await utils.request_corp_paymentmethods(
        taxi_corp_integration_api,
        mockserver,
        request_data,
        'ekb',
        nearestzone_error,
    )

    assert response.status == status_code
    assert await response.json() == expected_response


@pytest.mark.config(**utils.CONFIG)
@pytest.mark.config(CORP_INTEGRATION_API_USE_CLIENT_BALANCE=True)
@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.parametrize(
    'request_data, zone_name, accept_language, expected',
    [
        (
            {
                'identity': {
                    'uid': '',
                    'phone_id': '13a1a1a1a1a1a1a1a1a1a1a1',
                },
                'class': 'econom',
                'order_price': '400',
            },
            'moscow',
            'q=1, en-Us;tr-RU;q=0.9, ru-RU;q=0.8, en-AU;q=0.7, az-RU;q=0.6"',
            'Left',
        ),
        (
            {
                'identity': {
                    'uid': '',
                    'phone_id': '13a1a1a1a1a1a1a1a1a1a1a1',
                },
                'class': 'econom',
                'order_price': '400',
            },
            'moscow',
            'tr-RU;q=1, ru-RU;q=0.9, en-AU;q=0.8, az-RU;q=0.7"',
            'Осталось',
        ),
    ],
)
async def test_corp_paymentmethods_detect_locale(
        db,
        mockserver,
        taxi_config,
        mocked_time,
        mock_billing,
        exp3_decoupling_mock,
        taxi_corp_integration_api,
        request_data,
        zone_name,
        accept_language,
        expected,  # First word of tanker key "description"
):
    response = await utils.request_corp_paymentmethods(
        taxi_corp_integration_api,
        mockserver,
        request_data,
        zone_name,
        None,
        headers={'Accept-Language': accept_language},
    )
    assert response.status == 200
    data = await response.json()
    assert data['methods'][0]['description'].startswith(expected)


TEST_CORP_PAYMENTMETHODS_GEO_RESTRICTIONS_PARAMS = dict(
    argnames='additional_data, geo_restrictions, method',
    argvalues=[
        (
            dict(
                route=[
                    {'geopoint': [37.59, 55.73]},
                    {'geopoint': [37.60, 55.74]},
                ],
            ),
            [{'source': 'geo_id_1', 'destination': 'geo_id_2'}],
            {},
        ),  # 0
        (
            dict(
                route=[
                    {'geopoint': [37.60, 55.74]},
                    {'geopoint': [37.59, 55.73]},
                ],
            ),
            [{'source': 'geo_id_1', 'destination': 'geo_id_2'}],
            dict(
                zone_available=False,
                zone_disable_reason='error.order_is_restricted_in_the_geo',
            ),
        ),  # 1
    ],
)


@pytest.mark.config(
    ALL_CATEGORIES=['econom'], CORP_INTEGRATION_API_USE_CLIENT_BALANCE=True,
)
@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.parametrize(**TEST_CORP_PAYMENTMETHODS_GEO_RESTRICTIONS_PARAMS)
async def test_corp_paymentmethods_geo_restrictions(
        db,
        mockserver,
        taxi_config,
        mock_billing,
        exp3_decoupling_mock,
        taxi_corp_integration_api,
        additional_data,
        geo_restrictions,
        method,
):
    request_data = {
        'identity': {
            'uid': '12345678',
            'phone_id': '1a1a1a1a1a1a1a1a1a1a1a1a',
        },
        'class': 'econom',
    }
    request_data.update(additional_data)

    await db.corp_limits.update_one(
        {'_id': 'limit_id_1'},
        {'$set': {'geo_restrictions': geo_restrictions}},
    )

    response = await utils.request_corp_paymentmethods(
        taxi_corp_integration_api, mockserver, request_data, 'moscow', None,
    )

    method = dict(
        {
            'type': 'corp',
            'id': 'corp-client_id_1',
            'label': 'Yandex.Uber team',
            'description': 'Осталось 5000 из 5000 руб.',
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
