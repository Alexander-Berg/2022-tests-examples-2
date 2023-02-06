async def test_delete_special_requirement(taxi_virtual_tariffs):
    url = '/v1/special-requirement/?id=food_delivery'
    response = await taxi_virtual_tariffs.delete(url)
    assert response.status_code == 200
    assert response.json() == {
        'revision': 20,
        'special_requirement': {
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
    }

    response = await taxi_virtual_tariffs.delete(url)
    assert response.status_code == 404
    assert response.json() == {
        'code': 'record_not_found',
        'message': 'Спецтребование не найдено',
    }
