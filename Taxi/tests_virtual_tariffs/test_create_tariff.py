async def test_simple_create(taxi_virtual_tariffs):
    body = {
        'id': 'pj_tariff',
        'description': '',
        'coverages': [
            {
                'class': 'comfort',
                'corp_client_id': '01234567890123456789012345678912',
            },
        ],
        'special_requirements_ids': ['good_driver'],
    }
    response = await taxi_virtual_tariffs.post('/v1/tariff/add', json=body)
    assert response.status_code == 200
    assert response.json() == body


async def test_simple_create_then_delete(taxi_virtual_tariffs):
    body = {
        'id': 'pj_tariff',
        'description': '',
        'coverages': [
            {
                'class': 'comfort',
                'corp_client_id': '01234567890123456789012345678912',
            },
        ],
        'special_requirements_ids': ['good_driver'],
    }
    response = await taxi_virtual_tariffs.post('/v1/tariff/add', json=body)
    assert response.status_code == 200
    assert response.json() == body

    url = '/v1/tariff/?id=pj_tariff'
    response = await taxi_virtual_tariffs.delete(url)
    assert response.status_code == 200


async def test_already_exist_create(taxi_virtual_tariffs):
    body = {
        'id': 'econom_pj',
        'description': '',
        'special_requirements_ids': ['good_rating'],
        'coverages': [
            {
                'class': 'comfort',
                'corp_client_id': '01234567890123456789012345678912',
            },
        ],
    }
    response = await taxi_virtual_tariffs.post('/v1/tariff/add', json=body)
    assert response.status_code == 400
    assert response.json() == {
        'code': 'record_already_exist',
        'message': 'Тариф с таким id уже существует',
    }


async def test_already_exist_coverage_create(taxi_virtual_tariffs):
    body = {
        'id': 'econom_zone_null',
        'description': '',
        'special_requirements_ids': ['good_driver'],
        'coverages': [
            {
                'class': 'comfort',
                'corp_client_id': '01234567890123456789012345678912',
                'zone': 'moscow',
            },
        ],
    }
    response = await taxi_virtual_tariffs.post('/v1/tariff/add', json=body)
    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad_request',
        'details': {
            'errors': [
                {
                    'code': 'duplicate_coverage',
                    'location': '/coverages/0',
                    'message': 'Покрытие уже существует',
                },
            ],
        },
        'message': 'Ошибка покрытий',
    }
