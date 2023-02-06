import pytest


@pytest.mark.now('2020-01-01T03:00:00+03:00')
@pytest.mark.pgsql('fleet_feedback', files=('simple_poll.sql',))
async def test_success(web_app_client, headers, load_json):
    stub = load_json('common.json')

    response = await web_app_client.post(
        '/admin/v1/polls/list',
        headers=headers,
        json=stub['service']['success_request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['success_response']
