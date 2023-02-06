import decimal
import uuid

from . import consts
from . import headers
from . import models


async def test_response(grocery_cashback_reward, grocery_orders):
    amount = '10'

    response = await grocery_cashback_reward(amount=amount)

    assert response['amount'] == amount
    assert 'reward_id' in response


async def test_pg(
        grocery_cashback_reward, grocery_orders, grocery_cashback_db,
):
    amount = '10'
    response = await grocery_cashback_reward(amount=amount)
    reward_id = response['reward_id']

    rewards_pg = grocery_cashback_db.get_rewards(order_id=consts.ORDER_ID)

    assert rewards_pg == [
        models.Reward(
            order_id=consts.ORDER_ID,
            reward_id=reward_id,
            yandex_uid=headers.YANDEX_UID,
            type='tracking_game',
            amount=decimal.Decimal(amount),
        ),
    ]


async def test_idempotency(
        grocery_cashback_reward, grocery_orders, grocery_cashback_db,
):
    amount = '10'
    response = await grocery_cashback_reward(amount=amount)
    first_reward_id = response['reward_id']

    rewards_pg = grocery_cashback_db.get_rewards(order_id=consts.ORDER_ID)
    assert len(rewards_pg) == 1
    assert rewards_pg[0].reward_id == first_reward_id

    response = await grocery_cashback_reward(amount=amount)
    second_reward_id = response['reward_id']

    assert first_reward_id == second_reward_id

    rewards_pg = grocery_cashback_db.get_rewards(order_id=consts.ORDER_ID)
    assert len(rewards_pg) == 1
    assert rewards_pg[0].reward_id == first_reward_id


async def test_override_amount(
        grocery_cashback_reward, grocery_orders, grocery_cashback_db,
):
    reward_id = None
    for amount in ('10', '11', '12'):
        response = await grocery_cashback_reward(amount=amount)
        assert response['amount'] == amount

        if reward_id is None:
            reward_id = response['reward_id']

        assert reward_id == response['reward_id']

        rewards_pg = grocery_cashback_db.get_rewards(order_id=consts.ORDER_ID)
        assert len(rewards_pg) == 1
        assert rewards_pg[0].amount == decimal.Decimal(amount)


async def test_too_big_amount(
        grocery_cashback_reward, grocery_orders, grocery_cashback_configs,
):
    config_amount = 10
    request_amount = 20

    assert config_amount < request_amount

    grocery_cashback_configs.tracking_game_reward_params(
        max_amount=config_amount,
    )

    response = await grocery_cashback_reward(
        amount=str(request_amount), status_code=400,
    )
    assert response['code'] == 'not_allowed'


async def test_order_not_found(
        grocery_cashback_reward, grocery_orders, grocery_cashback_configs,
):
    amount = '10'

    response = await grocery_cashback_reward(
        order_id=str(uuid.uuid4()), amount=amount, status_code=404,
    )

    assert response['code'] == 'order_not_found'
