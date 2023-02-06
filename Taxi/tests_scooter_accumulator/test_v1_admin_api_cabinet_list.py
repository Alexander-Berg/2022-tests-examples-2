import pytest

ENDPOINT = '/scooter-accumulator/v1/admin-api/cabinet/list'

CABINET_ID1_JSON_RESPONSE = {
    'accums_available_for_booking': 1,
    'cabinet_id': 'cabinet_id1',
    'cabinet_name': 'cabinet_name1',
    'cabinet_type': 'cabinet',
    'created_at': '2019-12-17T04:38:54+00:00',
    'depot_id': 'depot_id1',
    'empty_cells_available_for_booking': 1,
    'updated_at': '2019-12-17T04:38:54+00:00',
    'accumulators_count': 3,
    'cells_count': 4,
}

CABINET_ID2_JSON_RESPONSE = {
    'accums_available_for_booking': 0,
    'cabinet_id': 'cabinet_id2',
    'cabinet_name': 'cabinet_name2',
    'cabinet_type': 'charge_station',
    'created_at': '2019-12-17T04:38:55+00:00',
    'depot_id': 'depot_id1',
    'empty_cells_available_for_booking': 1,
    'updated_at': '2019-12-17T04:38:55+00:00',
    'accumulators_count': 0,
    'cells_count': 2,
}

CABINET_ID3_JSON_RESPONSE = {
    'accums_available_for_booking': 1,
    'cabinet_id': 'cabinet_id3',
    'cabinet_name': 'cabinet_name3',
    'cabinet_type': 'charge_station_without_id_receiver',
    'created_at': '2019-12-17T04:38:56+00:00',
    'depot_id': 'depot_id2',
    'empty_cells_available_for_booking': 0,
    'updated_at': '2019-12-17T04:38:56+00:00',
    'accumulators_count': 2,
    'cells_count': 2,
}

CABINET_ID4_JSON_RESPONSE = {
    'accums_available_for_booking': 0,
    'cabinet_id': 'cabinet_id4',
    'cabinet_name': 'cabinet_name4',
    'cabinet_type': 'charge_station_without_id_receiver',
    'created_at': '2019-12-17T04:38:56+00:00',
    'depot_id': 'depot_id4',
    'empty_cells_available_for_booking': 0,
    'updated_at': '2019-12-17T04:38:56+00:00',
    'accumulators_count': 0,
    'cells_count': 0,
}


@pytest.mark.parametrize(
    'request_json, response_json',
    [
        pytest.param(
            {'limit': 2},
            {
                'cabinets': [
                    CABINET_ID4_JSON_RESPONSE,
                    CABINET_ID3_JSON_RESPONSE,
                ],
                'cursor': 'MjAxOS0xMi0xN1QwNDozODo1NiswMDAwfGNhYmluZXRfaWQz',
            },
            id='first request',
        ),
        pytest.param(
            {
                'limit': 2,
                'cursor': 'MjAxOS0xMi0xN1QwNDozODo1NiswMDAwfGNhYmluZXRfaWQz',
            },
            {
                'cabinets': [
                    CABINET_ID2_JSON_RESPONSE,
                    CABINET_ID1_JSON_RESPONSE,
                ],
            },
            id='second request',
        ),
        pytest.param(
            {'limit': 4},
            {
                'cabinets': [
                    CABINET_ID4_JSON_RESPONSE,
                    CABINET_ID3_JSON_RESPONSE,
                    CABINET_ID2_JSON_RESPONSE,
                    CABINET_ID1_JSON_RESPONSE,
                ],
            },
            id='one big request',
        ),
    ],
)
async def test_no_filter(
        taxi_scooter_accumulator, request_json, response_json,
):
    response = await taxi_scooter_accumulator.post(ENDPOINT, json=request_json)

    assert response.status_code == 200
    assert response.json() == response_json


@pytest.mark.parametrize(
    'request_json, response_json',
    [
        pytest.param(
            {'depot_ids': ['depot_id2', 'depot_id_not_exists', 'depot_id4']},
            {
                'cabinets': [
                    CABINET_ID4_JSON_RESPONSE,
                    CABINET_ID3_JSON_RESPONSE,
                ],
            },
            id='depot_id filter',
        ),
        pytest.param(
            {
                'depot_ids': ['id2', 'id_not_exists', 'id4'],
                'depot_id_is_substring': True,
            },
            {
                'cabinets': [
                    CABINET_ID4_JSON_RESPONSE,
                    CABINET_ID3_JSON_RESPONSE,
                ],
            },
            id='depot_id_is_substring filter',
        ),
        pytest.param(
            {'cabinet_id': 'id1', 'cabinet_id_is_substring': True},
            {'cabinets': [CABINET_ID1_JSON_RESPONSE]},
            id='cabinet_id_is_substring filter',
        ),
        pytest.param(
            {'cabinet_name': 'name1', 'cabinet_name_is_substring': True},
            {'cabinets': [CABINET_ID1_JSON_RESPONSE]},
            id='cabinet_name_is_substring filter',
        ),
        pytest.param(
            {'cabinet_id': 'cabinet_id1'},
            {'cabinets': [CABINET_ID1_JSON_RESPONSE]},
            id='cabinet_id filter',
        ),
        pytest.param(
            {'cabinet_type': 'charge_station'},
            {'cabinets': [CABINET_ID2_JSON_RESPONSE]},
            id='cabinet_type filter',
        ),
        pytest.param(
            {'created_at_max': '2019-12-17T04:38:55+00:00', 'limit': 1},
            {
                'cabinets': [CABINET_ID2_JSON_RESPONSE],
                'cursor': 'MjAxOS0xMi0xN1QwNDozODo1NSswMDAwfGNhYmluZXRfaWQy',
            },
            id='created_at_max filter',
        ),
        pytest.param(
            {'created_at_max': '2010-12-17T04:38:55+00:00', 'limit': 1},
            {'cabinets': []},
            id='empty response filter',
        ),
    ],
)
async def test_filter(taxi_scooter_accumulator, request_json, response_json):
    response = await taxi_scooter_accumulator.post(ENDPOINT, json=request_json)

    assert response.status_code == 200
    assert response.json() == response_json
