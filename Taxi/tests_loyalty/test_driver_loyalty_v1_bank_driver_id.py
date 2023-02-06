from . import utils as test_utils


async def test_bank_driver_id(taxi_loyalty, unique_drivers, pgsql):
    async def _make_bank_driver_id():
        response = await taxi_loyalty.post(
            'driver/loyalty/v1/bank-driver-id',
            params={'bank_id': 'tinkoff'},
            headers=test_utils.get_auth_headers(
                'driver_db_id1', 'driver_uuid1',
            ),
        )

        assert response.status_code == 200

        cursor = pgsql['loyalty'].cursor()
        cursor.execute('SELECT * FROM ' 'loyalty.bank_driver_ids ')
        pg_result = list(row for row in cursor)
        cursor.close()

        assert len(pg_result) == 1

        pg_bank_driver_id = pg_result[0][2]
        bank_driver_id = response.json().get('bank_driver_id')

        assert bank_driver_id == pg_bank_driver_id

        return bank_driver_id

    unique_drivers.set_unique_driver('driver_db_id1', 'driver_uuid1', '123')

    bank_driver_id = await _make_bank_driver_id()

    # Проверяем, что в базе остается тот же самый id
    assert await _make_bank_driver_id() == bank_driver_id


async def test_bad_bank_id(taxi_loyalty):

    response = await taxi_loyalty.post(
        'driver/loyalty/v1/bank-driver-id',
        params={'bank_id': 'blablabla'},
        headers=test_utils.get_auth_headers('driver_db_id1', 'driver_uuid1'),
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'invalid_bank_id'
