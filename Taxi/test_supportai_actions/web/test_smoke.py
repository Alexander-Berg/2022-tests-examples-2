import aiohttp
import pytest


@pytest.fixture(name='mock_service')
def _mock_service(monkeypatch, response_mock):
    def request(**_):
        class JsonRequestContextManager:
            async def __aenter__(self):
                return response_mock(status=200, json=[{'hello': 'hello'}])

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        return JsonRequestContextManager()

    monkeypatch.setattr(aiohttp, 'request', request)


@pytest.mark.parametrize(
    'action_id, project_id, version, _status',
    [
        ('echo', 'echo', '0', 200),
        ('echo', 'smoke2', '0', 404),
        ('test_smoke', 'echo', '0', 404),
        ('echo', 'echo', '-1', 404),
        ('generic_action', 'some_project', '1', 200),
    ],
)
async def test_smoke(
        web_app_client, action_id, project_id, version, _status, mock_service,
):
    async def check_response(response_):
        assert response_.status == _status
        if _status != 200:
            return

        response_json = await response.json()
        debug_info = response_json.get('debug_info', 'sentinel-like')
        if action_id == 'generic_action':
            assert debug_info == '[\n  {\n    "hello": "hello"\n  }\n]'
        else:
            assert debug_info == 'sentinel-like'

    params = []
    if action_id == 'generic_action':
        params = [
            {'url': 'some://url', 'method': 'GET', 'body_format': 'json'},
        ]

    response = await web_app_client.post(
        f'/v1/action/validate?'
        f'action_id={action_id}'
        f'&project_id={project_id}'
        f'&version={version}'
        f'&simulated=false',
        json={'params': params},
    )

    assert response.status == _status

    response = await web_app_client.post(
        f'/supportai-actions/v1/action?'
        f'action_id={action_id}'
        f'&project_id={project_id}'
        f'&version={version}'
        f'&simulated=false',
        json={'params': params, 'state': {'features': []}},
    )

    await check_response(response)
