async def test_instances_list_get(web_app_client):
    response = await web_app_client.get('/v1/admin/instances/list')

    assert response.status == 200
    body = await response.json()
    assert body == {
        'instances': [
            {'name': 'atlas-proxy'},
            {'name': 'order-events-producer'},
        ],
    }
