import dateutil.parser
import pytest

from tests_grocery_fav_goods.plugins import (
    recent_goods_db as recent_goods_db_plugin,
)


DEFAULT_YANDEX_UID = 'test_yandex_uid'
DEFAULT_HEADERS = {
    'X-YaTaxi-Session': 'taxi:user-id',
    'X-Yandex-UID': DEFAULT_YANDEX_UID,
}


@pytest.fixture(name='test_grocery_fav_goods')
def _test_grocery_fav_goods(taxi_grocery_fav_goods):
    class TestGroceryFavGoods:
        def __init__(self):
            pass

        @staticmethod
        async def recent_goods_add(product_ids, extra_headers=None):
            headers = DEFAULT_HEADERS.copy()

            if extra_headers is not None:
                for key, val in extra_headers.items():
                    if val is not None:
                        headers[key] = val
                    else:
                        headers.pop(key, None)

            return await taxi_grocery_fav_goods.post(
                '/internal/v1/recent-goods/add',
                headers=headers,
                json={'product_ids': product_ids},
            )

    return TestGroceryFavGoods()


@pytest.mark.parametrize('yandex_uid', (None, ''))
async def test_no_yandex_uid(test_grocery_fav_goods, yandex_uid):
    response = await test_grocery_fav_goods.recent_goods_add(
        product_ids=[], extra_headers={'X-Yandex-UID': yandex_uid},
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'NO_YANDEX_UID'


async def test_basic(test_grocery_fav_goods, recent_goods_db, mocked_time):
    product_ids = ['test_product_id_1', 'test_product_id_2']

    now = '2020-11-17T12:00:00+00:00'

    mocked_time.set(dateutil.parser.parse(now))

    response = await test_grocery_fav_goods.recent_goods_add(
        product_ids=product_ids,
    )
    assert response.status_code == 200

    recent_goods = recent_goods_db.get_all_recent_goods()

    expected_recent_goods = [
        recent_goods_db_plugin.RecentGood(
            yandex_uid=DEFAULT_YANDEX_UID,
            product_id=product_id,
            last_purchase=now,
        )
        for product_id in product_ids
    ]

    def sorted_recent_goods(recent_goods):
        return sorted(
            recent_goods, key=lambda recent_good: recent_good.product_id,
        )

    assert sorted_recent_goods(recent_goods) == sorted_recent_goods(
        expected_recent_goods,
    )


async def test_renew_recent_good(
        test_grocery_fav_goods, recent_goods_db, mocked_time,
):
    product_id = 'test_product_id'

    old_now = '2020-11-17T11:00:00+00:00'
    new_now = '2020-11-17T16:00:00+00:00'

    recent_goods_db.add_recent_good(
        yandex_uid=DEFAULT_YANDEX_UID,
        product_id=product_id,
        last_purchase=old_now,
    )

    mocked_time.set(dateutil.parser.parse(new_now))

    response = await test_grocery_fav_goods.recent_goods_add(
        product_ids=[product_id],
    )
    assert response.status_code == 200

    assert (
        recent_goods_db.get_last_purchase(
            yandex_uid=DEFAULT_YANDEX_UID, product_id=product_id,
        )
        == new_now
    )


@pytest.mark.config(GROCERY_FAV_GOODS_MAX_RECENT_GOODS=5)
async def test_remove_old_recent_goods(
        test_grocery_fav_goods, recent_goods_db, mocked_time,
):
    recent_goods_db.add_recent_goods(
        yandex_uid=DEFAULT_YANDEX_UID,
        product_ids=['product11', 'product12'],
        last_purchase='2020-11-11T15:00:00+00:00',
    )
    recent_goods_db.add_recent_goods(
        yandex_uid=DEFAULT_YANDEX_UID,
        product_ids=['product23', 'product22', 'product21'],
        last_purchase='2020-11-11T14:00:00+00:00',
    )

    now = '2020-11-11T16:00:00+00:00'

    mocked_time.set(dateutil.parser.parse(now))

    response = await test_grocery_fav_goods.recent_goods_add(
        product_ids=['product31'],
    )
    assert response.status_code == 200

    recent_goods = recent_goods_db.get_all_recent_goods()

    expected_recent_goods = [
        recent_goods_db_plugin.RecentGood(
            yandex_uid=DEFAULT_YANDEX_UID,
            product_id='product31',
            last_purchase='2020-11-11T16:00:00+00:00',
        ),
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
    ]

    def sorted_recent_goods(recent_goods):
        return sorted(
            recent_goods, key=lambda recent_good: recent_good.product_id,
        )

    assert sorted_recent_goods(recent_goods) == sorted_recent_goods(
        expected_recent_goods,
    )


@pytest.mark.config(GROCERY_FAV_GOODS_MAX_RECENT_GOODS=5)
async def test_not_remove_old_recent_goods(
        test_grocery_fav_goods, recent_goods_db, mocked_time,
):
    recent_goods_db.add_recent_goods(
        yandex_uid=DEFAULT_YANDEX_UID,
        product_ids=['product11', 'product12'],
        last_purchase='2020-11-11T15:00:00+00:00',
    )
    recent_goods_db.add_recent_goods(
        yandex_uid=DEFAULT_YANDEX_UID,
        product_ids=['product23', 'product22', 'product21'],
        last_purchase='2020-11-11T14:00:00+00:00',
    )

    now = '2020-11-11T16:00:00+00:00'

    mocked_time.set(dateutil.parser.parse(now))

    response = await test_grocery_fav_goods.recent_goods_add(
        product_ids=['product11'],
    )
    assert response.status_code == 200

    recent_goods = recent_goods_db.get_all_recent_goods()

    expected_recent_goods = [
        recent_goods_db_plugin.RecentGood(
            yandex_uid=DEFAULT_YANDEX_UID,
            product_id='product11',
            last_purchase='2020-11-11T16:00:00+00:00',
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
            product_id='product23',
            last_purchase='2020-11-11T14:00:00+00:00',
        ),
    ]

    def sorted_recent_goods(recent_goods):
        return sorted(
            recent_goods, key=lambda recent_good: recent_good.product_id,
        )

    assert sorted_recent_goods(recent_goods) == sorted_recent_goods(
        expected_recent_goods,
    )


async def test_id_type(test_grocery_fav_goods, recent_goods_db, mocked_time):
    now = '2020-11-11T16:00:00+00:00'

    mocked_time.set(dateutil.parser.parse(now))

    product_id = ['store_id', 'parcel_id:st-pa', 'markdown_id:st-md']
    response = await test_grocery_fav_goods.recent_goods_add(
        product_ids=product_id,
    )
    assert response.status_code == 200

    recent_goods = recent_goods_db.get_all_recent_goods()

    assert len(recent_goods) == 2

    test_recent_good = recent_goods_db_plugin.RecentGood(
        yandex_uid=DEFAULT_YANDEX_UID,
        product_id='store_id',
        last_purchase=now,
    )

    assert test_recent_good in recent_goods

    test_recent_good.product_id = 'markdown_id:st-md'
    assert test_recent_good not in recent_goods

    test_recent_good.product_id = 'markdown_id'
    assert test_recent_good in recent_goods

    test_recent_good.product_id = 'parcel_id:st-pa'
    assert test_recent_good not in recent_goods
