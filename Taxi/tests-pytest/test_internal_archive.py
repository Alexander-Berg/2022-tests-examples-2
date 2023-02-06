import pytest

from taxi import config
from taxi.core import async
from taxi.internal import archive


@pytest.mark.parametrize('func,fetcher,count', [
    (
        archive.get_many_orders,
        'taxi.external.archive.get_many_orders',
        100,
    ),
    (
        archive.get_many_orders,
        'taxi.external.archive.get_many_orders',
        2500,
    ),
    (
        archive.get_many_order_proc_by_ids,
        'taxi.external.archive.get_many_order_proc_by_ids',
        100,
    ),
    (
        archive.get_many_order_proc_by_ids,
        'taxi.external.archive.get_many_order_proc_by_ids',
        2500,
    ),
])
@pytest.inline_callbacks
def test_get_many_orders_procs(patch, func, fetcher, count):
    @patch(fetcher)
    @async.inline_callbacks
    def fetcher_func(ids, lookup_yt, src_tvm_service, log_extra):
        yield async.return_value({
            'items': [
                {
                    'doc': {'_id': i}
                } for i in ids
            ]
        })
    order_ids = ['%08x' % i for i in range(count)]
    result = yield func(order_ids, log_extra=None)
    fetched_ids = sorted(doc['_id'] for doc in result)
    assert order_ids == fetched_ids

    chunks = [i['args'][0] for i in fetcher_func.calls]
    chunk_lens = [len(chunk) for chunk in chunks]

    fetched_ids = set()
    for chunk in chunks:
        fetched_ids.update(chunk)

    chunk_size = yield config.ARCHIVE_API_BULK_FETCH_MAX_SIZE.get()

    def _chunk_lens(count):
        result = []
        while count > 0:
            if count > chunk_size:
                result.append(chunk_size)
            else:
                result.append(count)
            count -= chunk_size
        return result

    expected_chunk_lens = _chunk_lens(count)
    assert chunk_lens == expected_chunk_lens
    assert sorted(fetched_ids) == order_ids


CALL_KWARGS = {
        'lookup_yt': True,
        'log_extra': None,
        'src_tvm_service': None,
    }
CALL_INFO_ORDER_ID = {
    'args': ('archive_id', ),
    'kwargs': CALL_KWARGS,
}
CALL_INFO_ALIAS_ID = {
    'args': ('alias_id', ),
    'kwargs': CALL_KWARGS,
}
CALL_INFO_MANY_IDS = {
    'args': (['archive_id'], ),
    'kwargs': CALL_KWARGS,
}


@pytest.mark.parametrize(
    'skip_db,calls_expected',
    [
        (
            False,
            {
                'get_order_proc_by_id': None,
                'get_order_proc_by_id_or_alias': None,
                'get_order_proc_by_exact_alias': None,
                'get_many_order_proc_by_ids': None,
            }
        ),
        (
            True,
            {
                'get_order_proc_by_id': CALL_INFO_ORDER_ID,
                'get_order_proc_by_id_or_alias': CALL_INFO_ALIAS_ID,
                'get_order_proc_by_exact_alias': CALL_INFO_ALIAS_ID,
                'get_many_order_proc_by_ids': CALL_INFO_MANY_IDS,
            }
        ),
    ]
)
@pytest.inline_callbacks
def test_archive_api_order_proc(patch, skip_db, calls_expected):

    # get_order_proc_by_id
    @patch('taxi.external.archive.get_order_proc_by_id')
    @async.inline_callbacks
    def get_order_proc_by_id(*args, **kwargs):
        yield
        async.return_value({'doc': {'_id': 'archive_id'}})

    proc = yield archive.get_order_proc_by_id('archive_id', skip_db=skip_db)
    call = get_order_proc_by_id.call
    assert call == calls_expected['get_order_proc_by_id']
    assert proc['_id'] == 'archive_id'
    if skip_db:
        assert proc['archive_order']

    # get_order_proc_by_id_or_alias
    @patch('taxi.external.archive.get_order_proc_by_id_or_alias')
    @async.inline_callbacks
    def get_order_proc_by_id_or_alias(alias_id, *args, **kwargs):
        yield
        async.return_value({'doc': {
            '_id': 'archive_id',
            'aliases': [{'id': alias_id}]
        }})

    proc = yield archive.get_order_proc_by_id_or_alias(
        'alias_id', skip_db=skip_db
    )
    call = get_order_proc_by_id_or_alias.call
    assert call == calls_expected['get_order_proc_by_id_or_alias']
    assert proc['_id'] == 'archive_id'

    # get_order_proc_by_exact_alias
    @patch('taxi.external.archive.get_order_proc_by_exact_alias')
    @async.inline_callbacks
    def get_order_proc_by_exact_alias(alias_id='alias_id', *args, **kwargs):
        yield
        async.return_value({'doc': {
            '_id': 'archive_id',
            'aliases': [{'id': alias_id}]
        }})

    proc = yield archive.get_order_proc_by_exact_alias(
        'alias_id', skip_db=skip_db
    )
    call = get_order_proc_by_exact_alias.call
    assert call == calls_expected['get_order_proc_by_exact_alias']
    assert proc['_id'] == 'archive_id'

    # get_many_order_proc_by_ids
    @patch('taxi.external.archive.get_many_order_proc_by_ids')
    @async.inline_callbacks
    def get_many_order_proc_by_ids(*args, **kwargs):
        yield
        async.return_value({'items': [{'doc': {'_id': 'archive_id'}}]})

    procs = yield archive.get_many_order_proc_by_ids(
        ['archive_id'], skip_db=skip_db
    )
    call = get_many_order_proc_by_ids.call
    assert call == calls_expected['get_many_order_proc_by_ids']
    assert procs[0]['_id'] == 'archive_id'


@pytest.mark.parametrize('func,restorer,count', [
    (
        archive.restore_many_subvention_reasons,
        'taxi.external.archive.restore_many_subvention_reasons',
        100,
    ),
    (
        archive.restore_many_subvention_reasons,
        'taxi.external.archive.restore_many_subvention_reasons',
        2500,
    ),
    (
        archive.restore_many_mph_results,
        'taxi.external.archive.restore_many_mph_results',
        100,
    ),
    (
        archive.restore_many_mph_results,
        'taxi.external.archive.restore_many_mph_results',
        2500,
    ),
])
@pytest.inline_callbacks
def test_restore_many_docs_success(patch, func, restorer, count):
    @patch(restorer)
    @async.inline_callbacks
    def restorer_func(ids, update, src_tvm_service, log_extra):
        yield async.return_value([
            {
                'id': i,
                'status': 'restored',
            } for i in ids
        ])
    order_ids = ['%08x' % i for i in range(count)]
    failed_ids = yield func(order_ids, log_extra=None)
    assert len(failed_ids) == 0


@pytest.mark.parametrize('func,restorer,count', [
    (
        archive.restore_many_subvention_reasons,
        'taxi.external.archive.restore_many_subvention_reasons',
        100,
    ),
    (
        archive.restore_many_subvention_reasons,
        'taxi.external.archive.restore_many_subvention_reasons',
        2500,
    ),
    (
        archive.restore_many_mph_results,
        'taxi.external.archive.restore_many_mph_results',
        100,
    ),
    (
        archive.restore_many_mph_results,
        'taxi.external.archive.restore_many_mph_results',
        2500,
    ),
])
@pytest.inline_callbacks
def test_restore_many_docs_fail(patch, func, restorer, count):
    @patch(restorer)
    @async.inline_callbacks
    def restorer_func(ids, update, src_tvm_service, log_extra):
        yield async.return_value([
            {
                'id': i,
                'status': 'not_found',
            } for i in ids
        ])
    order_ids = ['%08x' % i for i in range(count)]
    failed_ids = yield func(order_ids, log_extra=None)
    assert order_ids == failed_ids

    chunks = [i['args'][0] for i in restorer_func.calls]
    chunk_lens = [len(chunk) for chunk in chunks]

    failed_ids = set()
    for chunk in chunks:
        failed_ids.update(chunk)

    chunk_size = yield config.ARCHIVE_API_BULK_RESTORE_MAX_SIZE.get()

    def _chunk_lens(count):
        result = []
        while count > 0:
            if count > chunk_size:
                result.append(chunk_size)
            else:
                result.append(count)
            count -= chunk_size
        return result

    expected_chunk_lens = _chunk_lens(count)
    assert chunk_lens == expected_chunk_lens
    assert sorted(failed_ids) == order_ids
