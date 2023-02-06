import pytest

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from music_plugins.generated_tests import *  # noqa


@pytest.mark.pgsql('music', files=['music.sql'])
async def test_database(taxi_music, pgsql):
    db = pgsql['music'].cursor()

    db.execute('select * from music.players')
    res = [x for x in db]
    assert len(res) == 4

    db.execute('select * from music.player_actions')
    res = [x for x in db]
    assert len(res) == 4


@pytest.mark.xfail(reason='Only for single test launch')
@pytest.mark.now('2019-06-14 19:01:53.000000+03')
@pytest.mark.pgsql('music', files=['old_players.sql'])
async def test_periodic_cleanup(taxi_music, pgsql):
    db = pgsql['music'].cursor()

    db.execute('select * from music.players')
    res = [x for x in db]
    assert len(res) == 2


async def test_sequence(taxi_music, driver_authorizer, mockserver):
    # Create player
    json = {
        'order_id': 'order-id-1',
        'alias_id': 'alias-id-1',
        'user_uid': 'yandex-uid-1',
        'user_id': 'user-id-1',
        'driver_id': 'driver_id-1',
    }
    response = await taxi_music.post('internal/player/create', json=json)
    assert response.status_code == 200

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
                        'next_button_available': True,
                        'player_version': 1,
                        'prev_button_available': True,
                        'redirect_scheme': 'musicsdk',
                        'status': 'unknown',
                        'webview_url': 'https://music.yandex.ru/pptouch',
                    },
                },
                'type': 'taxi_music',
                'subtype': 'player_info',
            },
        }
        assert body['user'] == 'user-id-1'
        return {}

    # Push player state
    json_1 = {
        'order_id': 'alias-id-1',
        'player': {
            'next_button_available': True,
            'prev_button_available': True,
            'status': 'unknown',
        },
    }
    driver_authorizer.set_session('driver', 'driver_session1', 'id-1')
    response = await taxi_music.post(
        'driver/music/player-status',
        json=json_1,
        params={'db': 'driver', 'session': 'driver_session1'},
    )
    assert response.status_code == 200

    # Client polling
    response = await taxi_music.post(
        '4.0/music/v1/player-info',
        json={'order_id': 'order-id-1'},
        headers={
            'X-Yandex-UID': 'yandex-uid-1',
            'X-YaTaxi-Pass-Flags': 'portal,ya-plus',
        },
    )
    assert response.status_code == 200
