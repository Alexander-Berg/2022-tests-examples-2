async def test_get_metric_existed(web_app_client, second_metric_dict_filtered):
    response = await web_app_client.get('/api/v2/metrics/requests_share_found')
    assert response.status == 200

    content = await response.json()
    # Emit sql_query_raw to not mocking it
    content['sql_query_raw'] = None
    assert content == second_metric_dict_filtered


async def test_get_metric_nonexisted(web_app_client):
    response = await web_app_client.get(
        '/api/v2/metrics/requests_share_foundd',
    )
    assert response.status == 404

    content = await response.json()
    assert content['code'] == 'NotFound'
    assert content['message'] == 'Metric was not found'
