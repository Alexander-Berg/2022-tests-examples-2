import pytest


@pytest.mark.servicetest
async def test_admin_test_kinds(taxi_persey_labs):
    response = await taxi_persey_labs.get('/admin/v1/test-kinds')

    assert response.status_code == 200
    assert response.json() == {
        'test_kinds': [{'id': 'covid_slow'}, {'id': 'covid_fast'}],
    }
