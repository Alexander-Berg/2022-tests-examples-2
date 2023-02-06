# pylint: disable=protected-access
import datetime
import typing

import pytest

from replication.sources.postgres import core as postgres

UTC_DT = datetime.datetime(2019, 4, 30, 10, 0)


@pytest.mark.pgsql('example_pg@0', files=['example_pg_shard0.sql'])
async def test_get_cursor_by_bounds(replace_frozen, replication_ctx):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='test_sharded_pg',
        source_types=[postgres.SOURCE_TYPE_POSTGRES],
    )
    source_shard_0 = None
    for rule in rules:
        if rule.source.name == 'test_sharded_pg_shard0':
            source_shard_0 = rule.source
            break
    assert source_shard_0

    docs = await _get_data(source_shard_0)
    assert docs.keys() == {'_id_2_'}
    assert docs['_id_2_']['modified_at'] == UTC_DT
    source_shard_0 = replace_frozen(source_shard_0, {'meta.timezone': 'UTC'})
    docs = await _get_data(source_shard_0)
    assert docs.keys() == {'_id_1_'}
    assert docs['_id_1_']['modified_at'] == UTC_DT


@pytest.mark.pgsql('conditioned', files=['conditioned.sql'])
async def test_conditioned_pg_source(replication_ctx):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='test_conditioned_pg',
        source_types=[postgres.SOURCE_TYPE_POSTGRES],
    )
    assert rules[0].source.name == 'test_conditioned_pg_shard0'
    docs = await _get_data(rules[0].source)
    assert docs.keys() == {'_id_1_'}
    assert docs['_id_1_']['condition_field'] == 1500


@pytest.mark.parametrize(
    'rule_name',
    [
        'basic_source_postgres_raw_replicate_by',
        'basic_source_postgres_sequence',
    ],
)
@pytest.mark.pgsql('sequence', files=['sequence.sql'])
async def test_sequence_pg_source(replication_ctx, rule_name):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name=rule_name, source_types=[postgres.SOURCE_TYPE_POSTGRES],
    )
    rule = rules[0]
    source = rule.source
    assert source.name == '_'.join([rule_name, 'shard0'])
    docs = await _get_data(source, 0, 5)
    assert docs == {
        1: {'id': 1, 'example_value': 1010},
        2: {'id': 2, 'example_value': 2000},
        3: {'id': 3, 'example_value': 1020},
    }
    docs = await _get_data(source, 1, 3, strict=True)
    assert docs == {
        2: {'id': 2, 'example_value': 2000},
        3: {'id': 3, 'example_value': 1020},
    }


@pytest.mark.pgsql('raw_select', files=['raw_select.sql'])
async def test_raw_select_pg_source(replication_ctx):
    rules = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='basic_source_postgres_raw_select',
        source_types=[postgres.SOURCE_TYPE_POSTGRES],
    )
    rule = rules[0]
    source = rule.source
    assert source.name == 'basic_source_postgres_raw_select_shard0'
    docs = await _get_data(source, primary_key='cart_id')
    assert docs == {
        '1': {
            'cart_id': '1',
            'updated': datetime.datetime(2019, 4, 30, 10, 0),
            'created': datetime.datetime(2019, 4, 30, 10, 0),
            'checked_out': True,
            'items': (
                '[{"cart_id":"1","item_id":"1","updated":'
                '"2020-02-20T15:55:01.4183+03:00"}, \n '
                '{"cart_id":"1","item_id":"2","updated":'
                '"2020-02-20T15:55:01.730137+03:00"}]'
            ),
        },
        '2': {
            'cart_id': '2',
            'updated': datetime.datetime(2019, 4, 30, 10, 0),
            'created': datetime.datetime(2019, 4, 30, 10, 0),
            'checked_out': True,
            'items': None,
        },
        '3': {
            'cart_id': '3',
            'updated': datetime.datetime(2019, 4, 30, 10, 0),
            'created': datetime.datetime(2019, 4, 30, 10, 0),
            'checked_out': True,
            'items': (
                '[{"cart_id":"3","item_id":"3","updated":'
                '"2020-02-20T15:55:01.911622+03:00"}]'
            ),
        },
    }


async def _get_data(
        source,
        left_bound: typing.Any = UTC_DT,
        right_bound: typing.Any = UTC_DT + datetime.timedelta(minutes=5),
        strict=False,
        primary_key='id',
):
    if not strict:
        cursor = await source.get_cursor_by_bounds(left_bound, right_bound)
    else:
        cursor = await source._get_cursor_by_bounds(
            left_bound, right_bound, exclude_left=True, sort_ascending=True,
        )
    docs = {}
    async for doc in cursor:
        docs[doc[primary_key]] = doc
    return docs


@pytest.fixture
def test_env_id_setter(test_env_testsuite):
    return test_env_testsuite
