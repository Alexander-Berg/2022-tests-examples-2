import pytest


@pytest.fixture(name='get_player_info')
def _get_player_info(taxi_music):
    async def _do(
            order_id,
            *,
            yandex_uid,
            flags=None,
            application=None,
            status_code=200,
    ):
        headers = {'X-Yandex-UID': yandex_uid}
        if flags:
            headers['X-YaTaxi-Pass-Flags'] = flags
        headers['X-Request-Application'] = (
            application or 'app_name=android,app_ver1=4,app_ver2=0,app_ver3=1'
        )
        response = await taxi_music.post(
            '4.0/music/v1/player-info',
            json={'order_id': order_id},
            headers=headers,
        )
        assert response.status_code == status_code
        return response

    return _do


@pytest.mark.parametrize('flags', [None, 'portal', 'ya-plus'])
async def test_flags(get_player_info, flags):
    await get_player_info(
        'order_id', yandex_uid='yandex-uid', flags=flags, status_code=406,
    )


@pytest.mark.pgsql('music', files=['music.sql'])
async def test_player_null(get_player_info):
    await get_player_info(
        'order-id-1',
        yandex_uid='yandex-uid-1',
        flags='portal,ya-plus',
        status_code=406,
    )


@pytest.mark.pgsql('music', files=['music.sql'])
@pytest.mark.parametrize(
    'order_id, user_uid, expected_state',
    [
        (
            'order-id-2',
            'yandex-uid-2',
            {
                'player_version': 1,
                'next_button_available': True,
                'prev_button_available': True,
                'status': 'unknown',
            },
        ),
        (
            'order-id-4',
            'yandex-uid-4',
            {
                'player_version': 3,
                'next_button_available': True,
                'prev_button_available': True,
                'status': 'unknown',
                'volume': 15,
            },
        ),
    ],
)
async def test_player_simple(
        get_player_info, order_id, user_uid, expected_state,
):
    response = await get_player_info(
        order_id, yandex_uid=user_uid, flags='portal,ya-plus',
    )
    assert response.json() == {
        'player': {
            **expected_state,
            'redirect_scheme': 'musicsdk',
            'webview_url': 'https://music.yandex.ru/pptouch',
        },
    }


@pytest.mark.config(TAXI_MUSIC_SERVICE_ENABLED=False)
async def test_service_disabled(get_player_info):
    await get_player_info(
        'order-id-1',
        yandex_uid='yandex-uid-1',
        flags='portal,ya-plus',
        status_code=406,
    )


@pytest.mark.parametrize(
    'application,expected_status_code',
    [
        ('app_name=android,app_ver1=3', 406),
        ('app_name=android,app_ver1=5', 200),
    ],
)
@pytest.mark.pgsql('music', files=['music.sql'])
@pytest.mark.experiments3(filename='experiments3.json')
async def test_waiting_for_driver_status(
        get_player_info, application, expected_status_code,
):
    response = await get_player_info(
        'order-id-1',
        yandex_uid='yandex-uid-1',
        flags='portal,ya-plus',
        application=application,
        status_code=expected_status_code,
    )

    if expected_status_code == 200:
        assert response.json()['player']['status'] == 'waiting_for_driver'
