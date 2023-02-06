import datetime

import pytest

from client_order_archive import components as client_order_archive


async def test_order_proc_retrieve(library_context, order_archive_mock):
    doc = {'_id': '1', 'updated': datetime.datetime(2020, 1, 1, 20, 10)}
    order_archive_mock.set_order_proc(doc)

    result = await library_context.client_order_archive.order_proc_retrieve(
        order_id='1', lookup_yt=True,
    )

    assert result == doc


async def test_order_proc_retrieve_404(library_context, order_archive_mock):
    with pytest.raises(client_order_archive.NotFoundError):
        await library_context.client_order_archive.order_proc_retrieve(
            order_id='not_found', lookup_yt=True,
        )


async def test_order_proc_retrieve_by_alias(
        library_context, order_archive_mock,
):
    doc = {
        '_id': '1',
        'updated': datetime.datetime(2020, 1, 1, 20, 10),
        'aliases': [{'id': 'alias1'}],
    }
    order_archive_mock.set_order_proc(doc)

    result = await library_context.client_order_archive.order_proc_retrieve(
        order_id='alias1', lookup_yt=True, by_alias=True,
    )

    assert result == doc


async def test_order_proc_bulk_retrieve(library_context, order_archive_mock):
    doc1 = {'_id': '1', 'updated': datetime.datetime(2020, 1, 1, 20, 10)}
    doc2 = {'_id': '2', 'updated': datetime.datetime(2020, 1, 1, 20, 10)}
    docs = [
        doc1,
        doc2,
        {'_id': '3', 'updated': datetime.datetime(2020, 1, 1, 20, 10)},
    ]
    order_archive_mock.set_order_proc(docs)

    result = (
        await library_context.client_order_archive.order_proc_bulk_retrieve(
            order_ids=['1', '2', '4'], lookup_yt=True,
        )
    )
    result_by_ids = {}
    for doc in result:
        result_by_ids[doc['doc']['_id']] = doc['doc']

    assert result_by_ids == {'1': doc1, '2': doc2}
