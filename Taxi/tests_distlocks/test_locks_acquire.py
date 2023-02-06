import pytest


@pytest.mark.parametrize(
    'input_data,expected_code,expected_data',
    [
        (
            {
                'namespace': 'namespace1',
                'name': 'lock1',
                'owner': 'owner1',
                'ttl': 60,
            },
            200,
            None,
        ),
        (
            {
                'namespace': 'namespace2',
                'name': 'lock1',
                'owner': 'owner1',
                'ttl': 60,
            },
            404,
            {
                'code': 'NAMESPACE_IS_NOT_FOUND',
                'message': 'namespace is not found',
            },
        ),
        (
            {
                'namespace': 'namespace1',
                'name': 'lock2',
                'owner': 'owner1',
                'ttl': 60,
            },
            200,
            {'owner': 'owner1'},
        ),
        (
            {
                'namespace': 'namespace1',
                'name': 'lock2',
                'owner': 'owner2',
                'ttl': 60,
            },
            409,
            {
                'code': 'LOCK_IS_ACQUIRED_BY_ANOTHER_OWNER',
                'message': 'lock is acquired by another owner',
            },
        ),
        (
            {
                'namespace': 'namespace1',
                'name': 'lock3',
                'owner': 'owner2',
                'ttl': 60,
            },
            200,
            {'owner': 'owner2'},
        ),
    ],
)
async def test_locks_acquire(
        taxi_distlocks, input_data, expected_code, expected_data,
):
    response = await taxi_distlocks.post('/v1/locks/acquire/', json=input_data)
    assert response.status_code == expected_code
    if expected_data is not None:
        lock_status = response.json()
        if response.status_code == 200:
            assert lock_status['owner'] == expected_data['owner']
        else:
            assert lock_status == expected_data
