# pylint: disable=protected-access
import datetime
import decimal
import uuid

import pytest

from replication_core.raw_types import classes as raw_classes
from replication_core.raw_types import common as common_hooks

from replication.common import queue_mongo
from replication.common import source_stamp
from replication.common.queue_mongo import indexes as queue_mongo_indexes
from replication.foundation import consts
from replication.tools import main

NOW = datetime.datetime(2019, 1, 25, 0, 10)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'data, serializer, indexes,' 'base_stamp,' 'expected',
    [
        (
            {},
            None,
            None,
            None,
            {
                '$currentDate': {'updated': True},
                '$set': {'data': {}},
                '$setOnInsert': {'created': NOW},
                '$inc': {'v': 1},
                '$unset': {'unit': True, 'bs': True},
            },
        ),
        (
            {},
            None,
            {},
            None,
            {
                '$currentDate': {'updated': True},
                '$set': {'data': {}},
                '$setOnInsert': {'created': NOW},
                '$inc': {'v': 1},
                '$unset': {'indexes': True, 'unit': True, 'bs': True},
            },
        ),
        (
            {},
            None,
            {'foo': 123, 'bar': {'key': 456}},
            None,
            {
                '$currentDate': {'updated': True},
                '$set': {
                    'data': {},
                    'indexes': {'foo': 123, 'bar': {'key': 456}},
                },
                '$setOnInsert': {'created': NOW},
                '$inc': {'v': 1},
                '$unset': {'unit': True, 'bs': True},
            },
        ),
        (
            {
                'foo': 1,
                'bar': decimal.Decimal('11'),
                'date_value': datetime.date(200, 2, 25),
            },
            raw_classes.JsonSerializer(
                hooks=[common_hooks.DateHook(), common_hooks.DecimalHook()],
            ),
            None,
            None,
            {
                '$currentDate': {'updated': True},
                '$set': {
                    'data': (
                        '{"bar": {"$a": {"raw_type": "decimal"}, '
                        '"$v": "11"}, "date_value": {"$a": '
                        '{"raw_type": "date"}, "$v": '
                        '"0200-02-25"}, "foo": 1}'
                    ),
                },
                '$setOnInsert': {'created': NOW},
                '$inc': {'v': 1},
                '$unset': {'unit': True, 'bs': True},
            },
        ),
        (
            {
                'foo': datetime.date(2020, 2, 25),
                'bar': datetime.timedelta(hours=2, microseconds=2021),
            },
            raw_classes.JsonSerializer(
                hooks=[common_hooks.DateHook(), common_hooks.TimedeltaHook()],
            ),
            None,
            None,
            {
                '$currentDate': {'updated': True},
                '$set': {
                    'data': (
                        '{"bar": {"$a": {"raw_attrs": {"microseconds"'
                        ': 2021, "seconds": 7200}, "raw_type": '
                        '"timedelta"}, "$v": 7200}, "foo": '
                        '{"$a": {"raw_type": "date"}, "$v": "2020-02-25"}}'
                    ),
                },
                '$setOnInsert': {'created': NOW},
                '$inc': {'v': 1},
                '$unset': {'unit': True, 'bs': True},
            },
        ),
        (
            {},
            None,
            None,
            source_stamp.StampObject(
                source_unit_name='unit1', raw_base_current_stamp=123,
            ),
            {
                '$currentDate': {'updated': True},
                '$set': {'data': {}, 'unit': 'unit1', 'bs': 123},
                '$setOnInsert': {'created': NOW},
                '$inc': {'v': 1},
            },
        ),
    ],
)
def test_get_insertion_update(
        monkeypatch, data, serializer, indexes, base_stamp, expected,
):
    class FakeUuid:
        hex = '_id_'

    monkeypatch.setattr(uuid, 'uuid4', FakeUuid)
    update = queue_mongo.get_insertion_update(
        data, indexes, serializer=serializer, base_stamp=base_stamp,
    )
    assert update == expected, 'Fail at get insertion update'


@pytest.mark.parametrize(
    'doc,expected',
    [
        ({'data': {}}, {'data': {}}),
        ({'data': {'foo': '1'}}, {'data': {'foo': '1'}}),
        ({'data': {'foo': '0200-02-10'}}, {'data': {'foo': '0200-02-10'}}),
    ],
)
def test_prepare_data_from_queue(doc, expected):
    doc = queue_mongo.prepare_data_from_queue(doc)
    assert doc == expected, 'Fail at prepare from queue'


@pytest.mark.parametrize(
    'rule_name, default_indexes, custom_indexes',
    [
        (
            'test_rule',
            {'_id', queue_mongo.UPDATED_FIELD},
            {
                '_id',
                queue_mongo.UPDATED_FIELD,
                'indexes.foo.bar',
                'indexes.value_1',
            },
        ),
        (
            'test_initialize_columns',
            {'_id', queue_mongo.UPDATED_FIELD},
            {'_id', queue_mongo.UPDATED_FIELD},
        ),
        (
            'basic_source_postgres_sequence',
            {'_id', queue_mongo.UPDATED_FIELD},
            {'_id', queue_mongo.UPDATED_FIELD},
        ),
        (
            'basic_source_postgres_strict_sequence',
            {'_id', queue_mongo.UPDATED_FIELD, queue_mongo.SEQUENCE_FIELD},
            {'_id', queue_mongo.UPDATED_FIELD, queue_mongo.SEQUENCE_FIELD},
        ),
    ],
)
async def test_has_staging_indexes(
        replication_ctx, rule_name, default_indexes, custom_indexes,
):
    rules_storage = replication_ctx.rule_keeper.rules_storage
    rule = rules_storage.get_rules_list(
        rule_name=rule_name, source_types=[consts.SOURCE_TYPE_QUEUE_MONGO],
    )[0]
    queue_mongo_shard = rule.source.meta.dependencies.queue_mongo_shard
    collection = queue_mongo_shard.primary
    await collection.drop_indexes()
    await queue_mongo_indexes.ensure_indexes(
        replication_ctx.rule_keeper, rule_name=rule_name,
    )

    indexes = await queue_mongo_indexes._get_ensured_indexes(collection)
    assert indexes == default_indexes

    await main.run(
        ['queue_mongo_indexes', '--rules', rule_name, '--sleep-time', 0],
    )
    indexes = await queue_mongo_indexes._get_ensured_indexes(collection)
    assert indexes == custom_indexes
