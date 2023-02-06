import pytest


@pytest.mark.pgsql('fleet_reports', files=('success.sql',))
async def test_success(web_app_client, headers):
    response = await web_app_client.post(
        '/reports-api/v2/summary/parks/download', headers=headers, json={},
    )

    assert response.status == 200
