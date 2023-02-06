ENDPOINT = '/scooter-accumulator/v1/depot/cell/available-for-booking'

DEPOT_ID1 = 'depot_id1'
DEPOT_ID2 = 'depot_id2'
DEPOT_ID_WITHOUT_CABINETS = 'depot_id_without_cabinets'

TEST_OK = {
    'depots': [
        {
            'depot_id': DEPOT_ID1,
            'cabinets': [
                {
                    'cabinet_id': 'cabinet_id1',
                    'cabinet_type': 'cabinet',
                    'accumulators_available_for_booking': 1,
                    'empty_cells_available_for_booking': 1,
                },
                {
                    'cabinet_id': 'cabinet_id2',
                    'cabinet_type': 'charge_station',
                    'accumulators_available_for_booking': 0,
                    'empty_cells_available_for_booking': 1,
                },
            ],
        },
        {
            'depot_id': DEPOT_ID2,
            'cabinets': [
                {
                    'cabinet_id': 'cabinet_id3',
                    'cabinet_type': 'charge_station_without_id_receiver',
                    'accumulators_available_for_booking': 1,
                    'empty_cells_available_for_booking': 0,
                },
            ],
        },
        {'depot_id': DEPOT_ID_WITHOUT_CABINETS, 'cabinets': []},
    ],
}

TEST_DEPOT_WITHOUT_CABINETS = {
    'depots': [{'depot_id': DEPOT_ID_WITHOUT_CABINETS, 'cabinets': []}],
}


def is_eq(response, exp_res):
    vals = sorted(
        response.json()['depots'], key=lambda depot: depot['depot_id'],
    )
    for k in vals:
        k['cabinets'].sort(key=lambda cabinet: cabinet['cabinet_id'])
    return vals == exp_res['depots']


async def test_ok(taxi_scooter_accumulator):
    response = await taxi_scooter_accumulator.get(
        ENDPOINT,
        params={
            'depot_ids': ','.join(
                [DEPOT_ID1, DEPOT_ID2, DEPOT_ID_WITHOUT_CABINETS],
            ),
        },
    )

    assert response.status_code == 200
    assert is_eq(response, TEST_OK)


async def test_depot_without_cabinets(taxi_scooter_accumulator):
    response = await taxi_scooter_accumulator.get(
        ENDPOINT, params={'depot_ids': DEPOT_ID_WITHOUT_CABINETS},
    )

    assert response.status_code == 200
    assert is_eq(response, TEST_DEPOT_WITHOUT_CABINETS)
