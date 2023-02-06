import pytest

from tests_grocery_products_feedback import models


YANDEX_UID = 'some_uid'
PRODUCT_ID = 'some_product_id'


@pytest.mark.parametrize(
    'score,comment,response_code',
    [
        (-1, None, 400),
        (0, None, 200),
        (1, 'great milk, awesome chocolate', 200),
        (0, None, 200),
        (6, None, 400),
    ],
)
async def test_basic(
        taxi_grocery_products_feedback, pgsql, score, comment, response_code,
):
    feedback = models.ProductFeedback(
        pgsql=pgsql,
        yandex_uid=YANDEX_UID,
        product_id=PRODUCT_ID,
        score=score,
        comment=comment,
    )

    response = await taxi_grocery_products_feedback.post(
        '/lavka/products/give/feedback',
        headers={'X-Yandex-UID': YANDEX_UID},
        json={
            'idempotency_token': '12345',
            'product_id': PRODUCT_ID,
            'score': score,
            'comment': comment,
        },
    )

    assert response.status_code == response_code

    if response_code == 200:
        feedback.compare_with_db()


async def test_idempotency(taxi_grocery_products_feedback, pgsql):
    feedback = models.ProductFeedback(
        pgsql=pgsql, yandex_uid=YANDEX_UID, product_id=PRODUCT_ID, score=1,
    )

    for _ in range(2):
        response = await taxi_grocery_products_feedback.post(
            '/lavka/products/give/feedback',
            headers={'X-Yandex-UID': YANDEX_UID},
            json={
                'idempotency_token': '12345',
                'product_id': PRODUCT_ID,
                'score': 1,
            },
        )

        assert response.status_code == 200

    feedback.check_entires_count(1)


async def test_no_yandex_uid(taxi_grocery_products_feedback, pgsql):
    response = await taxi_grocery_products_feedback.post(
        '/lavka/products/give/feedback',
        json={
            'idempotency_token': '12345',
            'product_id': PRODUCT_ID,
            'score': 1,
        },
    )

    assert response.status_code == 409
