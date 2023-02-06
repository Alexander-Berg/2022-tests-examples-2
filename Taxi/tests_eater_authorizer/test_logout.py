import pytest


@pytest.mark.parametrize('inner_session_id', ['i_missing', 'inner_missing'])
async def test_logout_missing_session(taxi_eater_authorizer, inner_session_id):
    request_json = {'inner_session_id': inner_session_id}
    response = await taxi_eater_authorizer.post(
        '/v1/eater/sessions/logout', json=request_json,
    )
    expected_error = {
        'code': 'session_data_not_found',
        'message': 'Session data not found (eap)',
    }
    assert response.status_code == 404
    assert response.json() == expected_error


async def test_logout_invalid_session(taxi_eater_authorizer):
    inner_session_id = ''
    request_json = {'inner_session_id': inner_session_id}
    response = await taxi_eater_authorizer.post(
        '/v1/eater/sessions/logout', json=request_json,
    )
    assert response.status_code == 400


@pytest.mark.redis_store(
    [
        'set',
        'i_existing_session2',
        '_sf2_attributes|a:1:{'
        's:13:"_security_api";s:144:"C:36:'
        '"Eda\\Eater\\Common\\Security\\EaterToken":95:'
        '{a:1:{i:0;C:15:"App\\Entity\\User":57:{a:2:'
        '{i:0;i:12345678;i:1;s:12:"user@eats.ru";}}}}";}'
        '_sf2_meta|a:3:{s:1:"u";i:1583845279;s:1:"c";'
        'i:1582975478;s:1:"l";s:7:"2592000";}',
    ],
    ['expire', 'i_existing_session2', 3000],
    [
        'set',
        'i_existing_session',
        '_sf2_attributes|a:1:{'
        's:13:"_security_api";s:144:"C:36:'
        '"Eda\\Eater\\Common\\Security\\EaterToken":95:'
        '{a:1:{i:0;C:15:"App\\Entity\\User":57:{a:2:'
        '{i:0;i:12345678;i:1;s:12:"user@eats.ru";}}}}";}'
        '_sf2_meta|a:3:{s:1:"u";i:1583845279;s:1:"c";'
        'i:1582975478;s:1:"l";s:7:"2592000";}',
    ],
    ['expire', 'i_existing_session', 3000],
)
@pytest.mark.parametrize(
    'inner_session_id', ['i_existing_session', 'i_existing_session2'],
)
async def test_logout(taxi_eater_authorizer, redis_store, inner_session_id):
    request_json = {'inner_session_id': inner_session_id}
    response = await taxi_eater_authorizer.post(
        '/v1/eater/sessions/logout', json=request_json,
    )
    assert response.status_code == 200

    session_str = redis_store.get(inner_session_id)

    assert session_str is None


@pytest.mark.parametrize('session', ['p_inner_session', 'p_outer_session'])
async def test_logout_with_wrong_session_type(taxi_eater_authorizer, session):
    response = await taxi_eater_authorizer.post(
        '/v1/eater/sessions/logout', json={'inner_session_id': session},
    )

    assert response.status_code == 403
