import pytest

PARAMS = {'db': '999', 'session': 'qwerty'}
FILES = {'file': bytearray([255, 254, 253, 252])}  # not utf8 body
PARKS_PARAMS = {'park_id': '999', 'driver_profile_id': 'vodilo'}
PARKS_RESPONSE = {
    'photos': [
        {
            'href': (
                'https://storage.mds.yandex.net/get-taximeter/'
                '3325/6a255a958d234fa497d99c21b4a1f166_large.jpg'
            ),
            'scale': 'large',
            'type': 'driver',
        },
    ],
}
EXPECTED_RESPONSE = {
    'Large': {
        'Driver': (
            'https://storage.mds.yandex.net/get-taximeter/'
            '3325/6a255a958d234fa497d99c21b4a1f166_large.jpg'
        ),
    },
}


def test_ok(mockserver, taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('999', 'qwerty', 'vodilo')

    @mockserver.json_handler('/parks/driver-profiles/photo')
    def mock_callback(request):
        assert request.method == 'POST'
        assert request.args.to_dict() == PARKS_PARAMS
        # dont know how to check binary content
        assert 'driver' in request.form.to_dict(True)
        return PARKS_RESPONSE

    response = taxi_driver_protocol.post(
        '/driver/photo/set', params=PARAMS, files=FILES, data={'number': '4'},
    )

    assert response.status_code == 200, response.text
    assert mock_callback.times_called == 1
    assert response.json() == EXPECTED_RESPONSE


@pytest.mark.parametrize(
    'files, args, error',
    [
        (
            {'image': 'image_binary_data'},
            {'number': '4'},
            'file in multipart request expected',
        ),
        (
            {'file': 'image_binary_data'},
            {'type': '4'},
            'number in multipart request expected',
        ),
    ],
)
def test_bad_request(
        mockserver,
        taxi_driver_protocol,
        files,
        args,
        error,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('999', 'qwerty', 'vodilo')

    @mockserver.json_handler('/parks/driver-profiles/photo')
    def mock_callback(request):
        return {}

    response = taxi_driver_protocol.post(
        '/driver/photo/set', params=PARAMS, files=files, data=args,
    )

    assert response.status_code == 400, response.text
    assert mock_callback.times_called == 0
    assert response.json() == {'error': {'text': error}}
