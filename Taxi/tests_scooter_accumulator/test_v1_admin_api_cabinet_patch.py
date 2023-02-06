import pytest

from . import sql

ENDPOINT = '/scooter-accumulator/v1/admin-api/cabinet'

CABINET_ID1_UPDATED = {
    'cabinet_type': 'cabinet',
    'cabinet_name': 'cabinet_name1',
    'depot_id': 'depot_id1',
    'cells_count': 15,
}

CABINET_ID2_UPDATED = {
    'cabinet_type': 'cabinet',
    'cabinet_name': 'cabinet_name2',
    'depot_id': 'depot_id_new',
    'cells_count': 0,
}

CABINET_ID3_UPDATED = {
    'cabinet_type': 'cabinet',
    'cabinet_name': 'cabinet_name3',
    'depot_id': 'depot_id1',
    'cells_count': 1,
}

CABINET_ID4_UPDATED = {
    'cabinet_type': 'cabinet',
    'cabinet_name': 'cabinet_name4',
    'depot_id': 'depot_id1',
    'cells_count': 15,
}

CABINET_ID3_UPDATED_NAME = {
    'cabinet_type': 'cabinet',
    'cabinet_name': 'new_cabinet_name',
    'depot_id': 'depot_id1',
    'cells_count': 4,
}


@pytest.mark.parametrize(
    'json_, cabinet_id, response_expected',
    [
        pytest.param(
            {
                'set': {
                    'cabinet_type': None,
                    'depot_id': None,
                    'cells_count': 15,
                },
                'unset': [],
            },
            'cabinet_id1',
            CABINET_ID1_UPDATED,
            id='cells insert in cabinet',
        ),
        pytest.param(
            {
                'set': {
                    'cabinet_type': 'cabinet',
                    'depot_id': 'depot_id_new',
                    'cells_count': None,
                },
                'unset': [],
            },
            'cabinet_id2',
            CABINET_ID2_UPDATED,
            id='change type and depot_id',
        ),
        pytest.param(
            {
                'set': {
                    'cabinet_type': None,
                    'depot_id': None,
                    'cells_count': 1,
                },
                'unset': [],
            },
            'cabinet_id3',
            CABINET_ID3_UPDATED,
            id='cells delete in cabinet',
        ),
        pytest.param(
            {
                'set': {
                    'cabinet_name': 'new_cabinet_name',
                    'cabinet_type': None,
                    'depot_id': None,
                    'cells_count': None,
                },
                'unset': [],
            },
            'cabinet_id3',
            CABINET_ID3_UPDATED_NAME,
            id='cabinet name update',
        ),
    ],
)
async def test_ok(
        taxi_scooter_accumulator, pgsql, json_, cabinet_id, response_expected,
):
    response = await taxi_scooter_accumulator.patch(
        ENDPOINT, params={'cabinet_id': cabinet_id}, json=json_,
    )

    assert response.status_code == 200

    response_json = response.json()

    assert response_json['cabinet_name'] == response_expected['cabinet_name']
    assert response_json['cabinet_type'] == response_expected['cabinet_type']
    assert response_json['depot_id'] == response_expected['depot_id']
    assert response_json['cells_count'] == response_expected['cells_count']

    if not json_['set']['depot_id']:
        json_['set']['depot_id'] = 'depot_id1'

    assert sql.select_cabinets_info(
        pgsql, cabinet_id, depot_id=True, cabinet_type=True,
    ) == [(cabinet_id, json_['set']['depot_id'], 'cabinet')]

    if json_['set']['cells_count']:
        cells = sql.select_cells_by_cabinet(pgsql, cabinet_id)

        assert len(cells) == json_['set']['cells_count']

        for i, cell in enumerate(cells):
            if (i >= json_['set']['cells_count']) or (
                    cabinet_id == 'cabinet_id1'
            ):
                assert cell == (cabinet_id, str(i + 1), None, None)
            else:
                assert cell == (cabinet_id, str(i + 1), 'accum_id222', None)


@pytest.mark.parametrize(
    'json_, cabinet_id, message',
    [
        pytest.param(
            {'set': {'cabinet_type': None, 'cells_count': 0}, 'unset': []},
            'cabinet_id3',
            'kCabinetsUpdate: imposible to delete cells, '
            'booked or not empty cells found',
            id='cells delete not empty from cabinet',
        ),
        pytest.param(
            {
                'set': {
                    'cabinet_type': None,
                    'depot_id': 'depot_id_new',
                    'cells_count': None,
                },
                'unset': [],
            },
            'cabinet_id222',
            'kCabinetsUpdate: cabinet with id `cabinet_id222` not found.',
            id='cabinet not exists',
        ),
        pytest.param(
            {
                'set': {
                    'cabinet_type': None,
                    'depot_id': 'depot_id_new',
                    'cells_count': 22,
                },
                'unset': [],
            },
            'cabinet_id222',
            None,
            id='cabinet not exists, cells update',
        ),
        pytest.param(
            {
                'set': {
                    'cabinet_type': None,
                    'cabinet_name': 'cabinet_name2',
                    'depot_id': 'depot_id1',
                    'cells_count': 15,
                },
                'unset': [],
            },
            'cabinet_id1',
            None,
            id='cabinet_name exists, cells update',
        ),
    ],
)
async def test_bad(
        taxi_scooter_accumulator, pgsql, json_, cabinet_id, message,
):
    response = await taxi_scooter_accumulator.patch(
        ENDPOINT, params={'cabinet_id': cabinet_id}, json=json_,
    )

    assert response.status_code == 400
    if message:
        assert response.json()['message'] == message
    else:
        assert response.json()['message']
