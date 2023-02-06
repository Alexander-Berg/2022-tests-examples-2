from typing import Dict
from typing import NamedTuple

import pytest

from configs_admin import exceptions
from configs_admin import storage


class Case(NamedTuple):
    data: Dict
    response_code: int = 200
    expected_response: Dict = {}
    db_schemas: str = 'db_success_group_schemas.json'
    db_schemas_history: str = 'db_success_group_schemas_history.json'
    db_configs: str = 'db_success_group_configs.json'
    db_configs_history: str = 'db_success_group_configs_history.json'
    db_meta: str = 'db_success_group_meta.json'
    headers: Dict = {'X-YaTaxi-Api-Key': 'secret'}
    is_fail_update: bool = False

    @classmethod
    def get_args(cls) -> str:
        return ','.join(cls.__annotations__.keys())  # pylint: disable=E1101


def sort_by_key(x):
    return x['_id']


def sort_by_name(x):
    return x['name']


@pytest.mark.parametrize(
    Case.get_args(),
    [
        pytest.param(
            *Case(
                data={
                    'schemas': {
                        'TEST': {
                            'name': 'TEST',
                            'default': 1,
                            'schema': {'type': 'number'},
                            'description': '',
                            'full_description': '',
                            'group': 'schemas',
                            'audit_namespace': 'taxi',
                        },
                    },
                    'group': 'schemas',
                    'actual_commit': (
                        'b805804d8b5ce277903492c549055f4b5a86ed0a'
                    ),
                    'new_commit': '321',
                },
                db_schemas='db_success_group_schemas_with_namespace.json',
                db_schemas_history=(
                    'db_success_group_schemas_history_with_namespace.json'
                ),
            ),
            id='success_update_schema_with_passesd_audit_namespace',
        ),
        pytest.param(
            *Case(
                data={
                    'schemas': {
                        'TEST': {
                            'name': 'TEST',
                            'default': 1,
                            'schema': {'type': 'number'},
                            'description': '',
                            'full_description': '',
                            'group': 'schemas',
                            'audit_namespace': 'unknown',
                        },
                    },
                    'group': 'schemas',
                    'actual_commit': (
                        'b805804d8b5ce277903492c549055f4b5a86ed0a'
                    ),
                    'new_commit': '321',
                },
                response_code=400,
                expected_response={
                    'code': 'NAMESPACE_DOES_NOT_EXIST',
                    'message': 'Provided namespace does not exist',
                },
                is_fail_update=True,
            ),
            id='fail_update_schema_with_unknown_audit_namespace',
        ),
        pytest.param(
            *Case(
                data={
                    'schemas': {
                        'TEST': {
                            'name': 'TEST',
                            'default': 1,
                            'schema': {'type': 'number'},
                            'description': '',
                            'full_description': '',
                            'group': 'schemas',
                            'audit_namespace': 'unknown',
                        },
                    },
                    'group': 'schemas',
                    'actual_commit': (
                        'b805804d8b5ce277903492c549055f4b5a86ed0a'
                    ),
                    'new_commit': '321',
                },
                response_code=403,
                expected_response={
                    'code': 'FORBIDDEN',
                    'message': 'Access is forbidden',
                    'details': {
                        'reason': 'X-YaTaxi-Api-Key header is missing',
                    },
                },
                is_fail_update=True,
                headers={},
            ),
            id='fail_update_schema_without_api_key',
        ),
        pytest.param(
            *Case(
                data={
                    'schemas': {
                        'TEST': {
                            'name': 'TEST',
                            'default': 1,
                            'schema': {'type': 'number'},
                            'description': '',
                            'full_description': '',
                            'group': 'schemas',
                            'audit_namespace': 'unknown',
                        },
                    },
                    'group': 'schemas',
                    'actual_commit': (
                        'b805804d8b5ce277903492c549055f4b5a86ed0a'
                    ),
                    'new_commit': '321',
                },
                response_code=403,
                expected_response={
                    'code': 'FORBIDDEN',
                    'message': 'Access is forbidden',
                    'details': {'reason': 'Invalid X-YaTaxi-Api-Key header'},
                },
                is_fail_update=True,
                headers={'X-YaTaxi-Api-Key': 'bad_secret'},
            ),
            id='fail_update_schema_with_bad_api_key',
        ),
        pytest.param(
            *Case(
                data={
                    'schemas': {
                        'TEST': {
                            'name': 'TEST',
                            'default': 1,
                            'schema': {'type': 'number'},
                            'description': '',
                            'full_description': '',
                            'group': 'schemas',
                            'audit_namespace': 'unknown',
                        },
                    },
                    'group': 'schemas',
                    'actual_commit': (
                        'b805804d8b5ce277903492c549055f4b5a86ed0a'
                    ),
                    'new_commit': '321',
                },
                db_schemas=(
                    'db_success_group_schemas_with_unknown_namespace.json'
                ),
                db_schemas_history=(
                    'db_success_group_schemas_history_'
                    'with_unknown_namespace.json'
                ),
            ),
            marks=pytest.mark.disable_check_namespace,
            id='success_update_schema_with_unknown_audit_namespace',
        ),
        pytest.param(
            *Case(
                data={
                    'schemas': {
                        'TEST': {
                            'name': 'TEST',
                            'default': 1,
                            'schema': {'type': 'number'},
                            'description': '',
                            'full_description': '',
                            'group': 'schemas',
                        },
                    },
                    'group': 'schemas',
                    'actual_commit': (
                        'b805804d8b5ce277903492c549055f4b5a86ed0a'
                    ),
                    'new_commit': '321',
                },
            ),
            id='success_update_schema_and_create_configs_values',
        ),
        pytest.param(
            *Case(
                data={
                    'schemas': {
                        'EXISTED': {
                            'name': 'EXISTED',
                            'default': 1,
                            'schema': {'type': 'number'},
                            'description': '',
                            'full_description': '',
                            'group': 'schemas',
                        },
                    },
                    'group': 'schemas',
                    'definitions': {},
                    'actual_commit': (
                        'b805804d8b5ce277903492c549055f4b5a86ed0a'
                    ),
                    'new_commit': '321',
                },
                db_schemas='db_success_2_group_schemas.json',
                db_schemas_history='db_success_2_group_schemas_history.json',
                db_configs='db_configs_no_changed.json',
                db_configs_history='db_configs_history_empty.json',
                db_meta='db_success_group_meta.json',
            ),
            id='success_update_schema_without_update_configs_values',
        ),
        pytest.param(
            *Case(
                data={
                    'schemas': {
                        'EXISTED': {
                            'name': 'EXISTED',
                            'default': 1,
                            'schema': {'type': 'string'},
                            'description': '',
                            'full_description': '',
                            'group': 'schemas',
                        },
                    },
                    'group': 'schemas',
                    'actual_commit': (
                        'b805804d8b5ce277903492c549055f4b5a86ed0a'
                    ),
                    'new_commit': '321',
                },
                is_fail_update=True,
                response_code=400,
                expected_response={
                    'code': 'VALIDATION_FAILED',
                    'message': 'Schemas of `schemas` has errors',
                    'details': {
                        'errors': [
                            {
                                'code': 'VALIDATION_FAILED',
                                'message': (
                                    'value for EXISTED '
                                    '(scope=default config value) '
                                    'is not valid: 1 '
                                    'is not of type \'string\''
                                ),
                                'status': 400,
                            },
                            {
                                'code': 'VALIDATION_FAILED',
                                'message': (
                                    'value for EXISTED '
                                    '(scope=main config value) '
                                    'is not valid: 4 '
                                    'is not of type \'string\''
                                ),
                                'status': 400,
                            },
                        ],
                    },
                },
            ),
            id='fail_update_schemas_by_validation_value',
        ),
        pytest.param(
            *Case(
                data={
                    'schemas': {
                        'TEST': {
                            'name': 'TEST',
                            'default': 1,
                            'schema': {'type': 'number'},
                            'description': '',
                            'full_description': '',
                            'group': 'schemas',
                        },
                    },
                    'group': 'schemas',
                    'actual_commit': (
                        'b805804d8b5ce277903492c549055f4b5a86ed0a'
                    ),
                    'new_commit': '321',
                },
                is_fail_update=True,
                response_code=409,
                expected_response={'code': 'CODE', 'message': 'message'},
            ),
            id='check restore',
        ),
        pytest.param(
            *Case(
                data={
                    'schemas': {
                        'TEST': {
                            'name': 'TEST',
                            'default': 1,
                            'validators': ['$integer'],
                            'description': '',
                            'full_description': '',
                            'group': 'schemas',
                        },
                    },
                    'group': 'schemas',
                    'actual_commit': (
                        'b805804d8b5ce277903492c549055f4b5a86ed0a'
                    ),
                    'new_commit': '321',
                },
                db_schemas='db_success_3_group_schemas.json',
                db_schemas_history='db_success_3_group_schemas_history.json',
            ),
            id='allow_validators',
        ),
        pytest.param(
            *Case(
                data={
                    'schemas': {
                        'TEST': {
                            'name': 'TEST',
                            'default': 1,
                            'description': '',
                            'full_description': '',
                            'group': 'schemas',
                            'tags': ['broken'],
                        },
                    },
                    'group': 'schemas',
                    'actual_commit': (
                        'b805804d8b5ce277903492c549055f4b5a86ed0a'
                    ),
                    'new_commit': '321',
                },
                db_schemas='db_success_4_group_schemas.json',
                db_schemas_history='db_success_4_group_schemas_history.json',
            ),
            id='success_update_broken_schema',
        ),
    ],
)
async def test(
        web_context,
        web_app_client,
        load_json,
        patch,
        data,
        response_code,
        expected_response,
        db_schemas,
        db_schemas_history,
        db_configs,
        db_configs_history,
        db_meta,
        headers,
        is_fail_update,
):
    if is_fail_update:

        @patch('configs_admin.db_wrappers.set_actual_commit')
        async def _handler(*args, **kwargs):
            raise exceptions.DbConflict(message='message', code='CODE')

    response = await web_app_client.post(
        '/v1/schemas/', headers=headers, json=data,
    )

    assert response.status == response_code, await response.text()
    assert await response.json() == expected_response
    if response_code != 200 and is_fail_update:
        return
    assert not is_fail_update, f'Must be fail: {await response.text()}'

    # check update meta
    docs_meta = await web_context.mongo.uconfigs_meta.find({}).to_list(None)
    for doc in docs_meta:
        doc.pop(storage.META_FIELDS.UPDATED)
    assert docs_meta == load_json(db_meta), db_meta

    # check schemas creation or update
    docs = await web_context.mongo.uconfigs_schemas.find({}).to_list(None)
    for doc in docs:
        doc.pop(storage.SCHEMA_FIELDS.UPDATED, None)
        if 'broken' in (doc.get(storage.SCHEMA_FIELDS.TAGS) or []):
            continue
        schema_or_validators = doc.get(
            storage.SCHEMA_FIELDS.SCHEMA,
        ) or doc.get(storage.SCHEMA_FIELDS.VALIDATORS)
        assert isinstance(schema_or_validators, str)
    assert sorted(docs, key=sort_by_key) == sorted(
        load_json(db_schemas), key=sort_by_key,
    ), f'{db_schemas}'

    # check schemas history
    docs = await web_context.mongo.uconfigs_schemas_history.find({}).to_list(
        None,
    )
    for doc in docs:
        doc.pop(storage.SCHEMA_HISTORY_FIELDS.ID, None)
        doc.pop(storage.SCHEMA_HISTORY_FIELDS.UPDATED, None)
        if 'broken' in doc.get(storage.SCHEMA_HISTORY_FIELDS.TAGS, []):
            continue
        schema_or_validators = doc.get(
            storage.SCHEMA_HISTORY_FIELDS.SCHEMA,
        ) or doc.get(storage.SCHEMA_HISTORY_FIELDS.VALIDATORS)
        assert isinstance(schema_or_validators, str)
    assert sorted(docs, key=sort_by_name) == sorted(
        load_json(db_schemas_history), key=sort_by_name,
    ), f'{db_schemas_history}'

    # check configs creation
    docs = await web_context.mongo.config.find({}).to_list(None)
    for doc in docs:
        doc.pop(storage.CONFIG_FIELDS.UPDATED, None)
    assert sorted(docs, key=sort_by_key) == sorted(
        load_json(db_configs), key=sort_by_key,
    )

    # check add fresh configs to history
    docs = await web_context.mongo.uconfigs_history.find({}).to_list(None)
    for doc in docs:
        doc.pop(storage.CONFIG_HISTORY_FIELDS.ID, None)
        doc.pop(storage.CONFIG_HISTORY_FIELDS.UPDATED, None)
        doc.pop(storage.CONFIG_HISTORY_FIELDS.collection_name, None)
    assert sorted(docs, key=sort_by_name) == sorted(
        load_json(db_configs_history), key=sort_by_name,
    )
