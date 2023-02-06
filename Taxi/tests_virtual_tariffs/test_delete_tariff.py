async def test_delete_tariff(taxi_virtual_tariffs):
    url = '/v1/tariff/?id=comfort_pj'
    response = await taxi_virtual_tariffs.delete(url)
    assert response.status_code == 200
    assert response.json() == {
        'revision': 2,
        'tariff': {
            'coverages': [{'class': 'business', 'zone': 'moscow'}],
            'description': 'Description2',
            'id': 'comfort_pj',
            'special_requirements_ids': ['good_driver'],
        },
    }

    response = await taxi_virtual_tariffs.delete(url)
    assert response.status_code == 404
    assert response.json() == {
        'code': 'record_not_found',
        'message': 'Тариф не найден',
    }
