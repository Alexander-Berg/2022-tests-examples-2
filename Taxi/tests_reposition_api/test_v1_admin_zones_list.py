# pylint: disable=C5521
import pytest


@pytest.mark.nofilldb()
@pytest.mark.pgsql('reposition')
async def test_empty(taxi_reposition_api):
    response = await taxi_reposition_api.get('/v1/admin/zones/list')
    assert response.status_code == 200
    assert response.json() == {'zones': []}


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'reposition',
    files=['zone_default.sql', 'zone_moscow.sql', 'zone_svo.sql'],
)
async def test_get(taxi_reposition_api):
    response = await taxi_reposition_api.get('/v1/admin/zones/list')
    assert response.status_code == 200

    data = response.json()['zones']
    data.sort(key=lambda x: x['zone_id'])
    assert data == [
        {'zone_id': '__default__'},
        {'zone_id': 'moscow'},
        {'zone_id': 'svo'},
    ]
