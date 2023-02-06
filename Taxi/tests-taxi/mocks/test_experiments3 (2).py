import pytest


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
            'clauses': [{'title': 'a'}],
            'match': {'consumers': [{'name': 'test_consumer'}]},
        },
    ]


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
            'name': 'exp1',
            'last_modified_at': 1,
            'clauses': [{'title': 'a'}],
            'match': {'consumers': [{'name': 'test_consumer'}]},
        },
    ]


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
            'match': {
                'applications': [],
                'action_time': {
                    'from': '2020-01-01T00:00:00+0300',
                    'to': '2120-12-31T23:59:59+0300',
                },
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
    default_value=True,
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
            'match': {
                'applications': [],
                'action_time': {
                    'from': '2020-01-01T00:00:00+0300',
                    'to': '2120-12-31T23:59:59+0300',
                },
                'enabled': True,
                'predicate': {'type': 'true'},
            },
            'default_value': True,
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
                    'clauses': [],
                    'match': {
                        'enabled': True,
                        'predicate': {'type': 'true'},
                        'applications': [],
                        'action_time': {
                            'from': '2020-01-01T00:00:00+0300',
                            'to': '2120-12-31T23:59:59+0300',
                        },
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
                        'applications': [],
                        'action_time': {
                            'from': '2020-01-01T00:00:00+0300',
                            'to': '2120-12-31T23:59:59+0300',
                        },
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
