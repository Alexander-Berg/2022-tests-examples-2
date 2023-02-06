import pytest

from . import consts
from . import helpers


def compensation_id(reward_id):
    return f'{consts.TRACKING_GAME_COMPENSATION_ID}_{reward_id}'


@pytest.fixture(name='base_create_reward')
async def _base_create_reward(
        grocery_cashback_reward, passport, transactions, grocery_orders,
):
    async def _do(amount, order_status='closed', flow_version=None):
        result = await grocery_cashback_reward(amount=amount)

        passport.set_has_plus(has_plus=True)
        grocery_orders.order['status'] = order_status

        if flow_version is not None:
            grocery_orders.order['grocery_flow_version'] = flow_version
        return result

    return _do


@pytest.fixture(name='create_reward')
async def _create_reward(base_create_reward, run_stq_cashback_reward):
    async def _do(amount, order_status='closed'):
        result = await base_create_reward(
            amount=amount, order_status=order_status,
        )
        await run_stq_cashback_reward(order_id=consts.ORDER_ID)
        return result

    return _do


async def test_save_compensation_pg(grocery_cashback_db, create_reward):
    amount = '10'
    result = await create_reward(amount)

    reward_id = result['reward_id']

    compensation = grocery_cashback_db.get_compensation(reward_id)

    assert compensation.order_id == consts.ORDER_ID
    assert compensation.payload == helpers.create_other_payload(amount)
    assert compensation.compensation_type == 'tracking_game'


async def test_put_cashback_stq(check_cashback_stq_event, create_reward):
    amount = '10'
    result = await create_reward(amount)

    reward_id = result['reward_id']
    stq_event_id = f'{consts.TRACKING_GAME_SERVICE}_{reward_id}'
    check_cashback_stq_event(
        times_called=1,
        stq_event_id=stq_event_id,
        order_id=helpers.make_invoice_id(reward_id),
        service=consts.TRACKING_GAME_SERVICE,
    )


@pytest.mark.parametrize(
    'status, universal_times_called, reward_times_called',
    [('closed', 1, 0), ('canceled', 0, 0), ('assembling', 0, 1)],
)
async def test_not_closed_order(
        check_cashback_stq_event,
        check_cashback_reward_stq_event,
        create_reward,
        grocery_orders,
        passport,
        run_stq_cashback_reward,
        status,
        universal_times_called,
        reward_times_called,
):
    if universal_times_called == 0:
        grocery_orders.order['status'] = status
        await run_stq_cashback_reward(order_id=consts.ORDER_ID)
    else:
        await create_reward(amount='10', order_status=status)

    check_cashback_stq_event(times_called=universal_times_called)
    check_cashback_reward_stq_event(times_called=reward_times_called)


@pytest.mark.parametrize(
    'enabled, flow_version, times_called',
    [
        (True, consts.BASIC_FLOW_VERSION, 1),
        (True, consts.TRISTERO_FLOW_VERSION, 0),
        (False, consts.BASIC_FLOW_VERSION, 0),
    ],
)
async def test_disabled_by_config(
        taxi_grocery_cashback,
        check_cashback_stq_event,
        grocery_cashback_configs,
        base_create_reward,
        run_stq_cashback_reward,
        enabled,
        flow_version,
        times_called,
):
    await base_create_reward(amount='10', flow_version=flow_version)

    grocery_cashback_configs.tracking_game_reward_enabled(enabled)
    await taxi_grocery_cashback.invalidate_caches()

    await run_stq_cashback_reward(order_id=consts.ORDER_ID)
    check_cashback_stq_event(times_called=times_called)


@pytest.mark.parametrize(
    'status, times_called',
    [('closed', 0), ('canceled', 0), ('pending_cancel', 0), ('assembling', 1)],
)
async def test_postponed(
        check_cashback_reward_stq_event,
        create_reward,
        run_stq_cashback_reward,
        status,
        times_called,
):
    await create_reward(amount='10', order_status=status)

    check_cashback_reward_stq_event(times_called=times_called)
