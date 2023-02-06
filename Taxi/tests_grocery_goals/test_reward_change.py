import copy

import pytest

from tests_grocery_goals import common
from tests_grocery_goals import models

USER_LOCATION = {'lat': 50, 'lon': 30}


async def _make_reward_change_sku_request(
        taxi_grocery_goals,
        goal_id=common.GOAL_ID,
        location=copy.deepcopy(USER_LOCATION),
):
    return await taxi_grocery_goals.post(
        '/lavka/v1/goals/v1/reward/change/sku',
        json={'goal_id': goal_id, 'location': location},
        headers={
            'X-Yandex-UID': common.YANDEX_UID,
            'X-YaTaxi-Session': 'taxi:1234',
            'X-YaTaxi-User': common.USER_INFO,
        },
    )


@pytest.mark.parametrize(
    'stocks, expected_response',
    [
        (
            [
                {
                    'in_stock': '10',
                    'product_id': 'user_reward_sku',
                    'quantity_limit': '5',
                },
                {
                    'in_stock': '10',
                    'product_id': 'more_sku',
                    'quantity_limit': '5',
                },
            ],
            {},
        ),
        (
            [
                {
                    'in_stock': '10',
                    'product_id': 'more_sku',
                    'quantity_limit': '5',
                },
            ],
            {'sku': 'more_sku'},
        ),
    ],
)
async def test_change_sku(
        taxi_grocery_goals,
        pgsql,
        mockserver,
        overlord_catalog,
        grocery_depots,
        stocks,
        expected_response,
):
    sku_user_reward = 'user_reward_sku'
    sku_reward = 'more_sku'

    sku_image_url_template = 'url/image_1.jpg'

    models.insert_goal(
        pgsql,
        goal_id=common.GOAL_ID,
        goal_reward={
            'type': common.GOAL_REWARD_SKU_TYPE,
            'extra': {'skus': [sku_user_reward, sku_reward]},
        },
    )

    models.insert_goal_progress(
        pgsql,
        goal_id=common.GOAL_ID,
        progress_status='completed',
        reward={'sku': sku_user_reward},
        yandex_uid=common.YANDEX_UID,
    )

    grocery_depots.add_depot(
        legacy_depot_id='legacy_depot_id',
        depot_id='1235123',
        location=USER_LOCATION,
    )

    overlord_catalog.add_product_data(
        product_id=sku_reward,
        title='Product 1',
        image_url_template=sku_image_url_template,
    )

    overlord_catalog.add_product_data(
        product_id=sku_user_reward,
        title='Product 1',
        image_url_template=sku_image_url_template,
    )

    @mockserver.json_handler('/overlord-catalog/internal/v1/catalog/v1/stocks')
    def _mock_stocks(request):
        return {'stocks': stocks}

    response = await _make_reward_change_sku_request(taxi_grocery_goals)

    assert response.status_code == 200
    assert response.json() == expected_response
