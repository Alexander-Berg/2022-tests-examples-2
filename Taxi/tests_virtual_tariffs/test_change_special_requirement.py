async def test_simple_change(taxi_virtual_tariffs):
    current_revision = 20
    next_revision = 23
    special_requirement = {
        'description': 'Способен доставлять еду2',
        'id': 'food_delivery',
        'requirements': [
            {
                'arguments': [{'value': 'foodbox'}, {'value': 'delivery'}],
                'field': 'Tags',
                'operation': 'ContainsAll',
            },
        ],
    }
    for _ in range(3):
        response = await taxi_virtual_tariffs.post(
            '/v1/special-requirement/update',
            json={
                'special_requirement': special_requirement,
                'revision': current_revision,
            },
        )
        assert response.status_code == 200
        assert response.json() == {
            'special_requirement': special_requirement,
            'revision': next_revision,
        }


async def test_change_not_existing(taxi_virtual_tariffs):
    body = {
        'special_requirement': {
            'description': 'Способен доставлять еду2',
            'id': 'food_delivery2',
            'requirements': [],
        },
        'revision': 20,
    }
    response = await taxi_virtual_tariffs.post(
        '/v1/special-requirement/update', json=body,
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'record_not_found',
        'message': 'Тариф не найден',
    }


async def test_validation(taxi_virtual_tariffs):
    body = {
        'special_requirement': {
            'description': 'Способен доставлять еду2',
            'id': 'food_delivery',
            'requirements': [
                {
                    'arguments': [],
                    'field': 'not_tags',
                    'operation': 'ContainsAll',
                },
            ],
        },
        'revision': 12,
    }
    response = await taxi_virtual_tariffs.post(
        '/v1/special-requirement/update', json=body,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad_request',
        'details': {
            'errors': [
                {
                    'code': 'requirement_error',
                    'location': '/requirements/0',
                    'message': 'Unknown requirement key = not_tags',
                },
            ],
        },
        'message': 'Неверный формат требования',
    }


async def test_conflict(taxi_virtual_tariffs):
    body = {
        'special_requirement': {
            'description': 'Способен доставлять еду2',
            'id': 'food_delivery',
            'requirements': [
                {'arguments': [], 'field': 'Tags', 'operation': 'ContainsAll'},
            ],
        },
        'revision': 12,
    }
    response = await taxi_virtual_tariffs.post(
        '/v1/special-requirement/update', json=body,
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'conflict',
        'message': 'Изменяемая версия отличается от актуальной',
    }
