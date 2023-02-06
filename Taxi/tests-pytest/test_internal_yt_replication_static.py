import os

import jsonschema
import pytest

from taxi.internal.data_manager import loader_utils
from taxi.internal.yt_replication.schema import loaders
from taxi.internal.yt_tools.combine_chunks import (
    schema as combine_chunks_schema
)
import helpers

SCHEMAS_DIR = 'json_schemas'


@pytest.mark.asyncenv('blocking')
def test_mappers_json_schemas():
    mappers_schema = _load_schema('mappers')
    helpers.validate_objects_in_dir(
        loaders.MAPPERS_DIR, mappers_schema, loader=loaders.load_obj
    )


@pytest.mark.asyncenv('blocking')
def test_rules_json_schemas():
    rules_schema = _load_schema('rules')
    helpers.validate_objects_in_dir(
        loaders.RULES_DIR, rules_schema, loader=loaders.load_obj
    )


@pytest.mark.asyncenv('blocking')
def test_tables_json_schemas():
    tables_schema = _load_schema('tables')
    helpers.validate_objects_in_dir(
        loaders.TABLES_META_DIR, tables_schema, loader=loaders.load_obj
    )


@pytest.mark.asyncenv('blocking')
def test_combine_chunks_json_schema():
    rules_schema = _load_schema('combine_chunks_rules')
    obj = loader_utils.load_yaml(combine_chunks_schema.RULES_PATH)
    jsonschema.validate(obj, rules_schema)


@pytest.mark.asyncenv('blocking')
def test_data_consistency():
    all_rules = loaders.load_all_rules()
    dest_rules_names = set()

    for rule in all_rules.itervalues():
        if rule.source.type != 'external':
            raise RuntimeError(
                'New rules should be added via replication service'
            )
        for output in rule.outputs:
            for dest_rule in output.destination_rules.itervalues():
                table_columns = dest_rule.destination.table_meta.get_columns()
                mapper_columns = dest_rule.mapper.get_output_columns()

                _check_only_unique(table_columns)
                _check_only_unique(mapper_columns)

                filtered_table_columns = (
                    dest_rule.destination.table_meta.get_columns(
                        exclude_expression=True)
                )

                if not dest_rule.destination.partial_update:
                    assert set(mapper_columns) == set(filtered_table_columns)
                else:
                    assert len(
                        set(mapper_columns) - set(filtered_table_columns)
                    ) == 0

                assert dest_rule.destination.name not in dest_rules_names
                dest_rules_names.add(dest_rule.destination.name)


def _check_only_unique(arr):
    unique_elements = set()
    for element in arr:
        assert element not in unique_elements
        unique_elements.add(element)


def _load_schema(name):
    schema_path = os.path.join(
        loaders.STATIC_BASEDIR, SCHEMAS_DIR, '%s.yaml' % name
    )
    return loader_utils.load_yaml(schema_path)
