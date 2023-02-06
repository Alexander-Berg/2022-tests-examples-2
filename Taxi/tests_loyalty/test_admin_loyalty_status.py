import pytest


@pytest.mark.parametrize(
    'unique_driver_id,expected_response',
    [
        ('000000000000000000000001', 'expected_response1.json'),
        ('000000000000000000000002', 'expected_response2.json'),
    ],
)
@pytest.mark.pgsql('loyalty', files=['status_logs.sql'])
async def test_admin_driver_status(
        taxi_loyalty, load_json, unique_driver_id, expected_response,
):
    response = await taxi_loyalty.post(
        'admin/loyalty/v1/status', json={'unique_driver_id': unique_driver_id},
    )

    assert response.status_code == 200
    assert response.json() == load_json('response/' + expected_response)
