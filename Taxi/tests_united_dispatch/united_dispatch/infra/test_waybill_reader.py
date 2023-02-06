# pylint: disable=import-error
from testsuite.utils import matching

WORKER_NAME = 'waybill-reader'
ROUTER_ID = 'united-dispatch'


def make_run_stats(*, journal_events_count, stq_runs_count=None):
    if stq_runs_count is None:
        stq_runs_count = journal_events_count

    return {
        'journal-events-count': journal_events_count,
        'stq-runs-count': stq_runs_count,
        'cursor-lag': matching.non_negative_float,
    }


async def test_happy_path(
        create_segment, state_waybill_proposed, run_waybill_reader, stq,
):
    """
        Check waybill journal event processed.

        - event was fetched from journal
        - stq was set
    """
    create_segment(crutches={'force_crutch_builder': True})

    await state_waybill_proposed()

    stats = await run_waybill_reader(only_journal=True)

    assert stats == make_run_stats(journal_events_count=1)
    assert stq.united_dispatch_waybill_reader.times_called == 1


async def test_cursor_stored(
        create_segment,
        state_waybill_proposed,
        run_waybill_reader,
        mock_waybill_dispatch_journal,
        get_worker_state,
        cargo_dispatch,
):
    """
        Check worker state processed:
            - started with empty cursor
            - fetched cursor from journal
            - cursor stored
            - started with new cursor
    """
    create_segment(crutches={'force_crutch_builder': True})

    await state_waybill_proposed()

    stats = await run_waybill_reader(only_journal=True)

    assert stats == make_run_stats(journal_events_count=1)

    # check first request
    assert mock_waybill_dispatch_journal.has_calls
    journal_request = mock_waybill_dispatch_journal.next_call()['request'].json

    assert 'cursor' not in journal_request
    assert journal_request['without_duplicates']
    assert journal_request['router_id'] == ROUTER_ID

    # check worker state saved
    cursor = cargo_dispatch.waybills.last_cursor
    new_worker_state = get_worker_state(WORKER_NAME)
    assert new_worker_state == {'cursor': cursor}

    # check worker state processed from worker_state
    stats = await run_waybill_reader(only_journal=True)

    # waybill already created
    assert stats == make_run_stats(journal_events_count=0)

    # check second time journal is processed with stored cursor
    journal_request = mock_waybill_dispatch_journal.next_call()['request'].json
    assert journal_request['cursor'] == cursor
