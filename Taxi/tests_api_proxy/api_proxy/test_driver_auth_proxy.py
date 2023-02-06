import pytest


@pytest.mark.parametrize(
    'version_type,version,enabled,expected_application',
    [
        ('', '0.1 (11)', False, 'taximeter'),
        ('', '2.0 (11)', True, 'taximeter'),
        ('', '3.4 (11)', False, 'taximeter'),
        ('uber', '2.0 (11)', False, 'uberdriver'),
        ('uber', '3.4 (1177)', True, 'uberdriver'),
        ('uber', '5.0 (134)', False, 'uberdriver'),
    ],
)
@pytest.mark.experiments3(filename='experiments3_defaults.json')
async def test_basic(
        taxi_api_proxy,
        load_yaml,
        version_type,
        version,
        enabled,
        endpoints,
        expected_application,
):
    headers = {
        'X-YaTaxi-Park-Id': 'my-park-id',
        'X-YaTaxi-Driver-Profile-Id': 'my-driver-id',
        'X-Request-Application-Version': version,
        'X-Request-Version-Type': version_type,
        'X-Request-Platform': 'android',
        'User-Agent': 'Taximeter 9.07 (1234)',
    }
    await endpoints.safely_create_endpoint(
        path='/endpoint',
        endpoint_id='driver-endpoint',
        get_handler=load_yaml('endpoint.yaml'),
    )
    response = await taxi_api_proxy.get('/endpoint', headers=headers)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['enabled'] == enabled
    assert response_json['application'] == expected_application
    assert response_json['app-brand'] == ''
    for header_hame, header_value in headers.items():
        assert response_json['headers'][header_hame] == header_value
