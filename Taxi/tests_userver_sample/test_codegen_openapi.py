import codecs
import json


async def test_response(taxi_userver_sample):
    response = await taxi_userver_sample.get('/openapi/simple')
    assert response.status_code == 200
    assert 'application/json' in response.headers['Content-Type']
    assert response.json() == {'Integer': 1}


async def test_request_body(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        '/openapi/request_body',
        data=json.dumps({'x': '123'}),
        headers={'content-type': 'application/json'},
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'image/png'
    assert response.json() == {'x': '123'}


async def test_request_body_ws(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        '/openapi/request_body',
        data='{\r\n"x": "123"\r\n}',
        headers={'content-type': 'application/json'},
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'image/png'
    assert response.json() == {'x': '123'}


async def test_request_body_bom(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        '/openapi/request_body',
        data=codecs.BOM_UTF8 + b'{\r\n"x": "123"\r\n}',
        headers={'content-type': 'application/json'},
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'image/png'
    assert response.json() == {'x': '123'}


async def test_request_body_ufeff(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        '/openapi/request_body',
        data='\ufeff{\r\n"x": "123"\r\n}',
        headers={'content-type': 'application/json'},
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'image/png'
    assert response.json() == {'x': '123'}


async def test_array(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        '/openapi/users/123',
        params={'pipe': 'a|b'},
        headers={
            'X-Request-id': '123',
            'content-type': 'application/json',
            'serialize': '1,2,3',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'serialize': [1, 2, 3], 'pipe': ['a', 'b']}


async def test_query_missing(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        '/openapi/users/123',
        headers={
            'X-Request-id': '123',
            'content-type': 'application/json',
            'serialize': '1,2,3',
        },
    )
    assert response.status_code == 400


async def test_header_missing(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        '/openapi/users/123',
        params={'pipe': 'a|b'},
        headers={'X-Request-id': '123', 'content-type': 'application/json'},
    )
    assert response.status_code == 400


async def test_array_optional(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        '/openapi/users/123',
        params={'pipe': 'a|b'},
        headers={
            'X-Request-id': '123',
            'content-type': 'application/json',
            'serialize': '1,2,3',
            'opt': 'zzz',
        },
    )
    assert response.status_code == 200
    assert response.json()['opt'] == 'zzz'
