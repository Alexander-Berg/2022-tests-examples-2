import pytest

from tests_grocery_fav_goods.plugins import (
    recent_goods_db as recent_goods_db_plugin,
)


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
        async def recent_goods_get(extra_headers=None):
            headers = DEFAULT_HEADERS.copy()

            if extra_headers is not None:
                for key, val in extra_headers.items():
                    if val is not None:
                        headers[key] = val
                    else:
                        headers.pop(key, None)

            return await taxi_grocery_fav_goods.post(
                '/internal/v1/recent-goods/get', headers=headers,
            )

    return TestGroceryFavGoods()


@pytest.mark.parametrize('yandex_uid', (None, ''))
async def test_no_yandex_uid(test_grocery_fav_goods, yandex_uid):
    response = await test_grocery_fav_goods.recent_goods_get(
        extra_headers={'X-Yandex-UID': yandex_uid},
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'NO_YANDEX_UID'


@pytest.mark.config(GROCERY_FAV_GOODS_MAX_RECENT_GOODS=MAX_RECENT_GOODS)
async def test_order_log_request(test_grocery_fav_goods, order_log, testpoint):
    @testpoint('add_recent_goods_from_eats')
    def add_recent_goods_from_eats(data):
        pass

    order_log.setup_request_checking(
        yandex_uid=DEFAULT_YANDEX_UID, count=MAX_RECENT_GOODS,
    )
    order_log.add_order(
        created_at='2020-11-11T07:00:00+00:00',
        product_ids=['test_product_id'],
    )

    response = await test_grocery_fav_goods.recent_goods_get()
    assert response.status_code == 200

    assert order_log.times_called == 1

    await add_recent_goods_from_eats.wait_call()


@pytest.mark.parametrize('order_presented', (True, False))
async def test_no_recent_goods(
        test_grocery_fav_goods, order_log, order_presented,
):
    if order_presented:
        order_log.add_order(
            created_at='2020-11-11T07:00:00+00:00', product_ids=[],
        )

    response = await test_grocery_fav_goods.recent_goods_get()
    assert response.status_code == 200
    assert response.json()['product_ids'] == []

    assert order_log.times_called == 1


async def test_recent_goods_from_eats(
        test_grocery_fav_goods, order_log, testpoint,
):
    @testpoint('add_recent_goods_from_eats')
    def add_recent_goods_from_eats(data):
        pass

    order_log.add_order(
        created_at='2020-11-11T07:00:00+00:00',
        product_ids=['productid11', 'productid12'],
    )
    order_log.add_order(
        created_at='2020-11-11T15:00:00+00:00', product_ids=['productid21'],
    )

    response = await test_grocery_fav_goods.recent_goods_get()
    assert response.status_code == 200
    assert response.json()['product_ids'] == [
        'productid21',
        'productid11',
        'productid12',
    ]

    await add_recent_goods_from_eats.wait_call()


async def test_recent_goods_from_db(
        test_grocery_fav_goods, recent_goods_db, order_log,
):
    recent_goods_db.add_recent_goods(
        yandex_uid=DEFAULT_YANDEX_UID,
        product_ids=['productid11', 'productid12'],
        last_purchase='2020-11-11T07:00:00+00:00',
    )
    recent_goods_db.add_recent_goods(
        yandex_uid=DEFAULT_YANDEX_UID,
        product_ids=['productid21'],
        last_purchase='2020-11-11T15:00:00+00:00',
    )

    response = await test_grocery_fav_goods.recent_goods_get()
    assert response.status_code == 200
    assert response.json()['product_ids'] == [
        'productid21',
        'productid11',
        'productid12',
    ]

    assert not order_log.has_calls


async def test_migrate_recent_goods_from_eats_to_db(
        test_grocery_fav_goods, recent_goods_db, order_log, testpoint,
):
    @testpoint('add_recent_goods_from_eats')
    def add_recent_goods_from_eats(data):
        pass

    order_log.add_order(
        created_at='2020-11-11T07:00:00+00:00',
        product_ids=['productid11', 'productid12'],
    )
    order_log.add_order(
        created_at='2020-11-11T15:00:00+00:00', product_ids=['productid21'],
    )

    response = await test_grocery_fav_goods.recent_goods_get()
    assert response.status_code == 200

    await add_recent_goods_from_eats.wait_call()

    recent_goods = recent_goods_db.get_all_recent_goods()

    expected_recent_goods = [
        recent_goods_db_plugin.RecentGood(
            yandex_uid=DEFAULT_YANDEX_UID,
            product_id='productid11',
            last_purchase='2020-11-11T07:00:00+00:00',
        ),
        recent_goods_db_plugin.RecentGood(
            yandex_uid=DEFAULT_YANDEX_UID,
            product_id='productid12',
            last_purchase='2020-11-11T07:00:00+00:00',
        ),
        recent_goods_db_plugin.RecentGood(
            yandex_uid=DEFAULT_YANDEX_UID,
            product_id='productid21',
            last_purchase='2020-11-11T15:00:00+00:00',
        ),
    ]

    def sorted_recent_goods(recent_goods):
        return sorted(
            recent_goods, key=lambda recent_good: recent_good.product_id,
        )

    assert sorted_recent_goods(recent_goods) == sorted_recent_goods(
        expected_recent_goods,
    )


@pytest.mark.config(GROCERY_FAV_GOODS_MAX_RECENT_GOODS=5)
async def test_sort_duplicate_truncate_from_eats(
        test_grocery_fav_goods, recent_goods_db, order_log, testpoint,
):
    @testpoint('add_recent_goods_from_eats')
    def add_recent_goods_from_eats(data):
        pass

    order_log.add_order(created_at='2020-11-11T16:00:00+00:00', product_ids=[])
    order_log.add_order(
        created_at='2020-11-11T15:00:00+00:00',
        product_ids=['product12', 'product11'],
    )
    order_log.add_order(
        created_at='2020-11-11T14:00:00+00:00',
        product_ids=['product21', 'product12', 'product22'],
    )
    order_log.add_order(
        created_at='2020-11-11T13:00:00+00:00',
        product_ids=['product22', 'product33', 'product32', 'product31'],
    )

    response = await test_grocery_fav_goods.recent_goods_get()
    assert response.status_code == 200
    assert response.json()['product_ids'] == [
        'product11',
        'product12',
        'product21',
        'product22',
        'product33',
    ]

    await add_recent_goods_from_eats.wait_call()

    recent_goods = recent_goods_db.get_all_recent_goods()

    expected_recent_goods = [
        recent_goods_db_plugin.RecentGood(
            yandex_uid=DEFAULT_YANDEX_UID,
            product_id='product11',
            last_purchase='2020-11-11T15:00:00+00:00',
        ),
        recent_goods_db_plugin.RecentGood(
            yandex_uid=DEFAULT_YANDEX_UID,
            product_id='product12',
            last_purchase='2020-11-11T15:00:00+00:00',
        ),
        recent_goods_db_plugin.RecentGood(
            yandex_uid=DEFAULT_YANDEX_UID,
            product_id='product21',
            last_purchase='2020-11-11T14:00:00+00:00',
        ),
        recent_goods_db_plugin.RecentGood(
            yandex_uid=DEFAULT_YANDEX_UID,
            product_id='product22',
            last_purchase='2020-11-11T14:00:00+00:00',
        ),
        recent_goods_db_plugin.RecentGood(
            yandex_uid=DEFAULT_YANDEX_UID,
            product_id='product33',
            last_purchase='2020-11-11T13:00:00+00:00',
        ),
    ]

    def sorted_recent_goods(recent_goods):
        return sorted(
            recent_goods, key=lambda recent_good: recent_good.product_id,
        )

    assert sorted_recent_goods(recent_goods) == sorted_recent_goods(
        expected_recent_goods,
    )


@pytest.mark.config(GROCERY_FAV_GOODS_MAX_RECENT_GOODS=5)
async def test_sort_truncate_from_db(test_grocery_fav_goods, recent_goods_db):
    recent_goods_db.add_recent_goods(
        yandex_uid=DEFAULT_YANDEX_UID,
        product_ids=['product12', 'product11'],
        last_purchase='2020-11-11T15:00:00+00:00',
    )
    recent_goods_db.add_recent_goods(
        yandex_uid=DEFAULT_YANDEX_UID,
        product_ids=['product21', 'product22'],
        last_purchase='2020-11-11T14:00:00+00:00',
    )
    recent_goods_db.add_recent_goods(
        yandex_uid=DEFAULT_YANDEX_UID,
        product_ids=['product33', 'product32', 'product31'],
        last_purchase='2020-11-11T13:00:00+00:00',
    )

    response = await test_grocery_fav_goods.recent_goods_get()
    assert response.status_code == 200
    assert response.json()['product_ids'] == [
        'product11',
        'product12',
        'product21',
        'product22',
        'product31',
    ]
