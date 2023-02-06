import pytest


ENDPOINT = '/scooter-accumulator/v1/cabinet/cell/available-for-booking'

CABINET_ID1 = 'cabinet_id1'
CABINET_ID2 = 'cabinet_id2'
CABINET_ID3 = 'cabinet_id3'
CABINET_ID4 = 'cabinet_id4'
CABINET_ID_NONEXISTENT = 'nonexistent_cabinet_id'


@pytest.mark.parametrize(
    'cabinet_id, response_json',
    [
        pytest.param(
            CABINET_ID1,
            {
                'cabinet_id': CABINET_ID1,
                'cabinet_type': 'cabinet',
                'accumulators_available_for_booking': 1,
                'empty_cells_available_for_booking': 1,
            },
            id='1 empty cell, 1 available accum, '
            '1 accum with low charge, 1 booked cell with accum',
        ),
        pytest.param(
            CABINET_ID2,
            {
                'cabinet_id': CABINET_ID2,
                'cabinet_type': 'charge_station',
                'accumulators_available_for_booking': 0,
                'empty_cells_available_for_booking': 1,
            },
            id='no accums, 1 booked cell, 1 available cell',
        ),
        pytest.param(
            CABINET_ID3,
            {
                'cabinet_id': CABINET_ID3,
                'cabinet_type': 'charge_station_without_id_receiver',
                'accumulators_available_for_booking': 1,
                'empty_cells_available_for_booking': 0,
            },
            id='no empty cells, 1 available accum, '
            '1 accum with expired relevant_accumulator_info_delta',
        ),
    ],
)
async def test_ok(taxi_scooter_accumulator, cabinet_id, response_json):
    response = await taxi_scooter_accumulator.get(
        ENDPOINT, params={'cabinet_id': cabinet_id},
    )

    assert response.status_code == 200
    assert response.json() == response_json


@pytest.mark.parametrize(
    'cabinet_id, code, message',
    [
        pytest.param(
            CABINET_ID_NONEXISTENT,
            '400',
            f'cabinet id `{CABINET_ID_NONEXISTENT}` does not exist',
        ),
        pytest.param(CABINET_ID4, '500', 'Internal Server Error'),
    ],
)
async def test_bad(taxi_scooter_accumulator, cabinet_id, code, message):

    response = await taxi_scooter_accumulator.get(
        ENDPOINT, params={'cabinet_id': cabinet_id},
    )

    assert response.status_code == int(code)
    assert response.json() == {'code': code, 'message': message}
