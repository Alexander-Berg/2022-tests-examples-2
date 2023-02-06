import pytest


async def test_cuorier_status_processed(taxi_cargo_misc, pgsql):
    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute(
        'INSERT INTO cargo_misc.couriers (id, car_id, driver_id)'
        'VALUES (\'some_courier_id\', \'some_car_id\', \'some_driver_id\')',
    )
    response = await taxi_cargo_misc.post(
        '/couriers/v1/status', json={'operation_id': 'some_courier_id'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'status': 'processed',
        'driver_id': 'some_driver_id',
        'car_id': 'some_car_id',
    }


@pytest.mark.parametrize(
    'column, val',
    [('car_id', 'some_car_id'), ('driver_id', 'some_driver_id')],
)
async def test_cuorier_status_processing(taxi_cargo_misc, pgsql, column, val):
    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute(
        'INSERT INTO cargo_misc.couriers (id, %s)'
        'VALUES (\'some_courier_id\', \'%s\')' % (column, val),
    )
    response = await taxi_cargo_misc.post(
        '/couriers/v1/status', json={'operation_id': 'some_courier_id'},
    )

    assert response.status_code == 200
    assert response.json() == {'status': 'processing', column: val}


async def test_cuorier_status_notfound(taxi_cargo_misc):
    response = await taxi_cargo_misc.post(
        '/couriers/v1/status', json={'operation_id': 'some_courier_id'},
    )

    assert response.status_code == 404
