async def test_filters_for_wizard(taxi_eats_catalog):
    response = await taxi_eats_catalog.get('/internal/v1/filters-for-wizard')
    assert response.status_code == 200

    data = response.json()
    data['payload']['quickFilters'].sort(key=lambda filter: filter['id'])

    assert data == {
        'payload': {
            'quickFilters': [
                {'id': 3, 'name': 'Бургеры'},
                {'id': 5, 'name': 'Суши'},
                {'id': 7, 'name': 'Пицца'},
                {'id': 9, 'name': 'Здоровая еда'},
                {'id': 11, 'name': 'Итальянская'},
                {'id': 13, 'name': 'Вегги'},
                {'id': 15, 'name': 'Стейки'},
                {'id': 17, 'name': 'Десерты'},
                {'id': 19, 'name': 'Грузинская'},
                {'id': 21, 'name': 'Завтраки'},
                {'id': 23, 'name': 'Русская'},
                {'id': 25, 'name': 'Для детей'},
                {'id': 31, 'name': 'Кавказская'},
                {'id': 33, 'name': 'Пироги'},
                {'id': 35, 'name': 'Китайская'},
                {'id': 43, 'name': 'Вьетнамская'},
                {'id': 45, 'name': 'Узбекская'},
                {'id': 47, 'name': 'Лапша Вок'},
                {'id': 49, 'name': 'Шашлык'},
                {'id': 51, 'name': 'Шаурма'},
                {'id': 54, 'name': 'Депо'},
                {'id': 130, 'name': 'Выпечка'},
                {'id': 145, 'name': 'Фастфуд'},
                {'id': 147, 'name': 'Фудхолл Дружба'},
                {'id': 152, 'name': 'Даниловский'},
            ],
        },
        'meta': {},
    }
