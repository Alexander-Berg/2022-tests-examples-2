import pytest


@pytest.mark.experiments3(filename='configs_match.json')
async def test_exp3_matcher_config_match_with_timepoint(
        taxi_exp3_matcher, now,
):
    request = {
        'consumer': 'launch',
        'args': [
            {
                'name': 'version',
                'type': 'application_version',
                'value': '5.5.5',
            },
            {'name': 'application', 'type': 'application', 'value': 'android'},
            {
                'name': 'created',
                'type': 'timepoint',
                'value': '2020-02-20T20:20:20+03:00',
            },
        ],
    }

    response = await taxi_exp3_matcher.post('/v1/configs/', request)
    assert response.status_code == 200
    content = response.json()
    assert content['version'] == 1
    assert len(content['items']) == 2
    assert content['items'][0]['value'] == 987543


@pytest.mark.experiments3(filename='configs_match.json')
async def test_exp3_matcher_config_match_by_name(taxi_exp3_matcher, now):
    config_name = 'test1'
    request = {
        'consumer': 'launch',
        'config_name': config_name,
        'args': [
            {
                'name': 'version',
                'type': 'application_version',
                'value': '5.5.5',
            },
            {'name': 'application', 'type': 'application', 'value': 'android'},
            {
                'name': 'created',
                'type': 'timepoint',
                'value': '2020-02-20T20:20:20+03:00',
            },
        ],
    }

    response = await taxi_exp3_matcher.post('/v1/configs/', request)
    assert response.status_code == 200
    content = response.json()
    assert content['version'] == 1
    assert len(content['items']) == 1
    assert content['items'][0]['value'] == 987543
    assert content['items'][0]['name'] == config_name


@pytest.mark.experiments3(
    is_config=True,
    name='test',
    consumers=['launch'],
    match={
        'predicate': {
            'type': 'lt',
            'init': {
                'arg_name': 'application.platform_version',
                'value': '10.0.0',
                'arg_type': 'version',
            },
        },
        'enabled': True,
        'applications': [
            {
                'name': 'android',
                'version_range': {'from': '0.0.0', 'to': '9.9.9'},
            },
        ],
    },
    clauses=[],
    default_value={'key': 'default_value'},
)
async def test_exp3_matcher_configs_application_header(taxi_exp3_matcher, now):
    request = {'consumer': 'launch', 'args': []}

    response = await taxi_exp3_matcher.post(
        '/v1/configs/',
        request,
        headers={
            'X-Request-Application': (
                'app_name=android,app_ver1=6,app_ver2=6,app_ver3=6,'
                'platform_ver1=2,platform_ver2=0,platform_ver3=0'
            ),
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content['items']) == 1
    assert content['items'][0]['value']['key'] == 'default_value'


def transform_decorator(country):
    return pytest.mark.experiments3(
        is_config=True,
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
        default_value={'key': 'default_value'},
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
async def test_exp3_matcher_configs_transform_country_by_ip(
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
    }

    response = await taxi_exp3_matcher.post('/v1/configs/', request)
    assert response.status_code == 200
    content = response.json()
    assert len(content['items']) == 1
    assert content['items'][0]['value']['key'] == 'default_value'


@pytest.mark.experiments3(
    is_config=True,
    name='test1',
    consumers=['launch', 'client_protocol/launch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'type': 'in_set',
                'init': {
                    'arg_name': 'bulk_kwarg',
                    'set': ['hit'],
                    'set_elem_type': 'string',
                },
            },
            'value': 'clause',
        },
    ],
    default_value='default',
)
async def test_exp3_matcher_configs_bulk(taxi_exp3_matcher, now):
    request = {
        'items': [
            {
                'consumer': 'launch',
                'args': [
                    {'name': 'bulk_kwarg', 'type': 'string', 'value': 'hit'},
                ],
            },
            {
                'consumer': 'launch',
                'args': [
                    {'name': 'bulk_kwarg', 'type': 'string', 'value': 'miss'},
                ],
            },
        ],
    }

    response = await taxi_exp3_matcher.post('/v1/configs/bulk/', request)
    assert response.status_code == 200
    content = response.json()
    assert len(content['results']) == 2
    assert content['results'][0]['items'][0]['value'] == 'clause'
    assert content['results'][1]['items'][0]['value'] == 'default'


@pytest.mark.experiments3(
    is_config=True,
    name='test1',
    consumers=['launch', 'client_protocol/launch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'foo': 9875},
)
async def test_exp3_matcher_config_match_metric(
        taxi_exp3_matcher, taxi_exp3_matcher_monitor,
):
    request = {
        'consumer': 'launch',
        'args': [
            {
                'name': 'version',
                'type': 'application_version',
                'value': '5.5.5',
            },
            {'name': 'application', 'type': 'application', 'value': 'android'},
        ],
    }

    metrics_before = await taxi_exp3_matcher_monitor.get_metric(
        'experiments3-cache',
    )
    match_metric_before = metrics_before.get(
        'experiments3.config.test1.default', 0,
    )

    response = await taxi_exp3_matcher.post('/v1/configs/', request)
    assert response.status_code == 200

    metrics_after = await taxi_exp3_matcher_monitor.get_metric(
        'experiments3-cache',
    )
    match_metric_after = metrics_after.get(
        'experiments3.config.test1.default', 0,
    )

    assert match_metric_after - match_metric_before == 1
