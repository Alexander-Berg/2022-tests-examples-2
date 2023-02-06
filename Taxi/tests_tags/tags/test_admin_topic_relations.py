# pylint: disable=too-many-lines
import datetime
import json
import re
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from tests_tags.tags import acl_tools
from tests_tags.tags import constants
from tests_tags.tags import tags_select
from tests_tags.tags import tags_tools
from tests_tags.tags import yql_tools


_OUTDATED = datetime.datetime(2011, 8, 29, 10, 54, 9)
_ENTITY_UDID = tags_tools.Entity(100, 'entity_udid', 'udid')
_TAG_NAME = tags_tools.TagName(1000, 'tag_name')
_TAG_NAME_2 = tags_tools.TagName(1001, 'tag_name_2')
# never gonna be in database
_TAG_NAME_UNKNOWN = tags_tools.TagName(1002, 'tag_name_unknown')
_REPOSITION = tags_tools.Provider(300, 'reposition', 'base service', True)
_REPOSITION_AUDITED = tags_tools.Provider(301, 'reposition_audited', '+', True)
_UDID_YQL = tags_tools.Provider(302, 'yql-udid-provider', '-', True)
_DBID_UUID_YQL = tags_tools.Provider(303, 'yql-dbid_uuid-provider', '+', True)
_EFFICIENCY = tags_tools.Provider(304, 'efficiency', 'manual', True)
_TOPIC_BASIC = tags_tools.Topic(2000, 'basic-topic', is_financial=False)
_TOPIC_FINANCIAL = tags_tools.Topic(2001, 'financial-topic', is_financial=True)
_TOPIC_COMISSIONS = tags_tools.Topic(2002, 'comissions', is_financial=True)
_TOPIC_SECURED = tags_tools.Topic(2003, 'secured-topic', is_financial=False)
_TOPIC_FINANCIAL_SECURED = tags_tools.Topic(
    2004, 'financial-secured-topic', is_financial=True,
)

_ALLOWED = 'allowed'
_APPROVAL_REQUIRED = 'approval_required'
_PROHIBITED = 'prohibited'


_DEFAULT_QUERIES = [
    tags_tools.insert_entities([_ENTITY_UDID]),
    tags_tools.insert_tag_names([_TAG_NAME, _TAG_NAME_2]),
    tags_tools.insert_topics(
        [
            _TOPIC_BASIC,
            _TOPIC_FINANCIAL,
            _TOPIC_COMISSIONS,
            _TOPIC_SECURED,
            _TOPIC_FINANCIAL_SECURED,
        ],
    ),
    tags_tools.insert_providers(
        [
            _REPOSITION,
            _REPOSITION_AUDITED,
            _UDID_YQL,
            _DBID_UUID_YQL,
            _EFFICIENCY,
        ],
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
]


def _body(topic: tags_tools.Topic, tags: List[tags_tools.TagName]):
    return {'topic': topic.name, 'tags': [tag.name for tag in tags]}


async def _get_relations(taxi_tags, topic: tags_tools.Topic):
    response = await taxi_tags.get(f'v1/topics/items?topic={topic.name}')
    if response.status_code == 404:
        return []

    assert response.status_code == 200

    items = response.json()['items']
    tags = [relation['tag'] for relation in items]
    tags.sort()
    return tags


def _tag_names(tag_names: List[tags_tools.TagName]):
    return [it.name for it in tag_names]


def _tag_name_ids(tag_names: List[tags_tools.TagName]):
    return [it.tag_name_id for it in tag_names]


def _insert_yql(
        provider: tags_tools.Provider,
        restriction: List[tags_tools.TagName] = None,
):
    _restriction = restriction or []
    return yql_tools.insert_queries(
        [
            yql_tools.Query(
                name=provider.name,
                provider_id=provider.provider_id,
                tags=list(tag.name for tag in _restriction),
                author='ivanov',
                last_modifier='ivanov',
                created='2018-08-30T12:34:56.0',
                changed='2018-08-30T12:34:56.0',
            ),
        ],
    )


def _find_topics(db, tag_names: List[str]):
    cursor = db.cursor()
    cursor.execute(
        'SELECT meta.topics.name '
        'FROM meta.relations '
        'INNER JOIN meta.topics ON (meta.relations.topic_id = meta.topics.id) '
        'INNER JOIN meta.tag_names '
        'ON (meta.relations.tag_name_id = meta.tag_names.id) '
        'WHERE meta.tag_names.name = ANY(%s)',
        [tag_names],
    )
    return [row[0] for row in cursor.fetchall()]


def mock_endpoint(mockserver, action: str, tags: List[str], status_code=200):
    @mockserver.json_handler('/topic/endpoint')
    def topic_endpoint(request):
        assert 'Content-Type' in request.headers
        expected_content_type = 'application/json; charset=utf-8'
        assert request.headers['Content-Type'] == expected_content_type

        body = json.loads(request.get_data())
        assert body == {'action': action, 'tags': tags}

        response = {
            'permission': 'allowed' if status_code == 200 else 'prohibited',
            'details': {},
        }

        if status_code != 200:
            response['message'] = 'error message'
            response['details'] = {'errors': []}

        return mockserver.make_response(json.dumps(response), status=200)

    return topic_endpoint


@pytest.mark.nofilldb()
@pytest.mark.config(
    TAGS_YQL_AUDIT_RULES={
        'product_audit_rules': [
            {
                'name': 'security',
                'title': 'Tests security team',
                'topics': [_TOPIC_SECURED.name],
            },
        ],
    },
)
@pytest.mark.pgsql('tags', queries=_DEFAULT_QUERIES)
@pytest.mark.parametrize(
    'acl_enabled', [True, False], ids=['acl_on', 'acl_off'],
)
@pytest.mark.parametrize('is_finance', (True, False))
@pytest.mark.parametrize(
    'pg_queries, topic, tags, base_expected_code, base_expected_relations, '
    'finance_expected_code, finance_expected_relations, audit_group_name',
    [
        pytest.param(
            [],
            tags_tools.Topic(1379, 'unknown-topic', False),
            [_TAG_NAME],
            404,
            [],
            404,
            [],
            None,
            id='unknown-topic',
        ),
        pytest.param(
            [],
            _TOPIC_BASIC,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            None,
            id='non-financial-success',
        ),
        pytest.param(
            [],
            _TOPIC_FINANCIAL,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            'financial',
            id='financial-success',
        ),
        pytest.param(
            [
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag.from_instances(
                            _TAG_NAME, _REPOSITION, _ENTITY_UDID,
                        ),
                    ],
                ),
            ],
            _TOPIC_BASIC,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            None,
            id='tag-from-base-service-provider',
        ),
        pytest.param(
            [
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag.from_instances(
                            _TAG_NAME, _REPOSITION, _ENTITY_UDID,
                        ),
                    ],
                ),
            ],
            _TOPIC_FINANCIAL,
            [_TAG_NAME],
            403,
            [],
            403,
            [],
            'financial',
            id='reject-tag-from-base-service-provider',
        ),
        pytest.param(
            [
                tags_tools.insert_relations(
                    [
                        tags_tools.Relation(
                            _TAG_NAME.tag_name_id, _TOPIC_COMISSIONS.topic_id,
                        ),
                    ],
                ),
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag.from_instances(
                            _TAG_NAME, _REPOSITION, _ENTITY_UDID,
                        ),
                    ],
                ),
            ],
            _TOPIC_FINANCIAL,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            'financial',
            id='disable-check-since-tag-is-financial',
        ),
        pytest.param(
            [
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag.from_instances(
                            _TAG_NAME, _EFFICIENCY, _ENTITY_UDID,
                        ),
                    ],
                ),
            ],
            _TOPIC_BASIC,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            None,
            id='tag-from-manual-provider',
        ),
        pytest.param(
            [
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag.from_instances(
                            _TAG_NAME, _EFFICIENCY, _ENTITY_UDID,
                        ),
                    ],
                ),
            ],
            _TOPIC_FINANCIAL,
            [_TAG_NAME],
            403,
            [],
            200,
            [_TAG_NAME],
            'financial',
            id='tag-from-manual-provider-should-be-approved',
        ),
        pytest.param(
            [
                tags_tools.insert_relations(
                    [
                        tags_tools.Relation(
                            _TAG_NAME.tag_name_id, _TOPIC_COMISSIONS.topic_id,
                        ),
                    ],
                ),
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag.from_instances(
                            _TAG_NAME, _EFFICIENCY, _ENTITY_UDID,
                        ),
                    ],
                ),
            ],
            _TOPIC_FINANCIAL,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            'financial',
            id='tag-from-manual-provider-is-already-financial',
        ),
        pytest.param(
            [
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag.from_instances(
                            _TAG_NAME, _REPOSITION_AUDITED, _ENTITY_UDID,
                        ),
                    ],
                ),
            ],
            _TOPIC_BASIC,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            None,
            id='tag-from-audited-service-provider-into-non-financial',
        ),
        pytest.param(
            [
                # tag exists, uploaded from audited service provider
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag.from_instances(
                            _TAG_NAME, _REPOSITION_AUDITED, _ENTITY_UDID,
                        ),
                    ],
                ),
            ],
            _TOPIC_FINANCIAL,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            'financial',
            id='tag-from-audited-service-provider-into-financial',
        ),
        pytest.param(
            [
                _insert_yql(_UDID_YQL, restriction=[]),
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag.from_instances(
                            _TAG_NAME, _UDID_YQL, _ENTITY_UDID,
                        ),
                    ],
                ),
            ],
            _TOPIC_BASIC,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            None,
            id='tag-from-non-restricted-yql-query',
        ),
        pytest.param(
            [
                _insert_yql(_UDID_YQL, restriction=[]),
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag.from_instances(
                            _TAG_NAME, _UDID_YQL, _ENTITY_UDID,
                        ),
                    ],
                ),
            ],
            _TOPIC_FINANCIAL,
            [_TAG_NAME],
            403,
            [],
            403,
            [],
            'financial',
            id='reject-tag-from-non-restricted-yql-query',
        ),
        pytest.param(
            [_insert_yql(_DBID_UUID_YQL, restriction=[_TAG_NAME])],
            _TOPIC_BASIC,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            None,
            id='manifested-tag-from-yql',
        ),
        pytest.param(
            [_insert_yql(_DBID_UUID_YQL, restriction=[_TAG_NAME])],
            _TOPIC_FINANCIAL,
            [_TAG_NAME],
            403,
            [],
            200,
            [_TAG_NAME],
            'financial',
            id='manifested-tag-from-yql-should-be-approved',
        ),
        pytest.param(
            [
                _insert_yql(_UDID_YQL, restriction=[_TAG_NAME]),
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag.from_instances(
                            _TAG_NAME, _UDID_YQL, _ENTITY_UDID,
                        ),
                    ],
                ),
            ],
            _TOPIC_BASIC,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            None,
            id='manifested-and-uploaded-tag-from-yql',
        ),
        pytest.param(
            [
                _insert_yql(_DBID_UUID_YQL, restriction=[_TAG_NAME]),
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag.from_instances(
                            _TAG_NAME, _UDID_YQL, _ENTITY_UDID,
                        ),
                    ],
                ),
            ],
            _TOPIC_FINANCIAL,
            [_TAG_NAME],
            403,
            [],
            200,
            [_TAG_NAME],
            'financial',
            id='manifested-and-uploaded-tag-from-yql-should-be-approved',
        ),
        pytest.param(
            [],
            _TOPIC_SECURED,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            200,
            [_TAG_NAME],
            'security',
            id='endpoint-approved-append',
        ),
        pytest.param(
            [],
            _TOPIC_SECURED,
            [_TAG_NAME],
            403,
            [],
            403,
            [],
            None,
            id='endpoint-rejected-append',
        ),
    ],
)
async def test_append_relations(
        taxi_tags,
        pgsql,
        mockserver,
        taxi_config,
        is_finance: bool,
        pg_queries: List[str],
        topic: tags_tools.Topic,
        tags: List[tags_tools.TagName],
        base_expected_code: int,
        base_expected_relations: List[tags_tools.TagName],
        finance_expected_code: int,
        finance_expected_relations: List[tags_tools.TagName],
        acl_enabled: bool,
        audit_group_name: Optional[str],
):
    # dynamic mockserver url required
    pg_queries.append(
        tags_tools.insert_endpoints(
            [
                tags_tools.Endpoint(
                    topic=_TOPIC_SECURED,
                    tvm_service_name='tvm',
                    url=f'{mockserver.base_url}topic/endpoint',
                ),
            ],
        ),
    )
    tags_tools.apply_queries(pgsql['tags'], pg_queries)

    mock_endpoint(
        mockserver,
        action='append',
        tags=[tag.name for tag in tags],
        status_code=base_expected_code,
    )

    await acl_tools.toggle_acl_and_mock_allowed(
        taxi_tags, taxi_config, mockserver, acl_enabled,
    )

    expected_topic_names = _find_topics(pgsql['tags'], [t.name for t in tags])
    expected_topic_names.append(topic.name)

    body = _body(topic, tags)
    response = await taxi_tags.post(
        'v2/admin/finance/topics/check_items',
        body,
        headers=constants.TEST_LOGIN_HEADER,
    )
    assert response.status_code == finance_expected_code
    if response.status_code == 200:
        response_json = response.json()
        # check change_doc_id like 'topic_{name}_{uuid}'
        regexp = f'^topic_{topic.name}_[A-Za-z0-9]{{32}}$'
        change_doc_id = response_json.get('change_doc_id', None)
        assert re.match(regexp, change_doc_id) is not None
        expected_data = body
        if audit_group_name:
            expected_data['audit_group_name'] = audit_group_name
        assert response_json['data'] == expected_data
        assert response_json['lock_ids'] == []

    suffix = '/finance' if is_finance else ''
    response = await taxi_tags.post(
        f'v2/admin{suffix}/topics/items',
        body,
        headers=constants.TEST_LOGIN_HEADER,
    )
    expected_code = finance_expected_code if is_finance else base_expected_code
    assert response.status_code == expected_code

    expected_relations = (
        finance_expected_relations if is_finance else base_expected_relations
    )
    assert await _get_relations(taxi_tags, topic) == _tag_names(
        expected_relations,
    )

    rows = tags_select.select_table_named(
        'service.topics_tags_update_queue', 'tag_name_id', pgsql['tags'],
    )
    tag_name_ids = [row['tag_name_id'] for row in rows]
    assert tag_name_ids == _tag_name_ids(expected_relations)


@pytest.mark.config(TAGS_ACL_TOPICS_ENABLED=True)
@pytest.mark.parametrize('is_finance', (True, False))
@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', queries=_DEFAULT_QUERIES)
@pytest.mark.parametrize(
    'pg_queries, topic, tags, expected_topics',
    [
        pytest.param(
            [],
            _TOPIC_SECURED,
            [_TAG_NAME],
            [_TOPIC_SECURED.name],
            id='topic prohibited, tag allowed',
        ),
        pytest.param(
            [
                tags_tools.insert_relations(
                    [
                        tags_tools.Relation(
                            _TAG_NAME.tag_name_id, _TOPIC_SECURED.topic_id,
                        ),
                    ],
                ),
            ],
            _TOPIC_BASIC,
            [_TAG_NAME],
            [_TOPIC_BASIC.name, _TOPIC_SECURED.name],
            id='topic prohibited, tag in different prohibited topic',
        ),
    ],
)
async def test_append_relations_acl_prohibited(
        taxi_tags,
        pgsql,
        mockserver,
        pg_queries: List[str],
        topic: tags_tools.Topic,
        tags: List[tags_tools.TagName],
        is_finance: bool,
        expected_topics: List[str],
):
    tags_tools.apply_queries(pgsql['tags'], pg_queries)

    mock_acl = acl_tools.make_mock_acl_prohibited(
        mockserver, constants.TEST_LOGIN, expected_topics,
    )

    body = _body(topic, tags)

    response = await taxi_tags.post(
        'v2/admin/finance/topics/check_items',
        body,
        headers=constants.TEST_LOGIN_HEADER,
    )

    assert response.status_code == 403
    assert mock_acl.times_called == 1

    suffix = '/finance' if is_finance else ''
    response = await taxi_tags.post(
        f'v2/admin{suffix}/topics/items',
        body,
        headers=constants.TEST_LOGIN_HEADER,
    )

    assert response.status_code == 403
    assert mock_acl.times_called == 2

    rows = tags_select.select_table_named(
        'service.topics_tags_update_queue', 'tag_name_id', pgsql['tags'],
    )
    assert rows == []


@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', queries=_DEFAULT_QUERIES)
@pytest.mark.parametrize(
    'pg_queries, topic, tags',
    [
        pytest.param(
            [], _TOPIC_BASIC, [], id='attempt to remove empty list of tags',
        ),
        pytest.param(
            [], _TOPIC_BASIC, [_TAG_NAME], id='remove non-existing relation',
        ),
        pytest.param(
            [
                tags_tools.insert_relations(
                    [
                        tags_tools.Relation(
                            _TAG_NAME.tag_name_id, _TOPIC_BASIC.topic_id,
                        ),
                    ],
                ),
            ],
            _TOPIC_BASIC,
            [_TAG_NAME],
            id='remove existing relation',
        ),
        pytest.param(
            [
                tags_tools.insert_relations(
                    [
                        tags_tools.Relation(
                            _TAG_NAME.tag_name_id, _TOPIC_FINANCIAL.topic_id,
                        ),
                    ],
                ),
            ],
            _TOPIC_FINANCIAL,
            [_TAG_NAME],
            id='remove existing relation from financial topic',
        ),
        pytest.param(
            [
                tags_tools.insert_relations(
                    [
                        tags_tools.Relation(
                            _TAG_NAME.tag_name_id, _TOPIC_FINANCIAL.topic_id,
                        ),
                        tags_tools.Relation(
                            _TAG_NAME.tag_name_id, _TOPIC_BASIC.topic_id,
                        ),
                    ],
                ),
            ],
            _TOPIC_BASIC,
            [_TAG_NAME],
            id=(
                'remove existing relation of basic topic'
                'and financial tag given'
            ),
        ),
    ],
)
async def test_remove_relations(
        taxi_tags,
        pgsql,
        mockserver,
        pg_queries: List[str],
        topic: tags_tools.Topic,
        tags: List[tags_tools.TagName],
):
    # dynamic mockserver url required
    pg_queries.append(
        tags_tools.insert_endpoints(
            [
                tags_tools.Endpoint(
                    topic=_TOPIC_FINANCIAL,
                    tvm_service_name='tvm',
                    url=f'{mockserver.base_url}topic/endpoint',
                ),
            ],
        ),
    )
    tags_tools.apply_queries(pgsql['tags'], pg_queries)

    mock_endpoint(
        mockserver, action='remove', tags=_tag_names(tags), status_code=200,
    )

    response = await taxi_tags.post(
        'v2/admin/topics/delete_items',
        _body(topic, tags),
        headers=constants.TEST_LOGIN_HEADER,
    )
    assert response.status_code == 200
    assert await _get_relations(taxi_tags, topic) == []


@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', queries=_DEFAULT_QUERIES)
@pytest.mark.parametrize(
    'add_relation, topic, tags, topics_policy, excepted_tags_update',
    [
        # attempt to remove empty list of tags
        (False, _TOPIC_BASIC, [], None, []),
        # remove non-existing relation
        (False, _TOPIC_BASIC, [_TAG_NAME], None, []),
        # remove existing relation
        (False, _TOPIC_BASIC, [_TAG_NAME_2], None, [_TAG_NAME_2]),
        # remove existing relation with whitelist
        (False, _TOPIC_BASIC, [_TAG_NAME_2], 'non_cached', []),
        # remove financial relation
        (False, _TOPIC_FINANCIAL, [_TAG_NAME], None, [_TAG_NAME]),
        # attempt to add empty list of tags
        (True, _TOPIC_BASIC, [], None, []),
        # add relations
        (True, _TOPIC_BASIC, [_TAG_NAME], None, [_TAG_NAME]),
        # add relations with no whitelist exception
        (True, _TOPIC_BASIC, [_TAG_NAME], 'cached', [_TAG_NAME]),
        # add relations with whitelist exception
        (True, _TOPIC_BASIC, [_TAG_NAME], 'non_cached', []),
    ],
)
async def test_edit_relations_tags_update(
        taxi_tags,
        pgsql,
        mockserver,
        add_relation: bool,
        topic: tags_tools.Topic,
        tags: List[tags_tools.TagName],
        topics_policy: str,
        excepted_tags_update: List[tags_tools.TagName],
        taxi_config,
):
    tags_tools.apply_queries(
        pgsql['tags'],
        [
            tags_tools.insert_endpoints(
                [
                    tags_tools.Endpoint(
                        topic=_TOPIC_FINANCIAL,
                        tvm_service_name='tvm',
                        url=f'{mockserver.base_url}topic/endpoint',
                    ),
                ],
            ),
            tags_tools.insert_relations(
                [
                    tags_tools.Relation(
                        _TAG_NAME_2.tag_name_id, _TOPIC_BASIC.topic_id,
                    ),
                    tags_tools.Relation(
                        _TAG_NAME.tag_name_id, _TOPIC_FINANCIAL.topic_id,
                    ),
                ],
            ),
        ],
    )

    if topics_policy is not None:
        taxi_config.set_values(
            dict(
                TAGS_TOPICS_POLICY={
                    '__default__': 'cached',
                    topic.name: topics_policy,
                },
            ),
        )
        await taxi_tags.invalidate_caches()

    mock_endpoint(
        mockserver, action='remove', tags=_tag_names(tags), status_code=200,
    )
    query = (
        'v2/admin/topics/items'
        if add_relation
        else 'v2/admin/topics/delete_items'
    )
    response = await taxi_tags.post(
        query, _body(topic, tags), headers=constants.TEST_LOGIN_HEADER,
    )
    assert response.status_code == 200

    rows = tags_select.select_table_named(
        'service.topics_tags_update_queue', 'tag_name_id', pgsql['tags'],
    )
    tag_name_ids = [row['tag_name_id'] for row in rows]
    assert tag_name_ids == _tag_name_ids(excepted_tags_update)


@pytest.mark.nofilldb()
@pytest.mark.config(
    TAGS_YQL_AUDIT_RULES={
        'product_audit_rules': [
            {
                'name': 'security',
                'title': 'Tests security team',
                'topics': [_TOPIC_SECURED.name],
            },
        ],
    },
)
@pytest.mark.pgsql('tags', queries=_DEFAULT_QUERIES)
@pytest.mark.parametrize(
    'product_audit_required, expected_code', [(False, 200), (True, 403)],
)
async def test_edit_audited_relations(
        taxi_tags,
        mockserver,
        product_audit_required: bool,
        expected_code: int,
        taxi_config,
):
    taxi_config.set_values(
        dict(TAGS_PRODUCT_AUDIT_TMP={'is_required': product_audit_required}),
    )
    await taxi_tags.invalidate_caches()

    topic = _TOPIC_SECURED
    tags = [_TAG_NAME]
    mock_endpoint(
        mockserver, action='remove', tags=_tag_names(tags), status_code=200,
    )
    for query in ['v2/admin/topics/items', 'v2/admin/topics/delete_items']:
        response = await taxi_tags.post(
            query, _body(topic, tags), headers=constants.TEST_LOGIN_HEADER,
        )
        assert response.status_code == expected_code


@pytest.mark.nofilldb()
@pytest.mark.pgsql(
    'tags',
    queries=(
        _DEFAULT_QUERIES
        + [
            tags_tools.insert_relations(
                [
                    tags_tools.Relation(
                        _TAG_NAME.tag_name_id, _TOPIC_BASIC.topic_id,
                    ),
                ],
            ),
        ]
    ),
)
@pytest.mark.parametrize(
    'topic, tags, expected_code, expected_topics, acl_enabled, acl_allowed',
    [
        pytest.param(
            _TOPIC_BASIC,
            [_TAG_NAME],
            200,
            [_TOPIC_BASIC.name],
            True,
            True,
            id='topic allowed',
        ),
        pytest.param(
            _TOPIC_BASIC,
            [_TAG_NAME],
            403,
            [_TOPIC_BASIC.name],
            True,
            False,
            id='topic prohibited, tag in that topic',
        ),
        pytest.param(
            _TOPIC_SECURED,
            [_TAG_NAME],
            403,
            [_TOPIC_SECURED.name],
            True,
            False,
            id='topic prohibited, tag prohibited, but tag no need check',
        ),
        pytest.param(
            _TOPIC_SECURED,
            [_TAG_NAME],
            200,
            [_TOPIC_SECURED.name],
            False,
            False,
            id='topic prohibited, acl disabled',
        ),
    ],
)
async def test_remove_relations_acl(
        taxi_tags,
        pgsql,
        mockserver,
        taxi_config,
        topic: tags_tools.Topic,
        tags: List[tags_tools.TagName],
        expected_code: int,
        expected_topics: List[str],
        acl_enabled: bool,
        acl_allowed: bool,
):
    await acl_tools.toggle_acl(taxi_tags, taxi_config, acl_enabled)

    if acl_allowed:
        mock_acl = acl_tools.make_mock_acl_allowed(mockserver)
    else:
        mock_acl = acl_tools.make_mock_acl_prohibited(
            mockserver, constants.TEST_LOGIN, expected_topics, expected_topics,
        )

    response = await taxi_tags.post(
        'v2/admin/topics/delete_items',
        _body(topic, tags),
        headers=constants.TEST_LOGIN_HEADER,
    )
    assert response.status_code == expected_code

    assert mock_acl.times_called == int(acl_enabled)


@pytest.mark.nofilldb()
@pytest.mark.config(
    TAGS_ACL_TOPICS_ENABLED=True,
    TAGS_YQL_AUDIT_RULES={
        'product_audit_rules': [
            {
                'name': 'security',
                'title': 'Tests security team',
                'topics': [_TOPIC_SECURED.name],
            },
        ],
    },
)
@pytest.mark.pgsql('tags', queries=_DEFAULT_QUERIES)
@pytest.mark.parametrize(
    'topic, tags, expected_code, audit_group_name',
    [
        pytest.param(
            _TOPIC_BASIC,
            [_TAG_NAME],
            200,
            None,
            id='not financial no endpoint allowed',
        ),
        pytest.param(
            _TOPIC_SECURED,
            [_TAG_NAME],
            200,
            'security',
            id='not financial verified by endpoint',
        ),
        pytest.param(
            _TOPIC_SECURED,
            [_TAG_NAME],
            403,
            None,
            id='not financial rejected by endpoint',
        ),
        pytest.param(
            _TOPIC_FINANCIAL,
            [_TAG_NAME],
            403,
            None,
            id='financial no endpoint forbidden',
        ),
        pytest.param(
            _TOPIC_FINANCIAL_SECURED,
            [_TAG_NAME],
            200,
            'financial',
            id='financial verified by endpoint',
        ),
        pytest.param(
            _TOPIC_FINANCIAL_SECURED,
            [_TAG_NAME],
            403,
            None,
            id='financial rejected by endpoint',
        ),
    ],
)
async def test_remove_relations_validation(
        taxi_tags,
        pgsql,
        mockserver,
        topic: tags_tools.Topic,
        tags: List[tags_tools.TagName],
        expected_code: int,
        audit_group_name: Optional[str],
):
    # dynamic mockserver url required
    pg_queries: List[str] = [
        tags_tools.insert_relations(
            [tags_tools.Relation(_TAG_NAME.tag_name_id, topic.topic_id)],
        ),
        tags_tools.insert_endpoints(
            [
                tags_tools.Endpoint(
                    topic=_TOPIC_SECURED,
                    tvm_service_name='tvm',
                    url=f'{mockserver.base_url}topic/endpoint',
                ),
                tags_tools.Endpoint(
                    topic=_TOPIC_FINANCIAL_SECURED,
                    tvm_service_name='tvm',
                    url=f'{mockserver.base_url}topic/endpoint',
                ),
            ],
        ),
    ]

    tags_tools.apply_queries(pgsql['tags'], pg_queries)

    acl_tools.make_mock_acl_allowed(mockserver)

    mock_endpoint(
        mockserver,
        action='remove',
        tags=_tag_names(tags),
        status_code=expected_code,
    )

    body = _body(topic, tags)

    response = await taxi_tags.post(
        'v2/admin/topics/delete/check_items',
        body,
        headers=constants.TEST_LOGIN_HEADER,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        response_json = response.json()
        # check change_doc_id like 'topic_{name}_{uuid}'
        regexp = f'^topic_{topic.name}_[A-Za-z0-9]{{32}}$'
        change_doc_id = response_json.get('change_doc_id', None)
        assert re.match(regexp, change_doc_id) is not None
        expected_data = body
        if audit_group_name:
            expected_data['audit_group_name'] = audit_group_name
        assert response_json['data'] == expected_data

    response = await taxi_tags.post(
        'v2/admin/topics/delete_items',
        _body(topic, tags),
        headers=constants.TEST_LOGIN_HEADER,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        assert await _get_relations(taxi_tags, topic) == _tag_names([])
    else:
        assert await _get_relations(taxi_tags, topic) == _tag_names(
            [_TAG_NAME],
        )

    excepted_tag_name_ids = _tag_name_ids(tags) if expected_code == 200 else []
    rows = tags_select.select_table_named(
        'service.topics_tags_update_queue', 'tag_name_id', pgsql['tags'],
    )
    tag_name_ids = [row['tag_name_id'] for row in rows]
    assert tag_name_ids == excepted_tag_name_ids


class Notice:
    def __init__(
            self,
            permission: str,
            tag_name: tags_tools.TagName,
            provider: tags_tools.Provider,
            provider_type: str,
            authority: str,
            tags_count: int,
    ):
        self.permission = permission
        self.tag_name = tag_name.name
        self.provider = provider.name
        self.provider_type = provider_type
        self.authority = authority
        self.tags_count = tags_count

    def message(self):
        return (
            f'tag \'{self.tag_name}\' has provider \'{self.provider}\' '
            f'of type {self.provider_type} with {self.authority} authority '
            f'and {self.tags_count} mentions'
        )


class NoticeAclTopicsByTag:
    def __init__(self, permission: str, tag_name: str, topic_names: List[str]):
        self.permission = permission
        self.tag_name = tag_name
        self.topic_names = topic_names

    def message(self):
        return (
            f'tag {self.tag_name} is in acl prohibited '
            f'topics: {", ".join(str(t) for t in self.topic_names)}'
        )


class NoticeAclTopic:
    def __init__(self, permission: str, topic_name: str):
        self.permission = permission
        self.topic_name = topic_name

    def message(self):
        return f'acl prohibited topic: {self.topic_name}'


class NoticeAclUnknown:
    def __init__(self):
        self.permission = _PROHIBITED

    def message(self):
        return 'prohibited by unknown acl reason'


class NoticeValidateEndpoint:
    def __init__(self):
        self.permission = _PROHIBITED

    def message(self):
        return (
            'endpoint tvm forbade the operation with message "error message"'
        )


def _permission(permission: str, notices):
    return {
        'permission': permission,
        'notices': [
            {'level': notice.permission, 'message': notice.message()}
            for notice in notices
        ],
    }


@pytest.mark.parametrize(
    'acl_enabled', [True, False], ids=['acl_on', 'acl_off'],
)
@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', queries=_DEFAULT_QUERIES)
@pytest.mark.parametrize(
    'pg_queries, topic, tags, expected_code, expected_response',
    [
        # unknown topic
        ([], tags_tools.Topic(1379, 'unknown', False), [_TAG_NAME], 404, None),
        # no providers for basic topic
        ([], _TOPIC_BASIC, [_TAG_NAME], 200, _permission(_ALLOWED, [])),
        # no providers for financial topic
        ([], _TOPIC_COMISSIONS, [_TAG_NAME], 200, _permission(_ALLOWED, [])),
        (
            [
                # tag exists, uploaded from base service provider
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag.from_instances(
                            _TAG_NAME, _REPOSITION, _ENTITY_UDID,
                        ),
                    ],
                ),
            ],
            _TOPIC_BASIC,
            [_TAG_NAME],
            200,
            _permission(
                _ALLOWED,
                [
                    Notice(
                        _ALLOWED, _TAG_NAME, _REPOSITION, 'service', 'base', 1,
                    ),
                ],
            ),
        ),
        (
            [
                # this service provider can't be approved so result is
                # PROHIBITED
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag.from_instances(
                            _TAG_NAME, _REPOSITION, _ENTITY_UDID,
                        ),
                    ],
                ),
                # this service provider is already audited and is ALLOWED
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag.from_instances(
                            _TAG_NAME, _REPOSITION_AUDITED, _ENTITY_UDID,
                        ),
                    ],
                ),
                # tag name is manifested by yql query that can be approved
                _insert_yql(_DBID_UUID_YQL, restriction=[_TAG_NAME]),
            ],
            _TOPIC_FINANCIAL,
            [_TAG_NAME],
            200,
            _permission(
                _PROHIBITED,
                [
                    Notice(
                        _ALLOWED,
                        _TAG_NAME,
                        _REPOSITION_AUDITED,
                        'service',
                        'audited',
                        1,
                    ),
                    Notice(
                        _APPROVAL_REQUIRED,
                        _TAG_NAME,
                        _DBID_UUID_YQL,
                        'yql',
                        'base',
                        0,
                    ),
                    Notice(
                        _PROHIBITED,
                        _TAG_NAME,
                        _REPOSITION,
                        'service',
                        'base',
                        1,
                    ),
                ],
            ),
        ),
        (
            [
                # this service provider is already audited and is ALLOWED
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag.from_instances(
                            _TAG_NAME, _REPOSITION_AUDITED, _ENTITY_UDID,
                        ),
                    ],
                ),
                # tag name is manifested by yql query that can be approved
                _insert_yql(_DBID_UUID_YQL, restriction=[_TAG_NAME]),
                # tag name was uploaded from yql query without restrictions
                _insert_yql(_UDID_YQL, restriction=[]),
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
            _TOPIC_FINANCIAL,
            [_TAG_NAME_UNKNOWN, _TAG_NAME],
            200,
            _permission(
                _PROHIBITED,
                [
                    Notice(
                        _ALLOWED,
                        _TAG_NAME,
                        _REPOSITION_AUDITED,
                        'service',
                        'audited',
                        1,
                    ),
                    Notice(
                        _APPROVAL_REQUIRED,
                        _TAG_NAME,
                        _DBID_UUID_YQL,
                        'yql',
                        'base',
                        0,
                    ),
                    Notice(
                        _PROHIBITED, _TAG_NAME, _UDID_YQL, 'yql', 'base', 1,
                    ),
                ],
            ),
        ),
        (
            [
                # this service provider is already audited and is ALLOWED
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag.from_instances(
                            _TAG_NAME_2, _REPOSITION_AUDITED, _ENTITY_UDID,
                        ),
                    ],
                ),
                # this query can be approved
                _insert_yql(_UDID_YQL, restriction=[_TAG_NAME]),
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
            _TOPIC_FINANCIAL,
            [_TAG_NAME, _TAG_NAME_2],
            200,
            _permission(
                _APPROVAL_REQUIRED,
                [
                    Notice(
                        _ALLOWED,
                        _TAG_NAME_2,
                        _REPOSITION_AUDITED,
                        'service',
                        'audited',
                        1,
                    ),
                    Notice(
                        _APPROVAL_REQUIRED,
                        _TAG_NAME,
                        _UDID_YQL,
                        'yql',
                        'base',
                        1,
                    ),
                ],
            ),
        ),
        (
            [
                # this query only mentioned second tag name
                _insert_yql(_UDID_YQL, restriction=[_TAG_NAME_2]),
                # but has uploaded the first tag name
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
            _TOPIC_FINANCIAL,
            [_TAG_NAME_2, _TAG_NAME],
            200,
            _permission(
                _PROHIBITED,
                [
                    # mentioned from yql without
                    Notice(
                        _APPROVAL_REQUIRED,
                        _TAG_NAME_2,
                        _UDID_YQL,
                        'yql',
                        'base',
                        0,
                    ),
                    Notice(
                        _PROHIBITED, _TAG_NAME, _UDID_YQL, 'yql', 'base', 1,
                    ),
                ],
            ),
        ),
        (
            [
                # this yql should be approved for tag name to become financial
                _insert_yql(_UDID_YQL, restriction=[_TAG_NAME]),
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag(
                            _TAG_NAME.tag_name_id,
                            _UDID_YQL.provider_id,
                            _ENTITY_UDID.entity_id,
                        ),
                    ],
                ),
                # but since it's already linked with this topic,
                # no action needed
                tags_tools.insert_relations(
                    [
                        tags_tools.Relation(
                            _TAG_NAME.tag_name_id, _TOPIC_FINANCIAL.topic_id,
                        ),
                    ],
                ),
            ],
            _TOPIC_FINANCIAL,
            [_TAG_NAME_2, _TAG_NAME],
            200,
            _permission(_ALLOWED, []),
        ),
        (
            [
                # this yql should be approved for tag name to become financial
                _insert_yql(_UDID_YQL, restriction=[_TAG_NAME]),
                tags_tools.insert_tags(
                    [
                        tags_tools.Tag(
                            _TAG_NAME.tag_name_id,
                            _UDID_YQL.provider_id,
                            _ENTITY_UDID.entity_id,
                        ),
                    ],
                ),
                # but since it's already linked with financial topic,
                # it's allowed
                tags_tools.insert_relations(
                    [
                        tags_tools.Relation(
                            _TAG_NAME.tag_name_id, _TOPIC_COMISSIONS.topic_id,
                        ),
                    ],
                ),
            ],
            _TOPIC_FINANCIAL,
            [_TAG_NAME_2, _TAG_NAME],
            200,
            _permission(
                _ALLOWED,
                [
                    # only mention that this tag already has that yql
                    Notice(
                        _ALLOWED, _TAG_NAME, _UDID_YQL, 'yql', 'audited', 1,
                    ),
                ],
            ),
        ),
    ],
)
async def test_permissions_check(
        taxi_tags,
        pgsql,
        pg_queries: List[str],
        topic: tags_tools.Topic,
        tags: List[tags_tools.TagName],
        expected_code: int,
        expected_response: Dict,
        mockserver,
        taxi_config,
        acl_enabled,
):
    tags_tools.apply_queries(pgsql['tags'], pg_queries)
    await acl_tools.toggle_acl_and_mock_allowed(
        taxi_tags, taxi_config, mockserver, acl_enabled,
    )
    response = await taxi_tags.post(
        'v2/admin/topics/permissions/check',
        _body(topic, tags),
        headers=constants.TEST_LOGIN_HEADER,
    )
    assert response.status_code == expected_code
    if expected_response is not None:
        response = response.json()
        response['notices'].sort(key=lambda notice: notice['level'])
        assert response == expected_response


@pytest.mark.config(TAGS_ACL_TOPICS_ENABLED=True)
@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', queries=_DEFAULT_QUERIES)
@pytest.mark.parametrize(
    'pg_queries, topic, tags, expected_topics, '
    'prohibited_topics, expected_response',
    [
        pytest.param(
            [],
            _TOPIC_BASIC,
            [_TAG_NAME],
            [_TOPIC_BASIC.name],
            [],
            _permission(_PROHIBITED, [NoticeAclUnknown()]),
            id='prohibited topic, allowed tag, empty prohibited response',
        ),
        pytest.param(
            [],
            _TOPIC_BASIC,
            [_TAG_NAME],
            [_TOPIC_BASIC.name],
            [_TOPIC_BASIC.name],
            _permission(
                _PROHIBITED, [NoticeAclTopic(_PROHIBITED, _TOPIC_BASIC.name)],
            ),
            id='prohibited topic, allowed tag',
        ),
        pytest.param(
            [
                tags_tools.insert_relations(
                    [
                        tags_tools.Relation(
                            _TAG_NAME.tag_name_id, _TOPIC_BASIC.topic_id,
                        ),
                    ],
                ),
            ],
            _TOPIC_BASIC,
            [_TAG_NAME],
            [_TOPIC_BASIC.name],
            [_TOPIC_BASIC.name],
            _permission(
                _PROHIBITED,
                [
                    NoticeAclTopic(_PROHIBITED, _TOPIC_BASIC.name),
                    NoticeAclTopicsByTag(
                        _PROHIBITED, _TAG_NAME.name, [_TOPIC_BASIC.name],
                    ),
                ],
            ),
            id='prohibited topic, prohibited tag in same topic',
        ),
        pytest.param(
            [
                tags_tools.insert_relations(
                    [
                        tags_tools.Relation(
                            _TAG_NAME.tag_name_id, _TOPIC_SECURED.topic_id,
                        ),
                    ],
                ),
            ],
            _TOPIC_BASIC,
            [_TAG_NAME],
            [_TOPIC_BASIC.name, _TOPIC_SECURED.name],
            [_TOPIC_BASIC.name, _TOPIC_SECURED.name],
            _permission(
                _PROHIBITED,
                [
                    NoticeAclTopic(_PROHIBITED, _TOPIC_BASIC.name),
                    NoticeAclTopicsByTag(
                        _PROHIBITED, _TAG_NAME.name, [_TOPIC_SECURED.name],
                    ),
                ],
            ),
            id='prohibited topic, prohibited tag in topic',
        ),
        pytest.param(
            [
                tags_tools.insert_relations(
                    [
                        tags_tools.Relation(
                            _TAG_NAME.tag_name_id, _TOPIC_SECURED.topic_id,
                        ),
                        tags_tools.Relation(
                            _TAG_NAME_2.tag_name_id, _TOPIC_BASIC.topic_id,
                        ),
                        tags_tools.Relation(
                            _TAG_NAME_2.tag_name_id, _TOPIC_SECURED.topic_id,
                        ),
                    ],
                ),
            ],
            _TOPIC_BASIC,
            [_TAG_NAME, _TAG_NAME_2],
            [_TOPIC_BASIC.name, _TOPIC_SECURED.name],
            [_TOPIC_BASIC.name, _TOPIC_SECURED.name],
            _permission(
                _PROHIBITED,
                [
                    NoticeAclTopic(_PROHIBITED, _TOPIC_BASIC.name),
                    NoticeAclTopicsByTag(
                        _PROHIBITED, _TAG_NAME.name, [_TOPIC_SECURED.name],
                    ),
                    NoticeAclTopicsByTag(
                        _PROHIBITED,
                        _TAG_NAME_2.name,
                        [_TOPIC_BASIC.name, _TOPIC_SECURED.name],
                    ),
                ],
            ),
            id='prohibited topic, multiple prohibited tags',
        ),
    ],
)
async def test_permissions_check_acl_prohibbited(
        taxi_tags,
        pgsql,
        pg_queries: List[str],
        topic: tags_tools.Topic,
        tags: List[tags_tools.TagName],
        expected_topics,
        expected_response: Dict,
        prohibited_topics,
        mockserver,
):
    tags_tools.apply_queries(pgsql['tags'], pg_queries)
    mock_acl = acl_tools.make_mock_acl_prohibited(
        mockserver, constants.TEST_LOGIN, expected_topics, prohibited_topics,
    )
    response = await taxi_tags.post(
        'v2/admin/topics/permissions/check',
        _body(topic, tags),
        headers=constants.TEST_LOGIN_HEADER,
    )
    assert response.status_code == 200
    assert mock_acl.times_called == 1

    if expected_response is not None:
        response = response.json()
        response['notices'].sort(key=lambda notice: notice['message'])
        expected_response['notices'].sort(key=lambda notice: notice['message'])
        assert response == expected_response


@pytest.mark.parametrize(
    'acl_enabled', [True, False], ids=['acl_on', 'acl_off'],
)
@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', queries=_DEFAULT_QUERIES)
@pytest.mark.parametrize(
    'pg_queries, topic, tags, endpoint_response, expected_response',
    [
        pytest.param(
            [],
            _TOPIC_BASIC,
            [_TAG_NAME, _TAG_NAME_2],
            403,
            _permission(_ALLOWED, []),
            id='basic topic',
        ),
        pytest.param(
            [],
            _TOPIC_SECURED,
            [_TAG_NAME, _TAG_NAME_2],
            200,
            _permission(_ALLOWED, []),
            id='secured topic, allowed',
        ),
        pytest.param(
            [],
            _TOPIC_SECURED,
            [_TAG_NAME, _TAG_NAME_2],
            403,
            _permission(_PROHIBITED, [NoticeValidateEndpoint()]),
            id='secured topic, prohibited',
        ),
    ],
)
async def test_permissions_check_validate_endpoint(
        taxi_tags,
        pgsql,
        pg_queries: List[str],
        topic: tags_tools.Topic,
        tags: List[tags_tools.TagName],
        endpoint_response: Dict[str, Any],
        expected_response: Dict[str, Any],
        mockserver,
        taxi_config,
        acl_enabled: bool,
):
    await acl_tools.toggle_acl_and_mock_allowed(
        taxi_tags, taxi_config, mockserver, acl_enabled,
    )

    # dynamic mockserver url required
    pg_queries.append(
        tags_tools.insert_endpoints(
            [
                tags_tools.Endpoint(
                    topic=_TOPIC_SECURED,
                    tvm_service_name='tvm',
                    url=f'{mockserver.base_url}topic/endpoint',
                ),
            ],
        ),
    )
    tags_tools.apply_queries(pgsql['tags'], pg_queries)

    mock_endpoint(
        mockserver,
        action='append',
        tags=[tag.name for tag in tags],
        status_code=endpoint_response,
    )

    response = await taxi_tags.post(
        'v2/admin/topics/permissions/check',
        _body(topic, tags),
        headers=constants.TEST_LOGIN_HEADER,
    )

    assert response.status_code == 200

    if expected_response is not None:
        response = response.json()
        response['notices'].sort(key=lambda notice: notice['message'])
        expected_response['notices'].sort(key=lambda notice: notice['message'])
        assert response == expected_response
