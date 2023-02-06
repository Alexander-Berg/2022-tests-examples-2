import uuid

from tests_grocery_cart import common

BASIC_HEADERS = common.TAXI_HEADERS.copy()


async def test_takeout_delete(cart):
    anonym_id = 'anonym_id'

    await cart.init(['test_item'], headers=BASIC_HEADERS)

    cart.update_db(
        personal_phone_id='some-personal-phone-id',
        bound_uids=['some-bound_uid'],
        bound_sessions=['some-bound-sessions'],
    )

    fetched_cart = cart.fetch_db()

    assert fetched_cart.user_id != ''
    assert fetched_cart.personal_phone_id is not None
    assert fetched_cart.bound_uids != []
    assert fetched_cart.bound_sessions != []
    assert fetched_cart.session != ''
    assert fetched_cart.yandex_uid != ''
    assert fetched_cart.anonym_id is None

    await cart.takeout_delete(cart_id=cart.cart_id, anonym_id=anonym_id)

    fetched_cart = cart.fetch_db()
    assert fetched_cart.user_id == ''
    assert fetched_cart.personal_phone_id is None
    assert fetched_cart.bound_uids == []
    assert fetched_cart.bound_sessions == []
    assert fetched_cart.session == ''
    assert fetched_cart.yandex_uid == ''
    assert fetched_cart.anonym_id == anonym_id


async def test_not_found(cart):
    cart_id = str(uuid.uuid4())
    anonym_id = 'anonym_id'

    await cart.takeout_delete(
        cart_id=cart_id, anonym_id=anonym_id, status_code=404,
    )
