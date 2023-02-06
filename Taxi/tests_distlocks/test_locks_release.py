import pytest


@pytest.mark.parametrize(
    'input_data,expected_code',
    [
        ({'namespace': 'namespace1', 'name': 'lock1', 'owner': 'owner1'}, 200),
        ({'namespace': 'namespace1', 'name': 'lock1', 'owner': 'owner2'}, 409),
        ({'namespace': 'namespace1', 'name': 'lock2', 'owner': 'owner1'}, 200),
    ],
)
async def test_locks_release(taxi_distlocks, input_data, expected_code):
    response = await taxi_distlocks.post('/v1/locks/release/', json=input_data)
    assert response.status_code == expected_code
    if response.status_code == 200:
        assert response.json() == {}
