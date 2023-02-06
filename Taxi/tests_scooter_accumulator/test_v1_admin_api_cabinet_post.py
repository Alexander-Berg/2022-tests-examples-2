import pytest

from . import sql

ENDPOINT = '/scooter-accumulator/v1/admin-api/cabinet'

CABINET_ID2 = {
    'depot_id': 'grocery_id2',
    'cabinet_name': 'cabinet_name2',
    'cabinet_type': 'charge_station',
    'cells_count': 2,
}

CABINET_ID4 = {
    'depot_id': 'depot_id123',
    'cabinet_name': 'cabinet_name4',
    'cabinet_type': 'cabinet',
    'cells_count': 10,
}


@pytest.mark.parametrize(
    'idempotency_token, json_, response_expected',
    [
        pytest.param(
            '0000000000000002',
            {
                'depot_id': 'grocery_id2',
                'cabinet_type': 'charge_station',
                'cabinet_name': 'cabinet_name2',
                'cells_count': 2,
                'cabinet_id': 'cabinet_id2',
            },
            CABINET_ID2,
            id='emulate retry',
        ),
        pytest.param(
            '0000000000000004',
            {
                'depot_id': 'depot_id123',
                'cabinet_type': 'cabinet',
                'cabinet_name': 'cabinet_name4',
                'cells_count': 10,
                'cabinet_id': 'cabinet_id4',
            },
            CABINET_ID4,
            id='correct insert',
        ),
    ],
)
async def test_ok(
        taxi_scooter_accumulator,
        pgsql,
        idempotency_token,
        json_,
        response_expected,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        headers={'X-Idempotency-Token': idempotency_token},
        json=json_,
    )

    assert response.status_code == 200

    response_json = response.json()

    assert response_json['cabinet_id'] == json_['cabinet_id']
    assert response_json['cabinet_name'] == response_expected['cabinet_name']
    assert response_json['depot_id'] == response_expected['depot_id']
    assert response_json['cells_count'] == response_expected['cells_count']
    assert response_json['cabinet_type'] == response_expected['cabinet_type']

    assert (
        sql.select_cabinets_info(
            pgsql,
            cabinet_id=json_['cabinet_id'],
            depot_id=True,
            cabinet_type=True,
            cabinet_name=True,
        )
        == [
            (
                json_['cabinet_id'],
                response_expected['depot_id'],
                response_expected['cabinet_type'],
                response_expected['cabinet_name'],
            ),
        ]
    )

    cells = sql.select_cells_by_cabinet(pgsql, json_['cabinet_id'])

    assert len(cells) == response_expected['cells_count']

    for i, cell in enumerate(cells):
        assert cell == (json_['cabinet_id'], str(i), None, None)


@pytest.mark.parametrize(
    'idempotency_token, json_, prev_cabinet',
    [
        pytest.param(
            '0000000000000004',
            {
                'depot_id': 'grocery_id1234',
                'cabinet_name': 'cabinet_name2',
                'cabinet_type': 'cabinet',
                'cells_count': 222,
                'cabinet_id': 'cabinet_id2',
            },
            CABINET_ID2,
            id='cabinet already exists',
        ),
    ],
)
async def test_bad(
        taxi_scooter_accumulator,
        pgsql,
        idempotency_token,
        json_,
        prev_cabinet,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        headers={'X-Idempotency-Token': idempotency_token},
        json=json_,
    )

    assert response.status_code == 400
    assert response.json()['message']

    assert (
        sql.select_cabinets_info(
            pgsql,
            cabinet_id=json_['cabinet_id'],
            depot_id=True,
            cabinet_type=True,
        )
        == [
            (
                json_['cabinet_id'],
                prev_cabinet['depot_id'],
                prev_cabinet['cabinet_type'],
            ),
        ]
    )

    cells = sql.select_cells_by_cabinet(pgsql, json_['cabinet_id'])

    assert len(cells) == prev_cabinet['cells_count']


@pytest.mark.parametrize(
    'idempotency_token, json_',
    [
        pytest.param(
            '0000000000000009',
            {
                'depot_id': 'grocery_id1234',
                'cabinet_name': 'cabinet_name2',
                'cabinet_type': 'cabinet',
                'cells_count': 222,
                'cabinet_id': 'cabinet_id2312',
            },
            id='cabinet name already exists',
        ),
    ],
)
async def test_cabinet_name_bad(
        taxi_scooter_accumulator, pgsql, idempotency_token, json_,
):
    response = await taxi_scooter_accumulator.post(
        ENDPOINT,
        headers={'X-Idempotency-Token': idempotency_token},
        json=json_,
    )

    assert response.status_code == 400
    assert response.json()['message']
