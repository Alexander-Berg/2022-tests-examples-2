import pytest

from tests_grocery_order_log import models


@pytest.mark.now(models.NOW)
@pytest.mark.parametrize(
    'order_ids, short_order_ids, request_id, found_id',
    [
        (
            ['order_id_1', 'order_id_2'],
            ['short_order_id', 'short_order_id'],
            'short_order_id',
            None,
        ),
        (
            ['order_id_1', 'order_id_2'],
            ['short_order_id_1', 'short_order_id_2'],
            'short_order_id_1',
            None,
        ),
        (
            ['order_id_1', 'order_id_2'],
            ['short_order_id', 'short_order_id'],
            'cant find',
            None,
        ),
        (
            ['order_id_1', 'order_id_2', 'order_id_3'],
            [
                'test_order_id-1111',
                'test_order_id-1234',
                '123412341234-grocery',
            ],
            '%-1234',
            'order_id_2',
        ),
    ],
)
async def test_basic(
        taxi_grocery_order_log,
        pgsql,
        order_ids,
        short_order_ids,
        request_id,
        found_id,
):
    indexes = list()
    for (order_id, short_order_id) in zip(order_ids, short_order_ids):
        indexes.append(
            models.OrderLogIndex(
                pgsql, order_id=order_id, short_order_id=short_order_id,
            ),
        )
        indexes[-1].update_db()

    response = await taxi_grocery_order_log.post(
        '/internal/orders/v1/get-order-ids',
        headers={
            'Accept-Language': 'ru-RU',
            'X-Request-Application': 'app_brand=yataxi',
        },
        json={
            'short_order_id': request_id,
            'expiration_time': 24,
            'max_order_ids': 10,
        },
    )

    assert response.status_code == 200

    correct_answer = list()

    for (order_id, short_order_id) in zip(order_ids, short_order_ids):
        if request_id == short_order_id:
            correct_answer.append(order_id)

    if found_id is not None:
        correct_answer.append(found_id)

    assert response.json()['order_ids'] == correct_answer
