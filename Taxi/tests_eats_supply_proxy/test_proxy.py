import pytest


REQUEST_BODY = {'key': 'value'}
DRIVER_PROFILE_ID = 'driver-profile-id'
PARK_ID = 'park-id'
COURIER_ID = 'courier_id'


@pytest.mark.parametrize(
    'proxy_handle, mocked_handle, headers, expected_status',
    [
        [
            '/eats/v1/mock/handle',
            '/rule1/handle',
            {'X-YaEda-CourierId': COURIER_ID},
            200,
        ],
        ['/eats/v1/mock/handle', '/rule1/handle', {}, 401],
        [
            '/eats/v1/mocked/handle',
            '/rule2/handle',
            {'X-YaEda-CourierId': COURIER_ID},
            200,
        ],
        [
            '/eats/v1/wrong/handle',
            None,
            {'X-YaEda-CourierId': COURIER_ID},
            404,
        ],
        [
            '/eats/v1/mocked/mock/handle',
            '/rule3/handle',
            {'X-YaEda-CourierId': COURIER_ID},
            200,
        ],
    ],
)
async def test_proxy(
        taxi_eats_supply_proxy,
        mockserver,
        proxy_handle,
        mocked_handle,
        headers,
        expected_status,
):
    headers['Cookie'] = (
        'foobarcookie=foobarvalue;skipcookie=skipvalue;'
        + headers.get('Cookie', '')
    )

    _mocked_handle = None
    if mocked_handle is not None:

        @mockserver.json_handler(mocked_handle)
        def _mocked_handle(request):
            assert request.method == 'POST'
            assert request.cookies == {'foobarcookie': 'foobarvalue'}
            assert request.headers['X-YaEda-CourierId'] == COURIER_ID
            return {}

    response = await taxi_eats_supply_proxy.post(
        proxy_handle, json=REQUEST_BODY, headers=headers,
    )
    assert response.status == expected_status
    if mocked_handle is not None:
        assert _mocked_handle.times_called == int(expected_status == 200)
