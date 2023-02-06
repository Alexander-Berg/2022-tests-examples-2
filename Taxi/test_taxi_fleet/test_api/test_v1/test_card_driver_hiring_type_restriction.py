import aiohttp.web


async def test_success(
        web_app_client, headers, mock_driver_work_modes, load_json,
):
    stub = load_json('success.json')

    @mock_driver_work_modes(
        '/v1/parks/driver-profiles/hiring-type-restriction',
    )
    async def __hiring_type_restriction(request):
        assert request.query == stub['dp_request']
        return aiohttp.web.json_response(stub['dp_response'])

    response = await web_app_client.post(
        '/api/v1/cards/driver/hiring-type-restriction',
        headers=headers,
        json={'driver_license': 'test'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
