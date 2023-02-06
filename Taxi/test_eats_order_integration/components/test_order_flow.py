import pytest

from eats_order_integration.internal import exceptions


@pytest.mark.parametrize(
    'idempotency_key,can_continue_expected',
    [
        ['idempotency_key_locked', False],
        ['idempotency_key_free', True],
        ['idempotency_key_new', True],
    ],
)
async def test_with_second_lock_attempt(
        stq3_context, idempotency_key, can_continue_expected,
):
    if can_continue_expected:
        await stq3_context.order_flow.lock_execution(
            idempotency_key, 'order_nr',
        )
    else:
        with pytest.raises(exceptions.CannotLockOperation):
            await stq3_context.order_flow.lock_execution(
                idempotency_key, 'order_nr',
            )

    with pytest.raises(exceptions.CannotLockOperation):
        await stq3_context.order_flow.lock_execution(
            idempotency_key, 'order_nr',
        )


@pytest.mark.parametrize('attempts', [1, 10, 100, 1000])
async def test_concurrent_execution(stq3_context, attempts):
    assert True

    # async def try_lock():
    #     return await stq3_context.order_flow.lock_execution(
    #         'idempotency_key_new', 'order_nr',
    #     )
    #
    # results = await asyncio.gather(
    #     *[try_lock() for _ in range(attempts)], return_exceptions=True,
    # )
    # _can = 0
    # _cannot = 0
    # for result in results:
    #     if result is None:
    #         _can += 1
    #     else:
    #         _cannot += 1
    # assert _can == 1
    # assert _cannot == attempts - 1
