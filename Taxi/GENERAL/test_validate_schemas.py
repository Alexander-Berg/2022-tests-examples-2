import pytest

from taxi_schemas import consts
from taxi_schemas import utils
from taxi_schemas.validators import mongo_validator


class BaseError(Exception):
    """Base class for all exceptions in this module."""


class ValidationError(BaseError):
    """Raise when trere are errors in schema"""


def _validate_schema(schema_doc, validator):
    errors = validator.iter_errors(schema_doc)

    for error in errors:
        error_id = ' > '.join(error.absolute_schema_path)
        if error_id == 'additionalProperties':
            error_id += ' ' + error.message.split('\'')[1]
        raise ValidationError(
            'Schema validation error. Message: {}\n'
            'Path: [{}]'.format(error.message, error_id),
        )

    return list(errors)


@pytest.fixture(scope='module', name='schema_validator')
def _schema_validator():
    validator = mongo_validator.get_validator(
        utils.load_yaml_with_definitions(consts.SCHEMA_VALIDATOR),
    )
    return validator


@pytest.mark.nofilldb()
@pytest.mark.parametrize('schema', utils.get_all_schemas_paths())
def test_mongo_schemas(schema, schema_validator):
    doc = utils.load_yaml(schema)
    assert not _validate_schema(doc, schema_validator)


@pytest.fixture(scope='module', name='jsonschema_validator')
def _jsonschema_validator():
    validator = mongo_validator.get_validator(
        utils.load_yaml(consts.JSONSCHEMA_VALIDATOR),
    )
    return validator


@pytest.mark.nofilldb()
@pytest.mark.parametrize('schema', utils.get_all_schemas_paths())
def test_mongo_jsonschemas(schema, jsonschema_validator):
    doc = utils.load_yaml(schema)
    jsonschema = doc.get('jsonschema', {})
    assert not _validate_schema(jsonschema, jsonschema_validator)

    indexes = doc.get('indexes', [])
    sharding = doc.get('sharding')
    if sharding:
        normalized_indexes = set(_normalize_index(i['key']) for i in indexes)
        sharding_key = _normalize_index(sharding['key'])
        assert (
            sharding_key in normalized_indexes
        ), 'Sharding key %r not found in indexes' % (sharding['key'])
        # check for unique indexes
        for index in indexes:
            assert not index.get(
                'unique',
            ), 'Unique index %r is not allowed in sharded collection' % (
                index,
            )


def _normalize_index(key):
    if isinstance(key, str):
        return (('name', key),)
    result = []
    for index in key:
        result.append(tuple(sorted(index.items())))
    return tuple(result)
