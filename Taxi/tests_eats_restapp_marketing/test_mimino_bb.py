import pytest


TEST_UID = '100'
TEST_HEADERS = {'X-Yandex-UID': TEST_UID, 'X-Remote-IP': '1.2.3.4'}


@pytest.mark.parametrize(
    'url, direct_url',
    [
        pytest.param(
            '/4.0/restapp-front/marketing/v1/check-partner',
            '/direct-internal/clients/checkClientState',
            id='check client',
        ),
        pytest.param(
            '/4.0/restapp-front/marketing/v1/register-partner',
            '/direct-internal/clients/addOrGet',
            id='register client',
        ),
    ],
)
async def test_use_mimino_bb(
        taxi_eats_restapp_marketing, mockserver, url, direct_url,
):
    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        return {}

    @mockserver.json_handler('/blackbox-mimino-test')
    def mock_blackbox_mimino(request):
        return {}

    @mockserver.json_handler(direct_url)
    def mock_direct_client(request):
        return {}

    await taxi_eats_restapp_marketing.post(url, headers=TEST_HEADERS)

    assert mock_blackbox_mimino.has_calls
    assert not mock_blackbox.has_calls

    assert mock_direct_client.has_calls
