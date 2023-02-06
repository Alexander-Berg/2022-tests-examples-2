from tests_grocery_goals import common


async def test_basic(taxi_grocery_goals):
    response = await taxi_grocery_goals.post(
        '/internal/v1/goals/v1/check/sku-rewards',
        json={'skus': ['sku_id_1']},
        headers={
            'X-Yandex-UID': common.YANDEX_UID,
            'X-YaTaxi-Session': 'taxi:1234',
            'X-YaTaxi-User': common.USER_INFO,
        },
    )

    assert response.status_code == 200
    assert response.json()['available']
