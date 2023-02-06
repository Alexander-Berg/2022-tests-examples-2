import pytest

from tests_grocery_order_log import models


ANONYM_ID = 'anonym_id'


@pytest.fixture(name='internal_delete')
def _internal_delete(taxi_grocery_order_log):
    async def _inner(
            order_id: str, anonym_id: str = ANONYM_ID, status_code=200,
    ):
        response = await taxi_grocery_order_log.post(
            '/internal/orders/v1/takeout/delete',
            json={'order_id': order_id, 'anonym_id': anonym_id},
        )

        assert response.status_code == status_code
        return response.json()

    return _inner


async def test_basic(internal_delete, pgsql, grocery_cold_storage):
    order_id = 'order_id'
    anonym_id = ANONYM_ID

    order_log = models.OrderLog(
        pgsql=pgsql,
        order_id=order_id,
        order_source='lavka',
        yandex_uid='yandex_uid',
        eats_user_id='eats_user_id',
        appmetrica_device_id='appmetrica_device_id',
    )
    order_log.update_db()

    order_log_index = models.OrderLogIndex(
        pgsql,
        order_id=order_id,
        yandex_uid='yandex_uid',
        eats_user_id='eats_user_id',
        personal_phone_id='personal_phone_id',
        personal_email_id='personal_email_id',
    )
    order_log_index.update_db()

    await internal_delete(order_id=order_id, anonym_id=anonym_id)

    order_log.update()
    assert order_log.anonym_id == anonym_id
    assert order_log.yandex_uid is None
    assert order_log.eats_user_id is None
    assert order_log.appmetrica_device_id is None

    order_log_index.update()
    assert order_log_index.yandex_uid is None
    assert order_log_index.eats_user_id is None
    assert order_log_index.personal_phone_id is None
    assert order_log_index.personal_email_id is None


async def test_404(internal_delete, grocery_cold_storage):
    await internal_delete(order_id='order_id', status_code=404)
