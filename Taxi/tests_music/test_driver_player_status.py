import pytest


DRIVER_ID = 'driver'
DRIVER_APP_PROFILE_ID = 'id-1'


def get_cursor(pgsql):
    return pgsql['music'].cursor()


def get_player_action_by_alias_id(order_id, pgsql):
    db = get_cursor(pgsql)
    db.execute(
        f"""select version, player_state from
         music.players where alias_id='{order_id}'""",
    )
    return [{'version': version, 'state': state} for version, state in db]


@pytest.fixture(name='post_player_status')
def _post_player_status(taxi_music, driver_authorizer):
    async def _do(body, status_code=200):
        driver_authorizer.set_session(
            DRIVER_ID, 'driver_session1', DRIVER_APP_PROFILE_ID,
        )
        driver_authorizer_params = {
            'db': DRIVER_ID,
            'session': 'driver_session1',
        }
        response = await taxi_music.post(
            'driver/music/player-status',
            json=body,
            params=driver_authorizer_params,
        )
        assert response.status_code == status_code
        if response.status_code == 200:
            assert response.text
        return response

    return _do


@pytest.mark.config(TAXI_MUSIC_SERVICE_ENABLED=False)
async def test_service_disabled(post_player_status):
    request = {
        'order_id': 'alias-id-1',
        'player': {
            'next_button_available': True,
            'prev_button_available': True,
            'status': 'unknown',
        },
    }
    await post_player_status(body=request, status_code=406)


@pytest.mark.parametrize(
    'new_state, expected_state',
    [
        (
            {
                'next_button_available': True,
                'prev_button_available': True,
                'status': 'unknown',
            },
            {
                'next_button_available': True,
                'prev_button_available': True,
                'status': 'unknown',
            },
        ),
        (
            {
                'next_button_available': True,
                'prev_button_available': True,
                'status': 'unknown',
                'volume': 35,
            },
            {
                'next_button_available': True,
                'prev_button_available': True,
                'status': 'unknown',
                'volume': 35,
            },
        ),
    ],
)
async def test_simple(
        taxi_music,
        pgsql,
        mockserver,
        post_player_status,
        new_state,
        expected_state,
):
    # create player
    request = {
        'order_id': 'order-id-1',
        'alias_id': 'alias-id-1',
        'user_uid': 'user-uid-1',
        'user_id': 'user-id-1',
        'driver_id': 'driver_id-1',
    }
    response = await taxi_music.post('internal/player/create', json=request)
    assert response.status_code == 200, response.text()

    actions = get_player_action_by_alias_id('alias-id-1', pgsql)
    assert actions == [{'version': 0, 'state': None}]

    # pylint: disable=unused-variable
    @mockserver.json_handler('/ucommunications/user/notification/push')
    def get_by_business_oid(request):
        body = request.json
        assert body['data'] == {
            'payload': {
                'extra': {
                    'type': 'taxi_music',
                    'subtype': 'player_info',
                    'order_id': 'order-id-1',
                    'data': {
                        'player_version': 1,
                        **expected_state,
                        'redirect_scheme': 'musicsdk',
                        'webview_url': 'https://music.yandex.ru/pptouch',
                    },
                },
                'type': 'taxi_music',
                'subtype': 'player_info',
            },
        }
        assert body['user'] == 'user-id-1'
        return {}

    # update player status
    request = {'order_id': 'alias-id-1', 'player': new_state}
    await post_player_status(body=request)

    actions = get_player_action_by_alias_id('alias-id-1', pgsql)
    assert actions == [{'version': 1, 'state': expected_state}]
