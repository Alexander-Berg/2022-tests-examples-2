import pytest

from configs_admin import storage
from test_configs_admin.web.schemas import common


@pytest.mark.parametrize(
    common.Case.get_args(),
    [
        pytest.param(
            *common.Case(
                data={
                    'schemas': {},
                    'definitions': {
                        '/common/definition.yaml': {
                            'Value': {
                                'type': 'object',
                                'additionalProperties': False,
                                'properties': {
                                    'value': {
                                        'type': 'number',
                                        'minimum': 100,
                                    },
                                },
                            },
                        },
                    },
                    'actual_commit': (
                        'b805804d8b5ce277903492c549055f4b5a86ed0a'
                    ),
                    'new_commit': '321',
                },
            ),
            id='success update definition',
        ),
        pytest.param(
            *common.Case(
                data={
                    'schemas': {},
                    'definitions': {
                        '/common/definition.yaml': {
                            'Value': {
                                'type': 'object',
                                'additionalProperties': False,
                                'properties': {
                                    'value': {
                                        'type': 'number',
                                        'minimum': 1000,
                                    },
                                },
                            },
                        },
                    },
                    'actual_commit': (
                        'b805804d8b5ce277903492c549055f4b5a86ed0a'
                    ),
                    'new_commit': '321',
                },
            ),
            id='fail update definition',
        ),
        pytest.param(
            *common.Case(
                data={
                    'schemas': {
                        'TEST': {
                            'name': 'TEST',
                            'default': 1,
                            'schema': {'$ref': '/path/to_unknoun.yaml#/Value'},
                            'description': '',
                            'full_description': '',
                            'group': 'schemas',
                        },
                    },
                    'definitions': {},
                    'actual_commit': (
                        'b805804d8b5ce277903492c549055f4b5a86ed0a'
                    ),
                    'new_commit': '321',
                },
                response_code=400,
                expected_response={
                    'code': 'VALIDATION_FAILED',
                    'message': (
                        'Schemas of `CONFIG_SCHEMAS_META_ID` has errors'
                    ),
                    'details': {
                        'errors': [
                            {
                                'code': 'VALIDATION_FAILED',
                                'message': (
                                    'Bad reference in schema TEST: '
                                    'unknown url type: '
                                    '\'/path/to_unknoun.yaml\''
                                ),
                                'status': 400,
                            },
                        ],
                    },
                },
            ),
            id='fail_if_use_link_without_target',
        ),
    ],
)
async def test(
        web_context,
        web_app_client,
        data,
        not_existed_names,
        response_code,
        expected_response,
):
    response = await web_app_client.post(
        '/v1/schemas/', headers={'X-YaTaxi-Api-Key': 'secret'}, json=data,
    )

    assert response.status == response_code, await response.text()
    assert await response.json() == expected_response
    if response_code == 200:
        doc = await web_context.mongo.uconfigs_meta.find_one(
            {storage.META_FIELDS.DOC: storage.CONFIG_SCHEMAS_META_ID},
        )
        assert doc[storage.META_FIELDS.HASH] == data['new_commit']

        schema_names = data['schemas'].get('schemas')
        if schema_names:
            docs = await web_context.mongo.uconfigs_schemas.find(
                {storage.SCHEMA_FIELDS.NAME: {'$in': schema_names}},
            ).to_list(None)
            for doc in docs:
                name = doc[storage.SCHEMA_FIELDS.NAME]
                doc.pop(storage.SCHEMA_FIELDS.NAME)
                doc.pop(storage.SCHEMA_FIELDS.UPDATED)
                assert doc == data['schemas'][name]

        def_names = data['schemas'].get('definitions')
        if def_names:
            docs = await web_context.mongo.uconfigs_schemas_definitions.find(
                {storage.DEFINITIONS_FIELDS.NAME: {'$in': def_names}},
            ).to_list(None)
            for doc in docs:
                name = doc[storage.DEFINITIONS_FIELDS.NAME]
                assert doc == data['defintions'][name]
