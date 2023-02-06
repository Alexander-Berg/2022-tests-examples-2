async def test_get_filters_list(web_app_client):
    response = await web_app_client.get(
        '/v1/filters/list/', headers={'X-YaTaxi-Api-Key': 'secret'},
    )
    assert response.status == 200
    filter_by_keys = {
        item['key']: item for item in (await response.json())['filters']
    }
    assert filter_by_keys
    assert 'protocol' in filter_by_keys['meta_order_id']['service_names']
