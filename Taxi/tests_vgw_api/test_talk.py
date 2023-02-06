import pytest


@pytest.mark.parametrize(
    ('params', 'talk_id'),
    [
        ({'talk_id': 'talk_id_1'}, 'talk_id_1'),
        ({'talk_id': 'talk_id_3'}, 'talk_id_3'),
    ],
)
async def test_talk_get(taxi_vgw_api, params, talk_id, mockserver):
    talks_url = '/talks/' + talk_id + '/record'

    @mockserver.json_handler(talks_url)
    def _mock_talk(request):
        assert request.headers['Authorization'] == 'Basic gateway_token_1'
        return 'binary_data'

    @mockserver.json_handler('/vgw/mds-s3/', prefix=True)
    def _handler(request):
        return mockserver.make_response(status=500)

    response = await taxi_vgw_api.get('v1/talk', params=params)
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'audio/mpeg'
    assert response.json() == 'binary_data'


async def test_talk_get_wav(taxi_vgw_api, mockserver):
    talks_url = '/talks/talk_id_1/record'

    @mockserver.json_handler(talks_url)
    def _mock_talk(request):
        return mockserver.make_response(
            b'binary_data', content_type='audio/x-wav',
        )

    @mockserver.json_handler('/vgw/mds-s3/', prefix=True)
    def _handler(request):
        return mockserver.make_response(status=500)

    response = await taxi_vgw_api.get(
        'v1/talk', params={'talk_id': 'talk_id_1'},
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'audio/wav'
    assert response.content == b'binary_data'


@pytest.mark.parametrize(
    [],
    [
        pytest.param(
            marks=pytest.mark.config(
                VGW_API_YT_REQUESTS_SETTINGS={
                    'db_rows_ttl_h': 24,
                    'limit': 100,
                    'get_gateway_id_use_new_replication': False,
                },
            ),
            id='old replica',
        ),
        pytest.param(
            marks=pytest.mark.config(
                VGW_API_YT_REQUESTS_SETTINGS={
                    'db_rows_ttl_h': 24,
                    'limit': 100,
                    'get_gateway_id_use_new_replication': True,
                },
            ),
            id='new replica',
        ),
    ],
)
@pytest.mark.yt(dyn_table_data=['yt_vgw_api_data.yaml'])
async def test_talk_get_yt(taxi_vgw_api, mockserver, yt_apply):
    @mockserver.json_handler('/talks/archived/record')
    def _mock_talk(request):
        assert request.headers['Authorization'] == 'Basic gateway_token_1'
        return 'binary_data'

    @mockserver.json_handler('/vgw/mds-s3/', prefix=True)
    def _handler(request):
        return mockserver.make_response(status=500)

    response = await taxi_vgw_api.get(
        'v1/talk', params={'talk_id': 'archived'},
    )
    assert response.status_code == 200
    assert response.json() == 'binary_data'


@pytest.mark.parametrize(
    ('params', 'response_code'),
    [({'talk_id': 'bad_talk_id'}, 404), ({'bad_request': 'talk_id_3'}, 400)],
)
async def test_talk_get_errors(
        taxi_vgw_api, params, response_code, mockserver,
):
    @mockserver.json_handler('/vgw/mds-s3/', prefix=True)
    def _handler(request):
        return mockserver.make_response(status=500)

    response = await taxi_vgw_api.get('v1/talk', params=params)
    assert response.status_code == response_code


@pytest.mark.parametrize(
    ('vgw_api_optimization_get_talk_enabled_value', 'expected_status_code'),
    [
        pytest.param(
            True,
            200,
            marks=pytest.mark.config(
                VGW_API_OPTIMIZATION_GET_TALK_ENABLED=True,
            ),
        ),
        pytest.param(
            False,
            404,
            marks=pytest.mark.config(
                VGW_API_OPTIMIZATION_GET_TALK_ENABLED=False,
            ),
        ),
    ],
)
async def test_config_work_correct(
        taxi_vgw_api,
        mockserver,
        testpoint,
        yt_apply,
        vgw_api_optimization_get_talk_enabled_value,
        expected_status_code,
):
    @mockserver.json_handler('/talks/archived/record')
    def _mock_talk(request):
        return 'binary_data'

    @mockserver.json_handler('/vgw/mds-s3/', prefix=True)
    def _handler(request):
        return mockserver.make_response(status=500)

    @testpoint('yt-get-talk-gateway')
    def _yt_get_gateway(data):
        pass

    response = await taxi_vgw_api.get(
        'v1/talk',
        params={'talk_id': 'archived', 'gateway_id': 'gateway_id_1'},
    )
    assert vgw_api_optimization_get_talk_enabled_value != bool(
        _yt_get_gateway.times_called,
    )
    assert response.status_code == expected_status_code
    assert response.status_code != 200 or response.json() == 'binary_data'
