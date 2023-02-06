async def test_get(web_app_client, load_json):
    # check for existing static consumer name
    await web_app_client.post(
        f'/taxi-surge/register/',
        json={
            'service_balancer_hostname': 'surge-calculator',
            'service_tvm_name': 'surge-calculator',
        },
    )

    response = await web_app_client.get(
        '/cache/taxi-surge/pipeline/',
        params={'id': '5de7baf5eb70bf332afa25f0'},
    )
    assert response.status == 200

    expected = load_json('taxi_cache_get_5de7baf5eb70bf332afa25f0.json')
    actual = await response.json()

    assert actual == expected

    # query missing
    response = await web_app_client.get(
        '/cache/taxi-surge/pipeline/', params={'id': 'missing'},
    )
    assert response.status == 404

    # query existing but for wrong consumer
    response = await web_app_client.get(
        '/cache/eda-surge/pipeline/',
        params={'id': '5de7baf5eb70bf332afa25f0'},
    )
    assert response.status == 404
