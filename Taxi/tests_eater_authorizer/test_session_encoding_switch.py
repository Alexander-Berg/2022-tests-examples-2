import json

import pytest

from tests_eater_authorizer import utils


PHP_SESSION_DATA_WITH_EATER = (
    '_sf2_attributes|a:1:{'
    's:13:"_security_api";s:144:"C:36:'
    '"Eda\\Eater\\Common\\Security\\EaterToken":95:'
    '{a:1:{i:0;C:15:"App\\Entity\\User":57:{a:2:'
    '{i:0;i:62888001;i:1;s:24:"+79876543210@example.com";}}}}";}'
    '_sf2_meta|a:3:{s:1:"u";i:1583845279;s:1:"c";'
    'i:1582975478;s:1:"l";s:7:"2592000";}'
)

PHP_SESSION_DATA_WITHOUT_EATER = (
    '_sf2_attributes|a:0:{}_sf2_meta|a:3:'
    '{s:1:"u";i:1584031032;s:1:"c";i:1584031032'
    ';s:1:"l";s:7:"2592000";}'
)

JSON_SESSION_DATA_WITH_EATER = (
    '{"m":{"c":1582975478,"u":1582975478,"t":2592000}'
    ',"a":{"e":{"i":62888001,"u":"+79876543210@example.com"}}}'
)

JSON_SESSION_DATA_WITHOUT_EATER = (
    '{"m":{"c":1584031032,"u":1584031032,"t":2592000},"a":null}'
)

EAP_STORAGE_KEY = 'EAP.'


@pytest.mark.redis_store(
    ['set', EAP_STORAGE_KEY + 'some_token1', 'i_token1'],
    ['expire', EAP_STORAGE_KEY + 'some_token1', 3000],
    ['set', 'i_token1', PHP_SESSION_DATA_WITH_EATER],
    ['expire', 'i_token1', 3000],
    ['set', EAP_STORAGE_KEY + 'some_token2', 'i_token2'],
    ['expire', EAP_STORAGE_KEY + 'some_token2', 3000],
    ['set', 'i_token2', PHP_SESSION_DATA_WITHOUT_EATER],
    ['expire', 'i_token2', 3000],
)
@pytest.mark.parametrize(
    'outer_session_id, inner_session_id, expected_str',
    [
        pytest.param(
            'some_token1',
            'i_token1',
            JSON_SESSION_DATA_WITH_EATER,
            id='with eater',
        ),
        pytest.param(
            'some_token2',
            'i_token2',
            JSON_SESSION_DATA_WITHOUT_EATER,
            id='without eater',
        ),
    ],
)
async def test_switch_php_to_json(
        taxi_eater_authorizer,
        redis_store,
        outer_session_id,
        inner_session_id,
        expected_str,
        taxi_eater_authorizer_monitor,
):
    await taxi_eater_authorizer.tests_control(reset_metrics=True)

    response = await taxi_eater_authorizer.put(
        '/v2/eater/sessions',
        json={'outer_session_id': outer_session_id, 'no_new_session': False},
    )
    assert response.status_code == 200

    session_str = redis_store.get(inner_session_id)

    session = json.loads(session_str)
    expected = json.loads(expected_str)

    utils.remove_key(session, ['m', 'u'])
    utils.remove_key(expected, ['m', 'u'])

    utils.is_subjson(expected, session)
