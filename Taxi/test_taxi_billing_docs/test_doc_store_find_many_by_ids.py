import pytest

from taxi_billing_docs import config as bd_config
from taxi_billing_docs.common import db


@pytest.mark.pgsql(
    'billing_docs@0', files=('meta.sql', 'doc@0.sql', 'event@0.sql'),
)
@pytest.mark.pgsql(
    'billing_docs@1', files=('meta.sql', 'doc@1.sql', 'event@1.sql'),
)
@pytest.mark.parametrize(
    'doc_ids',
    [
        [10000, 30002, 60003, 100003, 50004],
        [20000, 30002, 80003, 90003, 40004],
        # doubles
        [20000, 20000, 30002, 80003, 90003, 40004],
        [20000, 20000, 30002, 80003, 90003, 40004, 40004, 40004],
    ],
)
@pytest.mark.parametrize('fetch_mode', [True, False])
async def test_doc_store_find_many_by_ids_all(
        billing_docs_storage, doc_ids, fetch_mode,
):
    config = bd_config.Config()
    config.BILLING_DOCS_FETCH_BY_ID_SEQUENTIALLY = fetch_mode
    store = db.DocStore(storage=billing_docs_storage, config=config)
    docs = await store.find_many_by_ids(doc_ids=doc_ids, log_extra={})
    doc_ids = set(doc_ids)
    assert len(doc_ids) == len(docs)
    for doc in docs:
        assert doc.doc_id in doc_ids


@pytest.mark.pgsql(
    'billing_docs@0', files=('meta.sql', 'doc@0.sql', 'event@0.sql'),
)
@pytest.mark.pgsql(
    'billing_docs@1', files=('meta.sql', 'doc@1.sql', 'event@1.sql'),
)
@pytest.mark.parametrize(
    'doc_ids, expected_len',
    [
        ([], 0),
        ([10010000, 10060003, 100100003, 10050004], 0),
        ([10010000, 30002, 10060003, 100100003, 10050004], 1),
        ([10010000, 30002, 10060003, 100100003, 50004], 2),
        # double
        ([10010000, 30002, 30002, 10060003, 100100003, 10050004], 1),
        ([10010000, 30002, 10060003, 100100003, 50004, 50004, 130005], 3),
    ],
)
@pytest.mark.parametrize('fetch_mode', [True, False])
async def test_doc_store_find_many_by_ids_some(
        billing_docs_storage, doc_ids, expected_len, fetch_mode,
):
    config = bd_config.Config()
    config.BILLING_DOCS_FETCH_BY_ID_SEQUENTIALLY = fetch_mode
    store = db.DocStore(storage=billing_docs_storage, config=config)
    docs = await store.find_many_by_ids(doc_ids=doc_ids, log_extra={})
    assert expected_len == len(docs)
