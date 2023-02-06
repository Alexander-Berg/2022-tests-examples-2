import pytest


@pytest.mark.pgsql(
    'discounts_operation_calculations', files=['fill_pg_suggests_v2.sql'],
)
async def test_get_suggest_status(web_app_client):
    suggest_id = 1

    response = await web_app_client.get(f'/v2/suggests/{suggest_id}/status')
    assert response.status == 200
    content = await response.json()
    assert content == {'status': 'NOT_PUBLISHED'}
