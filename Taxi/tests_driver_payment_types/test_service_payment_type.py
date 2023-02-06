import pytest


@pytest.mark.parametrize('payment_type', ['cash', 'online', 'none'])
async def test_set_payment_type(
        taxi_driver_payment_types, mongodb, payment_type,
):
    response = await taxi_driver_payment_types.put(
        'service/v1/payment-type',
        json={
            'source': 'test',
            'reason': 'test_1',
            'payment_type': payment_type,
        },
        params={'park_id': 'park1', 'driver_profile_id': 'driver1'},
    )
    assert response.status_code == 200
    response = response.json()
    assert response == {}
    doc = mongodb.driver_payment_type.find_one(
        {'license_pd_id': 'driver_license_pd_id_1'},
    )
    assert doc['payment_type'] == payment_type
    assert doc['enabled'] is True
    assert 'cleanup_datetime' in doc
