import pytest


@pytest.mark.translations(
    client_messages={
        'string_for_translating': {'test_locale': 'result_string'},
    },
)
@pytest.mark.experiments3(
    is_config=True,
    name='test1',
    consumers=['launch', 'client_protocol/launch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'l10n': [
            {
                'default': 'default_string',
                'key': 'key_in_result_dict',
                'tanker': {
                    'key': 'string_for_translating',
                    'keyset': 'client_messages',
                },
            },
        ],
    },
)
async def test_exp3_matcher_localization(taxi_exp3_matcher, now):
    request = {'consumer': 'launch', 'args': [], 'locale': 'test_locale'}

    response = await taxi_exp3_matcher.post('/v1/typed_configs/', request)
    assert response.status_code == 200
    content = response.json()
    assert len(content['items']) == 1
    l10n = content['items'][0]['value']['l10n']
    assert l10n['key_in_result_dict'] == 'result_string'


@pytest.mark.config(
    EXPERIMENTS3_SERVICE_CONSUMER_RELOAD=['client_protocol/launch'],
)
@pytest.mark.translations(
    client_messages={
        'string_for_translating': {'test_locale': 'result_string'},
    },
)
@pytest.mark.parametrize(
    'cache_enabled, version, exp_version, exp_cache_status',
    [
        (True, '0:0:test_locale', '1:-1:test_locale', 'updated'),
        (True, '1:-1:test_locale', None, 'not_modified'),
        (False, '0:0:test_locale', None, 'no_cache'),
    ],
)
async def test_cached_experiments(
        taxi_exp3_matcher,
        taxi_config,
        cache_enabled,
        version,
        exp_version,
        exp_cache_status,
        experiments3,
):
    experiments3.add_config(
        name='test1',
        consumers=['client_protocol/launch'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'l10n': [
                {
                    'default': 'default_string',
                    'key': 'key_in_result_dict',
                    'tanker': {
                        'key': 'string_for_translating',
                        'keyset': 'client_messages',
                    },
                },
            ],
        },
        trait_tags=['cache-on-clients'] if cache_enabled else [],
    )
    request = {
        'consumer': 'client_protocol/launch',
        'args': [],
        'locale': 'test_locale',
        'cached_exp_result_identifiers': {
            'items': [{'name': 'test1', 'version': version}],
        },
    }
    expected_value = {'l10n': {'key_in_result_dict': 'result_string'}}
    response = await taxi_exp3_matcher.post('/v1/typed_configs/', request)
    assert response.status_code == 200
    assert len(response.json()['items']) == 1

    cached_item = response.json()['items'][0]
    assert cached_item['cache_status'] == exp_cache_status

    if exp_version:
        assert cached_item['version'] == exp_version
    else:
        assert 'version' not in cached_item

    if exp_cache_status == 'not_modified':
        assert 'value' not in cached_item
    else:
        assert cached_item['value'] == expected_value
