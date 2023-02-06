async def test_simple_create(taxi_virtual_tariffs):
    body = {
        'description': 'Способен доставлять еду2',
        'id': 'food_delivery2',
        'requirements': [
            {
                'arguments': [{'value': 'food_box'}, {'value': 'food_box2'}],
                'field': 'Tags',
                'operation': 'ContainsAll',
            },
            {
                'arguments': [{'value': '5'}],
                'field': 'Tags',
                'operation': 'ContainsAll',
            },
        ],
    }
    response = await taxi_virtual_tariffs.post(
        '/v1/special-requirement/add', json=body,
    )
    assert response.status_code == 200
    assert response.json() == body


async def test_already_exist_create(taxi_virtual_tariffs):
    body = {
        'description': 'Способен доставлять еду2',
        'id': 'food_delivery',
        'requirements': [],
    }
    response = await taxi_virtual_tariffs.post(
        '/v1/special-requirement/add', json=body,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'record_already_exist',
        'message': 'Спецтребование с таким id уже существует',
    }


async def test_create_with_validation_error(taxi_virtual_tariffs):
    body = {
        'description': 'Способен доставлять еду2',
        'id': 'food_delivery2',
        'requirements': [
            {
                'arguments': [{'value': 'food_box'}, {'value': 'food_box2'}],
                'field': 'Tags',
                'operation': 'ContainsAll',
            },
            {
                'arguments': [{'value': '5'}],
                'field': 'Tags',
                'operation': 'NotContains',
            },
        ],
    }
    response = await taxi_virtual_tariffs.post(
        '/v1/special-requirement/add', json=body,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad_request',
        'details': {
            'errors': [
                {
                    'code': 'requirement_error',
                    'location': '/requirements/1',
                    'message': 'Unknown operation key = NotContains',
                },
            ],
        },
        'message': 'Неверный формат требования',
    }
