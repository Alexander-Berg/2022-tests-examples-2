from tests_grocery_order_log import models


async def test_basic(taxi_grocery_order_log, pgsql):
    order_id = '123456-123456'
    yandex_uid = '10101010'
    appmetrica_device_id = 'some-appmetrica'

    order_log = models.OrderLog(
        pgsql=pgsql,
        order_id=order_id,
        yandex_uid=yandex_uid,
        appmetrica_device_id=appmetrica_device_id,
    )
    order_log.update_db()

    response = await taxi_grocery_order_log.post(
        '/internal/v1/order-log/v1/order-by-id',
        headers={
            'Accept-Language': 'ru-RU',
            'X-Request-Application': 'app_brand=yataxi',
        },
        json={'order_id': order_id},
    )

    assert response.status_code == 200
    assert response.json() == {
        'order_id': order_id,
        'yandex_uid': yandex_uid,
        'appmetrica_device_id': appmetrica_device_id,
    }


async def test_not_found(taxi_grocery_order_log, grocery_cold_storage, pgsql):
    order_id = '123456-123456'
    other_order_id = '123456-101010'

    order_log = models.OrderLog(
        pgsql=pgsql, order_id=order_id, yandex_uid='10101010',
    )
    order_log.update_db()

    response = await taxi_grocery_order_log.post(
        '/internal/v1/order-log/v1/order-by-id',
        headers={
            'Accept-Language': 'ru-RU',
            'X-Request-Application': 'app_brand=yataxi',
        },
        json={'order_id': other_order_id},
    )

    assert response.status_code == 404
