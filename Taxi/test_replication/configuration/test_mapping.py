# pylint: disable=protected-access
import pytest

from replication_core.mapping import context as mapping_context

from replication import settings
from replication.common import queue_mongo
from replication.configuration.mapping import exceptions
from replication.configuration.mapping import mapper_generators


@pytest.mark.nofilldb()
def test_bson_mapper(replication_ctx, mapper_check, load_py_yaml):
    mapper_config = mapper_generators.MAPPER_GENERATORS['$bson']
    cases = load_py_yaml('bson.yaml')
    for test_num, test_case in enumerate(cases):
        _test_generated_mapper(
            replication_ctx,
            mapper_check,
            mapper_config,
            test_desc=f'test no {test_num}',
            **test_case,
        )


@pytest.mark.nofilldb()
@pytest.mark.now('2019-01-01T00:00')
def test_raw_mapper(replication_ctx, mapper_check, load_py_yaml):
    mapper_config = mapper_generators.MAPPER_GENERATORS['$raw']
    cases = load_py_yaml('raw.yaml')
    for test_num, test_case in enumerate(cases):
        _test_generated_mapper(
            replication_ctx,
            mapper_check,
            mapper_config,
            test_desc=f'test no {test_num}',
            **test_case,
        )


@pytest.mark.nofilldb()
def test_index_mapper(replication_ctx, mapper_check, load_py_yaml):
    mapper_config = mapper_generators.MAPPER_GENERATORS['$index']
    cases = load_py_yaml('index.yaml')
    for test_num, test_case in enumerate(cases):
        _test_generated_mapper(
            replication_ctx,
            mapper_check,
            mapper_config,
            test_desc=f'test no {test_num}',
            **test_case,
        )


# TODO: add cast and input_transform tests
def _test_generated_mapper(
        replication_ctx,
        mapper_check,
        mapper_config: mapper_generators.MapperGeneratorConfig,
        *,
        test_desc,
        mapper_settings,
        expected_target,
        is_mapper_invalid,
        mapper_tests,
        source_type,
        expected_mapper=None,
        flaky_config=None,
):
    if flaky_config is not None:
        mapper_settings['flaky_config'] = flaky_config
    if mapper_config.load_target_raw_data is not None:
        if expected_target is None:
            with pytest.raises(exceptions.MapperGenerationError):
                mapper_config.load_target_raw_data(**mapper_settings)
        else:
            target = mapper_config.load_target_raw_data(**mapper_settings)
            assert target == expected_target, test_desc
    else:
        assert expected_target is None, test_desc

    source_definition = replication_ctx.pluggy_deps.source_definitions.data[
        source_type
    ]
    data_deserializer = source_definition.data_hooks.data_deserializer

    data_serializer = source_definition.get_data_serializer_to_queue()
    if is_mapper_invalid:
        with pytest.raises(exceptions.MapperGenerationError):
            mapper_config.load_mapper(
                map_context=mapping_context.create_context(
                    settings.TESTSUITE_MAP_PLUGINS,
                ),
                data_serializer=data_serializer,
                mapper_raw_data=mapper_settings,
            )
    else:
        mapper = mapper_config.load_mapper(
            map_context=mapping_context.create_context(
                settings.TESTSUITE_MAP_PLUGINS,
            ),
            data_serializer=data_serializer,
            mapper_raw_data=mapper_settings,
        )
        mapper_check(
            test_desc,
            mapper,
            testcase_docs=_prepare_tests_from_queue(
                mapper_tests, data_deserializer,
            ),
        )


def _prepare_tests_from_queue(mapper_tests, data_deserializer):
    return [
        {
            'input': queue_mongo.prepare_data_from_queue(
                mapper_test['input'], deserializer=data_deserializer,
            ),
            'expected': mapper_test['expected'],
        }
        for mapper_test in mapper_tests
    ]
