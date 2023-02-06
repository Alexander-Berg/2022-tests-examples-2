import pytest


@pytest.mark.pgsql('fleet_reports', files=('success.sql',))
async def test_success(web_app_client, headers, load_json):
    stub = load_json('success.json')

    response = await web_app_client.post(
        '/reports-api/v1/orders/moderation/moderation',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == 200
