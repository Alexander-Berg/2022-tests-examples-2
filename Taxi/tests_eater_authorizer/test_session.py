import pytest

from tests_eater_authorizer import utils

EXISTING_SESSION_DATA = (
    '_sf2_attributes|a:1:{'
    's:13:"_security_api";s:144:"C:36:'
    '"Eda\\Eater\\Common\\Security\\EaterToken":95:'
    '{a:1:{i:0;C:15:"App\\Entity\\User":57:{a:2:'
    '{i:0;i:62888001;i:1;s:24:"+79876543210@example.com";}}}}";}'
    '_sf2_meta|a:3:{s:1:"u";i:1583845279;s:1:"c";'
    'i:1582975478;s:1:"l";s:7:"2592000";}'
)

EAP_STORAGE_KEY = 'EAP.'

ANON_TTL = 7200
AUTHORIZED_TTL = 2592000


@pytest.mark.redis_store(
    ['set', EAP_STORAGE_KEY + 'outer_token1', 'inner_token1'],
    ['expire', EAP_STORAGE_KEY + 'outer_token1', 3000],
    ['set', 'inner_token1', EXISTING_SESSION_DATA],
    ['expire', 'inner_token1', 3000],
    ['set', EAP_STORAGE_KEY + 'outer_token2', 'inner_token2'],
    ['expire', EAP_STORAGE_KEY + 'outer_token2', 3000],
)
@pytest.mark.parametrize(
    'outer_session_id, eater_id, expect_metrics',
    [
        pytest.param(
            'outer_token1',
            '62888001',
            {'session-prolong': 1, 'not-anon': 1},
            id='with auth',
        ),
        pytest.param(
            'outer_token2',
            None,
            {'session-not-found': 1, 'anon': 1},
            id='without auth',
        ),
    ],
)
async def test_have_mapping(
        taxi_eater_authorizer,
        redis_store,
        outer_session_id,
        eater_id,
        expect_metrics,
        taxi_eater_authorizer_monitor,
):
    await taxi_eater_authorizer.tests_control(reset_metrics=True)

    response = await taxi_eater_authorizer.put(
        '/v2/eater/sessions',
        json={'outer_session_id': outer_session_id, 'no_new_session': False},
    )
    assert response.status_code == 200

    assert response.json()['outer_session_id'] == outer_session_id
    assert response.json()['inner_session_id'] != outer_session_id
    assert response.json()['cache_enabled']
    assert response.json()['session_type'] == 'native'
    assert response.json()['bound_sessions'] == [outer_session_id]

    if eater_id:
        assert response.json()['eater_id'] == eater_id
        assert response.json()['ttl'] == AUTHORIZED_TTL

        assert (
            redis_store.ttl(EAP_STORAGE_KEY + outer_session_id)
            == AUTHORIZED_TTL
        )
        assert (
            redis_store.ttl(response.json()['inner_session_id'])
            == AUTHORIZED_TTL
        )
    else:
        assert redis_store.ttl(EAP_STORAGE_KEY + outer_session_id) == ANON_TTL

    metrics = await taxi_eater_authorizer_monitor.get_metric('eater-sessions')
    utils.check_metrics(metrics, expect_metrics)


async def test_new_user(
        taxi_eater_authorizer, redis_store, taxi_eater_authorizer_monitor,
):
    await taxi_eater_authorizer.tests_control(reset_metrics=True)

    response = await taxi_eater_authorizer.put(
        '/v2/eater/sessions',
        json={'outer_session_id': '', 'no_new_session': False},
    )
    assert response.status_code == 200

    outer_session_id = response.json()['outer_session_id']
    inner_session_id = response.json()['inner_session_id']
    assert outer_session_id != inner_session_id
    assert inner_session_id.startswith('i_')
    assert response.json()['cache_enabled']
    assert response.json()['session_type'] == 'native'
    assert 'bound_sessions' not in response.json()

    assert redis_store.ttl(EAP_STORAGE_KEY + outer_session_id) == ANON_TTL
    assert redis_store.get(response.json()['inner_session_id']) is None

    metrics = await taxi_eater_authorizer_monitor.get_metric('eater-sessions')
    utils.check_metrics(metrics, {'request-no-token': 1})


@pytest.mark.config(
    EATER_AUTHORIZER_SESSION_SETTINGS={
        'session-ttl-seconds': 2592000,
        'session-prolong-threshold-seconds': 172800,
    },
    EATER_AUTHORIZER_SESSION_ANON_TTL=7200,
)
async def test_mapping_first_time_prolong(
        taxi_eater_authorizer, redis_store, taxi_eater_authorizer_monitor,
):
    # create anon mapping
    response = await taxi_eater_authorizer.put(
        '/v2/eater/sessions',
        json={'outer_session_id': '', 'no_new_session': False},
    )
    assert response.status_code == 200

    outer_session_id = response.json()['outer_session_id']
    inner_session_id = response.json()['inner_session_id']

    # create session
    request_json = {
        'inner_session_id': inner_session_id,
        'eater_id': '12345',
        'eater_username': 'user@eats.ru',
    }
    response = await taxi_eater_authorizer.post(
        '/v1/eater/sessions/login', json=request_json,
    )
    assert response.status_code == 200

    assert redis_store.get('EAP.' + outer_session_id) is not None
    assert redis_store.get(inner_session_id) is not None

    mapping_ttl_before_prolongation = redis_store.ttl(
        'EAP.' + outer_session_id,
    )
    assert mapping_ttl_before_prolongation <= 7200  # see config mock
    session_ttl_before_prolongation = redis_store.ttl(inner_session_id)

    # should be prolonged here
    response = await taxi_eater_authorizer.put(
        '/v2/eater/sessions',
        json={'outer_session_id': outer_session_id, 'no_new_session': False},
    )
    assert response.status_code == 200

    # just that it was prolonged
    assert (
        redis_store.ttl('EAP.' + outer_session_id)
        > mapping_ttl_before_prolongation
    )

    # because is was prolonged as session
    assert (
        redis_store.ttl('EAP.' + outer_session_id)
        >= session_ttl_before_prolongation
    )
    assert redis_store.ttl(inner_session_id) >= session_ttl_before_prolongation
