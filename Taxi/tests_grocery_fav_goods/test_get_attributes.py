# Проверяем что возвращаются нужные атрибуты для юзера
async def test_get_attributes(taxi_grocery_fav_goods, attributes_db):
    # Кладем атрибуты для 2 юзеров
    user_1 = 'yandex_uid_1'
    user_2 = 'yandex_uid_2'
    attributes_db.set_attributes(
        yandex_uid=user_1,
        important_ingredients=['luk'],
        main_allergens=['riba', 'oreh'],
        custom_tags=['halal'],
    )
    attributes_db.set_attributes(
        yandex_uid=user_2,
        important_ingredients=[],
        main_allergens=['orange'],
        custom_tags=['halal', 'kocher'],
    )

    # Проверяем атрибуты первого
    headers = {'X-YaTaxi-Session': 'taxi:user-id', 'X-Yandex-UID': user_1}
    response = await taxi_grocery_fav_goods.post(
        '/lavka/v1/fav-goods/v1/get-attributes', headers=headers, json={},
    )
    assert response.status == 200
    assert response.json()['attributes'] == {
        'important_ingredients': ['luk'],
        'main_allergens': ['oreh', 'riba'],
        'custom_tags': ['halal'],
    }
    assert response.json()['seen_onboarding']

    # Проверяем атрибуты второго
    headers['X-Yandex-UID'] = user_2
    response = await taxi_grocery_fav_goods.post(
        '/lavka/v1/fav-goods/v1/get-attributes', headers=headers, json={},
    )
    assert response.status == 200
    assert response.json()['attributes'] == {
        'important_ingredients': [],
        'main_allergens': ['orange'],
        'custom_tags': ['halal', 'kocher'],
    }
    assert response.json()['seen_onboarding']


async def test_unauthorized(taxi_grocery_fav_goods):
    response = await taxi_grocery_fav_goods.post(
        '/lavka/v1/fav-goods/v1/get-attributes', headers={}, json={},
    )
    assert response.status == 401
    assert response.json() == {'code': 'UNAUTHORIZED', 'message': ''}


async def test_no_uid(taxi_grocery_fav_goods):
    response = await taxi_grocery_fav_goods.post(
        '/lavka/v1/fav-goods/v1/get-attributes',
        headers={'X-YaTaxi-Session': 'taxi:user-id'},
        json={},
    )
    assert response.status == 400
    assert response.json() == {
        'code': 'NO_YANDEX_UID',
        'message': 'No YandexUid in request or it is empty',
    }


async def test_no_user(taxi_grocery_fav_goods):
    response = await taxi_grocery_fav_goods.post(
        '/lavka/v1/fav-goods/v1/get-attributes',
        headers={
            'X-YaTaxi-Session': 'taxi:user-id',
            'X-Yandex-UID': 'no_user',
        },
        json={},
    )
    assert response.status == 200
    assert response.json()['attributes'] == {
        'important_ingredients': [],
        'main_allergens': [],
        'custom_tags': [],
    }
    assert not response.json()['seen_onboarding']
