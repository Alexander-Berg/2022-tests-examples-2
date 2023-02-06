import pytest


@pytest.mark.parametrize(
    ['order_id', 'expected_result'],
    [
        (
            'order2',
            {
                'client': {'id': 'client1', 'name': 'client1'},
                'user': {
                    'is_active': False,
                    'no_specific_limit': True,
                    'spent': 0,
                    'cost_center': '123',
                    'is_cabinet_only': False,
                    'classes': ['vip', 'business', 'comfortplus', 'econom'],
                },
            },
        ),
        (
            'order1',
            {
                'client': {'id': 'client1', 'name': 'client1'},
                'user': {
                    'is_active': True,
                    'limit': 5000,
                    'no_specific_limit': False,
                    'spent': 0,
                    'is_cabinet_only': False,
                    'classes': ['econom', 'vip'],
                },
            },
        ),
        (
            'order3',
            {
                'client': {'id': 'client1', 'name': 'client1'},
                'user': {
                    'is_active': True,
                    'limit': 0,
                    'no_specific_limit': False,
                    'spent': 0,
                    'is_cabinet_only': True,
                    'classes': ['econom', 'business', 'vip'],
                },
            },
        ),
    ],
)
@pytest.mark.config(
    CORP_DEFAULT_CATEGORIES={'rus': ['econom', 'business', 'vip']},
)
async def test_single_get(taxi_corp_admin_client, order_id, expected_result):
    response = await taxi_corp_admin_client.get(
        '/v1/orders/{}'.format(order_id),
    )

    assert response.status == 200
    assert await response.json() == expected_result


@pytest.mark.parametrize(
    ['order_id', 'response_code'], [('No such order id', 404)],
)
async def test_single_get_fail(
        taxi_corp_admin_client, order_id, response_code,
):
    response = await taxi_corp_admin_client.get(
        '/v1/orders/{}'.format(order_id),
    )
    response_json = await response.json()
    assert response.status == response_code, response_json
