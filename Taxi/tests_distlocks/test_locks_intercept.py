import pytest


ERROR_400 = {'code': 'BAD_REQUEST', 'message': 'You must change owner'}

ERROR_409 = {
    'code': 'UNABLE_TO_INTERCEPT_LOCK',
    'message': (
        'lock is acquired by another owner or already '
        'released or already expired'
    ),
}


@pytest.mark.parametrize(
    'input_data,expected_code,expected_data',
    [
        (
            {
                'lock': {
                    'namespace': 'namespace1',
                    'name': 'lock1',
                    'owner': 'owner1',
                },
                'updates': {'owner': 'owner2', 'ttl': 60},
            },
            200,
            {
                'name': 'lock1',
                'namespace': 'namespace1',
                'owner': 'owner2',
                'status': 'acquired',
            },
        ),
        (
            {
                'lock': {'namespace': 'namespace1', 'name': 'lock1'},
                'updates': {'owner': 'owner2'},
            },
            200,
            {
                'name': 'lock1',
                'namespace': 'namespace1',
                'owner': 'owner2',
                'status': 'acquired',
            },
        ),
        (
            {
                'lock': {
                    'namespace': 'namespace1',
                    'name': 'lock1',
                    'owner': 'owner1',
                },
                'updates': {'owner': 'owner1', 'ttl': 60},
            },
            400,
            ERROR_400,
        ),
        (
            {
                'lock': {
                    'namespace': 'namespace1',
                    'name': 'lock1',
                    'owner': 'not_found',
                },
                'updates': {'owner': 'owner1', 'ttl': 60},
            },
            409,
            ERROR_409,
        ),
        (
            {
                'lock': {'namespace': 'namespace1', 'name': 'not_found'},
                'updates': {'owner': 'owner1', 'ttl': 60},
            },
            409,
            ERROR_409,
        ),
    ],
)
async def test_locks_intercept(
        taxi_distlocks, input_data, expected_code, expected_data,
):
    response = await taxi_distlocks.post(
        '/v1/locks/intercept/', json=input_data,
    )
    assert response.status_code == expected_code
    result = response.json()
    if expected_code == 200:
        for field in [
                'updated',
                'created',
                'expiration_time',
                'fencing_token',
        ]:
            assert result.pop(field)
    assert result == expected_data
