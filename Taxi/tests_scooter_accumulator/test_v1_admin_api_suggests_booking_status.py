ENDPOINT = '/scooter-accumulator/v1/admin-api/suggests/booking/status'

RESPONSE = {
    'booking_statuses': [
        'CREATED',
        'IN_PROCESS',
        'PROCESSED',
        'VALIDATED',
        'REVOKED',
    ],
}


async def test_ok(taxi_scooter_accumulator):
    response = await taxi_scooter_accumulator.get(ENDPOINT)

    assert response.status_code == 200
    assert response.json() == RESPONSE
