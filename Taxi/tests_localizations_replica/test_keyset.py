import pytest


@pytest.mark.parametrize(
    ('params', 'response_code', 'response_body'),
    [
        (
            {
                'name': 'chatterbox',
                'last_update': '2000-01-01T09:00:00.000+00:00',
            },
            200,
            {
                'keys': [
                    {
                        'key_id': 'test_key_1',
                        'values': [
                            {
                                'conditions': {
                                    'form': 1,
                                    'locale': {'language': 'ru'},
                                },
                                'value': 'test_key_1_on_rus',
                            },
                            {
                                'conditions': {
                                    'form': 1,
                                    'locale': {'language': 'en'},
                                },
                                'value': 'test_key_1_on_en',
                            },
                            {
                                'conditions': {
                                    'form': 2,
                                    'locale': {'language': 'en'},
                                },
                                'value': 'test_key_1_on_en_in_plural_form_few',
                            },
                        ],
                    },
                ],
                'keyset_name': 'chatterbox',
                'last_update': '2000-01-01T10:00:00+0000',
            },
        ),
        (
            {'name': 'chatterbox'},
            200,
            {
                'keys': [
                    {
                        'key_id': 'test_key_1',
                        'values': [
                            {
                                'conditions': {
                                    'form': 1,
                                    'locale': {'language': 'ru'},
                                },
                                'value': 'test_key_1_on_rus',
                            },
                            {
                                'conditions': {
                                    'form': 1,
                                    'locale': {'language': 'en'},
                                },
                                'value': 'test_key_1_on_en',
                            },
                            {
                                'conditions': {
                                    'form': 2,
                                    'locale': {'language': 'en'},
                                },
                                'value': 'test_key_1_on_en_in_plural_form_few',
                            },
                        ],
                    },
                ],
                'keyset_name': 'chatterbox',
                'last_update': '2000-01-01T10:00:00+0000',
            },
        ),
        (
            {'name': 'poputka'},
            200,
            {
                'keyset_name': 'poputka',
                'keys': [
                    {
                        'key_id': 'test_poputka_key_1',
                        'values': [
                            {
                                'conditions': {
                                    'form': 1,
                                    'locale': {'language': 'ru'},
                                },
                                'value': 'test_poputka_key_1_on_rus',
                            },
                        ],
                    },
                ],
            },
        ),
    ],
)
async def test_keyset_response_body(
        taxi_localizations_replica, params, response_code, response_body,
):
    response = await taxi_localizations_replica.get('v1/keyset', params=params)

    assert response.status_code == response_code
    assert response.json() == response_body


@pytest.mark.parametrize(
    ('params', 'response_code'),
    [
        (
            {'name': 'chatterbox', 'last_update': '2000-01-01T10:00:00+0000'},
            304,
        ),
        ({'name': 'poputka', 'last_update': '1970-01-01T00:00:00+0000'}, 304),
        (
            {
                'name': 'not_existing_keyset',
                'last_update': '2000-01-01T10:00:00+0000',
            },
            404,
        ),
        (
            {
                'no_keyset_name': 'abc',
                'last_update': '2000-01-01T10:00:00+0000',
            },
            400,
        ),
    ],
)
async def test_keyset_response_status(
        taxi_localizations_replica, params, response_code,
):
    response = await taxi_localizations_replica.get('v1/keyset', params=params)

    assert response.status_code == response_code


@pytest.mark.filldb(localizations_meta='poputka')
@pytest.mark.parametrize(
    ('params', 'response_code', 'response_body'),
    [
        (
            {'name': 'poputka'},
            200,
            {
                'keyset_name': 'poputka',
                'last_update': '2000-01-01T10:00:00+0000',
                'keys': [
                    {
                        'key_id': 'test_poputka_key_1',
                        'values': [
                            {
                                'conditions': {
                                    'form': 1,
                                    'locale': {'language': 'ru'},
                                },
                                'value': 'test_poputka_key_1_on_rus',
                            },
                        ],
                    },
                ],
            },
        ),
        (
            {'name': 'poputka', 'last_update': '1970-01-01T00:00:00+0000'},
            200,
            {
                'keyset_name': 'poputka',
                'last_update': '2000-01-01T10:00:00+0000',
                'keys': [
                    {
                        'key_id': 'test_poputka_key_1',
                        'values': [
                            {
                                'conditions': {
                                    'form': 1,
                                    'locale': {'language': 'ru'},
                                },
                                'value': 'test_poputka_key_1_on_rus',
                            },
                        ],
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.parametrize(
    'cache_control_config',
    [{'enabled': False}, {'enabled': True}, {'enabled': True, 'max-age': 600}],
    ids=[
        'cache_control_disabled',
        'cache_control_no_max_age',
        'cache_control_max_age',
    ],
)
async def test_keyset_got_new_last_update_field_in_meta(
        taxi_localizations_replica,
        taxi_config,
        params,
        response_code,
        response_body,
        cache_control_config,
):
    taxi_config.set(
        LOCALIZATIONS_REPLICA_API_PROXY_CACHE_CONTROL=cache_control_config,
    )

    response = await taxi_localizations_replica.get('v1/keyset', params=params)

    assert response.status_code == response_code
    assert 'application/json' in response.headers.get('Content-Type')
    assert response.json() == response_body

    assert response.headers.get('Cache-Control') == (
        'max-age={}'.format(cache_control_config.get('max-age', 60))
        if cache_control_config['enabled']
        else 'no-cache'
    )
