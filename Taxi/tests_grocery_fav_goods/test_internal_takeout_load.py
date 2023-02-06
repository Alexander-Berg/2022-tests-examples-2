import pytest

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


@pytest.mark.parametrize(
    'favorite_goods, recent_goods',
    [
        (FAVORITE_GOODS, None),
        (None, RECENT_GOODS),
        (FAVORITE_GOODS, RECENT_GOODS),
    ],
)
@pytest.mark.parametrize('important_ingredients', [IMPORTANT_INGREDIENTS, []])
@pytest.mark.parametrize('main_allergens', [MAIN_ALLERGENS, []])
@pytest.mark.parametrize('custom_tags', [CUSTOM_TAGS, []])
async def test_basic(
        taxi_grocery_fav_goods,
        favorites_db,
        recent_goods_db,
        attributes_db,
        favorite_goods,
        recent_goods,
        important_ingredients,
        main_allergens,
        custom_tags,
):
    attributes_db.set_attributes(
        yandex_uid=DEFAULT_UID,
        important_ingredients=important_ingredients,
        main_allergens=main_allergens,
        custom_tags=custom_tags,
    )

    if favorite_goods:
        favorites_db.insert_favorites(DEFAULT_UID, favorite_goods)

    if recent_goods:
        for recent_good in recent_goods:
            recent_goods_db.add_recent_good(
                yandex_uid=DEFAULT_UID,
                product_id=recent_good['product_id'],
                last_purchase=recent_good['last_purchase'],
            )

    response = await taxi_grocery_fav_goods.post(
        '/internal/fav-goods/v1/takeout/load',
        json={'yandex_uid': DEFAULT_UID},
    )

    assert response.status == 200
    object_ = response.json()['objects'][0]
    assert object_['id'] == f'grocery-fav-goods_{DEFAULT_UID}'
    object_data = object_['data']

    _check_lists_equal(recent_goods, object_data['recent_goods'])
    _check_lists_equal(favorite_goods, object_data['favorite_goods'])
    _check_lists_equal(
        important_ingredients, object_data['important_ingredients'],
    )
    _check_lists_equal(main_allergens, object_data['main_allergens'])
    _check_lists_equal(custom_tags, object_data['custom_tags'])


async def test_no_data(taxi_grocery_fav_goods):
    response = await taxi_grocery_fav_goods.post(
        '/internal/fav-goods/v1/takeout/load',
        json={'yandex_uid': DEFAULT_UID},
    )

    assert response.status == 200
    assert 'objects' not in response.json()


def _check_lists_equal(rhs, lhs):
    rhs = rhs or []
    lhs = lhs or []
    assert len(rhs) == len(lhs)
    assert all(r_item in lhs for r_item in rhs)
