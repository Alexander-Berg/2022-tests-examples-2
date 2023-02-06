# pylint: disable=too-many-lines
import copy
import datetime
import json
import os
import re
import subprocess
import warnings

from _pytest import outcomes
from dateutil import parser as date_parser
import jsonpath
import jsonschema
import pytest

from taxi_schemas import configs
from taxi_schemas import utils
from taxi_schemas.validators import config_validator

CONFIG_NAME_REGEX = re.compile(r'[A-Z]+[A-Z_\d]*?[A-Z\d]+\.yaml$')
CONFIG_EXTRACT_NAME_REGEX = re.compile(r'([A-Z]+[A-Z_\d]*?[A-Z\d]+)\.yaml$')

CONFIG_PATH_REGEX = re.compile(
    r'schemas/configs/declarations(/[a-z\d]+[a-z\d\-_]*?[a-z\d]+)+$',
)

ERROR_NO_TAGS_FIELD = 'tags field is required'
ERROR_NO_MAINTAINERS_FIELD = 'maintainers field is required'

ERROR_FALLBACK_NOTFALLBACK_TAGS = (
    'fallback or notfallback tag must be present, details see: '
    'https://wiki.yandex-team.ru/taxi/backend/architecture/configs/Manual/'
    '#tegi'
)

ERROR_NO_EDIT_WITHOUT_SERVICE = (
    'tag no-edit-without-service use with tag by-service only'
)

CHANGE_DEFAULT_MSG = (
    'Default values can not be changed, see: \n'
    'https://wiki.yandex-team.ru/taxi/backend/architecture/configs/'
    'manual/#izmenenieznachenijjpoumolchaniju\n'
    'Do not avoid this error by temporary renaming.'
)

ERROR_BACKWARD_INCOMPATIBLE_CHANGES = (
    'You are making backward-incompatible changes'
)
BACKWARD_INCOMPATIBLE_FIELDS = frozenset(
    [
        'multipleOf',
        'maximum',
        'exclusiveMaximum',
        'minimum',
        'exclusiveMinimum',
        'maxLength',
        'minLength',
        'pattern',
        'additionalItems',
        'items',
        'maxItems',
        'minItems',
        'uniqueItems',
        'maxProperties',
        'minProperties',
        'required',
        'patternProperties',
        'additionalProperties',
        'enum',
        'type',
        'allOf',
        'anyOf',
        'oneOf',
        'not',
        'default',
        '$ref',
    ],
)
CONFIG_YAML = {
    'default': [],
    'description': 'Описание конфига',
    'tags': [],
    'schema': {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'id': {'type': 'string', 'uniqueItems': True},
                'name': {'type': 'string', 'minLength': 1},
                'of_value': {
                    'anyOf': [{'type': 'string'}, {'type': 'integer'}],
                },
                'not': 'text',
            },
            'additionalProperties': {'$ref': '#/definitions/QosInfo'},
            'required': ['id', 'name'],
        },
    },
}

TAG_BY_SERVICE = 'by-service'
TAG_BROKEN = 'broken'
TAG_NO_EDIT_WITHOUT_SERVICE = 'no-edit-without-service'
TAG_FALLBACK = 'fallback'
TAG_NOTFALLBACK = 'notfallback'
TAG_TEMPORARY = 'temporary'
INCOMPATIBLE_CONFIRM_FIELD = 'confirm-incompatible-version'
# need for configs, migrated from validators
TAG_ALLOW_EMPTY_MAINTAINERS = 'allow-empty-maintainers'

NO_NEW_CONFIGS_TAGS = {TAG_ALLOW_EMPTY_MAINTAINERS}

CONFIG_SCHEMA_VALIDATOR = os.path.join(
    utils.REPO_PATH, 'schemas/configs/config-schema-validator.yaml',
)


def check_must_be_json_serializable(schema, message_prefix):
    try:
        json.dumps(schema)
    except TypeError as exception:
        pytest.fail(
            f'{message_prefix} not serialized to json with error: {exception}',
        )


def check_samples(samples, validators):
    for sample in samples:
        for validator in validators:
            try:
                validator(sample)
            except (
                config_validator.ValidatorError,
                jsonschema.exceptions.ValidationError,
                jsonschema.exceptions.SchemaError,
            ) as exception:
                pytest.fail(
                    f'Validation failed on {sample} with error: {exception}',
                )


def check_invalid_samples(invalid_samples, validators):
    for invalid in invalid_samples:
        for validator in validators:
            try:
                with pytest.raises(
                        (
                            config_validator.ValidatorError,
                            jsonschema.exceptions.ValidationError,
                            jsonschema.exceptions.SchemaError,
                        ),
                ):
                    validator(invalid)
            except outcomes.Failed as exc:
                pytest.fail(
                    f'Doesn\'t fail on invalid sample {invalid}: {exc.msg}',
                )


@pytest.fixture(scope='session', name='common_definitions')
def _common_definitions():
    return config_validator.get_common_definitions()


def check_fallback_config(config):
    assert 'full-description' in config, (
        'full-description field is required for fallbacks, details see: '
        'https://wiki.yandex-team.ru/taxi/backend/architecture/configs/Manual'
        '#konfigi-folbeki'
    )
    assert 'turn-off-immediately' in config, (
        'turn-off-immediately field is required for fallbacks, details see: '
        'https://wiki.yandex-team.ru/taxi/backend/architecture/configs/Manual'
        '#konfigi-folbeki'
    )


def check_temporary_config(config, config_name):
    assert 'end-of-life' in config, (
        'end-of-life field is required for temporary, details see: '
        'https://wiki.yandex-team.ru/taxi/backend/architecture/configs/Manual/'
        '#temporary-configs'
    )
    if date_parser.parse(config['end-of-life']) > datetime.datetime.now():
        raw_responsible = config.get('maintainers') or []
        responsible = ', '.join(raw_responsible)
        warnings.warn(
            f'Temporary config `{config_name}` life is expired. '
            f'Please inform those responsible for it {responsible} '
            f'or Experiments team (https://nda.ya.ru/t/7Be4lEZv3poxmf). '
            f'Details see: '
            f'https://wiki.yandex-team.ru/taxi/backend/architecture/'
            f'configs/Manual/#temporary-configs',
            ResourceWarning,
        )


def check_config(config, common_definitions):
    if 'tags' in config:
        assert isinstance(config['tags'], list), 'Tags must be list'
        if TAG_BROKEN in config['tags']:
            return
    schema = utils.load_yaml_with_definitions(CONFIG_SCHEMA_VALIDATOR)
    jsonschema.validate(config, schema)

    if 'validators' in config:
        assert isinstance(config['validators'], list), 'Validators is not list'

    validators = config_validator.get_validators(config, common_definitions)
    value = config['default']
    for validator in validators:
        validator(value)

    check_samples(config.get('samples', []), validators)

    check_invalid_samples(config.get('invalid-samples', []), validators)

    check_must_be_json_serializable(config, message_prefix='Config')

    assert 'audit_namespace' in config, (
        '`audit_namespace` required in configs. See '
        'https://wiki.yandex-team.ru/taxi/backend/'
        'architecture/configs/manual/#poljayaml'
    )


# pylint: disable=invalid-name
@pytest.mark.nofilldb()
def test_config(config_with_possible_modification, common_definitions):
    config = utils.load_yaml(config_with_possible_modification)

    check_config(config, common_definitions)


@pytest.mark.nofilldb()
def test_manual_selected_configs_schemas(
        specific_check_path, common_definitions,
):
    config = utils.load_yaml(specific_check_path)
    check_config(config, common_definitions)
    check_additional_properties(config)


@pytest.mark.nofilldb()
def test_all_configs_schemas(check_path_all, common_definitions):
    config = utils.load_yaml(check_path_all)
    check_config(config, common_definitions)
    if TAG_BROKEN in (config.get('tags') or []):
        return
    check_additional_properties(config)


@pytest.mark.nofilldb()
def test_duplicates():
    config_paths = configs.get_all_configs_paths()
    assert config_paths
    config_names = set()
    for config_path in config_paths:
        config_name = config_path.stem
        assert config_name not in config_names, 'config duplicate: {}'.format(
            config_name,
        )
        config_names.add(config_name)


@pytest.mark.nofilldb()
def test_default_change(modified_config_path):
    new_config = utils.load_yaml(modified_config_path)
    old_config = _load_old_config(modified_config_path)
    if 'default' not in old_config:
        return
    assert old_config['default'] == new_config['default'], CHANGE_DEFAULT_MSG


@pytest.mark.nofilldb()
def test_new_configs(new_config_path):
    new_config = utils.load_yaml(new_config_path)

    # no validators in new configs
    assert (
        'validators' not in new_config
    ), 'validators deprecated, use JSON schema'

    # no some tags in new configs
    tags = set(new_config.get('tags', []))
    used_tags = tags & NO_NEW_CONFIGS_TAGS
    assert not used_tags, 'Tags `{}` not allowed in new config'.format(
        ', '.join(sorted(used_tags)),
    )


@pytest.mark.nofilldb()
def test_names_valid():
    config_paths = configs.get_all_configs_paths()
    for path in config_paths:
        path, name = os.path.split(path)
        assert CONFIG_PATH_REGEX.search(path), (
            f'invalid group in path "{path}", check group contains only '
            f'small letters, numbers, underscore and dash'
        )
        assert CONFIG_NAME_REGEX.match(name), (
            f'invalid name "{name}", check name contains only upper '
            f'letters, numbers and underscore, and file extensions is ".yaml"'
        )


def get_schema(schema, definitions):
    if not isinstance(schema, dict):
        return {}
    if '$ref' in schema:
        return {}
    return schema


def check_is_valid_schema(schema, path):
    assert isinstance(schema, dict), f'Must be dict {path}'
    if schema.get('type', '') == 'object':
        assert (
            'additionalProperties' in schema
        ), f'No additionalProperties in object by path {path}'

    if schema.get('type', '') == 'array':
        assert 'items' in schema, f'No `items` field in array by {path}'


def walk_in_deep(
        schema,
        definitions,
        path,
        *args,
        old_schema=None,
        enable_check_additional_properties=False,
):
    if enable_check_additional_properties:
        previous_allow_wide_additional_properties = False
        if old_schema:
            previous_allow_wide_additional_properties = (
                _check_allow_wide_additional_properties(old_schema, path)
            )
        assert (
            schema.get('additionalProperties') is not True
            or schema.get('x-taxi-additional-properties-true-reason')
            or previous_allow_wide_additional_properties
        ), (
            'Using true in additionalProperties requires explanation in '
            '"x-taxi-additional-properties-true-reason" field, alternatively '
            'consider using additionalProperties: <schema> if possible'
        )
    else:
        check_is_valid_schema(schema, path)

    if 'properties' in schema:
        for property_name, property_schema in schema['properties'].items():
            walk_in_deep(
                get_schema(property_schema, definitions),
                definitions,
                f'{path}.properties.{property_name}',
                old_schema=old_schema,
                enable_check_additional_properties=(
                    enable_check_additional_properties
                ),
            )

    if 'additionalProperties' in schema:
        walk_in_deep(
            get_schema(schema['additionalProperties'], definitions),
            definitions,
            f'{path}.additionalProperties',
            old_schema=old_schema,
            enable_check_additional_properties=(
                enable_check_additional_properties
            ),
        )

    if 'items' in schema:
        walk_in_deep(
            get_schema(schema['items'], definitions),
            definitions,
            f'{path}.items',
            old_schema=old_schema,
            enable_check_additional_properties=(
                enable_check_additional_properties
            ),
        )

    for compose_key in ['oneOf', 'anyOf', 'allOf']:
        if compose_key in schema:
            for index, combine_schema in enumerate(schema[compose_key]):
                walk_in_deep(
                    get_schema(combine_schema, definitions),
                    definitions,
                    f'{path}.{compose_key}[{index}]',
                    old_schema=old_schema,
                    enable_check_additional_properties=(
                        enable_check_additional_properties
                    ),
                )


def _check_allow_wide_additional_properties(schema, path):
    found_schemes = jsonpath.jsonpath(schema, path)
    if found_schemes is False:
        return False

    if len(found_schemes) > 1:
        warnings.warn(
            f'Old additionalProperties may be incorrect, '
            f'see value: {found_schemes} '
            f'in path: {path}',
            ResourceWarning,
        )
    inner_schema = found_schemes[0]

    if (
            not isinstance(inner_schema, dict)
            or 'additionalProperties' not in inner_schema
    ):
        return False
    return inner_schema['additionalProperties'] is True


@pytest.mark.nofilldb()
def test_additional_properties_in_config_schemas(new_and_modified_config_path):
    config = utils.load_yaml(new_and_modified_config_path)
    check_additional_properties(config)


def check_additional_properties(config):
    if 'schema' not in config:
        return
    schema = config['schema']
    definitions = schema['definitions'] if 'definitions' in schema else {}

    walk_in_deep(schema, definitions, 'schema')

    for name, definition_schema in definitions.items():
        walk_in_deep(
            definition_schema, definitions, f'schema.definitions.{name}',
        )


@pytest.mark.nofilldb()
def test_true_not_in_additional_properties(new_and_modified_config_path):
    config = utils.load_yaml(new_and_modified_config_path)
    if 'schema' not in config:
        return
    schema = config['schema']
    definitions = schema['definitions'] if 'definitions' in schema else {}

    old_schema = _load_old_config(new_and_modified_config_path, fail=False)
    walk_in_deep(
        config['schema'],
        definitions,
        'schema',
        old_schema=old_schema,
        enable_check_additional_properties=True,
    )

    for name, definition_schema in definitions.items():
        walk_in_deep(
            definition_schema,
            definitions,
            f'schema.definitions.{name}',
            old_schema=old_schema,
            enable_check_additional_properties=True,
        )


@pytest.mark.nofilldb()
# pylint: disable=invalid-name
def test_check_common_definition(new_and_modified_definition_path):
    definitions = utils.load_yaml(new_and_modified_definition_path)
    check_must_be_json_serializable(definitions, message_prefix='Definition')
    for name, definition_schema in definitions.items():
        _, file_name = os.path.split(new_and_modified_definition_path)
        walk_in_deep(definition_schema, definitions, f'{file_name}:{name}')


@pytest.mark.nofilldb()
def test_tags(new_and_modified_config_path):
    config = utils.load_yaml(new_and_modified_config_path)
    assert 'tags' in config, ERROR_NO_TAGS_FIELD
    tags = config['tags']
    is_fallback = TAG_FALLBACK in tags
    is_notfallback = TAG_NOTFALLBACK in tags
    assert is_fallback != is_notfallback, ERROR_FALLBACK_NOTFALLBACK_TAGS
    if is_fallback:
        check_fallback_config(config)
    if TAG_TEMPORARY in tags:
        config_names = CONFIG_EXTRACT_NAME_REGEX.findall(
            new_and_modified_config_path,
        )
        check_temporary_config(config, config_names[0])
    if TAG_NO_EDIT_WITHOUT_SERVICE in tags:
        assert TAG_BY_SERVICE in tags, ERROR_NO_EDIT_WITHOUT_SERVICE


@pytest.mark.nofilldb()
def test_maintainers(new_and_modified_config_path):
    config = utils.load_yaml(new_and_modified_config_path)
    if TAG_ALLOW_EMPTY_MAINTAINERS in config.get('tags', []):
        return
    assert 'maintainers' in config, ERROR_NO_MAINTAINERS_FIELD
    assert config['maintainers'], 'At least 1 maintainer must be present'


@pytest.mark.parametrize(
    'old_config,updater,expected_problems',
    [
        (
            CONFIG_YAML,
            {
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string', 'uniqueItems': True},
                            'name': {'type': 'string', 'minLength': 1},
                            'of_value': {
                                'anyOf': [
                                    {'type': 'string'},
                                    {'type': 'integer'},
                                ],
                            },
                        },
                        'additionalProperties': {
                            '$ref': '#/definitions/QosInfo',
                        },
                    },
                },
            },
            ['root.schema.items.(required)'],
        ),
        (
            CONFIG_YAML,
            {
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string', 'uniqueItems': True},
                            'name': {'type': 'string', 'minLength': 1},
                            'of_value': {
                                'anyOf': [
                                    {'type': 'string'},
                                    {'type': 'integer'},
                                ],
                            },
                        },
                        'additionalProperties': {
                            '$ref': '#/definitions/QosInfo',
                        },
                        'required': ['id'],
                    },
                },
            },
            ['root.schema.items.required'],
        ),
        (
            CONFIG_YAML,
            {
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string', 'uniqueItems': True},
                            'name': {'type': 'string', 'minLength': 1},
                            'of_value': {
                                'anyOf': [
                                    {'type': 'string'},
                                    {'type': 'integer'},
                                ],
                            },
                        },
                        'additionalProperties': {
                            '$ref': '#/definitions/QosInfo',
                        },
                        'required': ['no_id', 'name'],
                    },
                },
            },
            ['root.schema.items.required'],
        ),
        (
            CONFIG_YAML,
            {
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string', 'uniqueItems': True},
                            'name': {'type': 'int', 'minLength': 1},
                            'of_value': {
                                'anyOf': [
                                    {'type': 'string'},
                                    {'type': 'integer'},
                                ],
                            },
                        },
                        'additionalProperties': {
                            '$ref': '#/definitions/QosInfo',
                        },
                        'required': ['id', 'name'],
                    },
                },
            },
            ['root.schema.items.properties.name.type'],
        ),
        (
            CONFIG_YAML,
            {
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string', 'uniqueItems': False},
                            'name': {'type': 'string', 'minLength': 1},
                            'of_value': {
                                'anyOf': [
                                    {'type': 'string'},
                                    {'type': 'integer'},
                                ],
                            },
                        },
                        'additionalProperties': {
                            '$ref': '#/definitions/QosInfo',
                        },
                        'required': ['id', 'name'],
                    },
                },
            },
            ['root.schema.items.properties.id.uniqueItems'],
        ),
        (
            CONFIG_YAML,
            {
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string', 'uniqueItems': False},
                            'name': {'type': 'string', 'minLength': 1},
                            'of_value': {
                                'anyOf': [
                                    {'type': 'string'},
                                    {'type': 'integer'},
                                ],
                            },
                        },
                    },
                },
            },
            [
                'root.schema.items.(additionalProperties|required)',
                'root.schema.items.properties.id.uniqueItems',
            ],
        ),
        (
            CONFIG_YAML,
            {
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string', 'uniqueItems': True},
                            'name': {'type': 'string', 'minLength': 1},
                            'of_value': {
                                'anyOf': [
                                    {'type': 'string'},
                                    {'type': 'integer'},
                                    {'type': 'boolean'},
                                ],
                            },
                        },
                        'additionalProperties': {
                            '$ref': '#/definitions/QosInfo',
                        },
                        'required': ['id', 'name'],
                    },
                },
            },
            ['root.schema.items.properties.of_value.anyOf'],
        ),
        (
            CONFIG_YAML,
            {
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string', 'uniqueItems': True},
                            'name': {'type': 'string', 'minLength': 1},
                            'of_value': {
                                'anyOf': [
                                    {'type': 'string'},
                                    {'type': 'integer'},
                                ],
                            },
                        },
                        'additionalProperties': {
                            '$ref': '#/definitions/AnotherDefinition',
                        },
                        'required': ['id', 'name'],
                    },
                },
            },
            ['root.schema.items.additionalProperties.$ref'],
        ),
        (
            CONFIG_YAML,
            {
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string', 'uniqueItems': True},
                            'name': {'type': 'string', 'minLength': 1},
                            'of_value': {
                                'anyOf': [
                                    {'type': 'string'},
                                    {'type': 'integer'},
                                ],
                            },
                            'some': {'type': 'string', 'uniqueItems': True},
                        },
                        'additionalProperties': {
                            '$ref': '#/definitions/QosInfo',
                        },
                        'required': ['id', 'name'],
                    },
                },
            },
            None,
        ),
        (
            CONFIG_YAML,
            {
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string', 'uniqueItems': True},
                            'name': {'type': 'string', 'minLength': 1},
                            'of_value': {
                                'anyOf': [
                                    {'type': 'string'},
                                    {'type': 'integer'},
                                ],
                            },
                            'some': {'type': 'string', 'uniqueItems': True},
                            'default': {'type': 'string'},
                            '$ref': {'type': 'integer'},
                            'not': 'text2',
                        },
                        'additionalProperties': {
                            '$ref': '#/definitions/QosInfo',
                        },
                        'required': ['id', 'name'],
                    },
                },
            },
            None,
        ),
    ],
)
def test_recursive_compatibility_check(old_config, updater, expected_problems):
    new_config = copy.deepcopy(old_config)
    new_config.update(updater)
    problem_fields = []
    recursive_compatibility_check(new_config, old_config, problem_fields)
    if not problem_fields:
        assert expected_problems is None
    else:
        assert [
            '.'.join(field_path) for field_path in problem_fields
        ] == expected_problems


@pytest.mark.parametrize(
    'case_name, schema, default_value, expected_exception',
    [
        pytest.param(
            'bad_date_time',
            {'type': 'string', 'format': 'date-time'},
            'aaaaaa',
            jsonschema.exceptions.ValidationError,
            id='check_test_algo_bad_date_time',
        ),
    ]
    + [
        # проверка работы модуля тегов
        pytest.param(
            case_name,
            schema,
            default_value,
            config_validator.ValidatorError,
            id=case_name,
        )
        for case_name, schema, default_value in [
            (
                'topic_must_be_array',
                {
                    'type': 'string',
                    'x-taxi-driver-tags-from-topic': {'rt': 'candidates'},
                },
                'aaaaaa',
            ),
            (
                'topic_must_be_array_with_string_type',
                {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'x-taxi-driver-tags-from-topic': [123],
                },
                ['123'],
            ),
            (
                'topic_must_be_array_with_non_empty',
                {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'x-taxi-driver-tags-from-topic': [None],
                },
                ['aaaaaa'],
            ),
            (
                'tags_must_be_array',
                {
                    'type': 'string',
                    'x-taxi-driver-tags-from-topic': ['candidates'],
                },
                'aaaaaa',
            ),
            (
                'tags_must_have_items_keyword',
                {
                    'type': 'array',
                    'x-taxi-driver-tags-from-topic': ['candidates'],
                },
                ['aaaaaa'],
            ),
            (
                'tags_must_be_array_with_string_type',
                {
                    'type': 'array',
                    'items': {'type': 'integer'},
                    'x-taxi-driver-tags-from-topic': ['candidates'],
                },
                [123],
            ),
        ]
    ],
)
def test_validators_creation(
        case_name,
        schema,
        default_value,
        expected_exception,
        common_definitions,
):
    config = copy.copy(CONFIG_YAML)
    config['schema'] = schema
    config['default'] = default_value

    try:
        with pytest.raises(expected_exception):
            try:
                check_config(config, common_definitions)
            except Exception as exc:
                assert isinstance(exc, expected_exception)
                raise
    except outcomes.Failed as exc:
        pytest.fail(f'Doesn\'t fail on invalid case {case_name}: {exc.msg}')


@pytest.mark.nofilldb()
def test_backward_compatibility(modified_config_path):
    new_config = utils.load_yaml(modified_config_path)
    old_config = _load_old_config(modified_config_path)
    change_tags_check(new_config, old_config)
    change_end_of_life_check(new_config, old_config)
    version_to_confirm_incompatible = (
        old_config.get(INCOMPATIBLE_CONFIRM_FIELD) or 0
    ) + 1
    currently_set = new_config.get(INCOMPATIBLE_CONFIRM_FIELD)

    problem_fields = []
    if not version_to_confirm_incompatible == currently_set:
        recursive_compatibility_check(new_config, old_config, problem_fields)

    if problem_fields:
        fields_info = '\n * '.join(
            set(
                '`{}`'.format('.'.join(field_path))
                for field_path in problem_fields
            ),
        )
        pytest.fail(
            f'{ERROR_BACKWARD_INCOMPATIBLE_CHANGES}: field(s) \n '
            f'{fields_info} \ncannot be changed. \n'
            f'See https://wiki.yandex-team.ru/taxi/backend/architecture/'
            f'configs/'
            f'Manual/#algoritmproverkiyamlovskonfigamispomoshhjuteamcity.\n'
            'You can confirm that you are aware of possible consequences \nif '
            'value set using this new schema will be set prior to clients\n'
            'being ready to work with it. \nTo confirm, set '
            f'`{INCOMPATIBLE_CONFIRM_FIELD}: '
            f'{version_to_confirm_incompatible}` at the root level.',
        )


def change_end_of_life_check(new_config, old_config):
    if TAG_TEMPORARY not in old_config.get('tags', []):
        return
    if old_config.get('end-of-life') is not None:
        assert old_config.get('end-of-life') == new_config.get(
            'end-of-life',
        ), (
            'Disallow change end-of-life field. See '
            'https://wiki.yandex-team.ru/taxi/backend/architecture/configs/'
            'Manual/#temporary-configs'
        )


def change_tags_check(new_config, old_config):
    old_tags = old_config.get('tags', [])
    new_tags = new_config.get('tags', [])
    for tag in {TAG_BY_SERVICE, TAG_TEMPORARY}:
        if tag in old_tags:
            assert tag in new_tags, (
                f'{ERROR_BACKWARD_INCOMPATIBLE_CHANGES}: '
                f'do not remove previously added "{tag}" tag'
            )


def recursive_compatibility_check(d1, d2, problems, level=None):
    if level is None:
        level = ['root']
    if isinstance(d1, dict) and isinstance(d2, dict):
        if d1.keys() != d2.keys():
            s1 = set(d1.keys())
            s2 = set(d2.keys())
            if level[-1] != 'properties':
                diff_keys = s1 ^ s2
                backward_keys = diff_keys & BACKWARD_INCOMPATIBLE_FIELDS
                if backward_keys:
                    problems.append(
                        [
                            *level,
                            '({})'.format('|'.join(sorted(backward_keys))),
                        ],
                    )
            common_keys = s1 & s2
        else:
            common_keys = set(d1.keys())

        for key in common_keys:
            recursive_compatibility_check(
                d1[key], d2[key], problems, level=[*level, key],
            )

    elif isinstance(d1, list) and isinstance(d2, list):
        if len(d1) != len(d2):
            if level[-1] in BACKWARD_INCOMPATIBLE_FIELDS:
                problems.append(level)
        common_len = min(len(d1), len(d2))

        for index in range(common_len):
            recursive_compatibility_check(
                d1[index], d2[index], problems, level=level,
            )

    else:
        if d1 != d2:
            if level[-1] in BACKWARD_INCOMPATIBLE_FIELDS:
                if len(level) >= 2 and level[-2] != 'properties':
                    problems.append(level)


def _load_old_config(modified_config_path, fail=True):
    modified_config_rel_path = modified_config_path.relative_to(
        configs.ARCADIA_ROOT,
    )
    commit_with_file = f'trunk:{modified_config_rel_path}'
    show_cmd = ['arc', 'show', commit_with_file]

    process = subprocess.run(
        show_cmd, stdout=subprocess.PIPE, encoding='utf-8',
    )
    old_config = utils.load_yaml_from_string(process.stdout)
    if old_config is None and fail:
        pytest.fail(
            'Config {} \ncould not be loaded from develop branch'.format(
                modified_config_rel_path,
            ),
        )
    return old_config
