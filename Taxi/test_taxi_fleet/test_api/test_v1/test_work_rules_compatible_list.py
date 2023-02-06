import aiohttp.web


async def test_work_rules(
        web_app_client, headers, mock_driver_work_rules, load_json,
):
    stub = load_json('success.json')

    @mock_driver_work_rules('/v1/dispatcher/work-rules/compatible/list')
    async def _work_rules_compatible_list(request):
        assert request.json == stub['work_rules']['request']
        return aiohttp.web.json_response(stub['work_rules']['response'])

    response = await web_app_client.post(
        '/api/v1/work-rules/compatible/list',
        headers=headers,
        json=stub['service']['request'],
    )
    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']
