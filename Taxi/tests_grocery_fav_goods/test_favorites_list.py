DEFAULT_UID = 'test_yandex_uid'
DEFAULT_HEADERS = {
    'X-YaTaxi-Session': 'taxi:user-id',
    'X-Yandex-UID': DEFAULT_UID,
}

# Проверяем, что из базы достаются все продукты
async def test_get_favorites_list(taxi_grocery_fav_goods, favorites_db):
    favorite_products = [
        {'product_id': 'product_1', 'is_favorite': True},
        {'product_id': 'product_2', 'is_favorite': False},
        {'product_id': 'product_3', 'is_favorite': False},
        {'product_id': 'product_4', 'is_favorite': True},
    ]
    favorites_db.insert_favorites(DEFAULT_UID, favorite_products)
    response = await taxi_grocery_fav_goods.post(
        '/internal/v1/favorites/list', headers=DEFAULT_HEADERS, json={},
    )
    assert response.status == 200
    assert response.json()['products'] == favorite_products


# Проверяем, что при отсутствии YandexUid отдаем 400
async def test_no_uid(taxi_grocery_fav_goods):
    response = await taxi_grocery_fav_goods.post(
        '/internal/v1/favorites/list',
        headers={'X-YaTaxi-Session': 'taxi:user-id'},
        json={},
    )
    assert response.status == 400
    assert response.json() == {
        'code': 'NO_YANDEX_UID',
        'message': 'No YandexUid in request or it is empty',
    }


# Проверяем, что для неавторизованных пользователей отдаем 401
async def test_unathorized(taxi_grocery_fav_goods):
    response = await taxi_grocery_fav_goods.post(
        '/internal/v1/favorites/list', headers={}, json={},
    )
    assert response.status == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}
