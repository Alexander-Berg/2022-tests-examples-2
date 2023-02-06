import pytest


@pytest.mark.parametrize(
    'input_data,expected_code,expected_data',
    [
        (
            {'namespace': 'namespace1', 'name': 'lock1'},
            200,
            {
                'status': 'acquired',
                'namespace': 'namespace1',
                'name': 'lock1',
                'owner': 'owner1',
            },
        ),
        (
            {'namespace': 'namespace1', 'name': 'lock2'},
            200,
            {'name': 'lock2', 'namespace': 'namespace1', 'status': 'free'},
        ),
        (
            {'namespace': 'namespace1', 'name': 'lock3'},
            200,
            {'name': 'lock3', 'namespace': 'namespace1', 'status': 'free'},
        ),
    ],
)
async def test_locks_status(
        taxi_distlocks, input_data, expected_code, expected_data,
):
    response = await taxi_distlocks.get('/v1/locks/status/', params=input_data)
    assert response.status_code == expected_code
    lock_status = response.json()
    assert lock_status['status'] == expected_data['status']
    assert lock_status['namespace'] == expected_data['namespace']
    assert lock_status['name'] == expected_data['name']
    if lock_status['status'] == 'acquired':
        assert lock_status['owner'] == expected_data['owner']
        assert 'expiration_time' in lock_status
        assert 'fencing_token' in lock_status
        assert 'updated' in lock_status
