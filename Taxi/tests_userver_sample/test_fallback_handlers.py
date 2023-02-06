async def test_implicit_options(taxi_userver_sample):
    response = await taxi_userver_sample.options('autogen/empty')
    assert response.status_code == 200
    assert set(response.headers['Allow'].split(', ')) == set(
        ['OPTIONS', 'POST', 'DELETE', 'GET'],
    )

    response = await taxi_userver_sample.options('autogen/info')
    assert response.status_code == 200
    assert set(response.headers['Allow'].split(', ')) == set(
        ['OPTIONS', 'GET', 'POST'],
    )

    response = await taxi_userver_sample.options('bla/v42/blablabla')
    assert response.status_code == 404


async def test_implicit_options_auth(taxi_userver_sample):
    auth_check_headers = {'X-YaTaxi-Allow-Auth-Request': 'tvm2'}
    response = await taxi_userver_sample.options(
        'autogen/info', headers=auth_check_headers,
    )
    assert response.status_code == 200
    assert set(response.headers['Allow'].split(', ')) == set(
        ['OPTIONS', 'GET', 'POST'],
    )
    assert response.headers['X-YaTaxi-Allow-Auth-Response'] == 'OK'


async def test_explicit_options(taxi_userver_sample):
    # check that implicit options handler does not shadow explicit one
    json_params = {'привет': 'мир'}
    response = await taxi_userver_sample.options(
        '/json-echo', json=json_params,
    )
    assert response.status_code == 200
    assert (
        response.headers['content-type'] == 'application/json; charset=utf-8'
    )
    assert response.encoding == 'utf-8'
    assert response.json() == json_params
