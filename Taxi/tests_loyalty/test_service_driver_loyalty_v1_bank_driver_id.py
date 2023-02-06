import json

MOCK_URL = '/unique-drivers/v1/driver/profiles/retrieve_by_uniques'


def _get_driver_profiles(unique_driver_id):
    profile = {
        'unique_driver_id': unique_driver_id,
        'data': [
            {
                'park_id': 'park_1',
                'driver_profile_id': 'driver_1',
                'park_driver_profile_id': 'park_driver_1',
            },
        ],
    }
    return {'profiles': [profile]}


async def test_bank_driver_id(taxi_loyalty, pgsql, mockserver):
    async def _make_bank_driver_id():
        @mockserver.json_handler(MOCK_URL)
        def _v1_profiles(request):
            data = json.loads(request.get_data())
            uniques = data['id_in_set']
            assert len(uniques) == 1
            return _get_driver_profiles(uniques[0])

        response = await taxi_loyalty.post(
            'service/driver/loyalty/v1/bank-driver-id',
            params={'bank_id': 'tinkoff', 'unique_driver_id': 'driver_id'},
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

    bank_driver_id = await _make_bank_driver_id()

    # Проверяем, что в базе остается тот же самый id
    assert await _make_bank_driver_id() == bank_driver_id


async def test_bad_bank_id(taxi_loyalty):
    response = await taxi_loyalty.post(
        'service/driver/loyalty/v1/bank-driver-id',
        params={'bank_id': 'blablabla', 'unique_driver_id': 'driver_id'},
    )

    assert response.status_code == 400, response.text
    assert response.json()['code'] == 'invalid_bank_id'


async def test_bad_unique_driver_id(taxi_loyalty, mockserver):
    @mockserver.json_handler(MOCK_URL)
    def _v1_profiles(request):
        profile = {'unique_driver_id': 'blablabla', 'data': []}
        return {'profiles': [profile]}

    response = await taxi_loyalty.post(
        'service/driver/loyalty/v1/bank-driver-id',
        params={'bank_id': 'tinkoff', 'unique_driver_id': 'blablabla'},
    )

    assert response.status_code == 404, response.text
    assert response.json()['code'] == 'unique_driver_id_not_found'
