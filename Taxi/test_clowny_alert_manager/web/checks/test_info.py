import pytest


HEJMDAL_BAD_RPS_INFO = {
    'source': 'hejmdal',
    'description': 'mock description',
    'url': 'https://wiki.yandex-team.ru/taxi/backend/hejmdal/bad-rps/',
}


@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_CHECKS_INFO={
        'check_infos': {'hejmdal-bad-rps': HEJMDAL_BAD_RPS_INFO},
    },
)
async def test_get_check_info(web_app_client):
    response = await web_app_client.get(
        '/v1/checks/info/?check_name=hejmdal-bad-rps',
    )
    assert response.status == 200
    resp_json = await response.json()
    assert resp_json == HEJMDAL_BAD_RPS_INFO

    response = await web_app_client.get(
        '/v1/checks/info/?check_name=invalid-check',
    )
    assert response.status == 404
