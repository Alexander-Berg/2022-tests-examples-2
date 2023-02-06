import pytest


URI = '/v1/eats-partner/sessions/logout'


@pytest.mark.parametrize(
    'session',
    [
        'anon_session',
        'eats_session',
        'inner_session',
        'p_inner_session',
        'asdf88d7q3gdaadj',
    ],
)
async def test_logout_wrong_session(taxi_eater_authorizer, session):
    request_json = {'outer_session_id': session}
    response = await taxi_eater_authorizer.post(URI, json=request_json)
    assert response.status_code == 403


async def test_logout_no_mapping_session(taxi_eater_authorizer):
    request_json = {'outer_session_id': 'p_outer_no_session'}
    response = await taxi_eater_authorizer.post(URI, json=request_json)
    assert response.status_code == 404
    assert response.json()['code'] == 'session_mapping_not_found'


@pytest.mark.redis_store(
    ['set', 'p_outer_no_data_session', 'p_inner_no_data_session'],
    ['expire', 'p_outer_no_data_session', 300],
)
async def test_logout_no_data_session(taxi_eater_authorizer):
    request_json = {'outer_session_id': 'p_outer_no_data_session'}
    response = await taxi_eater_authorizer.post(URI, json=request_json)
    assert response.status_code == 404
    assert response.json()['code'] == 'session_data_not_found'


@pytest.mark.redis_store(
    ['set', 'p_outer_wrong_session', 'p_inner_wrong_session'],
    ['expire', 'p_outer_wrong_session', 300],
    [
        'set',
        'p_inner_wrong_session',
        '{"m":{"c":1602595050,"u":1602595050,"t":300},"a":null}',
    ],
    ['expire', 'p_inner_wrong_session', 300],
)
async def test_logout_wrong_data_session(taxi_eater_authorizer, redis_store):
    request_json = {'outer_session_id': 'p_outer_wrong_session'}
    response = await taxi_eater_authorizer.post(URI, json=request_json)
    assert response.status_code == 200

    session_str = redis_store.get('p_inner_wrong_session')
    expected_no_user = b'"a":null'
    assert session_str is not None
    assert expected_no_user in session_str


@pytest.mark.redis_store(
    ['set', 'p_outer_ok_session', 'p_inner_ok_session'],
    ['expire', 'p_outer_ok_session', 300],
    [
        'set',
        'p_inner_ok_session',
        '{"m":{"c":1602595050,"u":1602595050,"t":300},"a":{"p":10}}',
    ],
    ['expire', 'p_inner_ok_session', 300],
)
async def test_logout_ok_session(taxi_eater_authorizer, redis_store):
    request_json = {'outer_session_id': 'p_outer_ok_session'}
    response = await taxi_eater_authorizer.post(URI, json=request_json)
    assert response.status_code == 200

    session_str = redis_store.get('p_inner_ok_session')
    expected_no_user = b'"a":null'
    assert session_str is not None
    assert expected_no_user in session_str
    assert redis_store.ttl('p_inner_ok_session') == 60
