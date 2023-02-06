import json

import pytest

from tests_eater_authorizer import utils

LOGIN_SESSION = (
    '_sf2_attributes|a:0:{}_sf2_meta|a:3:'
    '{s:1:"u";i:1584031032;s:1:"c";i:1584031032'
    ';s:1:"l";s:7:"2592000";}'
)
LOGIN_WITH_OFFER_SESSION = (
    '_sf2_attributes|a:1:{s:5:"offer";'
    's:130:"{"till":"2020-03-12T19:47:10+03:00",'
    '"since":"2020-03-12T19:37:10+03:00",'
    '"counter":0,"location":{"lat":55.823879,'
    '"long":37.497216}}";}_sf2_meta|a:3:'
    '{s:1:"u";i:1584031032;s:1:"c";i:1584031032'
    ';s:1:"l";s:7:"2592000";}'
)
LOGIN_REWRITE_USER_SESSION = (
    '_sf2_attributes|a:1:{'
    's:13:"_security_api";s:144:"C:36:'
    '"Eda\\Eater\\Common\\Security\\EaterToken":95:'
    '{a:1:{i:0;C:15:"App\\Entity\\User":57:{a:2:'
    '{i:0;i:12345678;i:1;s:24:"+79876543210@example.com";}}}}";}'
    '_sf2_meta|a:3:{s:1:"u";i:1583845279;s:1:"c";'
    'i:1582975478;s:1:"l";s:7:"2592000";}'
)
LOGIN_REWRITE_USER_WITH_OFFER_SESSION = (
    '_sf2_attributes|a:2:{s:5:"offer";'
    's:130:"{"till":"2020-03-12T19:47:10+03:00",'
    '"since":"2020-03-12T19:37:10+03:00",'
    '"counter":0,"location":{"lat":55.823879,'
    '"long":37.497216}}";'
    's:13:"_security_api";s:144:"C:36:'
    '"Eda\\Eater\\Common\\Security\\EaterToken":95:'
    '{a:1:{i:0;C:15:"App\\Entity\\User":57:{a:2:'
    '{i:0;i:12345678;i:1;s:24:"+79876543210@example.com";}}}}";}'
    '_sf2_meta|a:3:{s:1:"u";i:1583845279;s:1:"c";'
    'i:1582975478;s:1:"l";s:7:"2592000";}'
)


@pytest.mark.parametrize('inner_session_id', ['i_missing', 'inner_missing'])
async def test_login_missing_session(
        taxi_eater_authorizer,
        redis_store,
        taxi_eater_authorizer_monitor,
        inner_session_id,
):
    await taxi_eater_authorizer.tests_control(reset_metrics=True)

    request_json = {
        'inner_session_id': inner_session_id,
        'eater_id': '12345',
        'eater_username': 'user@eats.ru',
    }
    response = await taxi_eater_authorizer.post(
        '/v1/eater/sessions/login', json=request_json,
    )
    assert response.status_code == 200
    assert not response.json()
    assert redis_store.get(inner_session_id) is not None

    metrics = await taxi_eater_authorizer_monitor.get_metric(
        'eater-sessions-login',
    )
    utils.check_metrics(metrics, {'no-session': 1})


async def test_login_invalid_request(
        taxi_eater_authorizer, taxi_eater_authorizer_monitor,
):
    await taxi_eater_authorizer.tests_control(reset_metrics=True)

    session_id = 'valid_session_id'
    request_json = {
        'inner_session_id': session_id,
        'eater_id': '',
        'eater_username': 'user@eats.ru',
    }
    response = await taxi_eater_authorizer.post(
        '/v1/eater/sessions/login', json=request_json,
    )

    assert response.status_code == 400

    metrics = await taxi_eater_authorizer_monitor.get_metric(
        'eater-sessions-login',
    )
    utils.check_metrics(metrics, {})


@pytest.mark.redis_store(
    ['set', 'i_existing_session', LOGIN_SESSION],
    ['expire', 'i_existing_session', 3000],
    ['set', 'inner_existing_session', LOGIN_SESSION],
    ['expire', 'inner_existing_session', 3000],
)
@pytest.mark.parametrize(
    'inner_session_id', ['i_existing_session', 'inner_existing_session'],
)
async def test_login_json(
        taxi_eater_authorizer,
        redis_store,
        taxi_eater_authorizer_monitor,
        inner_session_id,
):
    await taxi_eater_authorizer.tests_control(reset_metrics=True)

    request_json = {
        'inner_session_id': inner_session_id,
        'eater_id': '12345678',
        'eater_username': 'user@eats.ru',
    }
    response = await taxi_eater_authorizer.post(
        '/v1/eater/sessions/login', json=request_json,
    )
    assert response.status_code == 200

    session_str = redis_store.get(inner_session_id)

    assert session_str is not None

    session = json.loads(session_str)
    expected_session = {
        'm': {'c': 1584031032, 't': 2592000},
        'a': {'e': {'i': 12345678, 'u': 'user@eats.ru'}},
    }
    utils.is_subjson(expected_session, session)
    assert redis_store.ttl(inner_session_id) > 5000

    metrics = await taxi_eater_authorizer_monitor.get_metric(
        'eater-sessions-login',
    )
    utils.check_metrics(metrics, {'has-session': 1, 'no-eater': 1})


@pytest.mark.redis_store(
    ['set', 'i_existing_session', LOGIN_WITH_OFFER_SESSION],
    ['expire', 'i_existing_session', 3000],
    ['set', 'inner_existing_session', LOGIN_WITH_OFFER_SESSION],
    ['expire', 'inner_existing_session', 3000],
)
@pytest.mark.parametrize(
    'inner_session_id', ['i_existing_session', 'inner_existing_session'],
)
async def test_login_with_offer_json(
        taxi_eater_authorizer,
        redis_store,
        taxi_eater_authorizer_monitor,
        inner_session_id,
):
    await taxi_eater_authorizer.tests_control(reset_metrics=True)

    request_json = {
        'inner_session_id': inner_session_id,
        'eater_id': '12345678',
        'eater_username': 'user@eats.ru',
    }
    response = await taxi_eater_authorizer.post(
        '/v1/eater/sessions/login', json=request_json,
    )
    assert response.status_code == 200

    session_str = redis_store.get(inner_session_id)

    assert session_str is not None

    session = json.loads(session_str)
    expected_session = {
        'm': {'c': 1584031032, 't': 2592000},
        'a': {'e': {'i': 12345678, 'u': 'user@eats.ru'}},
    }
    utils.is_subjson(expected_session, session)
    assert redis_store.ttl(inner_session_id) > 5000

    metrics = await taxi_eater_authorizer_monitor.get_metric(
        'eater-sessions-login',
    )
    utils.check_metrics(metrics, {'has-session': 1, 'no-eater': 1})


@pytest.mark.redis_store(
    ['set', 'i_existing_session', LOGIN_REWRITE_USER_SESSION],
    ['expire', 'i_existing_session', 3000],
    ['set', 'inner_existing_session', LOGIN_REWRITE_USER_SESSION],
    ['expire', 'inner_existing_session', 3000],
)
@pytest.mark.parametrize(
    'inner_session_id', ['i_existing_session', 'inner_existing_session'],
)
async def test_login_rewrite_user_json(
        taxi_eater_authorizer,
        redis_store,
        taxi_eater_authorizer_monitor,
        inner_session_id,
):
    await taxi_eater_authorizer.tests_control(reset_metrics=True)

    request_json = {
        'inner_session_id': inner_session_id,
        'eater_id': '12345678',
        'eater_username': 'user@eats.ru',
    }
    response = await taxi_eater_authorizer.post(
        '/v1/eater/sessions/login', json=request_json,
    )
    assert response.status_code == 200

    session_str = redis_store.get(inner_session_id)

    assert session_str is not None

    session = json.loads(session_str)
    expected_session = {
        'm': {'c': 1582975478, 't': 2592000},
        'a': {'e': {'i': 12345678, 'u': 'user@eats.ru'}},
    }
    utils.is_subjson(expected_session, session)
    assert redis_store.ttl(inner_session_id) > 5000

    metrics = await taxi_eater_authorizer_monitor.get_metric(
        'eater-sessions-login',
    )
    utils.check_metrics(metrics, {'has-session': 1})


@pytest.mark.redis_store(
    ['set', 'i_existing_session', LOGIN_REWRITE_USER_WITH_OFFER_SESSION],
    ['expire', 'i_existing_session', 3000],
    ['set', 'inner_existing_session', LOGIN_REWRITE_USER_WITH_OFFER_SESSION],
    ['expire', 'inner_existing_session', 3000],
)
@pytest.mark.parametrize(
    'inner_session_id', ['i_existing_session', 'inner_existing_session'],
)
async def test_login_rewrite_user_with_offer_json(
        taxi_eater_authorizer,
        redis_store,
        taxi_eater_authorizer_monitor,
        inner_session_id,
):
    await taxi_eater_authorizer.tests_control(reset_metrics=True)

    request_json = {
        'inner_session_id': inner_session_id,
        'eater_id': '12345678',
        'eater_username': 'user@eats.ru',
    }
    response = await taxi_eater_authorizer.post(
        '/v1/eater/sessions/login', json=request_json,
    )
    assert response.status_code == 200

    session_str = redis_store.get(inner_session_id)

    assert session_str is not None

    session = json.loads(session_str)
    expected_session = {
        'a': {'e': {'i': 12345678, 'u': 'user@eats.ru'}},
        'm': {'c': 1582975478, 't': 2592000},
    }

    utils.is_subjson(expected_session, session)
    assert redis_store.ttl(inner_session_id) > 5000

    metrics = await taxi_eater_authorizer_monitor.get_metric(
        'eater-sessions-login',
    )
    utils.check_metrics(metrics, {'has-session': 1})


@pytest.mark.parametrize('session', ['p_inner_session', 'p_outer_session'])
async def test_login_with_wrong_session_type(
        taxi_eater_authorizer, session, taxi_eater_authorizer_monitor,
):
    await taxi_eater_authorizer.tests_control(reset_metrics=True)

    response = await taxi_eater_authorizer.post(
        '/v1/eater/sessions/login',
        json={
            'inner_session_id': session,
            'eater_id': '123',
            'eater_username': 'user@eats.ru',
        },
    )

    assert response.status_code == 403

    metrics = await taxi_eater_authorizer_monitor.get_metric(
        'eater-sessions-login',
    )
    utils.check_metrics(metrics, {})
