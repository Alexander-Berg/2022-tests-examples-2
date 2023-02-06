import pytest


async def test_default(mockserver_client):
    response = await mockserver_client.get('v1/experiments/updates')
    assert response.status_code == 200

    data = response.json()
    assert 'experiments' in data
    assert data['experiments'] == []


async def test_no_consumer(mockserver_client):
    response = await mockserver_client.get(
        'v1/experiments/updates', params={'consumer': 'not_existing_consumer'},
    )
    assert response.status_code == 200

    data = response.json()
    assert 'experiments' in data
    assert data['experiments'] == []


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


@pytest.mark.driver_experiments3(
    uuid='0', dbid='a', name='test_exp', consumers=['test_consumer'],
)
async def test_mark_driver_experiments(mockserver_client):
    response = await mockserver_client.get(
        'v1/experiments/updates', params={'consumer': 'test_consumer'},
    )

    assert response.status_code == 200

    data = response.json()
    assert 'experiments' in data
    assert data['experiments'] == [
        {
            'clauses': [],
            'default_value': {},
            'last_modified_at': 1,
            'match': {
                'applications': [{'name': 'taximeter', 'version_range': {}}],
                'consumers': [{'name': 'test_consumer'}],
                'driver_id': '0',
                'enabled': True,
                'park_db_id': 'a',
                'predicate': {'type': 'true'},
            },
            'name': 'test_exp',
        },
    ]
