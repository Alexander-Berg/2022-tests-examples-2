import typing

import pytest

ENDPOINT = '/scooter-accumulator/v1/admin-api/accumulator/list'

TEST_EMPTY_RESPONSE: typing.Dict[str, typing.Any] = {'accumulators': []}

ACCUM1 = {
    'accumulator_id': 'accum_id1',
    'charge': 90,
    'created_at': '2019-12-17T04:38:54+00:00',
    'place': {'cabinet': {'cabinet_id': 'cabinet_id1', 'cell_id': 'cell_id1'}},
    'serial_number': 'serial_number1',
    'updated_at': '2019-12-17T04:38:54+00:00',
    'booking': {'booking_id': 'booking_id1', 'booking_status': 'CREATED'},
}

ACCUM2 = {
    'accumulator_id': 'accum_id2',
    'charge': 80,
    'created_at': '2019-12-17T04:38:55+00:00',
    'place': {'cabinet': {'cabinet_id': 'cabinet_id2', 'cell_id': 'cell_id3'}},
    'serial_number': 'serial_number2',
    'updated_at': '2019-12-17T04:38:55+00:00',
    'booking': {'booking_id': 'booking_id3', 'booking_status': 'IN_PROCESS'},
}

ACCUM3 = {
    'accumulator_id': 'accum_id3',
    'charge': 72,
    'created_at': '2019-12-17T04:38:56+00:00',
    'place': {'contractor_id': 'contractor_id2'},
    'serial_number': 'serial_number3',
    'updated_at': '2019-12-17T04:38:56+00:00',
}

ACCUM4 = {
    'accumulator_id': 'accum_id4',
    'charge': 75,
    'created_at': '2019-12-17T04:38:55+00:00',
    'place': {'cabinet': {'cabinet_id': 'cabinet_id2', 'cell_id': 'cell_id6'}},
    'serial_number': 'serial_number4',
    'updated_at': '2019-12-17T04:38:55+00:00',
    'booking': {'booking_id': 'booking_id4', 'booking_status': 'CREATED'},
}

ACCUM5 = {
    'accumulator_id': 'accum_id5',
    'charge': 70,
    'created_at': '2019-12-17T04:38:56+00:00',
    'place': {'contractor_id': 'contractor_id1'},
    'serial_number': 'serial_number5',
    'updated_at': '2019-12-17T04:38:56+00:00',
}

ACCUM6 = {
    'accumulator_id': 'accum_id6',
    'charge': 60,
    'created_at': '2019-12-17T04:38:57+00:00',
    'place': {'contractor_id': 'contractor_id1'},
    'serial_number': 'serial_number6',
    'updated_at': '2019-12-17T04:38:57+00:00',
}

ACCUM7 = {
    'accumulator_id': 'accum_id7',
    'charge': 50,
    'created_at': '2019-12-17T04:38:57+00:00',
    'place': {'cabinet': {'cabinet_id': 'cabinet_id3', 'cell_id': 'cell_id4'}},
    'serial_number': 'serial_number7',
    'updated_at': '2019-12-17T04:38:57+00:00',
    'booking': {'booking_id': 'booking_id5', 'booking_status': 'CREATED'},
}

ACCUM8 = {
    'accumulator_id': 'accum_id8',
    'charge': 40,
    'created_at': '2019-12-17T04:38:58+00:00',
    'place': {'cabinet': {'cabinet_id': 'cabinet_id4', 'cell_id': 'cell_id5'}},
    'serial_number': 'serial_number8',
    'updated_at': '2019-12-17T04:38:58+00:00',
    'booking': {'booking_id': 'booking_id6', 'booking_status': 'CREATED'},
}

ACCUM9 = {
    'accumulator_id': 'accum_id9',
    'charge': 30,
    'created_at': '2019-12-17T04:38:58+00:00',
    'place': {'scooter_id': 'scooter_id1'},
    'serial_number': 'serial_number9',
    'updated_at': '2019-12-17T04:38:58+00:00',
}

ACCUM10 = {
    'accumulator_id': 'accum_id10',
    'charge': 30,
    'created_at': '2019-12-17T04:38:58+00:00',
    'place': {
        'cabinet': {'cabinet_id': 'cabinet_id11', 'cell_id': 'cell_id1'},
    },
    'serial_number': 'serial_number10',
    'updated_at': '2019-12-17T04:38:58+00:00',
    'booking': {'booking_id': 'booking_id7', 'booking_status': 'CREATED'},
}

ACCUM11 = {
    'accumulator_id': 'accum_id11',
    'charge': 30,
    'created_at': '2019-12-17T04:38:58+00:00',
    'place': {'scooter_id': 'scooter_id1'},
    'serial_number': 'serial_number11',
    'updated_at': '2019-12-17T04:38:58+00:00',
}

TEST_NO_FILTERS_1_RESPONSE = {
    'accumulators': [ACCUM9, ACCUM8, ACCUM11, ACCUM10],
    'cursor': 'MjAxOS0xMi0xN1QwNDozODo1OCswMDAwfGFjY3VtX2lkMTA',
}

TEST_NO_FILTERS_2_RESPONSE = {
    'accumulators': [ACCUM5, ACCUM3, ACCUM4],
    'cursor': 'MjAxOS0xMi0xN1QwNDozODo1NSswMDAwfGFjY3VtX2lkNA',
}

TEST_NO_FILTERS_3_RESPONSE = {'accumulators': [ACCUM2, ACCUM1]}

TEST_FILTER_CREATED_AT_RESPONSE = {
    'accumulators': [ACCUM7, ACCUM6],
    'cursor': 'MjAxOS0xMi0xN1QwNDozODo1NyswMDAwfGFjY3VtX2lkNg',
}

TEST_FILTER_ACCUMULATOR_RESPONSE = {'accumulators': [ACCUM7]}

TEST_FILTER_ACCUMULATOR_SUBSTRING_RESPONSE = {
    'accumulators': [ACCUM11, ACCUM10, ACCUM1],
}

TEST_FILTER_CABINET_RESPONSE = {
    'accumulators': [ACCUM4],
    'cursor': 'MjAxOS0xMi0xN1QwNDozODo1NSswMDAwfGFjY3VtX2lkNA',
}

TEST_FILTER_CABINET_NULL_RESPONSE = {
    'accumulators': [ACCUM9, ACCUM11],
    'cursor': 'MjAxOS0xMi0xN1QwNDozODo1OCswMDAwfGFjY3VtX2lkMTE',
}

TEST_FILTER_CABINET_SUBSTRING_RESPONSE = {'accumulators': [ACCUM10, ACCUM1]}

TEST_FILTER_SCOOTER_RESPONSE = {
    'accumulators': [ACCUM9],
    'cursor': 'MjAxOS0xMi0xN1QwNDozODo1OCswMDAwfGFjY3VtX2lkOQ',
}

TEST_FILTER_SCOOTER_NULL_RESPONSE = {
    'accumulators': [ACCUM9, ACCUM8],
    'cursor': 'MjAxOS0xMi0xN1QwNDozODo1OCswMDAwfGFjY3VtX2lkOA',
}

TEST_FILTER_SCOOTER_SUBSTRING_RESPONSE = {'accumulators': [ACCUM9, ACCUM11]}

TEST_FILTER_CONTRACTOR_RESPONSE = {
    'accumulators': [ACCUM6],
    'cursor': 'MjAxOS0xMi0xN1QwNDozODo1NyswMDAwfGFjY3VtX2lkNg',
}

TEST_FILTER_CONTRACTOR_NULL_RESPONSE = {
    'accumulators': [ACCUM9, ACCUM8],
    'cursor': 'MjAxOS0xMi0xN1QwNDozODo1OCswMDAwfGFjY3VtX2lkOA',
}

TEST_FILTER_CONTRACTOR_SUBSTRING_RESPONSE = {'accumulators': [ACCUM6, ACCUM5]}

TEST_FILTER_SERIAL_NUMBER_RESPONSE = {'accumulators': [ACCUM1]}

TEST_FILTER_SERIAL_NUMBER_NULL_RESPONSE = {
    'accumulators': [ACCUM9, ACCUM8],
    'cursor': 'MjAxOS0xMi0xN1QwNDozODo1OCswMDAwfGFjY3VtX2lkOA',
}

TEST_FILTER_SERIAL_NUMBER_SUBSTRING_RESPONSE = {
    'accumulators': [ACCUM11, ACCUM10, ACCUM1],
}

TEST_FILTER_BOOKING_STATUS_RESPONSE = {'accumulators': [ACCUM2]}

TEST_FILTER_NO_BOOKING_RESPONSE = {
    'accumulators': [ACCUM9, ACCUM11, ACCUM6, ACCUM5, ACCUM3],
}


@pytest.mark.parametrize(
    'cursor, limit, json_',
    [
        pytest.param(None, 4, TEST_NO_FILTERS_1_RESPONSE),
        pytest.param(
            'MjAxOS0xMi0xN1QwNDozODo1NyswMDAwfGFjY3VtX2lkNg',
            3,
            TEST_NO_FILTERS_2_RESPONSE,
        ),
        pytest.param(
            'MjAxOS0xMi0xN1QwNDozODo1NSswMDAwfGFjY3VtX2lkNA',
            2,
            TEST_NO_FILTERS_3_RESPONSE,
        ),
    ],
)
async def test_no_filters(taxi_scooter_accumulator, cursor, limit, json_):
    request_json = {}
    if cursor:
        request_json['cursor'] = cursor
    if limit:
        request_json['limit'] = limit
    response = await taxi_scooter_accumulator.post(ENDPOINT, json=request_json)
    assert response.status_code == 200
    assert (response.json()) == json_


@pytest.mark.parametrize(
    'limit, created_at_max, created_at_min, json_',
    [
        pytest.param(
            2,
            '2019-12-17T04:38:57+0000',
            '2019-12-17T04:38:56+0000',
            TEST_FILTER_CREATED_AT_RESPONSE,
        ),
        pytest.param(
            2021,
            '2019-12-17T04:38:56+0000',
            '2019-12-17T04:38:57+0000',
            TEST_EMPTY_RESPONSE,
        ),
    ],
)
async def test_filter_created_at(
        taxi_scooter_accumulator, limit, created_at_max, created_at_min, json_,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        json={
            'limit': limit,
            'created_at_max': created_at_max,
            'created_at_min': created_at_min,
        },
    )
    assert response.status_code == 200
    assert response.json() == json_


@pytest.mark.parametrize(
    'limit, accumulator_id, accumulator_id_is_substring, json_',
    [
        pytest.param(100, 'accum_id7', None, TEST_FILTER_ACCUMULATOR_RESPONSE),
        pytest.param(100, 'accum_id33', None, TEST_EMPTY_RESPONSE),
        pytest.param(
            100, 'id1', True, TEST_FILTER_ACCUMULATOR_SUBSTRING_RESPONSE,
        ),
        pytest.param(100, 'id1', False, TEST_EMPTY_RESPONSE),
        pytest.param(100, 'id1', None, TEST_EMPTY_RESPONSE),
    ],
)
async def test_filter_accumulator(
        taxi_scooter_accumulator,
        limit,
        accumulator_id,
        accumulator_id_is_substring,
        json_,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        json={
            'limit': limit,
            'accumulator_id': accumulator_id,
            'accumulator_id_is_substring': accumulator_id_is_substring,
        },
    )
    assert response.status_code == 200
    assert response.json() == json_


@pytest.mark.parametrize(
    'limit, cabinet_id, cabinet_id_is_substring, cabinet_id_is_null, json_',
    [
        pytest.param(
            1, 'cabinet_id2', None, None, TEST_FILTER_CABINET_RESPONSE,
        ),
        pytest.param(100, 'cabinet_id33', None, None, TEST_EMPTY_RESPONSE),
        pytest.param(2, None, None, True, TEST_FILTER_CABINET_NULL_RESPONSE),
        pytest.param(
            100, 'id1', True, None, TEST_FILTER_CABINET_SUBSTRING_RESPONSE,
        ),
        pytest.param(100, 'id1', False, None, TEST_EMPTY_RESPONSE),
        pytest.param(100, 'id1', None, None, TEST_EMPTY_RESPONSE),
    ],
)
async def test_filter_cabinet(
        taxi_scooter_accumulator,
        limit,
        cabinet_id,
        cabinet_id_is_substring,
        cabinet_id_is_null,
        json_,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        json={
            'limit': limit,
            'cabinet_id': cabinet_id,
            'cabinet_id_is_substring': cabinet_id_is_substring,
            'cabinet_id_is_null': cabinet_id_is_null,
        },
    )
    assert response.status_code == 200
    assert response.json() == json_


@pytest.mark.parametrize(
    'limit, scooter_id, scooter_id_is_substring, scooter_id_is_null, json_',
    [
        pytest.param(
            1, 'scooter_id1', None, None, TEST_FILTER_SCOOTER_RESPONSE,
        ),
        pytest.param(100, 'scooter_id1111', None, None, TEST_EMPTY_RESPONSE),
        pytest.param(2, None, True, None, TEST_FILTER_SCOOTER_NULL_RESPONSE),
        pytest.param(
            1, 'scooter_id1', None, False, TEST_FILTER_SCOOTER_RESPONSE,
        ),
        pytest.param(1, 'scooter_id1', None, True, TEST_EMPTY_RESPONSE),
        pytest.param(
            100, 'id1', True, None, TEST_FILTER_SCOOTER_SUBSTRING_RESPONSE,
        ),
        pytest.param(100, 'id1', False, None, TEST_EMPTY_RESPONSE),
        pytest.param(100, 'id1', None, None, TEST_EMPTY_RESPONSE),
    ],
)
async def test_filter_scooter(
        taxi_scooter_accumulator,
        limit,
        scooter_id,
        scooter_id_is_substring,
        scooter_id_is_null,
        json_,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        json={
            'limit': limit,
            'scooter_id': scooter_id,
            'scooter_id_is_substring': scooter_id_is_substring,
            'scooter_id_is_null': scooter_id_is_null,
        },
    )
    assert response.status_code == 200
    assert response.json() == json_


@pytest.mark.parametrize(
    'limit, contractor_id,'
    'contractor_id_is_substring, contractor_id_is_null, json_',
    [
        pytest.param(
            1, 'contractor_id1', None, None, TEST_FILTER_CONTRACTOR_RESPONSE,
        ),
        pytest.param(
            100, 'contractor_id1111', None, None, TEST_EMPTY_RESPONSE,
        ),
        pytest.param(
            2, None, True, None, TEST_FILTER_CONTRACTOR_NULL_RESPONSE,
        ),
        pytest.param(1, 'contractor_id1', False, True, TEST_EMPTY_RESPONSE),
        pytest.param(
            1, 'contractor_id1', False, False, TEST_FILTER_CONTRACTOR_RESPONSE,
        ),
        pytest.param(
            100, 'id1', True, None, TEST_FILTER_CONTRACTOR_SUBSTRING_RESPONSE,
        ),
        pytest.param(100, 'id1', False, None, TEST_EMPTY_RESPONSE),
        pytest.param(100, 'id1', None, None, TEST_EMPTY_RESPONSE),
    ],
)
async def test_filter_contracor(
        taxi_scooter_accumulator,
        limit,
        contractor_id,
        contractor_id_is_substring,
        contractor_id_is_null,
        json_,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        json={
            'limit': limit,
            'contractor_id': contractor_id,
            'contractor_id_is_substring': contractor_id_is_substring,
            'contractor_id_is_null': contractor_id_is_null,
        },
    )
    assert response.status_code == 200
    assert response.json() == json_


@pytest.mark.parametrize(
    'limit, serial_number, serial_number_is_substring, json_',
    [
        pytest.param(
            1, 'serial_number1', None, TEST_FILTER_SERIAL_NUMBER_RESPONSE,
        ),
        pytest.param(100, 'serial_number1111', None, TEST_EMPTY_RESPONSE),
        pytest.param(2, None, True, TEST_FILTER_SERIAL_NUMBER_NULL_RESPONSE),
        pytest.param(
            100, 'number1', True, TEST_FILTER_SERIAL_NUMBER_SUBSTRING_RESPONSE,
        ),
        pytest.param(100, 'number1', False, TEST_EMPTY_RESPONSE),
        pytest.param(100, 'number1', None, TEST_EMPTY_RESPONSE),
    ],
)
async def test_filter_serial_number(
        taxi_scooter_accumulator,
        limit,
        serial_number,
        serial_number_is_substring,
        json_,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        json={
            'limit': limit,
            'serial_number': serial_number,
            'serial_number_is_substring': serial_number_is_substring,
        },
    )
    assert response.status_code == 200
    assert response.json() == json_


@pytest.mark.parametrize(
    'limit, booking_status, booking_is_absent, json_',
    [
        pytest.param(
            10, 'IN_PROCESS', None, TEST_FILTER_BOOKING_STATUS_RESPONSE,
        ),
        pytest.param(100, None, True, TEST_FILTER_NO_BOOKING_RESPONSE),
        pytest.param(100, 'CREATED', True, TEST_EMPTY_RESPONSE),
    ],
)
async def test_filter_booking_status(
        taxi_scooter_accumulator,
        limit,
        booking_status,
        booking_is_absent,
        json_,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        json={
            'limit': limit,
            'booking_status': booking_status,
            'booking_is_absent': booking_is_absent,
        },
    )
    assert response.status_code == 200
    assert response.json() == json_
