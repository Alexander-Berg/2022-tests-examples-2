import aiohttp.web
import pytest


@pytest.mark.parametrize('from_master', [None, False, True])
async def test_work_rules(
        web_app_client,
        headers,
        mock_driver_work_rules,
        load_json,
        from_master,
):
    stub = load_json('success.json')
    stub_master = load_json('success_from_master.json')

    @mock_driver_work_rules('/v1/work-rules/list')
    async def _work_rules_list(request):
        assert request.json == stub['work_rules']['request']
        return aiohttp.web.json_response(stub['work_rules']['response'])

    @mock_driver_work_rules('/v1/work-rules/list-from-master')
    async def _work_rules_master_list(request):
        assert request.json == stub_master['work_rules']['request']
        return aiohttp.web.json_response(stub_master['work_rules']['response'])

    response = (
        await web_app_client.get(
            '/api/v1/work-rules?from_master=true', headers=headers,
        )
        if from_master
        else await web_app_client.get('/api/v1/work-rules', headers=headers)
    )
    assert response.status == 200

    data = await response.json()
    assert data == (
        stub_master['service_response']
        if from_master
        else stub['service_response']
    )
