import time

import pytest


CURRENT_TIME = int(time.time())
SESSION_DATA = (
    '{"m":{"c":1602595050,"u":' + str(CURRENT_TIME) + ',"t":300},"a":{"p":10}}'
)
OLD_SESSION_DATA = (
    '{"m":{"c":1602595050,"u":'
    + str(CURRENT_TIME - 360)
    + ',"t":300},"a":{"p":10}}'
)

print(SESSION_DATA)
HEADERS = {
    'X-Request-Application': 'eats-partner',
    'X-Request-Application-Brand': 'eats-partner',
}
OUTER_PREFIX = 'p_outer_'
INNER_PREFIX = 'p_inner_'

EXPIRE_VAL = 300
EXPIRE_VAL_LOWEST = (
    300 - 2
)  # redis possible expire/ttl deviation value in sec.


@pytest.mark.redis_store(
    ['set', 'no_partner_existing_mapping', 'no_partner_existing_session'],
    ['expire', 'no_partner_existing_session', EXPIRE_VAL],
    ['set', 'no_partner_existing_session', SESSION_DATA],
    ['expire', 'no_partner_existing_session', EXPIRE_VAL],
    ['set', 'p_outer_missing_mapping', 'inner_missing_session'],
    ['expire', 'p_outer_missing_mapping', EXPIRE_VAL],
    ['set', 'p_outer_existing_mapping', 'p_inner_existing_session'],
    ['expire', 'p_outer_existing_mapping', EXPIRE_VAL],
    ['set', 'p_inner_existing_session', SESSION_DATA],
    ['expire', 'p_inner_existing_session', EXPIRE_VAL],
)
@pytest.mark.parametrize(
    'session,ok_',
    [
        ('', False),
        ('no_partner_existing_mapping', False),
        ('no_partner_existing_session', False),
        ('p_outer_missing_mapping', False),
        ('p_outer_existing_mapping', True),
        ('p_inner_existing_session', True),
    ],
)
async def test_no_new_session(taxi_eater_authorizer, session, ok_):
    response = await taxi_eater_authorizer.put(
        '/v2/eater/sessions',
        json={'outer_session_id': session, 'no_new_session': True},
        headers=HEADERS,
    )
    if ok_:
        assert response.status_code == 200
    else:
        assert response.status_code == 404
        assert response.json()['code'] == 'SESSION_NOT_FOUND'


@pytest.mark.redis_store(
    ['set', 'p_outer_existing_mapping', 'p_inner_existing_session'],
    ['expire', 'p_outer_existing_mapping', EXPIRE_VAL],
)
@pytest.mark.parametrize(
    'session_id',
    ['', 'p_inner_missing', 'p_outer_missing', 'p_outer_existing_mapping'],
)
async def test_missing_session(taxi_eater_authorizer, redis_store, session_id):
    response = await taxi_eater_authorizer.put(
        '/v2/eater/sessions',
        json={'outer_session_id': session_id},
        headers=HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'inner_session_id' in response_json
    assert 'outer_session_id' in response_json
    assert 'ttl' in response_json
    assert 'cache_enabled' in response_json
    assert 'session_type' in response_json
    assert response_json['session_type'] == 'partner'

    current_inner_session_id = response_json['inner_session_id']
    current_outer_session_id = response_json['outer_session_id']
    cache_enabled = response_json['cache_enabled']

    assert current_outer_session_id[: len(OUTER_PREFIX)] == OUTER_PREFIX
    assert current_inner_session_id[: len(INNER_PREFIX)] == INNER_PREFIX

    assert current_outer_session_id != session_id
    assert current_inner_session_id != session_id
    assert (
        redis_store.get(current_outer_session_id).decode('ascii')
        == current_inner_session_id
    )
    assert redis_store.get(current_outer_session_id) is not None
    assert redis_store.get(current_inner_session_id) is not None
    assert (
        EXPIRE_VAL_LOWEST
        <= redis_store.ttl(current_outer_session_id)
        <= EXPIRE_VAL
    )
    assert (
        EXPIRE_VAL_LOWEST
        <= redis_store.ttl(current_inner_session_id)
        <= EXPIRE_VAL
    )
    assert (
        redis_store.get(session_id) is None
    )  # missing or deleted if have no data
    assert cache_enabled is False


@pytest.mark.redis_store(
    ['set', 'p_outer_existing_mapping', 'p_inner_existing_session'],
    ['expire', 'p_outer_existing_mapping', EXPIRE_VAL],
    ['set', 'p_inner_existing_session', OLD_SESSION_DATA],
    ['expire', 'p_inner_existing_session', EXPIRE_VAL],
)
@pytest.mark.parametrize(
    'session_id', ['p_inner_existing_session', 'p_outer_existing_mapping'],
)
async def test_session_with_prolongation(
        taxi_eater_authorizer, redis_store, session_id,
):
    response = await taxi_eater_authorizer.put(
        '/v2/eater/sessions',
        json={'outer_session_id': session_id},
        headers=HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'inner_session_id' in response_json
    assert 'outer_session_id' in response_json
    assert 'cache_enabled' in response_json
    assert 'session_type' in response_json
    assert 'ttl' in response_json
    assert 'partner_user_id' in response_json
    assert 'eater_id' not in response_json
    assert response_json['session_type'] == 'partner'

    current_inner_session_id = response_json['inner_session_id']
    current_outer_session_id = response_json['outer_session_id']
    current_partner_user_id = response_json['partner_user_id']
    cache_enabled = response_json['cache_enabled']

    assert current_outer_session_id[: len(OUTER_PREFIX)] == OUTER_PREFIX
    assert current_inner_session_id[: len(INNER_PREFIX)] == INNER_PREFIX
    assert current_partner_user_id == '10'
    assert session_id in (current_outer_session_id, current_inner_session_id)
    assert (
        redis_store.get(current_outer_session_id).decode('ascii')
        == current_inner_session_id
    )
    assert redis_store.get(current_outer_session_id) is not None
    assert redis_store.get(current_inner_session_id) is not None
    assert (
        EXPIRE_VAL_LOWEST
        <= redis_store.ttl(current_outer_session_id)
        <= EXPIRE_VAL
    )
    assert (
        EXPIRE_VAL_LOWEST
        <= redis_store.ttl(current_inner_session_id)
        <= EXPIRE_VAL
    )
    assert cache_enabled is False


@pytest.mark.redis_store(
    ['set', 'p_outer_existing_mapping', 'p_inner_existing_session'],
    ['expire', 'p_outer_existing_mapping', EXPIRE_VAL],
    ['set', 'p_inner_existing_session', SESSION_DATA],
    ['expire', 'p_inner_existing_session', EXPIRE_VAL],
)
@pytest.mark.parametrize(
    'session_id', ['p_inner_existing_session', 'p_outer_existing_mapping'],
)
async def test_session_without_prolongation(
        taxi_eater_authorizer, redis_store, session_id,
):
    response = await taxi_eater_authorizer.put(
        '/v2/eater/sessions',
        json={'outer_session_id': session_id},
        headers=HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'inner_session_id' in response_json
    assert 'outer_session_id' in response_json
    assert 'cache_enabled' in response_json
    assert 'session_type' in response_json
    assert 'ttl' not in response_json
    assert 'partner_user_id' in response_json
    assert 'eater_id' not in response_json
    assert response_json['session_type'] == 'partner'

    current_inner_session_id = response_json['inner_session_id']
    current_outer_session_id = response_json['outer_session_id']
    current_partner_user_id = response_json['partner_user_id']
    cache_enabled = response_json['cache_enabled']

    assert current_outer_session_id[: len(OUTER_PREFIX)] == OUTER_PREFIX
    assert current_inner_session_id[: len(INNER_PREFIX)] == INNER_PREFIX
    assert current_partner_user_id == '10'
    assert session_id in (current_outer_session_id, current_inner_session_id)
    assert (
        redis_store.get(current_outer_session_id).decode('ascii')
        == current_inner_session_id
    )
    assert redis_store.get(current_outer_session_id) is not None
    assert redis_store.get(current_inner_session_id) is not None
    assert (
        EXPIRE_VAL_LOWEST
        <= redis_store.ttl(current_outer_session_id)
        <= EXPIRE_VAL
    )
    assert (
        EXPIRE_VAL_LOWEST
        <= redis_store.ttl(current_inner_session_id)
        <= EXPIRE_VAL
    )
    assert cache_enabled is False


@pytest.mark.redis_store(
    ['set', 'p_outer_existing_mapping', 'p_inner_existing_session'],
    ['expire', 'p_outer_existing_mapping', EXPIRE_VAL],
    [
        'set',
        'p_inner_existing_session',
        OLD_SESSION_DATA.replace('"a":{"p":10}', '"a":null'),
    ],
    ['expire', 'p_inner_existing_session', EXPIRE_VAL],
)
@pytest.mark.parametrize(
    'session_id', ['p_inner_existing_session', 'p_outer_existing_mapping'],
)
async def test_session_with_prolongation_without_user(
        taxi_eater_authorizer, redis_store, session_id,
):
    response = await taxi_eater_authorizer.put(
        '/v2/eater/sessions',
        json={'outer_session_id': session_id},
        headers=HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'inner_session_id' in response_json
    assert 'outer_session_id' in response_json
    assert 'cache_enabled' in response_json
    assert 'session_type' in response_json
    assert 'ttl' in response_json
    assert 'partner_user_id' not in response_json
    assert 'eater_id' not in response_json
    assert response_json['session_type'] == 'partner'

    current_inner_session_id = response_json['inner_session_id']
    current_outer_session_id = response_json['outer_session_id']
    cache_enabled = response_json['cache_enabled']

    assert current_outer_session_id[: len(OUTER_PREFIX)] == OUTER_PREFIX
    assert current_inner_session_id[: len(INNER_PREFIX)] == INNER_PREFIX
    assert session_id in (current_outer_session_id, current_inner_session_id)
    assert (
        redis_store.get(current_outer_session_id).decode('ascii')
        == current_inner_session_id
    )
    assert redis_store.get(current_outer_session_id) is not None
    assert redis_store.get(current_inner_session_id) is not None
    assert (
        EXPIRE_VAL_LOWEST
        <= redis_store.ttl(current_outer_session_id)
        <= EXPIRE_VAL
    )
    assert (
        EXPIRE_VAL_LOWEST
        <= redis_store.ttl(current_inner_session_id)
        <= EXPIRE_VAL
    )
    assert cache_enabled is False


@pytest.mark.redis_store(
    ['set', 'p_outer_existing_mapping', 'p_inner_existing_session'],
    ['expire', 'p_outer_existing_mapping', EXPIRE_VAL],
    [
        'set',
        'p_inner_existing_session',
        SESSION_DATA.replace('"a":{"p":10}', '"a":null'),
    ],
    ['expire', 'p_inner_existing_session', EXPIRE_VAL],
)
@pytest.mark.parametrize(
    'session_id', ['p_inner_existing_session', 'p_outer_existing_mapping'],
)
async def test_session_without_prolongation_without_user(
        taxi_eater_authorizer, redis_store, session_id,
):
    response = await taxi_eater_authorizer.put(
        '/v2/eater/sessions',
        json={'outer_session_id': session_id},
        headers=HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'inner_session_id' in response_json
    assert 'outer_session_id' in response_json
    assert 'cache_enabled' in response_json
    assert 'session_type' in response_json
    assert 'ttl' not in response_json
    assert 'partner_user_id' not in response_json
    assert 'eater_id' not in response_json
    assert response_json['session_type'] == 'partner'

    current_inner_session_id = response_json['inner_session_id']
    current_outer_session_id = response_json['outer_session_id']
    cache_enabled = response_json['cache_enabled']

    assert current_outer_session_id[: len(OUTER_PREFIX)] == OUTER_PREFIX
    assert current_inner_session_id[: len(INNER_PREFIX)] == INNER_PREFIX
    assert session_id in (current_outer_session_id, current_inner_session_id)
    assert (
        redis_store.get(current_outer_session_id).decode('ascii')
        == current_inner_session_id
    )
    assert redis_store.get(current_outer_session_id) is not None
    assert redis_store.get(current_inner_session_id) is not None
    assert (
        EXPIRE_VAL_LOWEST
        <= redis_store.ttl(current_outer_session_id)
        <= EXPIRE_VAL
    )
    assert (
        EXPIRE_VAL_LOWEST
        <= redis_store.ttl(current_inner_session_id)
        <= EXPIRE_VAL
    )
    assert cache_enabled is False
