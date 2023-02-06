async def test_external_echo(taxi_userver_sample):
    test_header_name = 'Echo-Test-Header'
    test_header_value = 'test header value'
    empty_header_name = 'Echo-Test-Empty'

    params = {'hello': 'world'}
    headers = {test_header_name: test_header_value, empty_header_name: ''}
    response = await taxi_userver_sample.get(
        'external-echo', params=params, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {'response': params}
    assert response.headers.get(test_header_name) == test_header_value
    assert response.headers.get(empty_header_name) == ''
