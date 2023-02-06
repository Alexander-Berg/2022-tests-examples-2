import datetime
import operator

import pytest

from replication.common import queue_mongo
from replication.foundation import consts

DOCS_COUNT = 3
NOW = datetime.datetime(2018, 11, 6, 12, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize('unset', [False, True])
@pytest.mark.parametrize('race', [False, True])
@pytest.mark.parametrize('empty', [False, True])
async def test_confirm(replication_ctx, unset, race, empty):
    source = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='test_rule', source_types=[consts.SOURCE_TYPE_QUEUE_MONGO],
    )[0].source

    docs_before = await _get_docs(replication_ctx)
    if race:
        to_confirm = []
        for doc in docs_before:
            if doc['_id'] == 'confirmed':
                doc = doc.copy()
                doc.pop(queue_mongo.CONFIRMATIONS_FIELD)
            to_confirm.append(doc)
    else:
        to_confirm = docs_before

    await source.confirm(
        to_confirm,
        target_names={'yt-test_rule_bson-arni', 'yt-test_rule_bson-hahn'}
        if not empty
        else set(),
        unset=unset,
    )

    docs_after = await _get_docs(replication_ctx)

    assert len(docs_before) == len(docs_after) == DOCS_COUNT
    for doc_before, doc_after in zip(docs_before, docs_after):
        assert doc_before['_id'] == doc_after['_id']

        version = doc_before[queue_mongo.DOC_VERSION_FIELD]
        expected_doc = doc_before.copy()
        if unset or empty:
            if doc_before['_id'] == 'confirmed' and not empty:
                expected_doc[queue_mongo.CONFIRMATIONS_FIELD] = {}
        else:
            expected_doc[queue_mongo.CONFIRMATIONS_FIELD] = {
                '9': {queue_mongo.DOC_VERSION_FIELD: version},
                'A': {queue_mongo.DOC_VERSION_FIELD: version},
            }

        doc_after = doc_after.copy()

        if not empty:
            assert 'targets_updated' in doc_after
            doc_after.pop('targets_updated')

        assert doc_after == expected_doc


async def _get_docs(replication_ctx):
    staging_db = replication_ctx.rule_keeper.staging_db
    collection = staging_db.get_queue_mongo_shard('test_rule').primary
    docs = await collection.find().to_list(None)
    assert len(docs) == DOCS_COUNT
    return sorted(docs, key=operator.itemgetter('_id'))
