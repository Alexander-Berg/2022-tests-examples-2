import pytest

from taxi_testsuite.plugins import experiments3 as exp_module


@pytest.fixture(autouse=True)
def setup_exp_module(experiments3):
    experiments3.strict_schema_checks = True


async def test_default(mockserver_client):
    response = await mockserver_client.get('v1/experiments/updates')
    assert response.status_code == 200

    data = response.json()
    assert 'experiments' in data
    assert data['experiments'] == []

    response = await mockserver_client.get('v1/configs/updates')
    assert response.status_code == 200

    data = response.json()
    assert 'configs' in data
    assert data['configs'] == []


async def test_no_consumer(mockserver_client):
    response = await mockserver_client.get(
        'v1/experiments/updates', params={'consumer': 'not_existing_consumer'},
    )
    assert response.status_code == 200

    data = response.json()
    assert 'experiments' in data
    assert data['experiments'] == []

    response = await mockserver_client.get(
        'v1/configs/updates', params={'consumer': 'not_existing_consumer'},
    )
    assert response.status_code == 200

    data = response.json()
    assert 'configs' in data
    assert data['configs'] == []


@pytest.mark.parametrize(
    'kwargs,is_bad',
    [
        pytest.param(
            {
                'match': {'enabled': True, 'predicate': {'type': 'true'}},
                'default_value': {},
                'name': 'test',
            },
            True,
            id='no consumers in match and args',
        ),
        pytest.param(
            {
                'match': {'enabled': True, 'predicate': {'type': 'true'}},
                'consumers': ['test'],
                'default_value': {},
                'name': 'test',
            },
            False,
            id='empty match and fill consumers',
        ),
        pytest.param(
            {
                'match': {
                    'enabled': True,
                    'predicate': {'type': 'true'},
                    'consumers': [{'name': 'test'}],
                },
                'default_value': {},
                'name': 'test',
            },
            False,
            id='fill match and no consumers',
        ),
    ],
)
async def test_fill_consumer(experiments3, kwargs, is_bad):
    if is_bad:
        with pytest.raises(AssertionError):
            experiments3.add_experiment(**kwargs)
    else:
        experiments3.add_experiment(**kwargs)


@pytest.mark.experiments3(filename='exp3.json')
async def test_mark_filename(mockserver_client, mockserver):
    response = await mockserver_client.get(
        'v1/experiments/updates', params={'consumer': 'test_consumer'},
    )

    assert response.status_code == 200

    data = response.json()
    assert 'experiments' in data
    assert data['experiments'] == [
        {
            'name': 'exp1',
            'last_modified_at': 1,
            'clauses': [
                {
                    'title': 'a',
                    'value': {'enabled': True},
                    'predicate': {'type': 'true'},
                },
            ],
            'match': {
                'consumers': [{'name': 'test_consumer'}],
                'enabled': True,
                'action_time': {'from': '2020-08-12', 'to': '2023-8-12'},
                'predicate': {'type': 'true'},
                'applications': [
                    {
                        'name': 'iphone',
                        'version_range': {'from': '1000.1000.1000'},
                    },
                ],
            },
        },
    ]


@pytest.mark.parametrize(
    'kwargs_value,exception_type',
    [
        ({'filename': 'bad.json'}, exp_module.BadTestArgs),
        ({'filename': 'bad_schema.json'}, exp_module.BadTestArgs),
        ({'filename': 'incorrect_schema.json'}, exp_module.BadTestStatic),
    ],
)
async def test_bad_json(experiments3, load_json, kwargs_value, exception_type):
    class _Marker:
        kwargs = kwargs_value

    with pytest.raises(exception_type):
        experiments3.add_experiment3_from_marker(_Marker, load_json)


@pytest.mark.experiments3(filename='configs3.json')
async def test_mark_configs_filename(mockserver_client, mockserver):
    response = await mockserver_client.get(
        'v1/configs/updates', params={'consumer': 'test_consumer'},
    )

    assert response.status_code == 200

    data = response.json()
    assert 'configs' in data
    assert data['configs'] == [
        {
            'name': 'config1',
            'last_modified_at': 1,
            'default_value': {},
            'clauses': [
                {
                    'title': 'a',
                    'value': {'enabled': True},
                    'predicate': {'type': 'true'},
                },
            ],
            'match': {
                'consumers': [{'name': 'test_consumer'}],
                'enabled': True,
                'predicate': {'type': 'true'},
            },
        },
    ]


@pytest.mark.experiments3(filename='many_experiments.json')
async def test_fill_last_modified_at(mockserver_client, mockserver):
    response = await mockserver_client.get(
        'v1/experiments/updates', params={'consumer': 'test_consumer'},
    )

    assert response.status_code == 200

    data = response.json()
    sorted(data['experiments'], key=lambda x: x['last_modified_at'])
    assert data['experiments'][-1]['last_modified_at'] == 4


@pytest.mark.experiments3(
    name='test_exp',
    consumers=['test_consumer'],
    clauses=[],
    default_value=True,
)
async def test_mark_kwargs(mockserver_client, mockserver):
    response = await mockserver_client.get(
        'v1/experiments/updates', params={'consumer': 'test_consumer'},
    )
    assert response.status_code == 200

    data = response.json()
    assert 'experiments' in data
    assert data['experiments'] == [
        {
            'name': 'test_exp',
            'last_modified_at': 1,
            'clauses': [],
            'enable_debug': False,
            'trait_tags': [],
            'match': {
                'consumers': [{'name': 'test_consumer'}],
                'enabled': True,
                'predicate': {'type': 'true'},
            },
            'default_value': True,
        },
    ]


@pytest.mark.experiments3(
    is_config=True,
    name='test_configs',
    consumers=['test_consumer_configs'],
    clauses=[],
    default_value={'enabled': True},
)
async def test_mark_kwargs_configs(mockserver_client, mockserver):
    response = await mockserver_client.get(
        'v1/configs/updates', params={'consumer': 'test_consumer_configs'},
    )
    assert response.status_code == 200

    data = response.json()
    assert 'configs' in data
    assert data['configs'] == [
        {
            'name': 'test_configs',
            'last_modified_at': 1,
            'clauses': [],
            'enable_debug': False,
            'trait_tags': [],
            'match': {
                'enabled': True,
                'consumers': [{'name': 'test_consumer_configs'}],
                'predicate': {'type': 'true'},
            },
            'default_value': {'enabled': True},
        },
    ]


@pytest.mark.parametrize(
    'consumer, expected_data',
    [
        pytest.param(
            'test_consumer',
            [
                {
                    'name': 'default_experiment',
                    'last_modified_at': 1,
                    'clauses': [],
                    'match': {
                        'consumers': [{'name': 'test_consumer'}],
                        'enabled': True,
                        'predicate': {'type': 'true'},
                        'applications': [],
                        'action_time': {
                            'from': '2020-01-01T00:00:00+0300',
                            'to': '2022-12-31T23:59:59+0300',
                        },
                    },
                    'default_value': True,
                },
            ],
            id='set all defaults from file',
            marks=pytest.mark.experiments3(),
        ),
        pytest.param(
            'client/launch',
            [
                {
                    'name': 'shortcut_experiment',
                    'last_modified_at': 1,
                    'enable_debug': False,
                    'trait_tags': [],
                    'clauses': [],
                    'match': {
                        'enabled': True,
                        'predicate': {'type': 'true'},
                        'consumers': [{'name': 'client/launch'}],
                    },
                    'default_value': {'enabled': True},
                },
            ],
            marks=pytest.mark.experiments3(
                name='shortcut_experiment',
                consumers=['client/launch'],
                default_value={'enabled': True},
            ),
            id='set name, consumers and value',
        ),
        pytest.param(
            'client/launch',
            [
                {
                    'name': 'shortcut_experiment',
                    'last_modified_at': 1,
                    'enable_debug': False,
                    'trait_tags': [],
                    'clauses': [
                        {
                            'title': 'first',
                            'predicate': {'type': 'true'},
                            'value': {'enbled': False},
                        },
                    ],
                    'match': {
                        'enabled': True,
                        'predicate': {'type': 'true'},
                        'consumers': [{'name': 'client/launch'}],
                    },
                },
            ],
            marks=pytest.mark.experiments3(
                name='shortcut_experiment',
                consumers=['client/launch'],
                clauses=[
                    {
                        'title': 'first',
                        'predicate': {'type': 'true'},
                        'value': {'enbled': False},
                    },
                ],
            ),
            id='set name, consumers and clause',
        ),
        pytest.param(
            'cargo-claims/finish-estimate',
            [
                {
                    'name': 'cargo_eta_config',
                    'last_modified_at': 1,
                    'enable_debug': False,
                    'trait_tags': [],
                    'clauses': [],
                    'match': {
                        'enabled': True,
                        'predicate': {'type': 'true'},
                        'consumers': [
                            {'name': 'cargo-claims/finish-estimate'},
                        ],
                    },
                    'default_value': {'unloading_time': 10},
                },
            ],
            marks=pytest.mark.experiments3(
                match={'predicate': {'type': 'true'}, 'enabled': True},
                name='cargo_eta_config',
                consumers=['cargo-claims/finish-estimate'],
                clauses=[],
                default_value={'unloading_time': 10},
            ),
            id='update match',
        ),
        pytest.param(
            'cargo-claims/finish-estimate',
            [
                {
                    'name': 'cargo_eta_config',
                    'last_modified_at': 1,
                    'enable_debug': False,
                    'trait_tags': [],
                    'clauses': [],
                    'match': {
                        'enabled': True,
                        'predicate': {'type': 'true'},
                        'consumers': [
                            {'name': 'cargo-claims/finish-estimate'},
                        ],
                        'applications': [
                            {
                                'name': 'android',
                                'version_range': {
                                    'from': '0.0.0',
                                    'to': '99.99.99',
                                },
                            },
                        ],
                    },
                    'default_value': {'unloading_time': 10},
                },
            ],
            marks=pytest.mark.experiments3(
                match={'predicate': {'type': 'true'}, 'enabled': True},
                name='cargo_eta_config',
                consumers=['cargo-claims/finish-estimate'],
                clauses=[],
                applications=['android'],
                default_value={'unloading_time': 10},
            ),
            id='update match with apps',
        ),
    ],
)
async def test_shortcut(
        mockserver_client, mockserver, consumer, expected_data,
):
    response = await mockserver_client.get(
        'v1/experiments/updates', params={'consumer': consumer},
    )
    assert response.status_code == 200

    data = response.json()
    assert 'experiments' in data
    assert data['experiments'] == expected_data
