import pytest


ENDPOINT = '/scooter-accumulator/v1/bookings'


@pytest.mark.parametrize(
    ['booking_ids', 'expected_response'],
    [
        pytest.param(
            ['booking_id1', 'booking_id2'],
            {
                'code': 200,
                'json': {
                    'bookings': [
                        {
                            'accumulator_id': 'accum_id1',
                            'booking_id': 'booking_id1',
                            'cabinet_id': 'cabinet_id1',
                            'cell_id': 'cell_id1',
                            'status': 'CREATED',
                            'cells_count': 1,
                            'contractor_id': 'contractor_id1',
                            'cabinet_type': 'cabinet',
                        },
                        {
                            'accumulator_id': 'accum_id2',
                            'booking_id': 'booking_id2',
                            'cabinet_id': 'cabinet_id1',
                            'cell_id': 'cell_id2',
                            'status': 'IN_PROCESS',
                            'cells_count': 1,
                            'contractor_id': 'contractor_id1',
                            'cabinet_type': 'cabinet',
                        },
                    ],
                },
            },
            id='ok 2 bookings',
        ),
        pytest.param(
            ['booking_id1', 'booking_id100500'],
            {
                'code': 404,
                'json': {
                    'code': '404',
                    'message': 'booking_ids don\'t exist: booking_id100500',
                },
            },
            id='one of not found',
        ),
    ],
)
async def test_handler(
        taxi_scooter_accumulator, booking_ids, expected_response,
):
    response = await taxi_scooter_accumulator.get(
        ENDPOINT, params={'booking_ids': ','.join(booking_ids)},
    )

    assert response.status_code == expected_response['code']
    assert response.json() == expected_response['json']
