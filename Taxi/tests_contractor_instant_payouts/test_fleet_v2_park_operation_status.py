import pytest

NOW = '2020-01-01T00:04:00+03:00'
NOW_EXPIRED = '2020-01-01T00:10:00+03:00'


@pytest.mark.now(NOW)
async def test_get_park_operation_status_processing(fleet_v2, mock_api):
    response = await fleet_v2.get_park_operation_status(park_id='PARK-01')
    assert response.status_code == 200
    assert response.json()['status'] == 'processing'


@pytest.mark.now(NOW_EXPIRED)
async def test_get_park_operation_status_expired(fleet_v2, mock_api):
    response = await fleet_v2.get_park_operation_status(park_id='PARK-02')
    assert response.status_code == 200
    assert response.json()['status'] == 'available'


@pytest.mark.now(NOW)
async def test_get_park_operation_status_finished(fleet_v2, mock_api):
    response = await fleet_v2.get_park_operation_status(park_id='PARK-02')
    assert response.status_code == 200
    assert response.json()['status'] == 'available'
