DEFAULT_UID = 'test_yandex_uid'

FAVORITE_GOODS = [
    {'product_id': 'product_1', 'is_favorite': True},
    {'product_id': 'product_2', 'is_favorite': False},
    {'product_id': 'product_3', 'is_favorite': False},
    {'product_id': 'product_4', 'is_favorite': True},
]

RECENT_GOODS = [
    {
        'product_id': 'productid_1',
        'last_purchase': '2020-11-11T07:00:00+00:00',
    },
    {
        'product_id': 'productid_2',
        'last_purchase': '2020-11-12T07:00:00+00:00',
    },
]

IMPORTANT_INGREDIENTS = ['ing1', 'ing2', 'ing3']
MAIN_ALLERGENS = ['allerg1', 'allerg2']
CUSTOM_TAGS = ['tag1', 'tag2']


async def test_basic(
        taxi_grocery_fav_goods, favorites_db, recent_goods_db, attributes_db,
):
    favorites_db.insert_favorites(DEFAULT_UID, FAVORITE_GOODS)
    for recent_good in RECENT_GOODS:
        recent_goods_db.add_recent_good(
            yandex_uid=DEFAULT_UID,
            product_id=recent_good['product_id'],
            last_purchase=recent_good['last_purchase'],
        )

    attributes_db.set_attributes(
        yandex_uid=DEFAULT_UID,
        important_ingredients=IMPORTANT_INGREDIENTS,
        main_allergens=MAIN_ALLERGENS,
        custom_tags=CUSTOM_TAGS,
    )

    response = await taxi_grocery_fav_goods.post(
        '/internal/fav-goods/v1/takeout/delete',
        json={'yandex_uid': DEFAULT_UID},
    )

    assert response.status == 200
    favorite_goods = favorites_db.get_favorites(DEFAULT_UID)
    assert not favorite_goods
    recent_goods = recent_goods_db.get_all_recent_goods()
    assert not recent_goods
    attributes = attributes_db.get_attributes(DEFAULT_UID)
    assert not attributes
