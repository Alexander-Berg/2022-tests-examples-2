import pytest


DEFAULT_YANDEX_UID = 'test_yandex_uid'
DEFAULT_HEADERS = {
    'X-YaTaxi-Session': 'taxi:user-id',
    'X-Yandex-UID': DEFAULT_YANDEX_UID,
}

MAX_RECENT_GOODS = 123777


@pytest.fixture(name='test_grocery_fav_goods')
def _test_grocery_fav_goods(taxi_grocery_fav_goods):
    class TestGroceryFavGoods:
        def __init__(self):
            pass

        @staticmethod
        async def recent_goods_check_presence(extra_headers=None):
            headers = DEFAULT_HEADERS.copy()

            if extra_headers is not None:
                for key, val in extra_headers.items():
                    if val is not None:
                        headers[key] = val
                    else:
                        headers.pop(key, None)

            return await taxi_grocery_fav_goods.post(
                '/internal/v1/recent-goods/check-presence', headers=headers,
            )

    return TestGroceryFavGoods()


@pytest.mark.parametrize('yandex_uid', (None, ''))
async def test_no_yandex_uid(test_grocery_fav_goods, yandex_uid):
    response = await test_grocery_fav_goods.recent_goods_check_presence(
        extra_headers={'X-Yandex-UID': yandex_uid},
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'NO_YANDEX_UID'


@pytest.mark.config(GROCERY_FAV_GOODS_MAX_RECENT_GOODS=MAX_RECENT_GOODS)
async def test_orders_log_request(test_grocery_fav_goods, order_log):
    order_log.setup_request_checking(
        yandex_uid=DEFAULT_YANDEX_UID, count=MAX_RECENT_GOODS,
    )
    order_log.add_order(
        created_at='2020-11-11T07:00:00+00:00',
        product_ids=['test_product_id'],
    )

    response = await test_grocery_fav_goods.recent_goods_check_presence()
    assert response.status_code == 200

    assert order_log.times_called == 1


@pytest.mark.parametrize('presented', (True, False))
async def test_recent_goods_from_db(
        test_grocery_fav_goods, recent_goods_db, order_log, presented,
):
    if presented:
        recent_goods_db.add_recent_goods(
            yandex_uid='test_yandex_uid',
            product_ids=['productid11'],
            last_purchase='2020-11-11T07:00:00+00:00',
        )

    response = await test_grocery_fav_goods.recent_goods_check_presence()
    assert response.status_code == 200
    assert response.json()['presented'] == presented

    assert order_log.has_calls is not presented
