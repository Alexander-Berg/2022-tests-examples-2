import datetime

from tests_grocery_cart import common

BASIC_UID = 'some-uid-1'
ANOTHER_UID = 'some-uid-2'

BASIC_HEADERS = common.TAXI_HEADERS.copy()
ANOTHER_HEADERS = common.TAXI_HEADERS.copy()

BASIC_HEADERS['X-Yandex-UID'] = BASIC_UID
ANOTHER_HEADERS['X-Yandex-UID'] = ANOTHER_UID


async def test_takeout_load_ids(overlord_catalog, cart_factory, cart, now):
    overlord_catalog.add_product(product_id='item1', price='345')

    cart_1 = cart_factory(headers={**BASIC_HEADERS})
    cart_2 = cart_factory(headers={**BASIC_HEADERS})
    cart_3 = cart_factory(headers={**BASIC_HEADERS})
    cart_4 = cart_factory(headers={**ANOTHER_HEADERS})

    await cart_1.modify({'item1': {'q': 1, 'p': '345'}})
    await cart_2.modify({'item1': {'q': 1, 'p': '345'}})
    await cart_3.modify({'item1': {'q': 1, 'p': '345'}})
    await cart_4.modify({'item1': {'q': 1, 'p': '345'}})

    before_now = now - datetime.timedelta(minutes=2)
    after_now = now + datetime.timedelta(minutes=2)

    cart_1.update_db(created=_iso_format(before_now))
    cart_2.update_db(created=_iso_format(before_now))
    cart_3.update_db(created=_iso_format(after_now))
    cart_4.update_db(created=_iso_format(before_now))

    response_basic = await cart.takeout_load_ids(
        yandex_uid=BASIC_UID, till_dt=_iso_format(now),
    )
    response_another = await cart.takeout_load_ids(
        yandex_uid=ANOTHER_UID, till_dt=_iso_format(now),
    )

    assert response_basic == {'ids': [cart_1.cart_id, cart_2.cart_id]}
    assert response_another == {'ids': [cart_4.cart_id]}


async def test_takeout_load_ids_empty(cart, now):
    response = await cart.takeout_load_ids(
        yandex_uid=BASIC_UID, till_dt=_iso_format(now),
    )

    assert response == {'ids': []}


def _iso_format(time):
    return f'{time.isoformat()}+0000'
