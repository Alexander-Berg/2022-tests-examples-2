import asyncio

import dateutil.parser
import pytest


@pytest.mark.config(CORP_BILLING_ORDERS_PROCESS_DOC_INTERVAL_MS=1)
@pytest.mark.config(CORP_BILLING_ORDERS_SYNC_INTERVAL_MS=1)
async def test_sync_disabled_by_default(
        _self_service, _build_orders_with_statuses, _push_orders,
):
    # by default CORP_BILLING_ORDERS_SYNC_ENABLED=false
    # So no call made from period task
    #
    # For tests we start procedure via `call_sync` fixture

    orders, statuses = _build_orders_with_statuses()
    state = _self_service(statuses)
    await _push_orders(orders)
    await asyncio.sleep(0.1)
    assert not state.service.requests


async def test_send_same_orders_as_received(
        _self_service,
        _build_orders_with_statuses,
        _push_orders,
        _do_sync_until_finish,
):
    orders, statuses = _build_orders_with_statuses()
    state = _self_service(statuses)
    dummy_responses = await _push_orders(orders)  # noqa: F841
    await _do_sync_until_finish()

    input_orders = list(map(_replace_with_datetime, orders))
    expected = list(map(_replace_with_datetime, state.service.requests))
    # import asyncio; await asyncio.sleep(50)
    assert input_orders == expected


async def test_send_ignore_finished_flag(
        _self_service, _build_orders_with_statuses, _push_orders, call_sync,
):
    refs_revs_finished_status = [('d1', 1, False, 'pending')]
    orders, statuses = _build_orders_with_statuses(refs_revs_finished_status)
    dummy_state = _self_service(statuses)  # noqa: F841
    dummy_responses = await _push_orders(orders)  # noqa: F841
    for dummy_i in range(3):
        pending_count = await call_sync()
        assert pending_count == 1


async def test_stop_processing_on_finished(
        _self_service, _build_orders_with_statuses, _push_orders, call_sync,
):
    refs_revs_finished_status = [
        ('d1', 1, False, 'failed'),
        ('d2', 1, False, 'complete'),
        ('d3', 1, True, 'failed'),
        ('d4', 1, True, 'complete'),
    ]
    orders, statuses = _build_orders_with_statuses(refs_revs_finished_status)
    state = _self_service(statuses)
    await _push_orders(orders)
    first_pending_count = await call_sync()
    first_requests_count = len(state.service.requests)
    second_pending_count = await call_sync()
    second_requests_count = len(state.service.requests)
    third_pending_count = await call_sync()

    assert first_pending_count == 4
    assert first_requests_count == 0  # first sync just marks as pending
    assert second_pending_count == 0  # no pending left
    assert second_requests_count == 4  # all requests done
    assert third_pending_count == 0  # no new requests


async def test_max_revision_taken(
        _self_service,
        _build_orders_with_statuses,
        _push_orders,
        _do_sync_until_finish,
):
    refs_revs_finished_status = [
        ('d1', 1, True, 'complete'),
        ('d1', 2, True, 'complete'),
        ('d1', 3, True, 'complete'),
    ]
    orders, statuses = _build_orders_with_statuses(refs_revs_finished_status)
    state = _self_service(statuses)
    await _push_orders(orders)
    num_calls = await _do_sync_until_finish()
    requests = state.service.requests

    assert num_calls == 2  # first mark as pending, second sync
    assert len(requests) == 1
    assert requests[0]['topic']['revision'] == 3


async def test_known_revisions_ignored(
        _self_service,
        _build_orders_with_statuses,
        _push_orders,
        _do_sync_until_finish,
):
    orders, statuses = _build_orders_with_statuses()
    state = _self_service(statuses)
    for dummy_i in range(5):
        await _push_orders(orders)  # second, third and so on do nothing
    num_calls = await _do_sync_until_finish()

    assert num_calls == 2
    assert len(state.service.requests) == 1


async def test_lock_even_with_max(
        _self_service, _build_orders_with_statuses, _push_orders, call_sync,
):
    refs_revs_finished_status = [
        ('d1', 1, False, 'pending'),
        ('d1', 2, True, 'complete'),
    ]
    orders, statuses = _build_orders_with_statuses(refs_revs_finished_status)
    state = _self_service(statuses)
    await _push_orders(orders[:1])
    await call_sync()
    await _push_orders(orders[1:])
    pending_count = await call_sync()

    assert pending_count == 1
    processed_revisions = [
        obj['topic']['revision'] for obj in state.service.requests
    ]
    assert len(set(processed_revisions)) == 1
    assert processed_revisions[0] == 1


def _replace_with_datetime(order):
    obj = order.copy()
    obj['event_at'] = dateutil.parser.parse(obj['event_at'])
    return obj
