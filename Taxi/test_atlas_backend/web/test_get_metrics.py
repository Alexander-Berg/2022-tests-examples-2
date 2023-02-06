async def test_get_metrics(web_app_client, first_metric_dict_filtered):
    response = await web_app_client.get('/api/v2/metrics')
    assert response.status == 200

    content = await response.json()
    assert len(content) == 10

    metric = next(
        (x for x in content if x['_id'] == 'requests_share_burnt'), None,
    )
    assert metric is not None

    # Emit sql_query_raw to not mocking it
    metric['sql_query_raw'] = None
    assert metric == first_metric_dict_filtered
