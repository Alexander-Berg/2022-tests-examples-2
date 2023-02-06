import datetime

from aiohttp import web
import pytest

from generated.models import billing_docs
from taxi.billing.util import dates

from billing.docs import service

_MOCK_NOW = '2021-01-01T00:00:00.000000+00:00'


async def test_docs_v2_update_returns_updates(
        library_context, mock_v2_docs_update,
):
    request = service.UpdateDocRequest(
        revision=1,
        entry_ids=[1, 2, 3],
        doc_id=6,
        idempotency_key='1',
        status='new',
        data={},
    )
    response = await library_context.docs.update(request)
    assert response == service.DocUpdate(
        status='new', entry_ids=[1, 2, 3], data={}, revision=2,
    )


@pytest.fixture(name='mock_v2_docs_update')
def mock_mock_v2_docs_update(mock_billing_docs, load_json):
    @mock_billing_docs('/v2/docs/update')
    def _v2_docs_update(request):
        return web.json_response(load_json('v2_docs_update_response.json'))

    yield _v2_docs_update


def test_doc_applies_patch(load_py_json):
    test_data = load_py_json('test_doc_applies_patch.json')
    doc = service.Doc(**test_data['doc'])
    patch = service.DocUpdate(**test_data['patch'])
    expected = service.Doc(**test_data['expected_doc'])
    assert doc.apply(patch) == expected


@pytest.mark.now(_MOCK_NOW)
async def test_create_doc(
        load_py_json, library_context, mock_billing_docs, mock_v1_docs_create,
):
    request_data = load_py_json('create_doc_request_data.json')
    expected_data = load_py_json('expected_created_doc.json')

    response = await library_context.docs.create(
        service.CreateDocRequest(**request_data),
    )
    assert response == service.Doc(**expected_data)


@pytest.fixture(name='mock_v1_docs_create')
def mock_mock_v1_docs_create(mock_billing_docs, load_json):
    @mock_billing_docs('/v1/docs/create')
    def _v1_docs_create(request):
        request_json = request.json
        return billing_docs.DocsCreateDocResponse(
            doc_id=1,
            created=datetime.datetime.now(),
            data=request_json['data'],
            external_event_ref=request_json['external_event_ref'],
            external_obj_id=request_json['external_obj_id'],
            kind=request_json['kind'],
            process_at=dates.parse_datetime(request_json['process_at']),
            event_at=dates.parse_datetime(request_json['event_at']),
            service='billing_docs',
            status=request_json['status'],
            tags=request_json['tags'],
        ).serialize()

    yield _v1_docs_create


@pytest.mark.parametrize('test_data_json', ['restore_test_data.json'])
@pytest.mark.now('1991-06-20T10:15:00+03:00')
async def test_restore(
        do_mock_billing_docs,
        do_mock_billing_reports,
        library_context,
        load_json,
        *,
        test_data_json,
):
    test_data = load_json(test_data_json)
    docs = do_mock_billing_docs()
    do_mock_billing_reports(test_data['docs'])
    await library_context.docs.restore(20000, idempotency_key='1')
    assert docs.restored_docs == test_data['expected_restored_docs']


async def test_select_docs_from_secondary(
        do_mock_billing_reports,
        do_mock_billing_docs,
        library_context,
        load_py_json,
):
    do_mock_billing_docs()
    test_data = load_py_json('test_select_docs_from_secondary.json')
    do_mock_billing_reports([test_data['existing_doc']])
    request = service.SelectDocsRequest(**test_data['query'])
    docs = await library_context.docs.select(request, secondary_preferred=True)
    assert len(docs) == 1
    assert docs[0] == service.Doc(**test_data['expected_doc'])


@pytest.mark.config(BILLING_DOCS_REPLICATION_LAG_MS=500)
async def test_get_replication_lag(library_context):
    assert library_context.docs.replication_lag == datetime.timedelta(
        milliseconds=500,
    )
