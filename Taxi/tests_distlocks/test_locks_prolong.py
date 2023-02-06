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
                'namespace': 'namespace1',
                'name': 'lock1',
                'owner': 'owner2',
                'ttl': 60,
            },
            409,
            {
                'code': 'UNABLE_TO_PROLONG_LOCK',
                'message': (
                    'lock is acquired by another owner or already '
                    'released or already expired'
                ),
            },
        ),
        (
            {
                'namespace': 'namespace1',
                'name': 'lock2',
                'owner': 'owner1',
                'ttl': 60,
            },
            409,
            None,
        ),
    ],
)
async def test_locks_prolong(
        taxi_distlocks, input_data, expected_code, expected_data,
):
    response = await taxi_distlocks.post('/v1/locks/prolong/', json=input_data)
    assert response.status_code == expected_code
    if expected_data is not None:
        assert response.json() == expected_data
