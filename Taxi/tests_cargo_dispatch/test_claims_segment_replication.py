import pytest


def test_happy_path_works(happy_path_state_first_import):
    result = happy_path_state_first_import
    assert result['stats']['new-journal-entries'] == 5


def test_first_request_without_cursor(
        happy_path_state_first_import,
        happy_path_claims_segment_journal_handler,
):
    handler = happy_path_claims_segment_journal_handler
    assert handler.has_calls
    assert handler.times_called == 1

    req_body = handler.next_call()['request'].json
    assert 'cursor' not in req_body


async def test_keep_server_cursor_even_without_entries(
        run_claims_segment_replication, incremented_cursor_handler,
):
    for _ in range(4):
        await run_claims_segment_replication()

    cursors_in_request = []
    while incremented_cursor_handler.has_calls:
        req_body = incremented_cursor_handler.next_call()['request'].json
        cursors_in_request.append(req_body.get('cursor'))

    assert cursors_in_request == [None, '0', '1', '2']


async def test_old_revisions_skipped(
        happy_path_state_first_import,
        obsolete_entry_handler,
        run_claims_segment_replication,
):
    result = await run_claims_segment_replication()
    assert obsolete_entry_handler.times_called == 1
    assert result['stats']['new-journal-entries'] == 1
    assert result['stats']['upserted-segments'] == 0


async def test_new_revision_applied(
        happy_path_state_first_import,
        happy_path_claims_segment_db,
        run_claims_segment_replication,
):
    happy_path_claims_segment_db.cancel_segment_by_user('seg1')
    result = await run_claims_segment_replication()
    assert result['stats']['new-journal-entries'] == 1
    assert result['stats']['upserted-segments'] == 1
    assert result['stats']['inserted-segments'] == 0


async def test_none_of_waybills_updated_if_points_version_doesnt_change(
        happy_path_state_all_waybills_proposed, run_claims_segment_replication,
):
    result = await run_claims_segment_replication()
    assert result['stats']['updated-waybills'] == 0


def test_only_chosen_waybill_updated(state_waybills_updated):
    result = state_waybills_updated
    assert result['stats']['updated-waybills'] == 1


@pytest.mark.now('2020-04-01T10:35:01+0000')
async def test_lag_metric(
        happy_path_state_first_import,
        mocked_entry_time_handler,
        run_claims_segment_replication,
):
    result = await run_claims_segment_replication()
    assert mocked_entry_time_handler.times_called == 1
    assert result['stats']['new-journal-entries'] == 1
    assert result['stats']['oldest-segment-lag-ms'] == 1000


@pytest.fixture(name='incremented_cursor_handler')
def _incremented_cursor_handler(mockserver, make_journal_response):
    cursor_list = []

    @mockserver.json_handler('/cargo-claims/v1/segments/journal')
    def handler(request):
        cursor_list.append(str(len(cursor_list)))
        return make_journal_response(cursor_list[-1], [])

    return handler


@pytest.fixture(name='obsolete_entry_handler')
async def _obsolete_entry_handler(
        mockserver, make_journal_response, happy_path_claims_segment_db,
):
    @mockserver.json_handler('/cargo-claims/v1/segments/journal')
    def handler(request):
        journal = happy_path_claims_segment_db.read_claims_journal()
        entry = journal['entries'][-1].copy()
        entry['revision'] = 0
        return make_journal_response('100', [entry])

    return handler


@pytest.fixture(name='mocked_entry_time_handler')
async def _mocked_entry_time_handler(
        mockserver, make_journal_response, happy_path_claims_segment_db,
):
    @mockserver.json_handler('/cargo-claims/v1/segments/journal')
    def handler(request):
        journal = happy_path_claims_segment_db.read_claims_journal()
        entry = journal['entries'][0].copy()
        entry['created_ts'] = '2020-04-01T10:35:00+0000'
        return make_journal_response('100', [entry])

    return handler


@pytest.fixture(name='make_journal_response')
def _make_journal_response(mockserver):
    def _wrapper(cursor, entries):
        resp_headers = {'X-Polling-Delay-Ms': '0'}
        resp_body = {'cursor': str(cursor), 'entries': entries}
        return mockserver.make_response(headers=resp_headers, json=resp_body)

    return _wrapper


@pytest.fixture(name='state_waybills_updated')
async def _state_waybills_updated(
        happy_path_state_waybills_chosen,
        run_claims_segment_replication,
        happy_path_claims_segment_db,
):
    happy_path_claims_segment_db.set_segment_point_visit_status(
        'seg1', 'p3', 'skipped', is_caused_by_user=True,
    )
    return await run_claims_segment_replication()
