import pytest


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_get(web_app_client):
    response = await web_app_client.get(
        '/v1/sys/affiliations/by-driver',
        params={'db_id': 'driver_park_id', 'uuid': 'driver_id'},
    )
    assert response.status == 200
    data = await response.json()
    ids = [r['record_id'] for r in data['records']]
    assert ids == ['record_id1']
