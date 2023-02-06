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
    match={'consumers': [{'name': 'test_consumer'}]},
    name='test_exp',
    consumers=['test_consumer'],
    clauses=[],
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
            'match': {'consumers': [{'name': 'test_consumer'}]},
        },
    ]


@pytest.mark.experiments3(
    is_config=True,
    match={'consumers': [{'name': 'test_consumer_configs'}]},
    name='test_configs',
    consumers=['test_consumer_configs'],
    clauses=[],
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
            'match': {'consumers': [{'name': 'test_consumer_configs'}]},
        },
    ]
