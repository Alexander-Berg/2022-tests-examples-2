from testsuite.utils import matching

from tests_united_dispatch.plugins import cargo_dispatch_manager

WORKER_NAME = 'segments-reader'
ROUTER_ID = 'united-dispatch'


def make_run_stats(*, journal_events_count=10, run_stq_count=None):
    if run_stq_count is None:
        run_stq_count = journal_events_count

    return {
        'journal-events-count': journal_events_count,
        'segment-reader-stq-count': run_stq_count,
        'cursor-lag': matching.non_negative_float,
    }


async def test_worker_state(
        cargo_dispatch: cargo_dispatch_manager.CargoDispatch,
        create_segment,
        get_worker_state,
        mock_segment_dispatch_journal,
        run_segments_reader,
):
    """
        Check worker state happy path
          - run with empty cursor
          - store cursor to worker_state
          - read cursor from worker_state
    """
    for _ in range(10):
        create_segment()

    stats = await run_segments_reader()

    assert stats == make_run_stats(journal_events_count=10)

    # check first request
    assert mock_segment_dispatch_journal.has_calls
    journal_request = mock_segment_dispatch_journal.next_call()['request'].json

    assert 'cursor' not in journal_request
    assert journal_request['without_duplicates']
    assert journal_request['router_id'] == ROUTER_ID

    # check worker state saved
    cursor = cargo_dispatch.segments.last_cursor
    new_worker_state = get_worker_state(WORKER_NAME)
    assert new_worker_state == {'cursor': cursor}

    # check worker state processed from worker_state
    stats = await run_segments_reader()

    # waybill already created
    assert stats == make_run_stats(journal_events_count=0)

    journal_request = mock_segment_dispatch_journal.next_call()['request'].json
    # check second time journal is processed with stored cursor
    assert journal_request['cursor'] == cursor


async def test_journal_events(
        stq,
        cargo_dispatch: cargo_dispatch_manager.CargoDispatch,
        create_segment,
        run_segments_reader,
):
    """
        Check stq was set for new journal events.
    """
    segment = create_segment()

    # first time proposed
    stats = await run_segments_reader()

    assert stats == make_run_stats(journal_events_count=1)

    # check args
    assert stq.united_dispatch_segment_reader.times_called == 1
    last_call_kwargs = stq.united_dispatch_segment_reader.next_call()['kwargs']
    assert 'created_ts' in last_call_kwargs
    assert last_call_kwargs['segment_id'] == segment.id
    assert last_call_kwargs['segment_revision'] == 1
    assert last_call_kwargs['waybill_building_version'] == 1

    # second time was not proposed
    stats = await run_segments_reader()

    assert stats == make_run_stats(journal_events_count=0)

    # proposed again on new waybill_building_version (pr any other event)
    cargo_dispatch.segments.inc_waybill_building_version(segment.id)
    stats = await run_segments_reader()

    assert stats == make_run_stats(journal_events_count=1)
    assert stq.united_dispatch_segment_reader.times_called == 1
    last_call_kwargs = stq.united_dispatch_segment_reader.next_call()['kwargs']
    assert last_call_kwargs['waybill_building_version'] == 2
