import pytest

YANDEX_UID = '1234567'
ORDER_ID = 'id_0'


@pytest.mark.parametrize(
    'push_type', ['order_being_late', 'order_under_the_door'],
)
async def test_basic(taxi_grocery_alice_gateway, mockserver, push_type):
    response = await taxi_grocery_alice_gateway.post(
        '/internal/v1/notifications/v1/order-notification',
        json={
            'yandex_uid': YANDEX_UID,
            'order_id': ORDER_ID,
            'push_type': push_type,
        },
    )

    assert response.status_code == 200
