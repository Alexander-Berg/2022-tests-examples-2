import pytest


async def test_default(mockserver_client):
    response = await mockserver_client.get(
        'v1/keyset', params={'name': 'some_keyset'},
    )
    assert response.status_code == 200

    data = response.json()
    assert data['keyset_name'] == 'some_keyset'
    assert data['keys'] == []


@pytest.mark.translations(
    notify={
        'key1': {'ru': '%(cost)s руб.', 'en': '%(cost)s dollars.'},
        'key2': {'en': 'fixed'},
    },
    client_messages={
        'key3': {'ru': 'сообщение2', 'en': ['message2', 'few_messages2']},
    },
)
async def test_mark(mockserver_client):
    response = await mockserver_client.get(
        'v1/keyset', params={'name': 'notify'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['keyset_name'] == 'notify'
    assert data['keys'] == [
        {
            'key_id': 'key1',
            'values': [
                {
                    'conditions': {'form': 1, 'locale': {'language': 'ru'}},
                    'value': '%(cost)s руб.',
                },
                {
                    'conditions': {'form': 1, 'locale': {'language': 'en'}},
                    'value': '%(cost)s dollars.',
                },
            ],
        },
        {
            'key_id': 'key2',
            'values': [
                {
                    'conditions': {'form': 1, 'locale': {'language': 'en'}},
                    'value': 'fixed',
                },
            ],
        },
    ]

    response2 = await mockserver_client.get(
        'v1/keyset', params={'name': 'client_messages'},
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2['keyset_name'] == 'client_messages'
    assert data2['keys'] == [
        {
            'key_id': 'key3',
            'values': [
                {
                    'conditions': {'form': 1, 'locale': {'language': 'ru'}},
                    'value': 'сообщение2',
                },
                {
                    'conditions': {'form': 1, 'locale': {'language': 'en'}},
                    'value': 'message2',
                },
                {
                    'conditions': {'form': 2, 'locale': {'language': 'en'}},
                    'value': 'few_messages2',
                },
            ],
        },
    ]


@pytest.mark.translations(keyset1={'key': {'en': 'enenen'}})
@pytest.mark.translations(keyset2={'key': {'en': 'enenen'}})
async def test_few_marks(mockserver_client):
    response = await mockserver_client.get(
        'v1/keyset', params={'name': 'keyset1'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['keyset_name'] == 'keyset1'
    assert data['keys'] == [
        {
            'key_id': 'key',
            'values': [
                {
                    'conditions': {'form': 1, 'locale': {'language': 'en'}},
                    'value': 'enenen',
                },
            ],
        },
    ]

    response = await mockserver_client.get(
        'v1/keyset', params={'name': 'keyset2'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['keyset_name'] == 'keyset2'
    assert data['keys'] == [
        {
            'key_id': 'key',
            'values': [
                {
                    'conditions': {'form': 1, 'locale': {'language': 'en'}},
                    'value': 'enenen',
                },
            ],
        },
    ]


@pytest.mark.translations(keyset1={'key': {'en': 'enenen'}})
async def test_request_errors(mockserver_client):
    response = await mockserver_client.get('v1/keyset')
    assert response.status_code == 400

    response = await mockserver_client.get(
        'v1/keyset',
        params={
            'name': 'keyset1',
            'last_update': '3000-01-01T00:00:03.012+0000',
        },
    )
    assert response.status_code == 304


async def test_file_keyset(mockserver_client):
    response = await mockserver_client.get(
        'v1/keyset', params={'name': 'test_file_keyset'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['keyset_name'] == 'test_file_keyset'
    assert data['keys'] == [
        {
            'key_id': 'test_file_key',
            'values': [
                {
                    'conditions': {'form': 1, 'locale': {'language': 'fi'}},
                    'value': 'test file key value fi from default dir',
                },
                {
                    'conditions': {'form': 2, 'locale': {'language': 'en'}},
                    'value': 'test file key value en form 2',
                },
                {
                    'conditions': {'form': 1, 'locale': {'language': 'en'}},
                    'value': 'test file key value en',
                },
                {
                    'conditions': {'form': 1, 'locale': {'language': 'ru'}},
                    'value': 'test file key value',
                },
            ],
        },
    ]


@pytest.mark.translations(
    test_file_keyset={
        'test_file_key': {
            'en': 'overwrite en',
            'ru': ['overwrite', 'new value form 2'],
        },
    },
)
async def test_file_keyset_overwrite(mockserver_client):
    response = await mockserver_client.get(
        'v1/keyset', params={'name': 'test_file_keyset'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['keyset_name'] == 'test_file_keyset'
    assert data['keys'] == [
        {
            'key_id': 'test_file_key',
            'values': [
                {
                    'conditions': {'form': 1, 'locale': {'language': 'fi'}},
                    'value': 'test file key value fi from default dir',
                },
                {
                    'conditions': {'form': 2, 'locale': {'language': 'en'}},
                    'value': 'test file key value en form 2',
                },
                {
                    'conditions': {'form': 1, 'locale': {'language': 'en'}},
                    'value': 'overwrite en',
                },
                {
                    'conditions': {'form': 1, 'locale': {'language': 'ru'}},
                    'value': 'overwrite',
                },
                {
                    'conditions': {'form': 2, 'locale': {'language': 'ru'}},
                    'value': 'new value form 2',
                },
            ],
        },
    ]
