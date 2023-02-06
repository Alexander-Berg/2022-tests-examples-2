import datetime
from typing import Any
from typing import List

import pytest

from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools


_OUTDATED = datetime.datetime(2011, 8, 29, 10, 54, 9)
_NOW = datetime.datetime(2011, 8, 30, 12, 45, 32)
_MINUTE_AGO = _NOW - datetime.timedelta(minutes=1)

_ENTITY_UDID = tags_tools.Entity(100, 'entity_udid', 'udid')
_ENTITY_PARK = tags_tools.Entity(101, 'park', 'park')
_TAG_NAME = tags_tools.TagName(1000, 'tag_name')
_REPOSITION = tags_tools.Provider(300, 'reposition', 'base service', True)
_REPOSITION_AUDITED = tags_tools.Provider(301, 'reposition_audited', '+', True)
_UDID_YQL = tags_tools.Provider(302, 'yql-udid-provider', '-', False)
_DBID_UUID_YQL = tags_tools.Provider(303, 'yql-dbid_uuid-provider', '+', True)
_TOPIC_BASIC = tags_tools.Topic(2000, 'basic-topic', False)
_TOPIC_FINANCIAL = tags_tools.Topic(2001, 'financial-topic', True)


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=[
        tags_tools.insert_entities([_ENTITY_UDID, _ENTITY_PARK]),
        tags_tools.insert_tag_names([_TAG_NAME]),
        tags_tools.insert_topics([_TOPIC_BASIC, _TOPIC_FINANCIAL]),
        tags_tools.insert_relations(
            [
                tags_tools.Relation(
                    _TAG_NAME.tag_name_id, _TOPIC_BASIC.topic_id,
                ),
            ],
        ),
        tags_tools.insert_providers(
            [_REPOSITION, _REPOSITION_AUDITED, _UDID_YQL, _DBID_UUID_YQL],
        ),
        tags_tools.insert_service_providers(
            [
                (
                    _REPOSITION.provider_id,
                    ['reposition', 'reposition_relocator'],
                    'base',
                ),
                (_REPOSITION_AUDITED.provider_id, ['reposition'], 'audited'),
            ],
        ),
        yql_tools.insert_queries(
            [
                # query without tag mentions (non-restricted, never financial)
                yql_tools.Query(
                    name='no-restriction-query',
                    provider_id=_UDID_YQL.provider_id,
                    tags=[],
                    changed='2018-08-30T12:34:56.0',
                    created='2018-08-30T12:34:56.0',
                    author='ivan',
                    last_modifier='ivan',
                    enabled=False,
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'pg_queries, tag_name, check_strictness, providers',
    [
        ([], 'non-existing-tag', 'account_active', []),
        ([], _TAG_NAME.name, 'account_active', []),
        (
            [  # yql query without any tags but with tag name in restriction
                # list
                yql_tools.insert_queries(
                    [
                        yql_tools.Query(
                            name='restricted-query',
                            provider_id=_DBID_UUID_YQL.provider_id,
                            tags=['tag_name', 'other_tag_name'],
                            changed='2018-08-30T12:34:56.0',
                            created='2018-08-30T12:34:56.0',
                        ),
                    ],
                ),
                yql_tools.insert_operation(
                    'op_applying',
                    _DBID_UUID_YQL.provider_id,
                    'dbid_uuid',
                    'downloading',
                    _MINUTE_AGO,
                ),
            ],
            _TAG_NAME.name,
            'account_active',
            [
                {
                    'name': _DBID_UUID_YQL.name,
                    'type': 'yql',
                    'authority': 'base',
                    'tags_count': 0,
                    'is_enabled': True,
                    'yql_query_info': {
                        'name': 'restricted-query',
                        'is_enabled': True,
                        'maintainers': ['petya', 'vasya'],
                        'last_run': {'status': 'running'},
                    },
                },
            ],
        ),
        (
            [  # make tag financial
                tags_tools.insert_relations(
                    [
                        tags_tools.Relation(
                            _TAG_NAME.tag_name_id, _TOPIC_FINANCIAL.topic_id,
                        ),
                    ],
                ),
                # yql query without any tags but with tag name in restriction
                # list
                yql_tools.insert_queries(
                    [
                        yql_tools.Query(
                            name='restricted-query',
                            provider_id=_DBID_UUID_YQL.provider_id,
                            tags=['tag_name', 'other_tag_name'],
                            changed='2018-08-30T12:34:56.0',
                            created='2018-08-30T12:34:56.0',
                        ),
                    ],
                ),
            ],
            _TAG_NAME.name,
            'account_active',
            [
                {
                    'name': _DBID_UUID_YQL.name,
                    'type': 'yql',
                    'authority': 'audited',
                    'tags_count': 0,
                    'is_enabled': True,
                    'yql_query_info': {
                        'name': 'restricted-query',
                        'is_enabled': True,
                        'maintainers': ['petya', 'vasya'],
                    },
                },
            ],
        ),
        (
            [
                # service provider with same tag
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag(
                            _TAG_NAME.tag_name_id,
                            _REPOSITION.provider_id,
                            _ENTITY_UDID.entity_id,
                            entity_type='udid',
                        ),
                    ],
                ),
            ],
            _TAG_NAME.name,
            'account_active',
            [
                {
                    'name': _REPOSITION.name,
                    'type': 'service',
                    'authority': 'base',
                    'tags_count': 1,
                    'is_enabled': True,
                },
            ],
        ),
        (
            [
                # audited service provider with same tag
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag(
                            _TAG_NAME.tag_name_id,
                            _REPOSITION_AUDITED.provider_id,
                            _ENTITY_UDID.entity_id,
                            entity_type='udid',
                        ),
                    ],
                ),
            ],
            _TAG_NAME.name,
            'account_active',
            [
                {
                    'name': _REPOSITION_AUDITED.name,
                    'type': 'service',
                    'authority': 'audited',
                    'tags_count': 1,
                    'is_enabled': True,
                },
            ],
        ),
        (
            [
                # provider with outdated tags do not count
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag(
                            _TAG_NAME.tag_name_id,
                            _REPOSITION.provider_id,
                            _ENTITY_UDID.entity_id,
                            entity_type='udid',
                            ttl=_OUTDATED,
                        ),
                    ],
                ),
            ],
            _TAG_NAME.name,
            'account_active',
            [],
        ),
        (
            [
                # provider with outdated tags DO count with this setting
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag(
                            _TAG_NAME.tag_name_id,
                            _REPOSITION.provider_id,
                            _ENTITY_UDID.entity_id,
                            entity_type='udid',
                            ttl=_OUTDATED,
                        ),
                    ],
                ),
            ],
            _TAG_NAME.name,
            'account_all',
            [
                {
                    'name': _REPOSITION.name,
                    'type': 'service',
                    'authority': 'base',
                    'tags_count': 1,
                    'is_enabled': True,
                },
            ],
        ),
        (
            [
                # query provided this tag earlier
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag(
                            _TAG_NAME.tag_name_id,
                            _UDID_YQL.provider_id,
                            _ENTITY_UDID.entity_id,
                        ),
                    ],
                ),
            ],
            _TAG_NAME.name,
            'account_active',
            [
                {
                    'name': _UDID_YQL.name,
                    'type': 'yql',
                    'authority': 'base',
                    'tags_count': 1,
                    'is_enabled': False,
                    'yql_query_info': {
                        'name': 'no-restriction-query',
                        'is_enabled': False,
                        'maintainers': ['ivan'],
                    },
                },
            ],
        ),
        (
            [  # make tag financial
                tags_tools.insert_relations(
                    [
                        tags_tools.Relation(
                            _TAG_NAME.tag_name_id, _TOPIC_FINANCIAL.topic_id,
                        ),
                    ],
                ),
                # query provided this tag earlier, but has no restrictions
                # that case is invariant corruption, because we can't allow
                # unrestricted's queries tags to be allowed into becoming
                # financial
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag(
                            _TAG_NAME.tag_name_id,
                            _UDID_YQL.provider_id,
                            _ENTITY_UDID.entity_id,
                        ),
                    ],
                ),
            ],
            _TAG_NAME.name,
            'account_active',
            [
                {
                    'name': _UDID_YQL.name,
                    'type': 'yql',
                    # this is a test that checks current behavior which is not
                    # right but that thing should never happen in production
                    'authority': 'audited',
                    'tags_count': 1,
                    'is_enabled': False,
                    'yql_query_info': {
                        'name': 'no-restriction-query',
                        'is_enabled': False,
                        'maintainers': ['ivan'],
                    },
                },
            ],
        ),
        pytest.param(
            [
                yql_tools.insert_queries(
                    [
                        yql_tools.Query(
                            name='restricted-query',
                            provider_id=_DBID_UUID_YQL.provider_id,
                            tags=[_TAG_NAME.name],
                            changed='2018-08-30T12:34:56.0',
                            created='2018-08-30T12:34:56.0',
                        ),
                    ],
                ),
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag(
                            _TAG_NAME.tag_name_id,
                            _REPOSITION.provider_id,
                            _ENTITY_UDID.entity_id,
                        ),
                        tags_tools.Tag(
                            _TAG_NAME.tag_name_id,
                            _REPOSITION.provider_id,
                            _ENTITY_PARK.entity_id,
                        ),
                        tags_tools.Tag(
                            _TAG_NAME.tag_name_id,
                            _REPOSITION_AUDITED.provider_id,
                            _ENTITY_UDID.entity_id,
                        ),
                        tags_tools.Tag(
                            _TAG_NAME.tag_name_id,
                            _DBID_UUID_YQL.provider_id,
                            _ENTITY_UDID.entity_id,
                        ),
                        tags_tools.Tag(
                            _TAG_NAME.tag_name_id,
                            _UDID_YQL.provider_id,
                            _ENTITY_UDID.entity_id,
                        ),
                        tags_tools.Tag(
                            _TAG_NAME.tag_name_id,
                            _UDID_YQL.provider_id,
                            _ENTITY_PARK.entity_id,
                        ),
                    ],
                ),
            ],
            _TAG_NAME.name,
            'account_all',
            [
                # sorting via (is_enabled, provider_type, tags_count)
                {
                    'name': _DBID_UUID_YQL.name,
                    'type': 'yql',
                    'authority': 'base',
                    'tags_count': 1,
                    'is_enabled': True,
                    'yql_query_info': {
                        'name': 'restricted-query',
                        'is_enabled': True,
                        'maintainers': ['petya', 'vasya'],
                    },
                },
                {
                    'name': _REPOSITION.name,
                    'type': 'service',
                    'authority': 'base',
                    'tags_count': 2,
                    'is_enabled': True,
                },
                {
                    'name': _REPOSITION_AUDITED.name,
                    'type': 'service',
                    'authority': 'audited',
                    'tags_count': 1,
                    'is_enabled': True,
                },
                # disabled providers come last
                {
                    'name': _UDID_YQL.name,
                    'type': 'yql',
                    'authority': 'base',
                    'tags_count': 2,
                    'is_enabled': False,
                    'yql_query_info': {
                        'name': 'no-restriction-query',
                        'is_enabled': False,
                        'maintainers': ['ivan'],
                    },
                },
            ],
            id='sorting_rules',
        ),
    ],
)
async def test_tag_providers(
        taxi_tags,
        pg_queries: List[str],
        tag_name: str,
        check_strictness: str,
        providers: List[Any],
        pgsql,
        taxi_config,
):
    if pg_queries:
        cursor = pgsql['tags'].cursor()
        for query in pg_queries:
            cursor.execute(query)

    taxi_config.set_values(
        dict(TAGS_PROVIDERS_CHECK_STRICTNESS=check_strictness),
    )
    await taxi_tags.invalidate_caches()

    response = await taxi_tags.get(
        f'v1/admin/tag/providers?tag_name={tag_name}',
    )
    assert response.status_code == 200
    assert response.json() == {'providers': providers}
