import json

import pytest

from configs_admin import db_wrappers
from configs_admin import storage
from configs_admin.generated.service.swagger.models.api import db_models

META_FIELDS = storage.META_FIELDS
SCHEMA_FIELDS = storage.SCHEMA_FIELDS

EMPTY_CLEANED = {
    'CONFIG_SCHEMAS_META_ID': 'aaaaa',
    'devicenotify': None,
    'new_group': None,
    'other_group': 'aaaaa',
}


@pytest.mark.now('2020-01-01')
async def test_cache(web_context, web_app_client, mocked_time):
    config_schemas_cache = web_context.config_schemas_cache

    assert config_schemas_cache.actual_commit_hashes == {
        'CONFIG_SCHEMAS_META_ID': 'b805804d8b5ce277903492c549055f4b5a86ed0a',
        'devicenotify': None,
        'first_name': '9055f4b5a86ed0ab805804d8b5ce277903492c54',
        'new_group': None,
    }
    assert sorted(config_schemas_cache.get_groups_names()) == [
        'devicenotify',
        'first_name',
        'new_group',
    ]
    assert sorted(config_schemas_cache.schemas_by_name) == [
        'A_FIRST_NAME',
        'BLOCKED_CONFIG',
        'DEVICENOTIFY_USER_TTL',
        'DEVICENOTIFY_USER_TTL_WITH_FAR_DEF',
        'FRIEND_BRANDS',
        'GET_GROUP',
        'SOME_CONFIG_BY_SERVICE',
        'SOME_CONFIG_BY_SERVICE_DISALLOWED',
    ]

    await db_wrappers.set_actual_commit(web_context, 'aaaaa', 'other_group')
    await db_wrappers.update_schemas(
        web_context,
        {
            'NEW_CONFIG_WITH_DEFINITIONS': db_models.SchemaEntity(
                schema=json.dumps(
                    {
                        'type': 'object',
                        'additionalProperties': {
                            '$ref': 'new_some_file.yaml/#definitions/obj',
                        },
                    },
                ),
                default={'value': {'inner_value': 123}},
                group='other_group',
                description='',
            ),
        },
    )
    await web_context.storage.schemas.remove_one('A_FIRST_NAME', None)
    count = await web_context.mongo.uconfigs_schemas.find(
        {'_id': 'A_FIRST_NAME'},
    ).count()
    assert not count
    config_schemas_cache.full_update_threshold = None

    await config_schemas_cache.refresh_cache()
    assert config_schemas_cache.actual_commit_hashes == {
        'CONFIG_SCHEMAS_META_ID': 'aaaaa',
        'devicenotify': None,
        'first_name': '9055f4b5a86ed0ab805804d8b5ce277903492c54',
        'new_group': None,
        'other_group': 'aaaaa',
    }, config_schemas_cache.actual_commit_hashes
    assert sorted(config_schemas_cache.get_groups_names()) == [
        'devicenotify',
        'first_name',
        'new_group',
        'other_group',
    ]
    assert (
        {
            group: sorted(schemas)
            for group, schemas in config_schemas_cache.schemas_by_group.items()
        }
        == {
            'devicenotify': [
                'BLOCKED_CONFIG',
                'DEVICENOTIFY_USER_TTL',
                'DEVICENOTIFY_USER_TTL_WITH_FAR_DEF',
                'FRIEND_BRANDS',
                'SOME_CONFIG_BY_SERVICE',
                'SOME_CONFIG_BY_SERVICE_DISALLOWED',
            ],
            'first_name': [],
            'new_group': ['GET_GROUP'],
            'other_group': ['NEW_CONFIG_WITH_DEFINITIONS'],
        }
    )
    assert (
        config_schemas_cache._schemas_by_name is None  # pylint: disable=W0212
    )
    assert sorted(config_schemas_cache.schemas_by_name) == [
        'BLOCKED_CONFIG',
        'DEVICENOTIFY_USER_TTL',
        'DEVICENOTIFY_USER_TTL_WITH_FAR_DEF',
        'FRIEND_BRANDS',
        'GET_GROUP',
        'NEW_CONFIG_WITH_DEFINITIONS',
        'SOME_CONFIG_BY_SERVICE',
        'SOME_CONFIG_BY_SERVICE_DISALLOWED',
    ]
