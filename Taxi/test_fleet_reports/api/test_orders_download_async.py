import aiohttp.web


async def test_success(
        web_app_client,
        headers,
        mock_parks,
        mock_fleet_reports_storage,
        patch,
        load_json,
):
    stub = load_json('success.json')

    @patch('uuid.uuid4')
    def _uuid4():
        class _uuid4:
            hex = 'base_operation_00000000000000001'

        return _uuid4()

    @mock_fleet_reports_storage('/internal/user/v1/operations/create')
    async def _create(request):
        frs = stub['fleet_reports_storage']
        assert request.json == frs['request']
        return aiohttp.web.json_response()

    response = await web_app_client.post(
        '/reports-api/v1/orders/download-async',
        headers=headers,
        json=stub['service']['request'],
        params={'operation_id': 'base_operation_00000000000000001'},
    )

    assert response.status == 204


async def test_429(
        web_app_client,
        headers,
        mock_parks,
        mock_fleet_reports_storage,
        patch,
        load_json,
):
    stub = load_json('success.json')

    @patch('uuid.uuid4')
    def _uuid4():
        class _uuid4:
            hex = 'base_operation_00000000000000001'

        return _uuid4()

    @mock_fleet_reports_storage('/internal/user/v1/operations/create')
    async def _create(request):
        return aiohttp.web.json_response(
            status=429, data={'code': 'NO_QUOTA', 'message': 'no quota'},
        )

    response = await web_app_client.post(
        '/reports-api/v1/orders/download-async',
        headers=headers,
        json=stub['service']['request'],
        params={'operation_id': 'base_operation_00000000000000001'},
    )

    assert response.status == 429

    data = await response.json()
    assert data['code'] == 'NO_QUOTA'
