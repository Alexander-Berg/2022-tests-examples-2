import pytest


@pytest.mark.config(FLEET_SUPPORT_CHAT_POLL_UPDATES={'enable': True})
@pytest.mark.pgsql('taxi_db_opteum', files=('taxi_db_opteum.sql',))
async def test_success(web_app_client, mock_parks, headers, load_json, patch):
    stub = load_json('success.json')

    response = await web_app_client.post(
        '/support-chat-api/v1/poll-updates',
        headers=headers,
        json={
            'chat_ids': [
                '5e218b322ca830162941c324',
                '5e218b322ca830162941c362',
            ],
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
