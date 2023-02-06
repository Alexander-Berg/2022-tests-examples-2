import os
import inspect

import jsonschema
import pytest
import yaml

from taxi.internal.yt_import.schema import classes
from taxi.internal.yt_import.schema import loaders


SCHEMAS_DIR = 'json_schemas'


@pytest.mark.asyncenv('blocking')
def test_yt_import_rules_json_schema():
    yt_import_rules_schema = _load_schema('yt_import_rule')
    _validate_objs_in_dir(loaders.RULES_DIR, yt_import_rules_schema)


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_yt_import_rules_load_success():
    yield loaders.load_all_rules()


def _validate_objs_in_dir(dir, schema):
    for dir_path, _, file_names in os.walk(dir):
        for file_name in file_names:
            if file_name.endswith('.yaml'):
                obj_file_path = os.path.join(dir_path, file_name)
                obj = loaders._load_obj(obj_file_path)
                try:
                    jsonschema.validate(obj, schema)
                except jsonschema.ValidationError as exc:
                    exc.message = 'error in %s\n%s' % (
                        obj_file_path, exc.message
                    )
                    raise


def _load_schema(name):
    schema_path = os.path.join(
        loaders.STATIC_BASEDIR, SCHEMAS_DIR, '%s.yaml' % name
    )
    with open(schema_path) as schema_file:
        schema = yaml.load(schema_file, Loader=yaml.CLoader)
    return schema


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
@pytest.mark.parametrize(
    'rule_dict,expected',
    [
        # valid rule
        (
            {
                'mapper': {
                    'column_mappers': [
                        {'output_column': '_id', 'input_column': 'user_id'},
                    ],
                },
                'mode': 'apply_updates',
                'chunk_size': 2000,
                'source': {
                    'sorted_by': 'updated_at',
                    'table_path': 'examples/example',
                    'yt_client_name': 'hahn-fraud'
                },
                'destination': 'example_collection',
                'period': 120
            },
            None,
        ),
        # missed required source.id_column tag for merge mode
        (
            {
                'mapper': {
                    'column_mappers': [
                        {'output_column': '_id', 'input_column': 'user_id'},
                    ],
                },
                'mode': 'merge',
                'chunk_size': 2000,
                'source': {
                    'table_path': 'examples/example',
                    'yt_client_name': 'hahn-fraud'
                },
                'destination': 'example_collection',
                'period': 120
            },
            classes.RuleValidationError,
        ),
        # forbidden column_mappers.suppress_errors tag for merge mode
        (
            {
                'mapper': {
                    'column_mappers': [
                        {
                            'output_column': '_id',
                            'input_column': 'user_id',
                            'suppress_errors': True,
                        },
                    ],
                },
                'mode': 'merge',
                'chunk_size': 2000,
                'source': {
                    'id_column': 'user_id',
                    'table_path': 'examples/example',
                    'yt_client_name': 'hahn-fraud'
                },
                'destination': 'example_collection',
                'period': 120
            },
            classes.RuleValidationError,
        ),
        # exclusive column_mappers.not_empty tag for mode != by_id
        (
            {
                'mapper': {
                    'column_mappers': [
                        {
                            'output_column': '_id',
                            'input_column': 'user_id',
                            'not_empty': True,
                        },
                    ],
                },
                'mode': 'by_created',
                'chunk_size': 2000,
                'source': {
                    'table_path': 'examples/example',
                    'yt_client_name': 'hahn-fraud'
                },
                'destination': 'example_collection',
                'period': 120
            },
            classes.RuleValidationError,
        ),
    ]
)
def test_rule_validation(rule_dict, expected):
    rule_name = 'test_rule_validation'
    if inspect.isclass(expected) and issubclass(expected, Exception):
        with pytest.raises(expected):
            yield loaders._build_yt_import_rule(rule_name, rule_dict)
    else:
        rule = yield loaders._build_yt_import_rule(rule_name, rule_dict)
        assert isinstance(rule, classes.YtImportRule)
