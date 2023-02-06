async def test_get_all(taxi_virtual_tariffs):
    response = await taxi_virtual_tariffs.get('/v1/special-requirements/list')
    assert response.status_code == 200
    assert response.json() == {
        'special_requirements': [
            {
                'description': 'Пустое спецтребование',
                'id': 'empty',
                'requirements': [],
            },
            {
                'description': 'Способен доставлять еду',
                'id': 'food_delivery',
                'requirements': [
                    {
                        'arguments': [{'value': 'food_box'}],
                        'field': 'tags',
                        'operation': 'contains',
                    },
                    {
                        'arguments': [{'value': '4.95'}],
                        'field': 'rating',
                        'operation': 'over',
                    },
                ],
            },
            {
                'description': 'Хороший водитель',
                'id': 'good_driver',
                'requirements': [],
            },
        ],
    }


async def test_get_by_id(taxi_virtual_tariffs):
    response = await taxi_virtual_tariffs.get(
        '/v1/special-requirement/?id=good_driver',
    )
    assert response.status_code == 200
    assert response.json() == {
        'revision': 22,
        'special_requirement': {
            'description': 'Хороший водитель',
            'id': 'good_driver',
            'requirements': [],
        },
    }
