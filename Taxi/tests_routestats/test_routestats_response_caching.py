import gzip
import io
import json

import pytest


PA_HEADERS = {
    'X-YaTaxi-UserId': 'user_id',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=iphone',
    'X-AppMetrica-DeviceId': 'DeviceId',
}


# In python this is reproducible via
# `hashlib.blake2b(source.encode('utf-8'), digest_size=16).digest().hex()`,
# but you need to build json string according to
# formats::json::ToStableString() implementation from userver.
REQUEST_BLAKE2B128_HASH = '48a4ef6f08dc9f3896c7051d3c3fdfe0'


def _gzip_decompress(message):
    data = io.BytesIO(message)
    with gzip.GzipFile(mode='rb', fileobj=data) as gzip_file:
        return gzip_file.read()


class Context:
    def __init__(self):
        self.cache_writes = 0
        self.cache_reads = 0


@pytest.fixture(name='mock_api_cache')
async def _mock_api_cache(mockserver, load_json, testpoint):
    context = Context()

    cache_storage = {}

    @mockserver.json_handler(
        '/api-cache/v1/cached-value/routestats-request-response',
    )
    def api_cache_handler(request):
        key = request.query['key']
        assert key == REQUEST_BLAKE2B128_HASH

        if request.method == 'PUT':
            assert request.headers.get('Cache-Control') == 'max-age=120'

            headers_bytes, data_gzipped = request.get_data().split(
                b'\x00', maxsplit=1,
            )

            headers = json.loads(headers_bytes.decode())
            assert headers['headers'] == {
                'X-YaTaxi-UserId': 'user_id',
                'X-Yandex-UID': '4003514353',
                'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
                'X-AppMetrica-DeviceId': 'DeviceId',
            }

            data = _gzip_decompress(data_gzipped).decode()
            data_json = json.loads(data)

            expected_request = load_json('request.json')
            expected_response = load_json('protocol_response.json')

            assert data_json == {
                'request': expected_request,
                'response': expected_response,
            }

            cache_storage[key] = data
            context.cache_writes += 1
            return {}

        # TODO (devcrab): uncomment when using cached values in response
        # if request.method == 'GET':
        #     data = cache_storage.get(key)
        #     if not data:
        #         return mockserver.make_response(status=404)
        #     cache_reads += 1
        #     return mockserver.make_response(
        #         data,
        #         headers={'Content-Type': 'application/octet-stream'},
        #         status=200,
        #     )
        raise RuntimeError(f'Unsupported method {request.method}')

    return context


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(names=['top_level:proxy'])
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='routestats_response_caching',
    consumers=['uservices/routestats'],
    clauses=[
        {
            'value': {'store_enabled': True, 'ttl_seconds': 120},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.parametrize(
    'is_lightweight',
    [pytest.param(True, id='lightweight'), pytest.param(False, id='full')],
)
async def test_response_caching(
        taxi_routestats,
        mockserver,
        testpoint,
        load_json,
        mock_api_cache,
        is_lightweight,
):
    response_file = 'protocol_response.json'

    @testpoint('response-stored-to-cache')
    def response_stored_to_cache(data):
        pass

    @mockserver.json_handler(f'/protocol-routestats/internal/routestats')
    def _protocol(request):
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json(response_file),
        }

    request = load_json('request.json')
    request['is_lightweight'] = is_lightweight

    response = await taxi_routestats.post(
        'v1/routestats', request, headers=PA_HEADERS,
    )
    assert response.status_code == 200

    expected_response = load_json(response_file)
    assert expected_response == response.json()

    should_store_to_cache = not is_lightweight

    if not should_store_to_cache:
        return

    await response_stored_to_cache.wait_call()

    assert mock_api_cache.cache_writes == 1
