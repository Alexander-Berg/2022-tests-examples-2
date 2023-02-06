import json


async def test_request(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/non-json/request',
        headers={'Content-Type': 'text/plain'},
        data='some data',
    )
    assert response.status_code == 200
    assert response.json() == {'data': 'some data'}


async def test_request_consumes2(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/non-json/request',
        headers={'Content-Type': 'text/plain; charset=utf-8'},
        data='some data',
    )
    assert response.status_code == 200
    assert response.json() == {'data': 'some data'}


async def test_request_consumes_uppercase(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/non-json/request',
        headers={'Content-Type': 'text/plain; Charset=utf-8'},
        data='some data',
    )
    assert response.status_code == 200
    assert response.json() == {'data': 'some data'}


async def test_request_bad_content_type(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/non-json/request',
        headers={'Content-Type': 'text/html'},
        data='some data',
    )
    assert response.status_code == 400
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


async def test_request_missing_content_type(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/non-json/request',
        data='some data',
        skip_auto_headers=('content-type',),
    )
    assert response.status_code == 400


async def test_response(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/non-json/response', data=json.dumps({'data': 'some data'}),
    )
    assert response.status_code == 200
    assert response.text == 'some data'
    assert response.headers['Content-Type'] == 'text/plain'


async def test_response_integer(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/non-json/response', data=json.dumps({'data': 'invalid'}),
    )
    assert response.status_code == 400
    assert response.text == '666'
    assert response.headers['Content-Type'] == 'text/plain'


async def test_response_missing_param(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/non-json/response', data=json.dumps({}),
    )
    assert response.status_code == 400
    assert response.text == (
        'Parse error at pos 1, path \'\': missing required field \'data\''
    )
    assert response.headers['Content-Type'] == 'text/html; charset=utf-8'


async def test_request_and_response(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/non-json/request-and-response',
        data='my data',
        headers={'Content-Type': 'text/markdown'},
    )
    assert response.status_code == 200
    assert response.text == 'my data'
    assert response.headers['Content-Type'] == 'text/smth'
