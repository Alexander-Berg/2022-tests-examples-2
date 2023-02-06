import datetime

import bson
import pytest

from replication.foundation import consts

_RULE_NAME = 'basic_source_mongo_timestamp'


@pytest.mark.filldb(test_coll='timestamp')
@pytest.mark.mongodb_collections('test_coll')
async def test_mongo_timestamp_source(replication_ctx, load_py_json):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name=_RULE_NAME, source_types=[consts.SOURCE_TYPE_MONGO],
    )
    rule = rules[0]
    source = rule.source
    assert source.name == _RULE_NAME
    start_dt = source.normalize_stamp(bson.Timestamp(1000000, 1))
    docs = await _get_data(
        source,
        left_bound=start_dt,
        right_bound=start_dt + datetime.timedelta(minutes=5),
    )
    expected_docs_list = load_py_json('expected.json')
    expected_docs = {doc['_id']: doc for doc in expected_docs_list}
    assert docs == expected_docs


async def _get_data(source, left_bound, right_bound):
    cursor = await source.get_cursor_by_bounds(left_bound, right_bound)
    docs = {}
    async for doc in cursor:
        docs[doc['_id']] = doc
    return docs
