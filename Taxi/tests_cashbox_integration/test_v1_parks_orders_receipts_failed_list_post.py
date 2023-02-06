ENDPOINT = 'v1/parks/orders/receipts/failed/list'


async def test_en_ok(taxi_cashbox_integration, pgsql):
    park_id = 'park_id_1'
    cashbox_id = 'cashbox_id_1'
    limit = 3

    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        headers={'Accept-Language': 'en'},
        json={'park_id': park_id, 'cashbox_id': cashbox_id, 'limit': limit},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'park_id': 'park_id_1',
        'failed_receipts': [
            {
                'created_at': '2019-10-01T10:12:00+00:00',
                'description': 'unknown error',
            },
            {
                'created_at': '2019-10-01T10:11:00+00:00',
                'description': 'unknow inn',
            },
        ],
    }


async def test_ru_ok(taxi_cashbox_integration, pgsql):
    park_id = 'park_id_1'
    cashbox_id = 'cashbox_id_1'
    limit = 3

    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        headers={'Accept-Language': 'ru'},
        json={'park_id': park_id, 'cashbox_id': cashbox_id, 'limit': limit},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'park_id': 'park_id_1',
        'failed_receipts': [
            {
                'created_at': '2019-10-01T10:12:00+00:00',
                'description': 'неизвестная ошибка',
            },
            {
                'created_at': '2019-10-01T10:11:00+00:00',
                'description': 'неизвестный инн',
            },
        ],
    }


async def test_nonexistent_translation(taxi_cashbox_integration, pgsql):
    # if there is no translation for requested locale
    # then will be fallback to "ru"
    # requested locale must be valid

    park_id = 'park_id_1'
    cashbox_id = 'cashbox_id_1'
    limit = 3

    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        headers={'Accept-Language': 'fr'},
        json={'park_id': park_id, 'cashbox_id': cashbox_id, 'limit': limit},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'park_id': 'park_id_1',
        'failed_receipts': [
            {
                'created_at': '2019-10-01T10:12:00+00:00',
                'description': 'неизвестная ошибка',
            },
            {
                'created_at': '2019-10-01T10:11:00+00:00',
                'description': 'неизвестный инн',
            },
        ],
    }


async def test_unknown_language(taxi_cashbox_integration, pgsql):
    park_id = 'park_id_1'
    cashbox_id = 'cashbox_id_1'
    limit = 1

    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        headers={'Accept-Language': 'unknown_lang'},
        json={'park_id': park_id, 'cashbox_id': cashbox_id, 'limit': limit},
    )
    assert response.status_code == 406, response.text
    assert response.json() == {
        'code': 'unknown_language',
        'message': 'unknown language \'unknown_lang\'',
    }


async def test_unknown_park(taxi_cashbox_integration, pgsql):
    park_id = 'unknown_park'
    cashbox_id = 'cashbox_id_1'
    limit = 1

    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        headers={'Accept-Language': 'en'},
        json={'park_id': park_id, 'cashbox_id': cashbox_id, 'limit': limit},
    )
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'unknown_park',
        'message': 'park_id \'unknown_park\' not found',
    }


async def test_unknown_cashbox(taxi_cashbox_integration, pgsql):
    park_id = 'park_id_1'
    cashbox_id = 'unknown_cashbox'
    limit = 1

    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        headers={'Accept-Language': 'en'},
        json={'park_id': park_id, 'cashbox_id': cashbox_id, 'limit': limit},
    )
    message = (
        'cashbox_id \'unknown_cashbox\' for park_id \'park_id_1\' not found'
    )
    assert response.status_code == 400, response.text
    assert response.json() == {'code': 'unknown_cashbox', 'message': message}


async def test_without_failure_id(taxi_cashbox_integration, pgsql):
    park_id = 'park_id_3'
    cashbox_id = 'cashbox_id_1'
    limit = 1

    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        headers={'Accept-Language': 'en'},
        json={'park_id': park_id, 'cashbox_id': cashbox_id, 'limit': limit},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'park_id': 'park_id_3',
        'failed_receipts': [
            {
                'description': 'unknown error',
                'created_at': '2019-10-01T10:13:00+00:00',
            },
        ],
    }
