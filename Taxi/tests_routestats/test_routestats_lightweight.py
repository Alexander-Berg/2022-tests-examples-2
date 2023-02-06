import pytest

import utils


# Use two files to catch race conditions:
# to do it we need to serve /routestats at least twice.
@pytest.mark.parametrize(
    'resp_file', ['protocol_response.json', 'protocol_response_2.json'],
)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(names=['top_level:proxy'])
async def test_basic_protocol_proxying(
        taxi_routestats, mockserver, load_json, resp_file,
):
    class Context:
        request = None

    protocol_context = Context()

    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        protocol_context.request = request.json
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json(resp_file),
        }

    source_request = load_json('request.json')
    response = await taxi_routestats.post(
        'v1/routestats/lightweight', source_request,
    )
    assert response.status_code == 200

    # TODO (devcrab): fix in next PR after adding proxy plugins
    # expected_response = load_json(resp_file)
    # assert response.json() == expected_response

    utils.sort_requests_for_comparison(
        source_request, protocol_context.request,
    )
    assert protocol_context.request == source_request


@pytest.mark.parametrize(
    'protocol_code, expected_code',
    [(400, 400), (401, 401), (404, 404), (429, 429), (500, 500)],
)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(names=['top_level:proxy'])
async def test_protocol_error_transparently_proxied(
        taxi_routestats, mockserver, load_json, protocol_code, expected_code,
):
    @mockserver.handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        return mockserver.make_response('{}', protocol_code)

    response = await taxi_routestats.post(
        'v1/routestats/lightweight', load_json('request.json'),
    )
    assert response.status_code == expected_code
    assert response.json() == {}


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(names=['top_level:proxy'])
async def test_protocol_headers_transparently_proxied(
        taxi_routestats, mockserver, load_json,
):
    request_headers = {
        'User-Agent': 'ua',
        'Accept-Language': 'ru-RU',
        'X-Remote-IP': '127.0.0.1',
        'X-Requested-With': 'nodejs',
        'X-Requested-Uri': '/some/uri',
        'X-Taxi': 'taxi-frontend',
        'Authorization': 'Bearer 123',
        'Cookie': 'a=b; c=d',
        'Origin': 'https://somesite.com',
    }

    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        for header_name, value in request_headers.items():
            assert [value] == request.headers.getall(header_name)
        return {'internal_data': {}, **load_json('protocol_response.json')}

    response = await taxi_routestats.post(
        'v1/routestats/lightweight',
        headers=request_headers,
        json=load_json('request.json'),
    )
    assert response.status_code == 200
