async def test_simple_change(taxi_virtual_tariffs):
    current_revision = 1
    next_revision = 3
    tariff = {
        'id': 'econom_pj',
        'description': '',
        'special_requirements_ids': ['good_driver'],
        'coverages': [
            {
                'class': 'comfort',
                'corp_client_id': '01234567890123456789012345678912',
            },
            {
                'class': 'econom',
                'corp_client_id': '01234567890123456789012345678912',
                'zone': 'spb',
            },
        ],
    }
    for _ in range(3):
        response = await taxi_virtual_tariffs.post(
            '/v1/tariff/update',
            json={'tariff': tariff, 'revision': current_revision},
        )
        assert response.status_code == 200
        assert response.json() == {'tariff': tariff, 'revision': next_revision}


async def test_simple_change_then_delete(taxi_virtual_tariffs):
    current_revision = 1
    next_revision = 3
    tariff = {
        'id': 'econom_pj',
        'description': '',
        'special_requirements_ids': ['good_driver'],
        'coverages': [
            {
                'class': 'comfort',
                'corp_client_id': '01234567890123456789012345678912',
            },
            {
                'class': 'econom',
                'corp_client_id': '01234567890123456789012345678912',
                'zone': 'spb',
            },
        ],
    }
    for _ in range(2):
        response = await taxi_virtual_tariffs.post(
            '/v1/tariff/update',
            json={'tariff': tariff, 'revision': current_revision},
        )
        assert response.status_code == 200
        assert response.json() == {'tariff': tariff, 'revision': next_revision}

    url = '/v1/tariff/?id=econom_pj'
    response = await taxi_virtual_tariffs.delete(url)
    assert response.status_code == 200

    response = await taxi_virtual_tariffs.post(
        '/v1/tariff/update',
        json={'tariff': tariff, 'revision': current_revision},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'record_not_found',
        'message': 'Тариф не найден',
    }


async def test_change_not_existing(taxi_virtual_tariffs):
    body = {
        'tariff': {
            'id': 'econom',
            'description': '',
            'special_requirements_ids': ['good_rating'],
            'coverages': [],
        },
        'revision': 1,
    }
    response = await taxi_virtual_tariffs.post('/v1/tariff/update', json=body)
    assert response.status_code == 404
    assert response.json() == {
        'code': 'record_not_found',
        'message': 'Тариф не найден',
    }
