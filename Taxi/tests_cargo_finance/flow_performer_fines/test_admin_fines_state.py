import dateutil.parser
import pytest


async def test_new_decision(load_json, get_admin_fines_state, inject_events):
    inject_events()
    expected = load_json('order_fines_state.json')
    expected['new_decision'].pop('operation_token')

    state = await get_admin_fines_state()
    state['new_decision'].pop('operation_token')
    assert state['new_decision'] == expected['new_decision']


async def test_unknown_new_decision(
        get_total_admin_fines_state, inject_events,
):
    inject_events()

    state = await get_total_admin_fines_state()
    assert 'new_decision' not in state


async def _prepare_order_unfinished(ctx):
    ctx.order_proc['status'] = 'assigned'
    ctx.order_archive_mock.set_order_proc(ctx.order_proc)


async def _prepare_order_without_performer(ctx):
    del ctx.order_proc['performer']
    ctx.order_archive_mock.set_order_proc(ctx.order_proc)


async def _prepare_order_with_performer_null_index(ctx):
    ctx.order_proc['performer']['candidate_index'] = None
    ctx.order_archive_mock.set_order_proc(ctx.order_proc)


async def _prepare_too_late_to_rebill(ctx):
    ctx.drop_events()
    now = '2021-05-15T10:00:00+00:00'
    ctx.mocked_time.set(dateutil.parser.parse(now))
    await ctx.taxi_cargo_finance.invalidate_caches()


@pytest.mark.parametrize(
    'prepare, expected_code',
    [
        (_prepare_order_unfinished, 'order_unfinished'),
        (_prepare_order_without_performer, 'order_without_performer'),
        (_prepare_order_with_performer_null_index, 'order_without_performer'),
        (_prepare_too_late_to_rebill, 'too_late_to_rebill'),
    ],
)
async def test_fail_because_of(
        recently,
        inject_events,
        order_archive_mock,
        order_proc,
        taxi_cargo_finance,
        mocked_time,
        get_disable_reason,
        drop_events,
        prepare,
        expected_code,
):
    class Ctx:
        def __init__(self):
            self.order_archive_mock = order_archive_mock
            self.order_proc = order_proc
            self.mocked_time = mocked_time
            self.taxi_cargo_finance = taxi_cargo_finance
            self.drop_events = drop_events

    inject_events()
    await prepare(Ctx())

    disable_reason = await get_disable_reason()
    assert disable_reason['code'] == expected_code


async def test_fail_has_pending_operations(
        recently, inject_events, get_admin_fines_state,
):
    inject_events()
    state = await get_admin_fines_state()
    disable_reason = state['new_decision']['disable_reason']
    assert disable_reason['code'] == 'has_pending_operations'
