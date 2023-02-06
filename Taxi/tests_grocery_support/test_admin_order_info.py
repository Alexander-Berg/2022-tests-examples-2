import pytest

from . import models


@pytest.mark.now(models.NOW)
async def test_get_user_info(taxi_grocery_support, pgsql, now):
    now = now.replace(tzinfo=models.UTC_TZ)
    support_login = 'superSupport'
    order_id = 'order-grocery'
    comment_order = 'Unicorn, be aware of a horn'

    proper_comment = {
        'comment': comment_order,
        'support_login': support_login,
        'timestamp': now.isoformat(),
    }

    request_json = {'order_id': order_id}
    headers = {'X-Yandex-Login': support_login}

    order = models.Order(pgsql, order_id=order_id, comments=[proper_comment])

    order.update_db()

    response = await taxi_grocery_support.post(
        '/v1/api/compensation/get-order-info',
        json=request_json,
        headers=headers,
    )

    assert response.status_code == 200

    assert response.json() == order.json()


async def test_save_without_compensation(taxi_grocery_support):
    support_login = 'superSupport'
    order_id = 'order-grocery'

    request_json = {'order_id': order_id}
    headers = {'X-Yandex-Login': support_login}

    response = await taxi_grocery_support.post(
        '/v1/api/compensation/get-order-info',
        json=request_json,
        headers=headers,
    )

    assert response.status_code == 200


@pytest.mark.now(models.NOW)
async def test_save_order_info(taxi_grocery_support, pgsql, now):
    now = now.replace(tzinfo=models.UTC_TZ)
    support_login = 'superSupport'
    order_id = 'order-grocery'
    comment_order = 'Unicorn, be aware of a horn'

    proper_comment = {
        'comment': comment_order,
        'support_login': support_login,
        'timestamp': now.isoformat(),
    }

    request_json = {'order_id': order_id, 'comment': comment_order}
    headers = {'X-Yandex-Login': support_login}

    order = models.Order(pgsql, order_id=order_id, comments=[proper_comment])

    response = await taxi_grocery_support.post(
        '/v1/api/compensation/save-order-info',
        json=request_json,
        headers=headers,
    )

    assert response.status_code == 200

    order.compare_with_db()


@pytest.mark.parametrize(
    'comment_number, support_login, edited',
    [
        (1, 'superSupport', True),
        (2, 'superSupport', True),
        (1, 'fakeSupport', False),
    ],
)
async def test_correct_order_info_comment(
        taxi_grocery_support, pgsql, comment_number, support_login, edited,
):
    order_id = 'order-grocery'
    order_comments = ['first order comment', 'second order comment']

    proper_comments = [
        {
            'comment': order_comments[0],
            'support_login': 'superSupport',
            'timestamp': models.NOW,
        },
        {
            'comment': order_comments[1],
            'support_login': 'superSupport',
            'timestamp': models.NOT_NOW,
        },
    ]
    new_comment = 'new order comment'

    request_json = {
        'order_id': order_id,
        'comment': new_comment,
        'comment_number': comment_number,
    }
    headers = {'X-Yandex-Login': support_login}

    order = models.Order(pgsql, order_id=order_id, comments=proper_comments)
    order.update_db()

    response = await taxi_grocery_support.post(
        '/v1/api/compensation/save-order-info',
        json=request_json,
        headers=headers,
    )

    assert response.status_code == 200

    if edited:
        order.comments[comment_number - 1]['comment'] = new_comment
    order.compare_with_db()
