# pylint: disable=protected-access
import traceback
import typing

import pytest

from taxi.util import performance

from replication import asyncpool
from replication.foundation import consts
from replication.foundation.mappers import base
from replication.foundation.mappers import identifier
from replication.replication.core import classes as core_classes
from replication.replication.core import consts as replication_consts
from replication.replication.core import mapping


class DummyTarget(typing.NamedTuple):
    name: str
    mapper: typing.Any


class DummyUnit(typing.NamedTuple):
    target: DummyTarget


MAPPER_NAME = identifier.MapperIdentifier(
    rule_scope='example_migration', name='api_example_rule', unique_id=None,
)


# pylint: disable=too-many-locals
# pylint: disable=unused-variable
@pytest.mark.parametrize(
    'doc_chunk, mapped_doc_chunk, expected_errors, can_continue',
    [
        (
            [
                {
                    'id': '1',
                    'data': {'_id': '1', 'test_data': {'int_value': 11}},
                },
            ],
            [
                {
                    'id': '1',
                    'int_value': 11,
                    'test_data': {'int_value': 11},
                    'test_data_safely': None,
                },
            ],
            {},
            False,
        ),
        (
            [
                {
                    '_id': '1',
                    'data': {'_id': '1', 'test_data': {'int_value': 11.1}},
                },
            ],
            [],
            {MAPPER_NAME: [0]},
            True,
        ),
        (
            [
                {
                    'id': '1',
                    'data': {'_id': '1', 'test_data': {'int_value': 11.1}},
                },
            ],
            None,
            {},
            False,
        ),
    ],
)
async def test_map_doc_chunk(
        replication_ctx,
        doc_chunk,
        mapped_doc_chunk,
        expected_errors,
        patch,
        can_continue,
):
    replication_units = {}

    rule = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='example_rule',
        source_types=[consts.SOURCE_TYPE_QUEUE_MONGO],
    )[0]
    example_mapper = rule.targets[0].mapper

    @patch('replication.foundation.invalid_docs.report.report_errors')
    async def report_errors(*args, **kwargs):
        return can_continue

    class Mapper:
        map_exceptions = example_mapper.map_exceptions

        mapper_calls = 0
        id = example_mapper.id  # pylint: disable=invalid-name

        @classmethod
        def transform(cls, *args, **kwargs):
            cls.mapper_calls += 1
            return example_mapper.transform(*args, **kwargs)

    monitors = {}
    for mapper in [Mapper, None]:
        for tg_name in ('tg-1', 'tg-2'):
            tg_name = tg_name + '_' + ('mapper' if mapper else 'as-is')

            replication_units[tg_name] = DummyUnit(
                DummyTarget(tg_name, mapper),
            )
            monitors[tg_name] = performance.PerformanceMonitor('dummy')

    assert len(replication_units) == 4

    with asyncpool.AsyncPool(1) as pool:
        args_kit = core_classes.ArgsKit(replication_ctx, pool=pool)
        mapped, mappers_errors = await mapping.map_doc_chunk(
            args_kit,
            replication_units,
            doc_chunk,
            rule_name='example_rule',
            monitors=monitors,
        )
    result = {}
    for mapper_name, docs in mapped.items():
        result[mapper_name] = [doc.mapped_doc for doc in docs]
    expected = {replication_consts.NO_MAPPER: doc_chunk}
    if mapped_doc_chunk is not None:
        expected[MAPPER_NAME] = mapped_doc_chunk
    assert mappers_errors == expected_errors

    assert result == expected
    assert Mapper.mapper_calls == 1


def test_map_error(replication_ctx):
    rule = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='example_rule',
        source_types=[consts.SOURCE_TYPE_QUEUE_MONGO],
    )[0]
    example_mapper = rule.targets[0].mapper
    tg_name = 'tg_name'

    mapped_data, mapper_errors = mapping._map_by_mappers(
        target_units={'': DummyUnit(DummyTarget(tg_name, example_mapper))},
        raw_doc_chunk=[
            {
                '_id': 'doc_id',
                'data': {'_id': 'doc_id', 'test_data': {'int_value': 11.1}},
            },
        ],
        monitors={'': performance.PerformanceMonitor('')},
    )
    assert not mapped_data[MAPPER_NAME]
    assert len(mapper_errors[MAPPER_NAME]) == 1
    assert isinstance(mapper_errors[MAPPER_NAME][0].exc, base.MapRuntimeError)
    assert str(mapper_errors[MAPPER_NAME][0].exc) == (
        'Mapper example_migration/api_example_rule '
        'got error during mapping _id=doc_id doc: '
        'cast error for output column [int_value]: '
        'Value 11.1 is not an integer'
    )


def test_try_map_doc_rough_error(replication_ctx):
    rule = replication_ctx.rule_keeper.rules_storage.get_rules_list(
        rule_name='example_rule',
        source_types=[consts.SOURCE_TYPE_QUEUE_MONGO],
    )[0]
    example_mapper = rule.targets[0].mapper
    doc_chunk_with_missing_data = {'_id': 'doc_id'}
    mapped_data, mapper_error = mapping._try_map_doc(
        doc=doc_chunk_with_missing_data,
        index=0,
        mapper=example_mapper,
        log_exception=True,
    )
    assert not mapped_data
    assert mapper_error is not None
    exc = mapper_error.exc
    assert isinstance(exc, base.MapRoughError)
    traceback_list = traceback.format_exception(
        type(exc), exc, exc.__traceback__,
    )
    assert traceback_list
    assert (
        '\nDuring handling of the above exception, '
        'another exception occurred:\n\n' in traceback_list
    )
