import pytest

from taxi.clients import integration_api

BASE_RESPONSE = {
    'currency_rules': {'code': 'RUB'},
    'is_fixed_price': True,
    'service_levels': [{'class': 'econom'}],
}

BASE_ORDER: dict = {
    'phone': '+79169222964',
    'requirements': {'nosmoking': True, 'door_to_door': False},
    'route': [[10.0, 10.0]],
    'selected_class': 'econom',
    'format_currency': True,
}

BASE_CALL: dict = {
    'payment': {'payment_method_id': 'corp-client_id', 'type': 'corp'},
    'requirements': {'nosmoking': True},
    'route': [[10.0, 10.0]],
    'selected_class': 'econom',
    'sourceid': 'corp_cabinet',
    'user': {'phone': '+79169222964'},
    'format_currency': True,
}


@pytest.mark.parametrize(
    [
        'api_response_code',
        'integration_response',
        'corp_response',
        'expected_status',
    ],
    [
        (200, {'first': 'second', 'offer': 'offer'}, {'offer': 'offer'}, 200),
        (404, {}, {}, 400),
        (403, {}, {}, 406),
        (500, {}, {}, 500),
    ],
)
async def test_order_estimate(
        taxi_corp_real_auth_client,
        patch,
        patch_doc,
        api_response_code,
        integration_response,
        corp_response,
        expected_status,
):
    @patch('taxi.clients.integration_api.IntegrationAPIClient.order_estimate')
    async def _order_estimate(*args, **kwargs):
        return integration_api.APIResponse(
            status=api_response_code,
            data=patch_doc(BASE_RESPONSE, integration_response),
            headers={},
        )

    @patch('taxi.clients.passport.get_passport_info')
    async def _get_passport_info(*args, **kwargs):
        return {'uid': 'client_uid', 'login': 'client_login'}

    response = await taxi_corp_real_auth_client.post(
        '/1.0/estimate', json=BASE_ORDER,
    )

    assert _order_estimate.calls[0]['kwargs']['data'] == BASE_CALL

    assert response.status == expected_status
    if response.status == 200:
        assert await response.json() == patch_doc(BASE_RESPONSE, corp_response)


async def test_order_estimate_all_classes(
        taxi_corp_real_auth_client, patch, patch_doc,
):
    @patch('taxi.clients.integration_api.IntegrationAPIClient.order_estimate')
    async def _order_estimate(*args, **kwargs):
        new_service_levels = [
            {'class': 'econom'},
            {'class': 'business'},
            {'class': 'vip'},
        ]

        return integration_api.APIResponse(
            status=200,
            data=patch_doc(
                dict(BASE_RESPONSE, service_levels=new_service_levels), {},
            ),
            headers={},
        )

    @patch('taxi.clients.passport.get_passport_info')
    async def _get_passport_info(*args, **kwargs):
        return {'uid': 'client_uid', 'login': 'client_login'}

    order = dict(BASE_ORDER, all_classes=True)
    response = await taxi_corp_real_auth_client.post(
        '/1.0/estimate', json=order,
    )

    assert _order_estimate.calls[0]['kwargs']['data'] == dict(
        BASE_CALL, all_classes=True,
    )

    assert response.status == 200
    assert await response.json() == patch_doc(BASE_RESPONSE, {})


@pytest.mark.parametrize(
    [
        'api_response_code',
        'integration_response',
        'corp_response',
        'expected_status',
    ],
    [
        (200, {'first': 'second', 'offer': 'offer'}, {'offer': 'offer'}, 200),
        (404, {}, {}, 400),
        (403, {}, {}, 406),
        (500, {}, {}, 500),
    ],
)
async def test_combo_order_estimate(
        taxi_corp_real_auth_client,
        patch,
        patch_doc,
        api_response_code,
        integration_response,
        corp_response,
        expected_status,
):
    @patch('taxi.clients.integration_api.IntegrationAPIClient.order_estimate')
    async def _order_estimate(*args, **kwargs):
        service_levels = [{'class': kwargs['data']['selected_class']}]
        return integration_api.APIResponse(
            status=api_response_code,
            data=patch_doc(
                dict(BASE_RESPONSE, service_levels=service_levels),
                integration_response,
            ),
            headers={},
        )

    @patch('taxi.clients.passport.get_passport_info')
    async def _get_passport_info(*args, **kwargs):
        return {'uid': 'client_uid', 'login': 'client_login'}

    post_content = {
        'orders': [BASE_ORDER, dict(BASE_ORDER, selected_class='comfort')],
    }
    response = await taxi_corp_real_auth_client.post(
        '/1.0/combo/estimate', json=post_content,
    )

    _expected_order_estimate_calls = [
        BASE_CALL,
        dict(BASE_CALL, selected_class='comfort'),
    ]
    _order_estimate_calls = [
        call['kwargs']['data'] for call in _order_estimate.calls
    ]
    assert len(_order_estimate_calls) == len(_expected_order_estimate_calls)
    for item in _order_estimate_calls:
        assert item in _expected_order_estimate_calls

    assert response.status == expected_status
    if response.status == 200:
        expected_response = {
            'orders': [
                patch_doc(BASE_RESPONSE, corp_response),
                patch_doc(
                    dict(BASE_RESPONSE, service_levels=[{'class': 'comfort'}]),
                    corp_response,
                ),
            ],
        }
        assert await response.json() == expected_response
