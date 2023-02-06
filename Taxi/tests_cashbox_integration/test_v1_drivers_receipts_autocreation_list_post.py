import pytest

ENDPOINT = '/v1/drivers/receipts/autocreation/list'


@pytest.mark.pgsql(
    'cashbox_integration',
    queries=[
        'INSERT INTO cashbox_integration.drivers '
        'VALUES(\'{}\',\'{}\',\'{}\')'.format('park_123', 'driver_123', True),
    ],
)
async def test_ok(taxi_cashbox_integration, fleet_parks):
    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        params={'park_id': 'park_123'},
        json={'driver_ids': ['driver_123', 'driver_456']},
    )
    json = response.json()
    json['autocreation_list'].sort(key=lambda a: a['driver_id'])
    assert response.status_code == 200, response.text
    assert json == {
        'autocreation_list': [
            {'driver_id': 'driver_123', 'is_enabled': True},
            {'driver_id': 'driver_456', 'is_enabled': False},
        ],
        'is_changeable': True,
    }


@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.pgsql(
    'cashbox_integration',
    queries=[
        'INSERT INTO cashbox_integration.drivers '
        'VALUES(\'{}\',\'{}\',\'{}\')'.format('park_123', 'driver_123', True),
    ],
)
async def test_autocreation_by_park_id(taxi_cashbox_integration, fleet_parks):
    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        params={'park_id': 'park_123'},
        json={'driver_ids': ['driver_123', 'driver_456']},
    )
    json = response.json()
    json['autocreation_list'].sort(key=lambda a: a['driver_id'])
    assert response.status_code == 200, response.text
    assert json == {
        'autocreation_list': [
            {'driver_id': 'driver_123', 'is_enabled': True},
            {'driver_id': 'driver_456', 'is_enabled': True},
        ],
        'is_changeable': False,
    }
