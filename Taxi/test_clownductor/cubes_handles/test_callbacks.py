import pytest

CALLBACK_URL = (
    'http://frontend-dev-api.taxi.yandex.net/api/webhook/clownductor/deploy'
)


@pytest.mark.features_on('send_callback_enabled')
@pytest.mark.parametrize(
    'file_name',
    [
        'StableSendCallback.json',
        'PrestableSendCallback.json',
        'TestingSendCallback.json',
        'UnstableSendCallback.json',
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_send_callback(
        call_cube_handle,
        load_json,
        file_name,
        mock_clowny_balancer,
        patch_aiohttp_session,
        response_mock,
):
    json_data = load_json(file_name)

    @mock_clowny_balancer('/v1/entry-points/fqdn/search/')
    def fqdn_search(request):
        assert request.query['branch_id'] == str(json_data['branch_id'])
        return {'fqdns': ['test-service.taxi.yandex.net']}

    @patch_aiohttp_session(CALLBACK_URL, 'post')
    def mock_callback(method, url, **kwargs):
        assert method == 'post'
        assert url == CALLBACK_URL
        assert kwargs['timeout'] == 10
        assert kwargs['headers'] == json_data['expected_headers']
        assert kwargs['json'] == json_data['expected_data']
        return response_mock(b'unexpected')

    await call_cube_handle('SendCallback', json_data)
    assert fqdn_search.times_called == 1
    assert len(mock_callback.calls) == 1
