# pylint: disable=protected-access

import json

import pytest

from config_schemas_lib import storage

META_FIELDS = storage.META_FIELDS
SCHEMA_FIELDS = storage.SCHEMA_FIELDS
DEFINITIONS_FIELDS = storage.DEFINITIONS_FIELDS


@pytest.mark.config(
    CONFIG_SCHEMAS_RUNTIME_FEATURES={'mongo_cache_schemas': 'enabled'},
)
async def test(web_app_client):
    config_schemas_cache = web_app_client.app['context'].config_schemas_cache
    await config_schemas_cache.refresh_cache()

    assert config_schemas_cache._actual_commit_hashes == {
        'CONFIG_SCHEMAS_META_ID': 'b805804d8b5ce277903492c549055f4b5a86ed0a',
        'billing': None,
        'chatterbox': None,
        'devicenotify': 'b805804d8b5ce277903492c549055f4b5a86ed0a',
        'devices': None,
        'tech': None,
    }
    assert sorted(config_schemas_cache.get_groups()) == [
        'billing',
        'chatterbox',
        'devicenotify',
        'devices',
        'tech',
    ]
    assert sorted(config_schemas_cache.get_all_config_names()) == [
        'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
        'CONFIG_WITH_DATE',
        'DEVICENOTIFY_USER_TTL',
        'DEVICENOTIFY_USER_TTL_WITH_COMMAND',
        'FRIEND_BRANDS',
        'SOME_CONFIG_WITH_DEFINITIONS',
        'TECHNICAL_CONFIG',
        'TECHNICAL_CONFIG_WITH_COMMAND',
        'TECHNICAL_CONFIG_WITH_COMMAND_AND_BLOCK_SELF_OK',
    ]
    assert config_schemas_cache.get_common_definitions() == {
        '/some_file.yaml': {'int': {'type': 'number'}},
        'some_file.yaml': {'int': {'type': 'number'}},
    }

    mongo_db = web_app_client.app['context'].mongo
    await mongo_db.uconfigs_meta.update(
        {META_FIELDS.DOC: 'other_group'},
        {'$set': {META_FIELDS.HASH: 'aaaaa'}},
        upsert=True,
    )
    await mongo_db.uconfigs_schemas.update(
        {SCHEMA_FIELDS.NAME: 'NEW_CONFIG_WITH_DEFINITIONS'},
        {
            '$set': {
                SCHEMA_FIELDS.SCHEMA: json.dumps(
                    {
                        'type': 'object',
                        'additionalProperties': {
                            '$ref': 'new_some_file.yaml/#definitions/obj',
                        },
                    },
                ),
                SCHEMA_FIELDS.DEFAULT: {'value': {'inner_value': 123}},
                SCHEMA_FIELDS.GROUP: 'other_group',
            },
        },
        upsert=True,
    )
    await mongo_db.uconfigs_meta.update(
        {META_FIELDS.DOC: 'CONFIG_SCHEMAS_META_ID'},
        {'$set': {META_FIELDS.HASH: 'aaaaa'}},
        upsert=True,
    )
    await mongo_db.uconfigs_schemas_definitions.update(
        {DEFINITIONS_FIELDS.NAME: 'new_some_file.yaml'},
        {
            '$set': {
                DEFINITIONS_FIELDS.SCHEMA: json.dumps(
                    {
                        'definitions': {
                            'obj': {
                                'type': 'object',
                                'additionalProperties': False,
                                'properties': {
                                    'inner_value': {'type': 'integer'},
                                },
                                'required': ['inner_value'],
                            },
                        },
                    },
                ),
            },
        },
        upsert=True,
    )

    await config_schemas_cache.refresh_cache()
    assert config_schemas_cache._actual_commit_hashes == {
        'CONFIG_SCHEMAS_META_ID': 'aaaaa',
        'billing': None,
        'chatterbox': None,
        'devicenotify': 'b805804d8b5ce277903492c549055f4b5a86ed0a',
        'devices': None,
        'tech': None,
        'other_group': 'aaaaa',
    }
    assert sorted(config_schemas_cache.get_groups()) == [
        'billing',
        'chatterbox',
        'devicenotify',
        'devices',
        'other_group',
        'tech',
    ]
    assert sorted(config_schemas_cache.get_all_config_names()) == [
        'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
        'CONFIG_WITH_DATE',
        'DEVICENOTIFY_USER_TTL',
        'DEVICENOTIFY_USER_TTL_WITH_COMMAND',
        'FRIEND_BRANDS',
        'NEW_CONFIG_WITH_DEFINITIONS',
        'SOME_CONFIG_WITH_DEFINITIONS',
        'TECHNICAL_CONFIG',
        'TECHNICAL_CONFIG_WITH_COMMAND',
        'TECHNICAL_CONFIG_WITH_COMMAND_AND_BLOCK_SELF_OK',
    ]
    assert config_schemas_cache.get_common_definitions() == {
        '/some_file.yaml': {'int': {'type': 'number'}},
        'some_file.yaml': {'int': {'type': 'number'}},
        '/new_some_file.yaml': {
            'definitions': {
                'obj': {
                    'additionalProperties': False,
                    'properties': {'inner_value': {'type': 'integer'}},
                    'required': ['inner_value'],
                    'type': 'object',
                },
            },
        },
        'new_some_file.yaml': {
            'definitions': {
                'obj': {
                    'additionalProperties': False,
                    'properties': {'inner_value': {'type': 'integer'}},
                    'required': ['inner_value'],
                    'type': 'object',
                },
            },
        },
    }
