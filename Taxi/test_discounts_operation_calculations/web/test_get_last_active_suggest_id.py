import pytest


@pytest.mark.pgsql(
    'discounts_operation_calculations', files=['fill_pg_suggests.sql'],
)
async def test_get_last_active_suggest_id(web_app_client):
    # SUCCEEDED case
    response = await web_app_client.get(
        '/v1/last_active_suggest_id', params={'city': 'Москва'},
    )
    assert response.status == 200

    content = await response.json()
    assert content['last_suggest_id'] == 4

    # WAITING_TO_STOP case
    response = await web_app_client.get(
        '/v1/last_active_suggest_id', params={'city': 'Санкт-Петербург'},
    )
    assert response.status == 200

    content = await response.json()
    assert content['last_suggest_id'] == 6
    # not existed case
    response = await web_app_client.get(
        '/v1/last_active_suggest_id', params={'city': 'Бирюлёво'},
    )
    assert response.status == 200

    content = await response.json()
    assert content.get('last_suggest_id') is None
