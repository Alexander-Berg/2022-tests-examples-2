import pytest

# Generated via `tvmknife unittest service -s 111 -d 2001716`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxC0lno:Mq'
    '_Uxj0_0uU3TVGgtA9c9sSWyCryh9ngXRS76Hk0'
    'cKlf1Tx7SPDgwKbB8Wji18-jCGYwCf8kh-hXD'
    'iiWUaV2p9hZ5GovU_dTYXiDfnNxzLDL848PW-V'
    'FYJ-YMi3DFjwA08njKnRQEnzzllwqPN_1aUBM3W6lbgQZ4RaODfkHR3s'
)

# Generated via `tvmknife unittest service -s 2001716 -d 2001716`
MUSIC_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IggItJZ6ELSWeg'
    ':Ub6VhOZcj0V93-TSypyEqqwxTUs7uaaeb46PA'
    'HNiMnAuNrGXVbuR9wSfKvjTM_7defPpjqsiGf'
    'xeZLUdjcM8pVxLeXC-cE5O62YmXLyQawXU5IKB'
    'NFna0ZbvepJ69NeXag1hfSiqCXYi6Ih_v39fEjO8MWeSGGNsThNX9Ze9k1s'
)


def get_cursor(pgsql):
    return pgsql['music'].cursor()


def sql_player_to_json(res):
    schema = [
        'order_id',
        'alias_id',
        'driver_id',
        'user_id',
        'user_uid',
        'created',
        'player_state',
    ]
    json = {}
    for i, elem in enumerate(schema):
        json[elem] = res[i]
    return json


def get_player_by_order_id(order_id, pgsql):
    db = get_cursor(pgsql)
    db.execute(
        'select * from music.players where order_id=\'{}\''.format(order_id),
    )
    players = [sql_player_to_json(x) for x in db]
    return players[0] if players else None


def get_actions_by_order_id(order_id, pgsql):
    db = get_cursor(pgsql)
    db.execute(
        'select * from music.player_actions where order_id=\'{}\''.format(
            order_id,
        ),
    )
    return [x for x in db]


async def test_internal_create(taxi_music, pgsql):
    request = {
        'order_id': 'order-id-1',
        'alias_id': 'alias-id-1',
        'user_uid': 'user-uid-1',
        'user_id': 'user-id-1',
        'driver_id': 'driver-id-1',
    }

    player = get_player_by_order_id(request['order_id'], pgsql)
    assert player is None

    response = await taxi_music.post('internal/player/create', json=request)
    assert response.status_code == 200

    player = get_player_by_order_id(request['order_id'], pgsql)
    assert player['order_id'] == request['order_id']
    assert player['driver_id'] == request['driver_id']
    assert player['alias_id'] == request['alias_id']
    assert player['user_uid'] == request['user_uid']
    assert player['user_id'] == request['user_id']


async def test_internal_create_double(taxi_music, pgsql):
    request = {
        'order_id': 'order-id-1',
        'alias_id': 'alias-id-1',
        'user_uid': 'user-uid-1',
        'user_id': 'user-id-1',
        'driver_id': 'driver-id-1',
    }
    response = await taxi_music.post('internal/player/create', json=request)
    assert response.status_code == 200

    request_2 = {
        'order_id': 'order-id-1',
        'alias_id': 'alias-id-2',
        'user_uid': 'user-uid-3',
        'user_id': 'user-id-3',
        'driver_id': 'driver-id-4',
    }
    response = await taxi_music.post('internal/player/create', json=request_2)
    assert response.status_code == 200

    player = get_player_by_order_id(request['order_id'], pgsql)
    assert player['order_id'] == request['order_id']
    assert player['driver_id'] == request['driver_id']
    assert player['alias_id'] == request['alias_id']
    assert player['user_uid'] == request['user_uid']
    assert player['user_id'] == request['user_id']


async def test_internal_delete_not_exists(taxi_music, pgsql):
    request = {'order_id': 'order-id-1', 'alias_id': 'alias-id-1'}
    response = await taxi_music.post('internal/player/delete', json=request)
    assert response.status_code == 200

    player = get_player_by_order_id(request['order_id'], pgsql)
    assert player is None


@pytest.mark.pgsql('music', files=['music.sql'])
@pytest.mark.parametrize(
    'order_id,alias_id,must_delete',
    [('order-id-2', 'alias-id-2', True), ('order-id-2', 'alias-id-1', False)],
)
async def test_internal_delete(
        order_id, alias_id, must_delete, taxi_music, pgsql,
):
    request = {'order_id': 'order-id-2', 'alias_id': alias_id}

    player = get_player_by_order_id(request['order_id'], pgsql)
    actions = get_actions_by_order_id(request['order_id'], pgsql)
    assert player is not None
    assert len(actions) == 4

    response = await taxi_music.post('internal/player/delete', json=request)
    assert response.status_code == 200

    player = get_player_by_order_id(request['order_id'], pgsql)
    actions = get_actions_by_order_id(request['order_id'], pgsql)
    if must_delete:
        assert player is None
        assert not actions
    else:
        assert player is not None
        assert len(actions) == 4


@pytest.mark.pgsql('music', files=['music.sql'])
async def test_internal_userinfo(taxi_music, pgsql):
    request = {'driver_id': 'driver_id-2'}
    player = get_player_by_order_id('order-id-2', pgsql)

    response = await taxi_music.post('internal/player/userinfo', json=request)
    assert response.status_code == 200
    assert response.json() == {
        'yandex_uid': player['user_uid'],
        'order_id': player['order_id'],
        'alias_id': player['alias_id'],
    }


@pytest.mark.pgsql('music', files=['music.sql'])
async def test_internal_userinfo_null(taxi_music, pgsql):
    request = {'driver_id': 'driver_id-1'}
    response = await taxi_music.post('internal/player/userinfo', json=request)
    assert response.status_code == 406


async def test_internal_userinfo_noplayer(taxi_music, pgsql):
    request = {'driver_id': 'driver-id-1'}

    response = await taxi_music.post('internal/player/userinfo', json=request)
    assert response.status_code == 406


@pytest.mark.config(TAXI_MUSIC_SERVICE_ENABLED=False)
async def test_service_disabled(taxi_music):
    request = {'driver_id': 'driver_id-2'}
    response = await taxi_music.post('internal/player/userinfo', json=request)
    assert response.status_code == 406

    request = {
        'order_id': 'order-id-1',
        'alias_id': 'alias-id-1',
        'user_uid': 'user-uid-1',
        'user_id': 'user-id-1',
        'driver_id': 'driver-id-1',
    }
    response = await taxi_music.post('internal/player/create', json=request)
    assert response.status_code == 406

    request = {'order_id': 'order-id-2', 'alias_id': 'alias-id-2'}
    response = await taxi_music.post('internal/player/delete', json=request)
    assert response.status_code == 406


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'music'}],
    TVM_SERVICES={'music': 2001716, 'mock': 111},
)
@pytest.mark.tvm2_ticket(
    {111: MOCK_SERVICE_TICKET, 2001716: MUSIC_SERVICE_TICKET},
)
async def test_internal_tvm2_create(taxi_music):
    await taxi_music.invalidate_caches()
    request = {
        'order_id': 'order-id-1',
        'alias_id': 'alias-id-1',
        'user_uid': 'user-uid-1',
        'user_id': 'user-id-1',
        'driver_id': 'driver-id-1',
    }

    response = await taxi_music.post(
        'internal/player/create',
        json=request,
        headers={'X-Ya-Service-Ticket': 'wrong'},
    )
    assert response.status_code == 401

    header = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}
    response = await taxi_music.post(
        'internal/player/create', json=request, headers=header,
    )
    assert response.status_code == 200


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'music'}],
    TVM_SERVICES={'music': 2001716, 'mock': 111},
)
@pytest.mark.tvm2_ticket(
    {111: MOCK_SERVICE_TICKET, 2001716: MUSIC_SERVICE_TICKET},
)
async def test_internal_tvm2_delete(taxi_music):
    await taxi_music.invalidate_caches()
    request = {'order_id': 'order-id-1', 'alias_id': 'alias-id-1'}

    response = await taxi_music.post(
        'internal/player/delete',
        json=request,
        headers={'X-Ya-Service-Ticket': 'wrong'},
    )
    assert response.status_code == 401

    headers = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}
    response = await taxi_music.post(
        'internal/player/delete', json=request, headers=headers,
    )
    assert response.status_code == 200
