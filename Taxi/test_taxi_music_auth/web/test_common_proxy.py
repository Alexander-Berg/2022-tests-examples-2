from urllib import parse

import pytest

from taxi_music_auth.generated.service.client_yandex_music import (
    plugin as yandex_music_plugin,
)  # noqa: F403 F401 E501 pylint: disable=C0301


# Generated via `tvmknife unittest service -s 222 -d 111`
TEST_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUI3gEQbw:'
    'MJdL6op9oanuskpKoCNWa_YBG8JuEkVAts'
    'svrMP6iHVU3W7PNMnYvSrUcWghepD3wjZ5'
    'lyl2HXyf-sTHNrK8lOINE33jN_CN5YSRPs'
    'bjObrgphIwZjeLBqKixk-vSuQTjpNEHTD1'
    'rl2Tw_BqryWhNRQdDokXeBKlcJoLIHudN9w'
)


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'driver_authproxy', 'dst': 'music-auth'}],
    TVM_SERVICES={'music-auth': 111, 'driver_authproxy': 222},
    TVM_API_URL='$mockserver/tvm',
)
@pytest.mark.usefixtures('mocked_tvm')
@pytest.mark.usefixtures('yandex_music_200_mock')
@pytest.mark.usefixtures('taxi_music_userinfo_200_mock')
@pytest.mark.parametrize(
    'headers, params',
    [
        (
            {'Authorization': 'dbid_session'},
            {'ip': '37.140.140.42', '__uid': '1'},
        ),
        # api v1
        (
            {
                'X-Ya-Service-Ticket': TEST_SERVICE_TICKET,
                'X-YaTaxi-Driver-Profile-Id': 'uuid',
                'X-YaTaxi-Park-Id': 'dbid',
            },
            {'ip': '37.140.140.42', '__uid': '1'},
        ),
        # legacy query params
        (
            {'X-Driver-Session': 'session', 'X-YaTaxi-Park-Id': 'dbid'},
            {'ip': '37.140.140.42', '__uid': '1'},
        ),
        (
            {'X-Driver-Session': 'session'},
            {'ip': '37.140.140.42', '__uid': '1', 'park_id': 'dbid'},
        ),
        (
            {'X-Driver-Session': 'session'},
            {'ip': '37.140.140.42', '__uid': '1', 'db': 'dbid'},
        ),
        (
            {},
            {
                'ip': '37.140.140.42',
                '__uid': '1',
                'db': 'dbid',
                'session': 'session',
            },
        ),
    ],
)
async def test_common_proxy(
        web_app_client, mock_authorize_for_driver, headers, params,
):
    mock_authorize_for_driver(authorized=True)
    response = await web_app_client.get(
        '/driver/music-auth/artists/1/tracks', params=params, headers=headers,
    )
    assert response.status == 200
    content = await response.text()
    assert content == '{"key": "value"}'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'driver_authproxy', 'dst': 'music-auth'}],
    TVM_SERVICES={'music-auth': 111, 'driver_authproxy': 222},
    TVM_API_URL='$mockserver/tvm',
)
@pytest.mark.usefixtures('mocked_tvm')
@pytest.mark.usefixtures('taxi_music_userinfo_200_mock')
@pytest.mark.parametrize(
    'headers, params',
    [
        (
            {
                'Authorization': 'dbid_session',
                'Host': 'test.host',  # must not be passed
                'X-Yandex-Login': 'test_login',  # must not be passed
            },
            {'ip': '37.140.140.42', 'param1': '1', 'param2': '2'},
        ),
        # api v1
        (
            {
                'X-Ya-Service-Ticket': TEST_SERVICE_TICKET,
                'X-YaTaxi-Driver-Profile-Id': 'uuid',
                'X-YaTaxi-Park-Id': 'dbid',
                'X-Request-Application-Version': '13.37 (9731)',
                'X-Request-Application': 'taximeter',
                'X-Request-Platform': 'ios',
            },
            {'ip': '37.140.140.42', 'param1': '1', 'param2': '2'},
        ),
        # legacy query params
        (
            {'X-Driver-Session': 'session', 'X-YaTaxi-Park-Id': 'dbid'},
            {'ip': '37.140.140.42', 'param1': '1', 'param2': '2'},
        ),
    ],
)
async def test_get_arguments_passing(
        web_app_client, mock_authorize_for_driver, patch, headers, params,
):
    @patch(
        'taxi_music_auth.generated.service.client_yandex_music.'
        'plugin.YandexMusicClient._request',
    )
    async def _make_request(method, url, *, data, headers, log_extra=None):
        return yandex_music_plugin.APIResponse(
            status=200, data=data, headers=headers,
        )

    mock_authorize_for_driver(authorized=True)
    response = await web_app_client.get(
        '/driver/music-auth/artists/1/tracks', params=params, headers=headers,
    )
    assert response.status == 200
    calls = _make_request.calls
    assert len(calls) == 1
    assert calls[0]['method'] == 'GET'

    for header, _ in headers.items():
        assert header not in calls[0]['headers']
    parsed_url = parse.urlparse(calls[0]['url'])
    assert parsed_url.path == '/internal-api/artists/1/tracks'
    query_dict = dict(parse.parse_qsl(parsed_url.query))
    assert query_dict == {
        'ip': '37.140.140.42',
        'param1': '1',
        'param2': '2',
        '__uid': 'test_yandex_uid',
    }


@pytest.mark.parametrize(
    ['content_type', 'expected_data'],
    [
        ('application/json', '{"param1": "1", "param2": "2"}'),
        ('application/x-www-form-urlencoded', 'param1=1&param2=2'),
    ],
)
@pytest.mark.usefixtures('taxi_music_userinfo_200_mock')
async def test_post_arguments_passing(
        web_app_client,
        mock_authorize_for_driver,
        patch,
        content_type,
        expected_data,
):
    @patch(
        'taxi_music_auth.generated.service.client_yandex_music.'
        'plugin.YandexMusicClient._request',
    )
    async def _make_request(method, url, *, data, headers, log_extra=None):
        return yandex_music_plugin.APIResponse(
            status=200, data=data, headers=headers,
        )

    mock_authorize_for_driver(authorized=True)
    headers = {
        'Authorization': 'dbid_session',
        'Host': 'test.host',  # must not be passed
        'X-Yandex-Login': 'test_login',  # must not be passed
        'Content-Type': content_type,
    }
    response = await web_app_client.post(
        '/driver/music-auth/plays', headers=headers, data=expected_data,
    )
    assert response.status == 200
    calls = _make_request.calls
    assert len(calls) == 1
    assert calls[0]['method'] == 'POST'
    assert calls[0]['data'] == expected_data
    assert 'Host' not in calls[0]['headers']
    assert 'X-Yandex-Login' not in calls[0]['headers']
    parsed_url = parse.urlparse(calls[0]['url'])
    assert parsed_url.path == '/internal-api/plays'
    query_dict = dict(parse.parse_qsl(parsed_url.query))
    assert query_dict == {'__uid': 'test_yandex_uid'}
