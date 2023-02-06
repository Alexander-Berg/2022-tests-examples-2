import pytest

EXCLUDE_HEADERS = {'X-External-API-Key'}
FILE_REQUESTS = 'requests.json'


@pytest.mark.parametrize(
    'request_type_name',
    [
        'valid.some-service',
        'valid.other-service',
        'invalid.api-keys-forbids',
        'invalid.api-keys-exception',
    ],
)
async def test_apikey(
        load_json,
        _request_exams_authproxy,
        _mock_remote,
        _uapi_keys,
        request_type_name,
):
    _type, _name = request_type_name.split('.')
    data = load_json(FILE_REQUESTS)[_type][_name]

    handler = _mock_remote(data['path'], exclude_headers=EXCLUDE_HEADERS)
    _mock_uapi = _uapi_keys(data['uapi_keys_response'])
    response = await _request_exams_authproxy(
        data['path'], headers=data['headers'],
    )

    assert _mock_uapi.has_calls
    assert handler.has_calls is data['proxied']
    assert not response.cookies
