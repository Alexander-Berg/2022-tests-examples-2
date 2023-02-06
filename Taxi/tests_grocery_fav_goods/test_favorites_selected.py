DEFAULT_UID = 'test_yandex_uid'
DEFAULT_HEADERS = {
    'X-YaTaxi-Session': 'taxi:user-id',
    'X-Yandex-UID': DEFAULT_UID,
}

# Проверяем, в ответе ручки лежит пересечение продуктов из базы
# и продуктов из response
async def test_get_favorites_selected(taxi_grocery_fav_goods, favorites_db):
    favorite_products = [
        {'product_id': 'product_1', 'is_favorite': True},
        {'product_id': 'product_2', 'is_favorite': False},
        {'product_id': 'product_3', 'is_favorite': False},
        {'product_id': 'product_4', 'is_favorite': True},
    ]
    favorites_db.insert_favorites(DEFAULT_UID, favorite_products)
    other_user_products = [
        {'product_id': 'product_5', 'is_favorite': True},
        {'product_id': 'product_6', 'is_favorite': False},
    ]
    favorites_db.insert_favorites('other_uid', other_user_products)
    response = await taxi_grocery_fav_goods.post(
        '/internal/v1/favorites/selected',
        headers=DEFAULT_HEADERS,
        json={
            'product_ids': [
                'product_1',
                'product_2',
                'product_5',
                'product_6',
            ],
        },
    )
    assert response.status == 200
    assert response.json()['products'] == [
        {'product_id': 'product_1', 'is_favorite': True},
        {'product_id': 'product_2', 'is_favorite': False},
    ]


# Проверяем, что при отсутствии YandexUid отдаем 400
async def test_no_uid(taxi_grocery_fav_goods, favorites_db):
    response = await taxi_grocery_fav_goods.post(
        '/internal/v1/favorites/selected',
        headers={'X-YaTaxi-Session': 'taxi:user-id'},
        json={'product_ids': ['product_1']},
    )
    assert response.status == 400
    assert response.json() == {
        'code': 'NO_YANDEX_UID',
        'message': 'No YandexUid in request or it is empty',
    }


# Проверяем, что для неавторизованных пользователей отдаем 401
async def test_unathorized(taxi_grocery_fav_goods, favorites_db):
    response = await taxi_grocery_fav_goods.post(
        '/internal/v1/favorites/selected',
        headers={},
        json={'product_ids': ['product_1']},
    )
    assert response.status == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}
