import pytest


REQUIRED_FLAGS = 'portal,ya-plus'


def get_cursor(pgsql):
    return pgsql['music'].cursor()


def sql_player_actions_to_json(res):
    schema = [
        'action_id',
        'action_code',
        'action_time',
        'action_data',
        'order_id',
        'alias_id',
    ]
    json = {}
    for i, elem in enumerate(schema):
        json[elem] = res[i]
    return json


def get_player_action_by_order_id(order_id, pgsql):
    db = get_cursor(pgsql)
    db.execute(
        'select * from music.player_actions where order_id=\'{}\''.format(
            order_id,
        ),
    )
    return [sql_player_actions_to_json(x) for x in db]


@pytest.fixture(name='post_player_action')
def _post_player_action(taxi_music):
    async def _do(body, yandex_uid, *, flags=None, status_code=200):
        headers = {'X-Yandex-UID': yandex_uid}
        if flags:
            headers['X-YaTaxi-Pass-Flags'] = flags
        response = await taxi_music.post(
            '4.0/music/v1/player-action', json=body, headers=headers,
        )
        assert response.status_code == status_code
        return response

    return _do


@pytest.mark.parametrize('flags', [None, 'portal', 'ya-plus'])
async def test_insufficient_flags(post_player_action, flags):
    body = {
        'order_id': 'order_id',
        'action_code': 'next',
        'action_id': 'action_id',
    }
    await post_player_action(
        body, yandex_uid='yandex-uid-1', flags=flags, status_code=406,
    )


@pytest.mark.pgsql('music', files=['music.sql'])
@pytest.mark.parametrize(
    'order_id, yandex_uid',
    [
        ('order-id-2', 'bad-uid'),
        ('bad-id', 'alias-id-2'),
        ('bad-id', 'bad-uid'),
    ],
)
async def test_player_not_found(post_player_action, order_id, yandex_uid):
    body = {
        'order_id': order_id,
        'action_code': 'next',
        'action_id': 'action_id',
    }
    await post_player_action(
        body, yandex_uid=yandex_uid, flags=REQUIRED_FLAGS, status_code=406,
    )


@pytest.mark.pgsql('music', files=['music.sql'])
@pytest.mark.parametrize(
    'action_code, action_data',
    [
        ('next', None),
        ('play_music', {'deeplink': 'some_link'}),
        ('set_volume', {'volume': 45}),
    ],
)
async def test_post_one_action(
        post_player_action, pgsql, mockserver, action_code, action_data,
):
    request = {
        'order_id': 'order-id-1',
        'action_code': action_code,
        'action_id': 'action_id',
    }
    if action_data is not None:
        request['action_data'] = action_data

    # pylint: disable=unused-variable
    @mockserver.json_handler('/communications/driver/notification/push')
    def get_by_business_oid(request):
        body = request.json
        assert body['dbid'] == 'driver'
        assert body['uuid'] == 'id-1'
        assert body['code'] == 1400

        _action = {'action_id': 'action_id', 'action_code': action_code}
        if action_data is not None:
            _action['action_data'] = action_data

        assert body['data'] == {
            'order_id': 'alias-id-1',
            'is_first_actions': True,
            'actions': [_action],
        }
        return {}

    await post_player_action(
        request, yandex_uid='yandex-uid-1', flags=REQUIRED_FLAGS,
    )

    actions = get_player_action_by_order_id('order-id-1', pgsql)
    action = actions[0]

    assert action['order_id'] == request['order_id']
    assert action['action_code'] == request['action_code']
    assert action['action_id'] == request['action_id']
    if action_data is not None:
        assert action['action_data'] == request['action_data']
    else:
        assert action['action_data'] is None


@pytest.mark.pgsql('music', files=['music.sql'])
async def test_actions_duplicate(post_player_action, pgsql, mockserver):
    request = {
        'order_id': 'order-id-2',
        'action_code': 'play',
        'action_id': 'hex-id-3',
    }

    # pylint: disable=unused-variable
    @mockserver.json_handler('/communications/driver/notification/push')
    def get_by_business_oid(request):
        body = request.json
        assert body['dbid'] == 'driver'
        assert body['uuid'] == 'id-2'
        assert body['code'] == 1400
        assert body['data'] == {
            'order_id': 'alias-id-2',
            'is_first_actions': True,
            'actions': [
                {
                    'action_id': 'hex-id-1',
                    'action_code': 'play_music',
                    'action_data': {'deeplink': 'some_link'},
                },
                {'action_id': 'hex-id-2', 'action_code': 'pause'},
                {'action_id': 'hex-id-3', 'action_code': 'play'},
                {
                    'action_id': 'hex-id-4',
                    'action_code': 'set_volume',
                    'action_data': {'volume': 50},
                },
            ],
        }
        return {}

    await post_player_action(
        request, yandex_uid='yandex-uid-2', flags=REQUIRED_FLAGS,
    )

    actions = get_player_action_by_order_id('order-id-2', pgsql)
    assert len(actions) == 4


@pytest.mark.config(TAXI_MUSIC_SERVICE_ENABLED=False)
async def test_service_disabled(post_player_action):
    request = {
        'order_id': 'order-id-1',
        'action_code': 'next',
        'action_id': 'action_id',
    }
    await post_player_action(
        request,
        yandex_uid='yandex-uid-1',
        flags=REQUIRED_FLAGS,
        status_code=406,
    )


@pytest.mark.pgsql('music', files=['driver_pushes.sql'])
@pytest.mark.config(TAXI_MUSIC_DRIVER_PUSH_SETTINGS={'actions_tail_length': 3})
async def test_no_all_actions(post_player_action, pgsql, mockserver):
    request = {
        'order_id': 'order-id-4',
        'action_code': 'next',
        'action_id': 'action_id',
    }

    # pylint: disable=unused-variable
    @mockserver.json_handler('/communications/driver/notification/push')
    def get_by_business_oid(request):
        body = request.json
        assert body['dbid'] == 'driver'
        assert body['uuid'] == 'id-4'
        assert body['code'] == 1400
        assert body['data'] == {
            'order_id': 'alias-id-4',
            'is_first_actions': False,
            'actions': [
                {'action_id': '4hex-id-7', 'action_code': 'play'},
                {'action_id': '4hex-id-8', 'action_code': 'next'},
                {'action_id': 'action_id', 'action_code': 'next'},
            ],
        }
        return {}

    response = await post_player_action(
        request, yandex_uid='yandex-uid-4', flags=REQUIRED_FLAGS,
    )
    assert response.text


@pytest.mark.pgsql('music', files=['driver_pushes.sql'])
@pytest.mark.config(TAXI_MUSIC_DRIVER_PUSH_SETTINGS={'actions_tail_length': 5})
async def test_only_last_play_music(post_player_action, pgsql, mockserver):
    request = {
        'order_id': 'order-id-5',
        'action_code': 'pause',
        'action_id': 'action_id',
    }

    # pylint: disable=unused-variable
    @mockserver.json_handler('/communications/driver/notification/push')
    def get_by_business_oid(request):
        body = request.json
        assert body['dbid'] == 'driver'
        assert body['uuid'] == 'id-5'
        assert body['code'] == 1400
        assert body['data'] == {
            'order_id': 'alias-id-5',
            'is_first_actions': False,
            'actions': [
                {'action_id': '5hex-id-5', 'action_code': 'pause'},
                {
                    'action_id': '5hex-id-6',
                    'action_code': 'play_music',
                    'action_data': {'deeplink': 'some_link'},
                },
                {'action_id': '5hex-id-7', 'action_code': 'next'},
                {'action_id': 'action_id', 'action_code': 'pause'},
            ],
        }
        return {}

    response = await post_player_action(
        request, yandex_uid='yandex-uid-5', flags=REQUIRED_FLAGS,
    )
    assert response.text
