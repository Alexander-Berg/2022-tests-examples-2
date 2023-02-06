import pytest

pytest_plugins = ['taxi_tests.plugins.taxi.mocks.metadata_storage']


TEST_VALUE = {
    'experiments': [
        {'name': 'exp1', 'position': 1, 'version': 1, 'json': '{}'},
        {
            'name': 'exp2',
            'position': 3,
            'version': 2,
            'json': '{"name1": "val1"}',
        },
    ],
}
TEST_UPDATED = '2018-01-01T00:00:00+00:00'


async def test_store(mockserver_client, mock_metadata_storage):
    store_response = await mockserver_client.put(
        'v1/metadata/store',
        params={'ns': 'some_namespace', 'id': 'some_id'},
        json=TEST_VALUE,
    )

    assert store_response.status_code in [200, 201]


@pytest.mark.metadata_storage(
    metadata_array=[
        {
            'ns': 'some_namespace',
            'id': 'some_id',
            'value': TEST_VALUE,
            'updated': TEST_UPDATED,
        },
    ],
)
async def test_mark(mockserver_client, mock_metadata_storage):
    retrieve_response = await mockserver_client.post(
        'v1/metadata/retrieve',
        params={'ns': 'some_namespace', 'id': 'some_id'},
    )
    assert retrieve_response.status_code == 200
    assert retrieve_response.json() == {
        'value': TEST_VALUE,
        'updated': TEST_UPDATED,
    }

    retrieve_response = await mockserver_client.post(
        'v1/metadata/retrieve',
        params={'ns': 'some_namespace', 'id': 'some_unknown_id'},
    )
    assert retrieve_response.status_code == 404


@pytest.mark.metadata_storage(filename='db_metadata_storage.json')
async def test_mark_file(mockserver_client, mock_metadata_storage):
    retrieve_response = await mockserver_client.post(
        'v1/metadata/retrieve', params={'ns': 'ns1', 'id': 'id2'},
    )
    assert retrieve_response.status_code == 200
    assert retrieve_response.json() == {
        'value': TEST_VALUE,
        'updated': '1970-01-15T06:56:08.000',
    }
    retrieve_response = await mockserver_client.post(
        'v1/metadata/retrieve', params={'ns': 'ns1', 'id': 'some_unknown_id'},
    )
    assert retrieve_response.status_code == 404
