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
    'yandex_uids', [[DEFAULT_UID], [DEFAULT_UID, DEFAULT_UID + '_']],
)
@pytest.mark.parametrize('favorite_goods', [True, False])
@pytest.mark.parametrize('recent_goods', [True, False])
@pytest.mark.parametrize('attributes', [True, False])
async def test_basic(
        taxi_grocery_fav_goods,
        favorites_db,
        recent_goods_db,
        attributes_db,
        favorite_goods,
        recent_goods,
        attributes,
        yandex_uids,
):
    for yandex_uid in yandex_uids:
        if attributes:
            attributes_db.set_attributes(
                yandex_uid=yandex_uid,
                important_ingredients=IMPORTANT_INGREDIENTS,
                main_allergens=MAIN_ALLERGENS,
                custom_tags=CUSTOM_TAGS,
            )

        if favorite_goods:
            favorites_db.insert_favorites(yandex_uid, FAVORITE_GOODS)

        if recent_goods:
            for recent_good in RECENT_GOODS:
                recent_goods_db.add_recent_good(
                    yandex_uid=yandex_uid,
                    product_id=recent_good['product_id'],
                    last_purchase=recent_good['last_purchase'],
                )

    response = await taxi_grocery_fav_goods.post(
        '/internal/fav-goods/v1/takeout/status',
        json={'yandex_uids': yandex_uids},
    )

    assert response.status == 200
    status = response.json()['status']

    assert (
        status == 'ready_to_delete'
        if (attributes or favorite_goods or recent_goods)
        else 'empty'
    )
