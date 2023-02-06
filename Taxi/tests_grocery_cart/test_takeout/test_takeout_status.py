import datetime

from tests_grocery_cart import common

BASIC_UID = 'some-uid-1'
ANOTHER_UID = 'some-uid-2'

BASIC_HEADERS = common.TAXI_HEADERS.copy()
ANOTHER_HEADERS = common.TAXI_HEADERS.copy()

BASIC_HEADERS['X-Yandex-UID'] = BASIC_UID
ANOTHER_HEADERS['X-Yandex-UID'] = ANOTHER_UID


async def test_takeout_status(overlord_catalog, cart_factory, cart, now):
    overlord_catalog.add_product(product_id='item_id_1')

    cart_1 = cart_factory(headers={**BASIC_HEADERS})
    cart_2 = cart_factory(headers={**ANOTHER_HEADERS})

    await cart_1.modify(['item_id_1'])
    await cart_2.modify(['item_id_1'])

    cart_1.update_db(created=_iso_format(now - datetime.timedelta(minutes=2)))
    cart_2.update_db(created=_iso_format(now + datetime.timedelta(minutes=2)))

    response = await cart.takeout_status(
        yandex_uids=[BASIC_UID, ANOTHER_UID], till_dt=_iso_format(now),
    )

    assert response['status'] == 'ready_to_delete'

    response = await cart.takeout_status(
        yandex_uids=[ANOTHER_UID], till_dt=_iso_format(now),
    )

    assert response['status'] == 'empty'


async def test_takeout_status_empty(cart, now):
    response = await cart.takeout_status(
        yandex_uids=[BASIC_UID], till_dt=_iso_format(now),
    )

    assert response['status'] == 'empty'


def _iso_format(time):
    return f'{time.isoformat()}+0000'
