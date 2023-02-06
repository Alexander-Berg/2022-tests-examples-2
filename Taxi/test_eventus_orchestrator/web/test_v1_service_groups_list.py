# pylint:disable=no-member
# type: ignore


async def test_base(web_app_client):
    response = await web_app_client.post('/v1/service/groups/list')
    assert response.status == 200
    body = await response.json()
    assert sorted(body['polygon_groups']) == ['group1', 'group2', 'group3']
