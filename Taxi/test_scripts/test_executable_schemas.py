# pylint: disable=invalid-name
import asyncio
import copy
import os

import jsonschema
import pytest
import yaml

import scripts.app
from scripts.internal import args_only_manager
from scripts.lib import executable_schemas


_SCHEMAS = executable_schemas.Schemas(
    os.path.join(scripts.app.BASE_DIR, 'executor_schemas'),
)
asyncio.run(_SCHEMAS.load())


@pytest.mark.parametrize(
    'schema_to_validate,is_valid',
    [
        ({}, False),
        ({'extra-key': 1}, False),
        ({'python': {'executable': 'python2'}}, True),
        ({'psql': {'executable': 'python2'}}, False),
        ({'psql': {'downloadable_executable': 'python2'}}, True),
        ({'python': {'envs': {'A': 'b'}}}, True),
        ({'envs': {'A': 'b'}}, False),
        ({'python': {'envs': {'A': 1}}}, False),
        ({'python': {'path': []}}, False),
        ({'python': {'pythonpath': []}}, False),
        (
            {
                'pgmigrate': {
                    'downloadable_executable': 'python',
                    'args_only': True,
                    'organization': 'some',
                },
            },
            True,
        ),
        (
            {
                'pgmigrate': {
                    'downloadable_executable': 'python',
                    'args_only': True,
                    'organization_from': {
                        'argument_name': 'some',
                        'strategy': {'name': 'some'},
                    },
                },
            },
            True,
        ),
        (
            {
                'pgmigrate': {
                    'downloadable_executable': 'python',
                    'args_only': True,
                },
            },
            False,
        ),
    ],
)
def test_check_validator_schema(schema_to_validate, is_valid):
    validator_schema = os.path.join(
        scripts.app.BASE_DIR, 'docs', 'executable_schema.yaml',
    )
    with open(validator_schema) as fp:
        validator_schema = yaml.safe_load(fp)
    jsonschema.Draft4Validator.check_schema(validator_schema)
    validator = jsonschema.Draft4Validator(validator_schema)

    if is_valid:
        validator.validate(schema_to_validate)
    else:
        with pytest.raises(jsonschema.ValidationError):
            validator.validate(schema_to_validate)


@pytest.mark.parametrize(
    'schema',
    [pytest.param(value, id=name) for name, value in _SCHEMAS.items()],
)
def test_executor_schemas(schema):
    validator_schema = os.path.join(
        scripts.app.BASE_DIR, 'docs', 'executable_schema.yaml',
    )
    with open(validator_schema) as fp:
        validator_schema = yaml.safe_load(fp)
    jsonschema.Draft4Validator.check_schema(validator_schema)
    validator = jsonschema.Draft4Validator(validator_schema)
    validator.validate(schema)


@pytest.mark.parametrize(
    'schema',
    [pytest.param(value, id=name) for name, value in _SCHEMAS.items()],
)
async def test_merged_executor_schemas(scripts_app, schema):
    validator_schema = os.path.join(
        scripts.app.BASE_DIR, 'docs', 'executable_schema.yaml',
    )
    executables_dir = os.path.join(
        scripts.app.BASE_DIR, '..', 'debian', 'scripts-executors',
    )
    with open(validator_schema) as fp:
        validator_schema = yaml.safe_load(fp)
    jsonschema.Draft4Validator.check_schema(validator_schema)
    validator = jsonschema.Draft4Validator(validator_schema)

    default = _SCHEMAS.default
    merged = copy.deepcopy(default)
    merged.update(schema)

    validator.validate(merged)
    for executor in merged.keys() - {'python', 'service_settings'}:
        executor_schema = merged[executor]
        executor_path = os.path.join(
            executables_dir, executor_schema['downloadable_executable'],
        )
        assert os.path.exists(executor_path)
        assert os.path.isfile(executor_path)

        if not executor_schema.get('args_only'):
            continue

        assert (
            len(
                {
                    'organization',
                    'organization_from',
                    'organization_from_service_name',
                }
                & executor_schema.keys(),
            )
            == 1
        )

        if executor_schema.get('organization_from'):
            if 'argument_name' in executor_schema['organization_from']:
                assert (
                    executor_schema['organization_from']['argument_name']
                    in executor_schema['required_arguments']
                )
            assert (
                executor_schema['organization_from']['strategy']['name']
                in args_only_manager.ORG_FROM_STRATEGIES
            )
            strategy_handler = args_only_manager.ORG_FROM_STRATEGIES[
                executor_schema['organization_from']['strategy']['name']
            ]
            kwargs = copy.deepcopy(
                executor_schema['organization_from']['strategy'],
            )
            kwargs.pop('name')
            # check if all params are presents in schema and acceptable
            await strategy_handler(scripts_app, 'some-val', **kwargs)
