import datetime as dt

from aiohttp import web
import pytest

import generated.models.billing_reports as models

from billing.clients import reports


async def test_select_all_docs_limit_is_positive(library_context):
    client = library_context.clients.billing_reports
    with pytest.raises(AssertionError):
        await reports.select_all_docs(
            client,
            external_obj_id='',
            external_event_ref='',
            kind='',
            begin_time=dt.datetime.min,
            end_time=dt.datetime.max,
            page_size=0,
        )


async def test_select_all_docs_paginates(library_context, mockserver):
    doc_count = 5
    doc = models.DocsSelectEntry(
        created=dt.datetime(2020, 1, 1),
        data={},
        doc_id=1,
        event_at=dt.datetime(2020, 1, 1),
        external_event_ref='external_event_ref',
        external_obj_id='external_obj_id',
        kind='kind',
        process_at=dt.datetime(2020, 1, 1),
        service='billing',
        status='complete',
        tags=[],
    )

    @mockserver.json_handler('/billing-reports/v1/docs/select')
    async def _v1_docs_select(request):
        cursor = request.json.get('cursor') or {'offset': 0}
        docs_left = doc_count - cursor['offset']
        docs_to_return = min(docs_left, request.json['limit'])
        return mockserver.make_response(
            json={
                'docs': [doc.serialize()] * docs_to_return,
                'cursor': {'offset': cursor['offset'] + docs_to_return},
            },
        )

    client = library_context.clients.billing_reports
    docs = await reports.select_all_docs(
        client,
        external_obj_id='external_obj_id',
        external_event_ref='external_event_ref',
        kind='kind',
        begin_time=dt.datetime(2021, 1, 1),
        end_time=dt.datetime(2021, 1, 10),
        page_size=2,
    )
    assert [doc.serialize() for doc in docs] == [doc.serialize()] * doc_count


async def test_select_all_docs_secondary_preferred(
        library_context,
        do_mock_billing_reports,
        do_mock_billing_docs,
        load_py_json,
):
    test_data = load_py_json('test_select_all_docs_secondary_preferred.json')
    do_mock_billing_docs()
    do_mock_billing_reports(test_data['existing_docs'])

    client = library_context.clients.billing_reports
    docs = await reports.select_all_docs_secondary_preferred(
        client, **test_data['query'],
    )
    assert [doc.serialize() for doc in docs] == test_data['expected_docs']


async def test_select_all_entries_limit_is_positive(library_context):
    client = library_context.clients.billing_reports
    with pytest.raises(AssertionError):
        await reports.select_all_entries(
            client,
            accounts=[],
            begin_time=dt.datetime.min,
            end_time=dt.datetime.max,
            page_size=0,
        )


async def test_select_all_entries_paginates(library_context, mockserver):
    entry_count = 5
    entry = models.JournalEntry(
        account=models.Account(0, '', '', '', ''),
        amount='0',
        created=dt.datetime(2020, 1, 1),
        entry_id=0,
        event_at=dt.datetime(2020, 1, 1),
    )

    @mockserver.json_handler('/billing-reports/v2/journal/select')
    async def _v2_journal_select(request):
        cursor = request.json.get('cursor') or '0'
        entries_left = entry_count - int(cursor)
        entries_to_return = min(entries_left, request.json['limit'])
        response = {'entries': [entry.serialize()] * entries_to_return}
        if entries_left:
            response['cursor'] = str(int(cursor) + entries_to_return)
        return mockserver.make_response(json=response)

    client = library_context.clients.billing_reports
    entries = await reports.select_all_entries(
        client,
        accounts=[models.JournalSelectRequestAccount('', '', '')],
        begin_time=dt.datetime(2021, 1, 1),
        end_time=dt.datetime(2021, 1, 10),
        page_size=2,
    )
    assert [entry.serialize() for entry in entries] == [
        entry.serialize(),
    ] * entry_count


@pytest.mark.config(BILLING_REPORTS_JOURNAL_BY_ID_CHUNK_LIMIT=1)
async def test_select_all_entries_by_ids(
        library_context, mock_billing_reports,
):
    entry_count = 5
    entry = models.JournalByIdEntry(
        account=models.Account(0, '', '', '', ''),
        amount='0',
        doc_ref='',
        created=dt.datetime(2020, 1, 1),
        entry_id=0,
        event_at=dt.datetime(2020, 1, 1),
    )

    @mock_billing_reports('/v1/journal/by_id')
    def _journal_by_id(request):
        desired_entry_count = len(request.json['entry_ids'])
        response = {'entries': [entry.serialize()] * desired_entry_count}
        return web.json_response(response)

    client = library_context.clients.billing_reports
    config = library_context.config
    entries = await reports.select_all_entries_by_ids(
        config, client, entry_ids=[1] * entry_count,
    )
    assert [entry.serialize() for entry in entries] == [
        entry.serialize(),
    ] * entry_count
    assert _journal_by_id.times_called == 5
