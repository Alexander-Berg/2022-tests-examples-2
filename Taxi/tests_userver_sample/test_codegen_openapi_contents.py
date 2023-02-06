# pylint: disable=import-error
import flatbuffers
import pytest
from userver_sample.autogen import testing_response_pb2
from userver_sample.autogen.fbs import TestPostResponse as fb_resp200


async def test_contents_json(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        '/openapi/employees', headers={'test_id': 'Json'},
    )
    assert response.status_code == 200
    assert 'application/json' in response.headers['Content-Type']
    assert response.json() == {'id': 42, 'name': 'John Snow', 'fullTime': True}


async def test_contents_jsonld(taxi_userver_sample):
    response = await taxi_userver_sample.get(
        '/openapi/employees', headers={'test_id': 'JsonLd'},
    )
    assert response.status_code == 200
    assert 'application/ld+json' in response.headers['Content-Type']
    assert response.json() == {
        'id': 43,
        'name': 'Ramsay Bolton',
        'fullTime': True,
    }


#  ->  userver-sample     ->  _handler      ->  userver-sample  ->
#  ^                      ^                 ^                   ^
#  |_ test_id==EchoJson   |_ test_id==Json  |_ id==82           |_ id==1082
async def test_contents_echo_json(taxi_userver_sample, mockserver):
    @mockserver.json_handler('/userver-sample/openapi/employees')
    async def _handler(request):
        assert request.headers['test_id'] == 'Json'
        return mockserver.make_response(
            json={'id': 82, 'name': 'John Snow', 'fullTime': True},
            content_type='application/json',
        )

    response = await taxi_userver_sample.get(
        '/openapi/employees', headers={'test_id': 'EchoJson'},
    )
    assert _handler.times_called >= 1
    assert response.status_code == 200
    assert 'application/json' in response.headers['Content-Type']
    assert response.json() == {
        'id': 1082,
        'name': 'John Snow',
        'fullTime': True,
    }


#  ->  userver-sample       ->  _handler        ->  userver-sample  ->
#  ^                        ^                   ^                   ^
#  |_ test_id==EchoJsonLd   |_ test_id==JsonLd  |_ id==83           |_ id==1083
async def test_contents_echo_jsonld(taxi_userver_sample, mockserver):
    @mockserver.json_handler('/userver-sample/openapi/employees')
    async def _handler(request):
        assert request.headers['test_id'] == 'JsonLd'
        return mockserver.make_response(
            json={'id': 83, 'name': 'Ramsay Bolton', 'fullTime': True},
            content_type='application/ld+json',
        )

    response = await taxi_userver_sample.get(
        '/openapi/employees', headers={'test_id': 'EchoJsonLd'},
    )
    assert _handler.times_called == 1
    assert response.status_code == 200
    assert 'application/ld+json' in response.headers['Content-Type']
    assert response.json() == {
        'id': 1083,
        'name': 'Ramsay Bolton',
        'fullTime': True,
    }


#  ->  userver-sample       ->  _handler       ->  userver-sample    ->  test
#  ^                        ^                  ^                     ^
#  |_ test_id==EchoJsonLd   |_ test_id==JsonLd |_ no Content-Type    |_ 500
async def test_contents_no_content_type(taxi_userver_sample, mockserver):
    @mockserver.json_handler('/userver-sample/openapi/employees')
    async def _handler(request):
        assert request.headers['test_id'] == 'JsonLd'
        return mockserver.make_response(
            json={'id': 83, 'name': 'Ramsay Bolton', 'fullTime': True},
        )

    response = await taxi_userver_sample.get(
        '/openapi/employees', headers={'test_id': 'EchoJsonLd'},
    )
    assert _handler.times_called == 1
    assert response.status_code == 500


#  ->  userver-sample       ->  _handler       ->  userver-sample     ->  test
#  ^                        ^                  ^                      ^
#  |_ test_id==EchoJsonLd   |_ test_id==JsonLd |_ unexpected content  |_ 500
async def test_contents_unexp_content_type(taxi_userver_sample, mockserver):
    @mockserver.json_handler('/userver-sample/openapi/employees')
    async def _handler(request):
        assert request.headers['test_id'] == 'JsonLd'
        return mockserver.make_response(
            json={'id': 83, 'name': 'Ramsay Bolton', 'fullTime': True},
            content_type='foo/bar',
        )

    response = await taxi_userver_sample.get(
        '/openapi/employees', headers={'test_id': 'EchoJsonLd'},
    )
    assert _handler.times_called == 1
    assert response.status_code == 500


@pytest.mark.parametrize(
    'content',
    [
        ('0', 'application/json'),
        ('1', 'application/ld+json'),
        ('2', 'application/xml'),
    ],
)
async def test_contents_all_errors(taxi_userver_sample, content):
    response = await taxi_userver_sample.get(
        '/openapi/content_types_all_erors', headers={'content_id': content[0]},
    )
    assert response.status_code == 402
    assert content[1] in response.headers['Content-Type']


#  ->  userver-sample       ->  _handler       ->  userver-sample     ->  test
@pytest.mark.parametrize('resp_data', [b'', b'{}'])
async def test_no_contents(taxi_userver_sample, mockserver, resp_data):
    @mockserver.json_handler('/userver-sample/openapi/empty_response_body')
    async def _handler(request):
        return mockserver.make_response(resp_data, 204)

    response = await taxi_userver_sample.get('/openapi/empty_response_body')
    assert _handler.times_called == 1
    assert response.status_code == 204
    assert response.content == b''


#  ->  userver-sample       ->  _handler       ->  userver-sample     ->  test
async def test_no_contents_error(taxi_userver_sample, mockserver):
    @mockserver.json_handler('/userver-sample/openapi/empty_response_body')
    async def _handler(request):
        raise mockserver.NetworkError()

    response = await taxi_userver_sample.get('/openapi/empty_response_body')
    assert _handler.times_called >= 1
    assert response.status_code == 500
    assert response.json()['code'] == '500'


def make_protobuf_response() -> str:
    response = testing_response_pb2.TestResponse()
    response.sum = 42
    return response.SerializeToString()


def make_flatbuf_response() -> str:
    builder = flatbuffers.Builder(0)
    fb_resp200.TestPostResponseStart(builder)
    fb_resp200.TestPostResponseAddSum(builder, 100)
    input_fbb = fb_resp200.TestPostResponseEnd(builder)
    builder.Finish(input_fbb)
    return builder.Output()


#  ->  userver-sample       ->  _handler       ->  userver-sample     ->  test
@pytest.mark.parametrize(
    'content',
    [
        ('JSON', 'application/json', '{"message":"test"}'),
        ('PROTO', 'application/protobuf', make_protobuf_response()),
        ('FLAT', 'application/flatbuffer', make_flatbuf_response()),
    ],
)
async def test_contents_mix(taxi_userver_sample, content, mockserver):
    @mockserver.handler('/userver-sample/openapi/mix_content_types')
    async def _handler(request):
        assert content[0] == request.headers['content_id']
        return mockserver.make_response(content[2], content_type=content[1])

    response = await taxi_userver_sample.get(
        '/openapi/mix_content_types', headers={'content_id': content[0]},
    )
    assert _handler.times_called >= 1
    assert response.status_code == 200
    assert content[1] in response.headers['Content-Type']
