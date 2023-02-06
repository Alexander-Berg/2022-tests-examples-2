import gzip
import json
import zlib

import pytest


@pytest.mark.disable_config_check
@pytest.mark.parametrize(
    'a_called, b_called, result',
    [
        pytest.param(
            1,
            0,
            'rA',
            marks=[pytest.mark.config(A_ENABLED=True, B_ENABLED=False)],
        ),
        pytest.param(
            1,
            1,
            'rA',
            marks=[pytest.mark.config(A_ENABLED=True, B_ENABLED=True)],
        ),
        pytest.param(
            0,
            1,
            'rB',
            marks=[pytest.mark.config(A_ENABLED=False, B_ENABLED=True)],
        ),
    ],
)
async def test_if(
        taxi_api_proxy,
        resources,
        endpoints,
        load_yaml,
        mockserver,
        a_called,
        b_called,
        result,
):
    @mockserver.json_handler('/upstream-a')
    def mock_a(request):
        return mockserver.make_response(
            status=200, response='rA', content_type='application/json',
        )

    @mockserver.json_handler('/upstream-b')
    def mock_b(request):
        return mockserver.make_response(
            status=200, response='rB', content_type='application/json',
        )

    await resources.safely_create_resource(
        resource_id='upstream-a',
        url=mockserver.url('upstream-a'),
        method='post',
    )

    await resources.safely_create_resource(
        resource_id='upstream-b',
        url=mockserver.url('upstream-b'),
        method='post',
    )

    handler_def = load_yaml('ep_if.yaml')
    await endpoints.safely_create_endpoint('/ep', post_handler=handler_def)

    response = await taxi_api_proxy.post(
        '/ep?data=0',
        json={'property': 'value'},
        headers={'content-type': 'application/json'},
    )
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.text == result
    assert mock_a.times_called == a_called
    assert mock_b.times_called == b_called


@pytest.mark.parametrize(
    'client_accept, upstream_compress, client_encoding, status_code',
    [
        (None, None, None, 200),
        ('gzip', 'gzip', 'gzip', 200),
        ('super-lol4t0', 'super-lol4t0', 'super-lol4t0', 200),
        ('super-lol4t0, deflate', 'super-lol4t0', 'super-lol4t0', 200),
        ('gzip, deflate', 'gzip', 'gzip', 200),
        ('gzip, deflate', 'deflate', 'deflate', 200),
        ('deflate', 'gzip', None, 200),
        ('gzip', 'deflate', None, 500),
        (None, 'gzip', None, 200),
        ('gzip', None, None, 200),
        ('*', None, None, 200),
        ('*', 'gzip', 'gzip', 200),
        ('*', 'deflate', 'deflate', 200),
    ],
)
async def test_compression(
        taxi_api_proxy,
        resources,
        endpoints,
        load_yaml,
        mockserver,
        client_accept,
        upstream_compress,
        client_encoding,
        status_code,
):
    @mockserver.json_handler('/upstream')
    def mock_upstream(request):
        assert request.headers['Accept-Encoding'] == 'gzip'
        json_response = json.dumps({'result': 'OK'})
        response = None
        if upstream_compress is None:
            response = json_response
        elif upstream_compress == 'gzip':
            response = gzip.compress(json_response.encode('utf-8'))
        elif upstream_compress == 'super-lol4t0':
            response = '42'
        elif upstream_compress == 'deflate':
            response = zlib.compress(json_response.encode('utf-8'))
        else:
            raise ValueError('unknown compression %s' % upstream_compress)

        headers = None
        if upstream_compress is not None:
            headers = {'Content-Encoding': upstream_compress}
        return mockserver.make_response(
            status=200,
            response=response,
            content_type='application/json',
            headers=headers,
        )

    await resources.safely_create_resource(
        resource_id='upstream', url=mockserver.url('upstream'), method='get',
    )

    handler_def = load_yaml('ep_simple.yaml')
    await endpoints.safely_create_endpoint('/ep', get_handler=handler_def)

    headers = {'Accept-Encoding': client_accept or 'identity'}

    response = await taxi_api_proxy.get('/ep', headers=headers)
    assert response.status_code == status_code
    if status_code == 200:
        assert response.content_type == 'application/json'
        if client_encoding is not None:
            assert response.headers['content-encoding'] == client_encoding
        else:
            assert 'content-encoding' not in response.headers
        decompressed_response = {}
        if client_encoding in (None, 'gzip', 'deflate'):
            decompressed_response = response.json()
        elif client_encoding == 'super-lol4t0':
            assert response.text == '42'
            decompressed_response = {'result': 'OK'}
        assert decompressed_response == {'result': 'OK'}
    assert mock_upstream.times_called == 1


async def test_get_body(
        mockserver, resources, load_yaml, endpoints, taxi_api_proxy,
):
    @mockserver.json_handler('/upstream')
    def mock_upstream(request):
        assert request.method == 'GET'
        return {'result': 'OK'}

    await resources.safely_create_resource(
        resource_id='upstream', url=mockserver.url('upstream'), method='get',
    )

    handler_def = load_yaml('ep_simple.yaml')
    await endpoints.safely_create_endpoint('/ep', get_handler=handler_def)

    response = await taxi_api_proxy.get('/ep')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.json() == {'result': 'OK'}
    assert mock_upstream.times_called == 1
