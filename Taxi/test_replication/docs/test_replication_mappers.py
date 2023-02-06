# pylint: disable=protected-access, no-self-use
import operator

import bson
import pytest

from replication_core import load
from replication_core.mapping import context as context_mod
from replication_core.parsers import mappers as mappers_mod

from replication import settings
from replication.common import queue_mongo
from replication.foundation import consts
from replication.foundation import loaders
from replication.foundation import map_plugin
from replication.foundation.mappers import constructor as mapper_constructor
from replication.utils import data_helpers

_MAPPERS_COMPARE = (
    ('excluded_fields', lambda v: v),
    ('_mapper._nulls_in_non_nullable', lambda v: v),
    ('_mapper._premappers', len),
)
_COLUMNS_COMPARE = ('output_column', 'input_column', 'nullable')


def test_test_get_mappers(replication_ctx):
    mappers_from_storage = {
        mapper_id: mapper
        for mapper_id, mapper in _get_mappers_from_storage(
            replication_ctx,
        ).items()
    }
    mappers = _get_mappers(replication_ctx)[0]
    assert len(mappers_from_storage) == len(mappers)
    assert mappers_from_storage.keys() == mappers.keys()
    for key in mappers:
        mapper1, mapper2 = mappers_from_storage[key], mappers[key]
        assert mapper1.id == mapper2.id
        for attr_name, comp_func in _MAPPERS_COMPARE:
            get_attr_func = operator.attrgetter(attr_name)
            assert comp_func(get_attr_func(mapper1)) == comp_func(
                get_attr_func(mapper2),
            ), f'{attr_name}: {mapper1.id}'
        columns1 = mapper1._mapper._columns
        columns2 = mapper2._mapper._columns
        assert len(columns1) == len(columns2), mapper1.id
        for column1, column2 in zip(columns1, columns2):
            for attr_name in _COLUMNS_COMPARE:
                get_attr_func = operator.attrgetter(attr_name)
                assert get_attr_func(column1) == get_attr_func(
                    column2,
                ), f'{mapper1.id}: {column1.formatted_column}'


# pylint: disable=too-many-nested-blocks
def _get_mappers_from_storage(replication_ctx):
    mappers = {}
    rules_storage = replication_ctx.rule_keeper.rules_storage
    source_definitions = replication_ctx.pluggy_deps.source_definitions
    for rule in rules_storage.get_rules_list(
            source_types=source_definitions.all_types,
    ):
        rule_mappers = {}
        for target_core in rule.targets:
            target_type = target_core.type
            mapper = target_core.mapper
            if mapper:
                rule_scope = None
                if not mapper.id.generated:
                    rule_scope = mapper.id.rule_scope
                mapper_id = (
                    rule.source.type,
                    target_type,
                    mapper.id.name,
                    rule_scope,
                )
                if mapper_id not in rule_mappers:
                    rule_mappers[mapper_id] = mapper
            else:
                assert target_type != consts.TARGET_TYPE_YT
        mappers.update(rule_mappers)

    return mappers


def _get_mappers(replication_ctx):
    mappers = {}
    queue_mappers = {}
    master_rules = loaders.load_rules(
        replication_ctx.rule_keeper.replication_yaml,
        replication_ctx.pluggy_deps.source_definitions,
    )
    for master_rule in master_rules.values():
        queue_mapper = None
        rule_mappers = {}
        for source_core, target_cores in master_rule.iter_replication_cores():
            for target_core in target_cores:
                map_plugins_storage = map_plugin.MapPluginStorage(
                    master_rule.map_plugins,
                    parameters={},
                    pythonpath=master_rule.pythonpath,
                )
                mapper = mapper_constructor.construct(
                    replication_ctx.pluggy_deps.source_definitions,
                    map_plugins_storage,
                    source_core,
                    target_core,
                )
                if mapper is None:
                    continue
                rule_scope = None
                if not mapper.id.generated:
                    rule_scope = mapper.id.rule_scope
                mapper_id = (
                    source_core.type,
                    target_core.type,
                    mapper.id.name,
                    rule_scope,
                )
                if mapper_id not in rule_mappers:
                    rule_mappers[mapper_id] = mapper
                    if target_core.type in consts.ALL_QUEUE_SOURCE_TYPES:
                        queue_mapper = mapper

        mappers.update(rule_mappers)
        queue_mapper = _get_mapper_to_queue(
            queue_mapper, master_rule.base_source_type,
        )
        if queue_mapper is not None:
            queue_mappers.update(
                {
                    mapper_id: queue_mapper
                    for mapper_id in rule_mappers
                    if mapper_id[0] in consts.ALL_QUEUE_SOURCE_TYPES
                },
            )
    return mappers, queue_mappers


def _get_mapper_to_queue(queue_mapper, base_source_type):
    if queue_mapper is None and base_source_type == consts.SOURCE_TYPE_API:

        def _queue_mapper(_doc):
            yield None, {'data': _doc}

    else:
        _queue_mapper = queue_mapper

    if _queue_mapper is None:
        return None

    def _map_doc(doc):
        if base_source_type == consts.SOURCE_TYPE_MONGO:
            doc = data_helpers.handle_raw_bson(bson.BSON.encode(doc))
        for _, mapped in _queue_mapper(doc):
            yield _, queue_mongo.prepare_data_from_queue(mapped)

    return _map_doc


@pytest.mark.nofilldb
@pytest.mark.now('2019-09-01T01:12:00+0000')
def test_example_mappers(mapper_check):
    has_mappers = False
    example_scopes = load.load_rule_scopes(
        settings.BASE_STATIC_DIR, ensure_pythonpath=True,
    ).rule_scopes
    for scope in example_scopes.values():
        map_context = context_mod.create_context(scope.plugins)
        for rule in scope.rules.values():
            for target in rule.targets.values():
                if target.mapper_doc is not None:
                    mapper_check(
                        target.mapper_testcase_full_path,
                        mappers_mod.load_doc(target.mapper_doc, map_context),
                    )
                    has_mappers = True
    assert has_mappers
