DEFAULT_UID = 'test_yandex_uid'
DEFAULT_HEADERS = {
    'X-YaTaxi-Session': 'taxi:user-id',
    'X-Yandex-UID': DEFAULT_UID,
}

# Проверяем, что товары добавляются в базу
async def test_create_is_favorite(taxi_grocery_fav_goods, favorites_db):
    product_1 = 'product_1'
    response = await taxi_grocery_fav_goods.post(
        '/lavka/v1/fav-goods/v1/favorites',
        headers=DEFAULT_HEADERS,
        json={'product_id': product_1, 'is_favorite': True},
    )
    assert response.status == 200
    assert response.json() == {'product_id': product_1, 'is_favorite': True}
    fav_products = favorites_db.get_all_favorites()
    assert fav_products == [
        {
            'yandex_uid': DEFAULT_UID,
            'product_id': product_1,
            'is_favorite': True,
        },
    ]


# Проверяем, что is_favorite обновляется в базе
async def test_update_is_favorite(taxi_grocery_fav_goods, favorites_db):
    product_1 = 'product_1'
    favorites_db.set_is_favorite(DEFAULT_UID, product_1, True)
    response = await taxi_grocery_fav_goods.post(
        '/lavka/v1/fav-goods/v1/favorites',
        headers=DEFAULT_HEADERS,
        json={'product_id': product_1, 'is_favorite': False},
    )
    assert response.status == 200
    assert response.json() == {'product_id': product_1, 'is_favorite': False}
    fav_products = favorites_db.get_all_favorites()
    assert fav_products == [
        {
            'yandex_uid': DEFAULT_UID,
            'product_id': product_1,
            'is_favorite': False,
        },
    ]


# Проверяем, что при отсутствии YandexUid отдаем 400
async def test_no_uid(taxi_grocery_fav_goods, favorites_db):
    product_1 = 'product_1'
    response = await taxi_grocery_fav_goods.post(
        '/lavka/v1/fav-goods/v1/favorites',
        headers={'X-YaTaxi-Session': 'taxi:user-id'},
        json={'product_id': product_1, 'is_favorite': True},
    )
    assert response.status == 400
    assert response.json() == {
        'code': 'NO_YANDEX_UID',
        'message': 'No YandexUid in request or it is empty',
    }


# Проверяем, что для неавторизованных пользователей отдаем 401
async def test_unathorized(taxi_grocery_fav_goods, favorites_db):
    product_1 = 'product_1'
    response = await taxi_grocery_fav_goods.post(
        '/lavka/v1/fav-goods/v1/favorites',
        headers={},
        json={'product_id': product_1, 'is_favorite': True},
    )
    assert response.status == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}
