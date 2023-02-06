DEFAULT_UID = 'test_yandex_uid'
DEFAULT_HEADERS = {
    'X-YaTaxi-Session': 'taxi:user-id',
    'X-Yandex-UID': DEFAULT_UID,
}

# Проверяем что атрибуты попадают в базу и обновляются
async def test_update_attributes(
        taxi_grocery_fav_goods, attributes_db, mocked_time,
):
    attributes_1 = {
        'important_ingredients': [],
        'main_allergens': ['riba'],
        'custom_tags': [],
    }
    response = await taxi_grocery_fav_goods.post(
        '/lavka/v1/fav-goods/v1/set-attributes',
        headers=DEFAULT_HEADERS,
        json={'attributes': attributes_1},
    )
    assert response.status == 200
    assert response.json()['attributes'] == attributes_1
    attributes = attributes_db.get_all_attributes()
    assert attributes[0]['updated'] is not None
    attributes[0].pop('updated')
    assert attributes == [{'yandex_uid': DEFAULT_UID, **attributes_1}]

    # Проверяем что аттрибуты обновляются, старые не сохраняются
    attributes_2 = {
        'important_ingredients': [],
        'main_allergens': [],
        'custom_tags': ['halal'],
    }
    response = await taxi_grocery_fav_goods.post(
        '/lavka/v1/fav-goods/v1/set-attributes',
        headers=DEFAULT_HEADERS,
        json={'attributes': attributes_2},
    )
    assert response.status == 200
    assert response.json()['attributes'] == attributes_2
    attributes = attributes_db.get_all_attributes()
    assert attributes[0]['updated'] is not None
    attributes[0].pop('updated')
    assert attributes == [{'yandex_uid': DEFAULT_UID, **attributes_2}]


async def test_unauthorized(taxi_grocery_fav_goods):
    response = await taxi_grocery_fav_goods.post(
        '/lavka/v1/fav-goods/v1/set-attributes',
        headers={},
        json={
            'attributes': {
                'important_ingredients': [],
                'main_allergens': ['riba'],
                'custom_tags': [],
            },
        },
    )
    assert response.status == 401
    assert response.json() == {'code': 'UNAUTHORIZED', 'message': ''}


async def test_no_uid(taxi_grocery_fav_goods):
    response = await taxi_grocery_fav_goods.post(
        '/lavka/v1/fav-goods/v1/set-attributes',
        headers={'X-YaTaxi-Session': 'taxi:user-id'},
        json={
            'attributes': {
                'important_ingredients': [],
                'main_allergens': ['riba'],
                'custom_tags': [],
            },
        },
    )
    assert response.status == 400
    assert response.json() == {
        'code': 'NO_YANDEX_UID',
        'message': 'No YandexUid in request or it is empty',
    }
