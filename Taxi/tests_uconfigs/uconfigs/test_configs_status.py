import pytest


CONFIGS_STATUS_URL = 'configs/status'


@pytest.mark.now('2019-02-15T15:00:00Z')
async def test_status(taxi_uconfigs):
    response = await taxi_uconfigs.get(CONFIGS_STATUS_URL)
    assert response.status_code == 200
    data = response.json()
    assert data['updated_at'] == '2019-02-15T15:00:09Z'
