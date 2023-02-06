import pytest

from tests_grocery_goals import common
from tests_grocery_goals import models


async def test_basic(taxi_grocery_goals, pgsql):
    reward_sku = models.GoalRewardSku()
    order_id = 'order_id'

    models.insert_goal(
        pgsql,
        goal_id=common.GOAL_ID,
        goal_reward=reward_sku.get_reward_db_info(),
    )

    models.insert_goal_progress(
        pgsql,
        goal_id=common.GOAL_ID,
        progress_status='completed',
        completed_seen=True,
        reward=reward_sku.get_user_reward_db_info(),
        complete_at=common.GOAL_COMPLETE_AT,
    )

    response = await taxi_grocery_goals.post(
        '/internal/v1/goals/v1/reward/reserve',
        json={'skus': [reward_sku.skus[0]], 'order_id': order_id},
        headers={
            'X-Yandex-UID': common.YANDEX_UID,
            'X-YaTaxi-Session': 'taxi:1234',
        },
    )

    assert response.status_code == 200
    progress = models.get_goal_progress(
        pgsql, yandex_uid=common.YANDEX_UID, goal_id=common.GOAL_ID,
    )
    assert progress.reward_reserved_by == order_id

    response = await taxi_grocery_goals.post(
        '/internal/v1/goals/v1/reward/release',
        json={'skus': [reward_sku.skus[0]], 'order_id': order_id},
        headers={
            'X-Yandex-UID': common.YANDEX_UID,
            'X-YaTaxi-Session': 'taxi:1234',
        },
    )

    assert response.status_code == 200
    progress = models.get_goal_progress(
        pgsql, yandex_uid=common.YANDEX_UID, goal_id=common.GOAL_ID,
    )
    assert progress.reward_reserved_by is None


@pytest.mark.parametrize('operation_type', ['reserve', 'release'])
async def test_idempotency(taxi_grocery_goals, operation_type, pgsql):
    reward_sku = models.GoalRewardSku()
    order_id = 'order_id'

    models.insert_goal(
        pgsql,
        goal_id=common.GOAL_ID,
        goal_reward=reward_sku.get_reward_db_info(),
    )

    models.insert_goal_progress(
        pgsql,
        goal_id=common.GOAL_ID,
        progress_status='completed',
        completed_seen=True,
        reward=reward_sku.get_user_reward_db_info(),
        complete_at=common.GOAL_COMPLETE_AT,
        reward_reserved_by=order_id,
    )

    response = await taxi_grocery_goals.post(
        '/internal/v1/goals/v1/reward/' + operation_type,
        json={'skus': [reward_sku.skus[0]], 'order_id': order_id},
        headers={
            'X-Yandex-UID': common.YANDEX_UID,
            'X-YaTaxi-Session': 'taxi:1234',
        },
    )

    assert response.status_code == 200

    response = await taxi_grocery_goals.post(
        '/internal/v1/goals/v1/reward/' + operation_type,
        json={'skus': [reward_sku.skus[0]], 'order_id': order_id},
        headers={
            'X-Yandex-UID': common.YANDEX_UID,
            'X-YaTaxi-Session': 'taxi:1234',
        },
    )

    assert response.status_code == 200


@pytest.mark.parametrize('operation_type', ['reserve', 'release'])
async def test_reserve_user_has_no_such_reward(
        taxi_grocery_goals, pgsql, operation_type,
):
    reward_sku = models.GoalRewardSku()
    order_id = 'order_id'

    response = await taxi_grocery_goals.post(
        '/internal/v1/goals/v1/reward/' + operation_type,
        json={'skus': [reward_sku.skus[0]], 'order_id': order_id},
        headers={
            'X-Yandex-UID': common.YANDEX_UID,
            'X-YaTaxi-Session': 'taxi:1234',
        },
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'user_has_no_such_reward'


@pytest.mark.parametrize('operation_type', ['reserve', 'release'])
async def test_partial_success(taxi_grocery_goals, pgsql, operation_type):
    reward_sku = models.GoalRewardSku()
    order_id = 'order_id'

    models.insert_goal(
        pgsql,
        goal_id=common.GOAL_ID,
        goal_reward=reward_sku.get_reward_db_info(),
    )

    models.insert_goal_progress(
        pgsql,
        goal_id=common.GOAL_ID,
        progress_status='completed',
        completed_seen=True,
        reward=reward_sku.get_user_reward_db_info(),
        complete_at=common.GOAL_COMPLETE_AT,
    )

    response = await taxi_grocery_goals.post(
        '/internal/v1/goals/v1/reward/' + operation_type,
        json={
            'skus': [reward_sku.skus[0], 'unavailable_sku'],
            'order_id': order_id,
        },
        headers={
            'X-Yandex-UID': common.YANDEX_UID,
            'X-YaTaxi-Session': 'taxi:1234',
        },
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'user_has_no_such_reward'
    assert response.json()['failed_skus'] == ['unavailable_sku']
