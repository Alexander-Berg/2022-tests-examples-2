import pytest


@pytest.mark.translations(
    client_messages={
        'string_for_translating': {'test_locale': 'result_string'},
    },
)
@pytest.mark.experiments3(
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

    response = await taxi_exp3_matcher.post('/v1/typed_experiments/', request)
    assert response.status_code == 200
    content = response.json()
    assert len(content['items']) == 1
    l10n = content['items'][0]['value']['l10n']
    assert l10n['key_in_result_dict'] == 'result_string'


@pytest.mark.translations(
    client_messages={
        'string_for_translating': {'test_locale': 'result_string'},
    },
)
@pytest.mark.experiments3(
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
                    'keyset': 'BAD_KEYSET',
                },
            },
        ],
    },
)
async def test_exp3_matcher_localization_fails(taxi_exp3_matcher, now):
    request = {'consumer': 'launch', 'args': [], 'locale': 'test_locale'}
    response = await taxi_exp3_matcher.post('/v1/typed_experiments/', request)
    assert response.status_code == 200
    contents = response.json()
    assert len(contents['items']) == 1
    l10n = contents['items'][0]['value']['l10n']
    assert l10n['key_in_result_dict'] == 'default_string'


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
        (True, '1:-2:test_locale', '1:-1:test_locale', 'updated'),
        (True, '2:0:test_locale', '1:-1:test_locale', 'updated'),
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
    experiments3.add_experiment(
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
    response = await taxi_exp3_matcher.post('/v1/typed_experiments/', request)
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


def transform_decorator(country):
    return pytest.mark.experiments3(
        name='test',
        consumers=['launch'],
        match={
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'country',
                    'arg_type': 'string',
                    'value': country,
                },
            },
            'enabled': True,
        },
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


@pytest.mark.translations(
    client_messages={
        'string_for_translating': {'test_locale': 'result_string'},
    },
)
@pytest.mark.parametrize(
    'ipaddress,preserve_src_kwargs',
    (
        pytest.param('95.59.90.0', True, marks=[transform_decorator('kz')]),
        pytest.param('185.15.98.233', True, marks=[transform_decorator('ru')]),
        pytest.param(
            '93.170.252.25', False, marks=[transform_decorator('by')],
        ),
    ),
)
async def test_exp3_matcher_typed_transform_country_by_ip(
        taxi_exp3_matcher, ipaddress, preserve_src_kwargs, now,
):

    request = {
        'consumer': 'launch',
        'args': [{'name': 'ip', 'type': 'string', 'value': ipaddress}],
        'kwargs_transformations': [
            {
                'type': 'country_by_ip',
                'src_kwargs': ['ip'],
                'dst_kwarg': 'country',
                'preserve_src_kwargs': preserve_src_kwargs,
            },
        ],
        'locale': 'test_locale',
    }

    response = await taxi_exp3_matcher.post('/v1/typed_experiments/', request)
    assert response.status_code == 200
    content = response.json()
    assert len(content['items']) == 1
    assert (
        content['items'][0]['value']['l10n']['key_in_result_dict']
        == 'result_string'
    )
