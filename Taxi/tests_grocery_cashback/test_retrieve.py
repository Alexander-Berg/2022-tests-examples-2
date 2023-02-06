REWARD_ID1 = 'reward-id-1'
REWARD_ID2 = 'reward-id-2'

REWARD_TYPE = 'tracking_game'

REWARD_AMOUNT = '15'


async def test_basic(grocery_cashback_db, cashback_reward_retrieve):
    order_id = 'order-id'

    for reward_id in (REWARD_ID1, REWARD_ID2):
        grocery_cashback_db.insert_reward(
            order_id=order_id,
            amount=REWARD_AMOUNT,
            reward_type=REWARD_TYPE,
            reward_id=reward_id,
        )

    result = await cashback_reward_retrieve(order_id)

    assert len(result['rewards']) == 2
    assert result['rewards'][0] == _get_reward(reward_id=REWARD_ID1)
    assert result['rewards'][1] == _get_reward(reward_id=REWARD_ID2)


async def test_empty_result(grocery_cashback_db, cashback_reward_retrieve):
    grocery_cashback_db.insert_reward(order_id='order-id-1')

    result = await cashback_reward_retrieve(order_id='order-id-2')

    assert not result['rewards']


def _get_reward(reward_id=REWARD_ID1, reward_type=REWARD_TYPE):
    return {
        'reward_id': reward_id,
        'payload': {'amount': REWARD_AMOUNT, 'reward_type': reward_type},
    }
