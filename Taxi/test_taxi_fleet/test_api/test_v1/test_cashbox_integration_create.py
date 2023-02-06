import aiohttp.web


async def test_success_atol(
        web_app_client, headers, mock_cashbox_integration, load_json,
):
    stub = load_json('success.json')

    @mock_cashbox_integration('/v1/parks/cashboxes')
    async def _cashbox_create(request):
        assert request.json == stub['cashbox_atol_request']
        return aiohttp.web.json_response(stub['cashbox_atol_response'])

    response = await web_app_client.post(
        '/api/v1/cashbox-integration/create',
        headers=headers,
        json={
            'cashbox': {
                'login': 'login',
                'password': 'password',
                'cashbox_type': 'atol_online',
                'tax_identification_number': '012345678999',
                'tax_scheme_type': 'simple',
                'group_code': '33',
            },
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_atol_response']


async def test_success_orange(
        web_app_client, headers, mock_cashbox_integration, load_json,
):
    stub = load_json('success.json')

    @mock_cashbox_integration('/v1/parks/cashboxes')
    async def _cashbox_create(request):
        assert request.json == stub['cashbox_orange_request']
        return aiohttp.web.json_response(stub['cashbox_orange_response'])

    response = await web_app_client.post(
        '/api/v1/cashbox-integration/create',
        headers=headers,
        json={
            'cashbox': {
                'signature_private_key': 'signature_private_key',
                'cashbox_type': 'orange_data',
                'tax_identification_number': '012345678999',
                'tax_scheme_type': 'simple',
                'group_code': '33',
            },
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_orange_response']


async def test_success_cloud(
        web_app_client, headers, mock_cashbox_integration, load_json,
):
    stub = load_json('success.json')

    @mock_cashbox_integration('/v1/parks/cashboxes')
    async def _cashbox_create(request):
        assert request.json == stub['cashbox_cloud_request']
        return aiohttp.web.json_response(stub['cashbox_cloud_response'])

    response = await web_app_client.post(
        '/api/v1/cashbox-integration/create',
        headers=headers,
        json={
            'cashbox': {
                'api_secret': 'api_secret',
                'public_id': 'public_id',
                'cashbox_type': 'cloud_kassir',
                'tax_identification_number': '012345678999',
                'tax_scheme_type': 'simple',
                'group_code': '33',
            },
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_cloud_response']
