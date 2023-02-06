import copy
import datetime as dt
from typing import Any
from typing import Dict
from typing import Optional

import pytest
import pytz

from tests_segments_provider import quota_tools
from tests_segments_provider import shipment_tools


_TZ_MOSCOW = pytz.timezone('Europe/Moscow')

_NOW = dt.datetime(2021, 12, 14, 15, 0, 0).astimezone(_TZ_MOSCOW)
_NOW_PLUS_10_MIN = dt.datetime(2021, 12, 14, 15, 0, 10).astimezone(_TZ_MOSCOW)
_UPDATED_AT = dt.datetime(2021, 12, 14, 16, 0, 0).astimezone(_TZ_MOSCOW)
_START_AT_1 = dt.datetime(2021, 12, 14, 17, 0, 0).astimezone(_TZ_MOSCOW)
_START_AT_2 = dt.datetime(2021, 12, 14, 18, 0, 0).astimezone(_TZ_MOSCOW)

# sha256(tags.shipment_name)
_TAGS_TASK_ID = (
    '85335d4133d28c3b1b163aac8387bae71c4ff0d7c957216332b050cec58c8bf0'
)
# sha256(passenger-tags.new_shipment_name)
_PASSENGER_TAGS_TASK_ID = (
    '10d0e7c2ff8f57dfc2c57bb05c109df96539f09e82d9455f4cda402abab70ed3'
)


def normalized_datetime(value: dt.datetime):
    return value.astimezone(pytz.UTC)


def check_tags_providers_exists(pgsql, consumer_name: str, shipment_name: str):
    cursor = pgsql['segments_provider'].cursor()
    cursor.execute(
        f"""
        SELECT tags_providers.name
        FROM config.shipments
                JOIN config.consumers ON shipments.consumer_id = consumers.id
                JOIN config.tags_providers
                    ON shipments.tag_provider_id = tags_providers.id
        WHERE consumers.name = '{consumer_name}'
        AND shipments.name = '{shipment_name}'
        """,
    )
    rows = list(row for row in cursor)
    assert len(rows) == 1
    assert rows[0][0] == f'seagull_{shipment_name}'


_TAG_1 = 'tag1'
_TAG_2 = 'tag2'
_TAG_3 = 'tag3'
_TAG_4 = 'tag4'
_TAG_5 = 'tag5'
_TAG_6 = 'tag6'
_TAG_7 = 'tag7'

_TOPIC_1 = 'topic1'
_TOPIC_2 = 'topic2'
_TOPIC_3 = 'topic3'
_TOPIC_4 = 'topic4'

_TOPICS = [
    {
        'topic': _TOPIC_1,
        'tags': [_TAG_1, _TAG_2, _TAG_3, _TAG_4, _TAG_5],
        'acl': 'allowed',
        'is_financial': False,
        'is_audited': False,
    },
    {
        'topic': _TOPIC_2,
        'tags': [_TAG_5],
        'acl': 'prohibited',
        'is_financial': False,
        'is_audited': False,
    },
    {
        'topic': _TOPIC_3,
        'tags': [_TAG_6],
        'acl': 'allowed',
        'is_financial': True,
        'is_audited': False,
    },
    {
        'topic': _TOPIC_4,
        'tags': [_TAG_7],
        'acl': 'allowed',
        'is_financial': False,
        'is_audited': True,
    },
]


@pytest.mark.pgsql(
    'segments_provider',
    queries=[
        shipment_tools.get_shipment_insert_query(
            'passenger-tags',
            shipment_tools.DbShipment(
                name='shipment_name',
                ticket='A-2',
                maintainers=['developer'],
                is_enabled=False,
                labels=['CLICKHOUSE', 'passenger-tags'],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT_1,
                    unit=shipment_tools.UnitOfTime.SECONDS,
                    count=3600,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.CLICKHOUSE, 'SELECT 2',
                ),
                consumer=shipment_tools.TagsConsumerSettings([_TAG_3]),
                created_at=_NOW,
                updated_at=_UPDATED_AT,
                status=shipment_tools.Status.READY,
            ),
        ),
        shipment_tools.get_consumer_insert_query('tags'),
    ],
)
@pytest.mark.parametrize('language', ['en', 'ru'])  # translated & fallback
@pytest.mark.parametrize(
    'consumer, request_shipment, quota_requirements, quotas,'
    'expected_response_http_code, '
    'expected_error_response, expected_stq_arguments',
    [
        pytest.param(
            'tags',
            shipment_tools.Shipment(
                name='shipment_name',
                ticket='A-1',
                maintainers=['maintainer'],
                is_enabled=True,
                labels=[],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT_1,
                    unit=shipment_tools.UnitOfTime.HOURS,
                    count=2,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1,
                    '[_INSERT_HERE_]SELECT \'1\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    [_TAG_1, _TAG_2], 'udid',
                ),
            ),
            None,
            None,
            200,
            None,
            {
                'args': [],
                'eta': _NOW_PLUS_10_MIN.astimezone(pytz.UTC).replace(
                    tzinfo=None,
                ),
                'kwargs': {
                    'consumer_name': 'tags',
                    'shipment_name': 'shipment_name',
                },
                'queue': 'segments_shipment',
                'id': _TAGS_TASK_ID,
            },
            id='ok_insert_tags_yql',
        ),
        pytest.param(
            'tags',
            shipment_tools.Shipment(
                name='shipment_name',
                ticket='A-1',
                maintainers=['maintainer'],
                is_enabled=True,
                labels=[],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT_1,
                    unit=shipment_tools.UnitOfTime.HOURS,
                    count=2,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1,
                    '[_INSERT_HERE_]SELECT \'1\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    [_TAG_1, _TAG_2], 'udid',
                ),
                quotas=shipment_tools.Quotas(
                    owner='efficiency',
                    assignments={quota_tools.TAGS_COUNT: 10},
                ),
            ),
            quota_tools.DEFAULT_QUOTA_REQUIREMENTS,
            {
                'efficiency': {
                    quota_tools.TAGS_SHIPMENTS: 10,
                    quota_tools.TAGS_COUNT: 1000,
                },
            },
            200,
            None,
            {
                'args': [],
                'eta': _NOW_PLUS_10_MIN.astimezone(pytz.UTC).replace(
                    tzinfo=None,
                ),
                'kwargs': {
                    'consumer_name': 'tags',
                    'shipment_name': 'shipment_name',
                },
                'queue': 'segments_shipment',
                'id': _TAGS_TASK_ID,
            },
            id='ok_insert_tags_yql_with_quotas',
        ),
        pytest.param(
            'passenger-tags',
            shipment_tools.Shipment(
                name='new_shipment_name',
                ticket='A-2',
                maintainers=['maintainer'],
                is_enabled=False,
                labels=[],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT_2,
                    unit=shipment_tools.UnitOfTime.MINUTES,
                    count=30,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1,
                    '[_INSERT_HERE_]SELECT \'1\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings([_TAG_3]),
            ),
            None,
            None,
            200,
            None,
            {
                'args': [],
                'eta': _NOW_PLUS_10_MIN.astimezone(pytz.UTC).replace(
                    tzinfo=None,
                ),
                'kwargs': {
                    'consumer_name': 'passenger-tags',
                    'shipment_name': 'new_shipment_name',
                },
                'queue': 'segments_shipment',
                'id': _PASSENGER_TAGS_TASK_ID,
            },
            id='ok_insert_passenger_tags_yql',
        ),
        pytest.param(
            'passenger-tags',
            shipment_tools.Shipment(
                name='shipment_name',
                ticket='A-2',
                maintainers=[],
                is_enabled=False,
                labels=[],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT_2,
                    unit=shipment_tools.UnitOfTime.MINUTES,
                    count=30,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1,
                    '[_INSERT_HERE_]SELECT \'1\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings([_TAG_3]),
            ),
            None,
            None,
            409,
            {
                'code': 'SHIPMENT_EXISTS',
                'messages': {
                    'en': (
                        'Shipment shipment_name already exists for consumer '
                        'passenger-tags'
                    ),
                    'ru': (
                        'Shipment "shipment_name" already exists for consumer '
                        '"passenger-tags"'
                    ),
                },
            },
            None,
            id='conflict',
        ),
        pytest.param(
            'grocery-tags',
            shipment_tools.Shipment(
                name='shipment_name',
                ticket='A-2',
                maintainers=[],
                is_enabled=False,
                labels=[],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT_2,
                    unit=shipment_tools.UnitOfTime.MINUTES,
                    count=30,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1,
                    '[_INSERT_HERE_]SELECT \'1\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings([_TAG_3]),
            ),
            None,
            None,
            404,
            {
                'code': 'NOT_FOUND',
                'messages': {
                    'en': 'Consumer grocery-tags not found',
                    'ru': 'Consumer "grocery-tags" not found',
                },
            },
            None,
            id='unknown_consumer',
        ),
        pytest.param(
            'tags',
            shipment_tools.Shipment(
                name=' shipment, Карл',
                ticket='A-3',
                maintainers=['loginef'],
                is_enabled=False,
                labels=['SQLv1', 'tags', 'unimportant'],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT_2,
                    unit=shipment_tools.UnitOfTime.SECONDS,
                    count=2000,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1,
                    '[_INSERT_HERE_]SELECT \'2\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    [_TAG_3, _TAG_4], 'dbid_uuid',
                ),
            ),
            None,
            None,
            400,
            {
                'code': 'INVALID_SHIPMENT',
                'messages': {
                    'en': 'Shipment name " shipment, Карл" mismatch pattern',
                    'ru': (
                        'Shipment name " shipment, Карл" does not match '
                        'pattern. It can contain latin characters, digits, '
                        'hyphens and underscores only'
                    ),
                },
            },
            None,
            id='wrong_name',
        ),
        pytest.param(
            'tags',
            shipment_tools.Shipment(
                name='shipment_name',
                ticket='A-3',
                maintainers=['loginef'],
                is_enabled=True,
                labels=['SQLv1', 'tags', 'unimportant'],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT_2,
                    unit=shipment_tools.UnitOfTime.SECONDS,
                    count=2000,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1,
                    '[_INSERT_HERE_]SELECT \'2\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings([], 'dbid_uuid'),
            ),
            None,
            None,
            400,
            {
                'code': 'INVALID_SHIPMENT',
                'messages': {
                    'en': 'Empty tags list',
                    'ru': 'Tag names list must not be empty',
                },
            },
            None,
            id='empty_tag_names_list',
        ),
        pytest.param(
            'tags',
            shipment_tools.Shipment(
                name='shipment_name',
                ticket='A-3',
                maintainers=['loginef'],
                is_enabled=True,
                labels=['SQLv1', 'tags', 'unimportant'],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT_2,
                    unit=shipment_tools.UnitOfTime.SECONDS,
                    count=2000,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1,
                    '[_INSERT_HERE_]SELECT \'2\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    [_TAG_3, _TAG_5], 'dbid_uuid',
                ),
            ),
            None,
            None,
            400,
            {
                'code': 'INVALID_SHIPMENT',
                'messages': {
                    'en': 'Denied topics access: topic2',
                    'ru': 'User has no access to topics: topic2',
                },
            },
            None,
            id='prohibited_topic',
        ),
        pytest.param(
            'tags',
            shipment_tools.Shipment(
                name='shipment_name',
                ticket='A-3',
                maintainers=['loginef'],
                is_enabled=True,
                labels=['SQLv1', 'tags', 'unimportant'],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT_2,
                    unit=shipment_tools.UnitOfTime.SECONDS,
                    count=2000,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1,
                    '[_INSERT_HERE_]SELECT \'2\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    [_TAG_3, _TAG_6], 'dbid_uuid',
                ),
            ),
            None,
            None,
            400,
            {
                'code': 'INVALID_SHIPMENT',
                'messages': {
                    'en': 'Financial influence found: topic3',
                    'ru': 'Can not influence financial topics: topic3',
                },
            },
            None,
            id='financial_topic',
        ),
        pytest.param(
            'tags',
            shipment_tools.Shipment(
                name='shipment_name',
                ticket='A-3',
                maintainers=['loginef'],
                is_enabled=True,
                labels=['SQLv1', 'tags', 'unimportant'],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT_2,
                    unit=shipment_tools.UnitOfTime.SECONDS,
                    count=2000,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1,
                    '[_INSERT_HERE_]SELECT \'2\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    [_TAG_3, _TAG_7], 'dbid_uuid',
                ),
            ),
            None,
            None,
            400,
            {
                'code': 'INVALID_SHIPMENT',
                'messages': {
                    'en': 'Audited influence found: topic4',
                    'ru': 'Can not influence audited topics: topic4',
                },
            },
            None,
            id='audited_topic',
        ),
        pytest.param(
            'tags',
            shipment_tools.Shipment(
                name='shipment_name',
                ticket='A-3',
                maintainers=['loginef'],
                is_enabled=True,
                labels=['SQLv1', 'tags', 'unimportant'],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT_2,
                    unit=shipment_tools.UnitOfTime.SECONDS,
                    count=2000,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1,
                    '[_INSERT_HERE_]SELECT \'2\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    [_TAG_3, _TAG_4], 'corp_client_id',
                ),
            ),
            None,
            None,
            400,
            {
                'code': 'INVALID_SHIPMENT',
                'messages': {
                    'en': (
                        'Invalid entity type \'corp_client_id\' for consumer '
                        'tags'
                    ),
                    'ru': (
                        'Value \'corp_client_id\' is not parseable into '
                        'clients::tags::EntityType'
                    ),
                },
            },
            None,
            id='wrong_entity_type',
        ),
        pytest.param(
            'tags',
            shipment_tools.Shipment(
                name='shipment_name',
                ticket='A-3',
                maintainers=['loginef'],
                is_enabled=True,
                labels=['tags', 'unimportant'],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT_2,
                    unit=shipment_tools.UnitOfTime.SECONDS,
                    count=2000,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1,
                    '[_INSERT_HERE_]SELECT \'2\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    [_TAG_3, _TAG_4], 'unparsable entity type',
                ),
            ),
            None,
            None,
            400,
            {
                'code': 'INVALID_SHIPMENT',
                'messages': {
                    'en': (
                        'Invalid entity type \'unparsable entity type\' for'
                        ' consumer tags'
                    ),
                    'ru': (
                        'Value \'unparsable entity type\' is not parseable '
                        'into clients::tags::EntityType'
                    ),
                },
            },
            None,
            id='unparsable_entity_type',
        ),
        pytest.param(
            'tags',
            shipment_tools.Shipment(
                name='shipment_name',
                ticket='A-3',
                maintainers=['loginef'],
                is_enabled=True,
                labels=['tags', 'unimportant'],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT_2,
                    unit=shipment_tools.UnitOfTime.SECONDS,
                    count=2000,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.CLICKHOUSE,
                    '[_INSERT_HERE_]SELECT \'2\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings([_TAG_3, _TAG_4]),
            ),
            None,
            None,
            400,
            {
                'code': 'INVALID_SHIPMENT',
                'messages': {
                    'en': 'Query type not supported',
                    'ru': 'CHYT queries support not implemented',
                },
            },
            None,
            id='unsupported_syntax',
        ),
        pytest.param(
            'tags',
            shipment_tools.Shipment(
                name='shipment_name',
                ticket='A-3',
                maintainers=['loginef'],
                is_enabled=True,
                labels=['tags', 'unimportant'],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT_2,
                    unit=shipment_tools.UnitOfTime.SECONDS,
                    count=2000,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1, 'SELECT \'2\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings([_TAG_3, _TAG_4]),
            ),
            None,
            None,
            400,
            {
                'code': 'INVALID_SHIPMENT',
                'messages': {
                    'en': 'No placeholder [_INSERT_HERE_]',
                    'ru': 'Query doesn\'t contain placeholder [_INSERT_HERE_]',
                },
            },
            None,
            id='no_placeholder',
        ),
        pytest.param(
            'tags',
            shipment_tools.Shipment(
                name='shipment_name',
                ticket='A-1',
                maintainers=['maintainer'],
                is_enabled=True,
                labels=[],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT_1,
                    unit=shipment_tools.UnitOfTime.HOURS,
                    count=2,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1,
                    '[_INSERT_HERE_]SELECT \'1\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    [_TAG_1, _TAG_2], 'udid',
                ),
                quotas=shipment_tools.Quotas(
                    owner='efficiency', assignments={},
                ),
            ),
            quota_tools.DEFAULT_QUOTA_REQUIREMENTS,
            None,
            400,
            {
                'code': 'INVALID_SHIPMENT',
                'messages': {
                    'en': 'Required quota assignment for tags_count is absent',
                    'ru': 'Required quota assignment for tags_count is absent',
                },
            },
            None,
            id='bad_missing_quota_assignment',
        ),
        pytest.param(
            'tags',
            shipment_tools.Shipment(
                name='shipment_name',
                ticket='A-1',
                maintainers=['maintainer'],
                is_enabled=True,
                labels=[],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT_1,
                    unit=shipment_tools.UnitOfTime.HOURS,
                    count=2,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1,
                    '[_INSERT_HERE_]SELECT \'1\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    [_TAG_1, _TAG_2], 'udid',
                ),
                quotas=shipment_tools.Quotas(
                    owner='cargo', assignments={quota_tools.TAGS_COUNT: 10},
                ),
            ),
            quota_tools.DEFAULT_QUOTA_REQUIREMENTS,
            None,
            400,
            {
                'code': 'INVALID_SHIPMENT',
                'messages': {
                    'en': 'Non-existent quota tags_count with owner cargo',
                    'ru': 'Non-existent quota tags_count with owner cargo',
                },
            },
            None,
            id='bad_non_existent_quota',
        ),
        pytest.param(
            'tags',
            shipment_tools.Shipment(
                name='shipment_name',
                ticket='A-1',
                maintainers=['maintainer'],
                is_enabled=True,
                labels=[],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT_1,
                    unit=shipment_tools.UnitOfTime.HOURS,
                    count=2,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1,
                    '[_INSERT_HERE_]SELECT \'1\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    [_TAG_1, _TAG_2], 'udid',
                ),
                quotas=shipment_tools.Quotas(
                    owner='efficiency',
                    assignments={quota_tools.TAGS_COUNT: 100},
                ),
            ),
            quota_tools.DEFAULT_QUOTA_REQUIREMENTS,
            {
                'efficiency': {
                    quota_tools.TAGS_SHIPMENTS: 10,
                    quota_tools.TAGS_COUNT: 10,
                },
            },
            400,
            {
                'code': 'INVALID_SHIPMENT',
                'messages': {
                    'en': (
                        'Assignment for quota tags_count with owner '
                        'efficiency will exceed its limit'
                    ),
                    'ru': (
                        'Assignment for quota tags_count with owner '
                        'efficiency will exceed its limit'
                    ),
                },
            },
            None,
            id='bad_quota_will_exceed_limit',
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_shipment_create(
        taxi_segments_provider,
        pgsql,
        stq,
        mockserver,
        language: str,
        consumer: str,
        request_shipment: shipment_tools.Shipment,
        quota_requirements: Optional[Dict[str, str]],
        quotas: Optional[Dict[str, Dict[str, int]]],
        expected_response_http_code: int,
        expected_error_response: Optional[Dict[str, Any]],
        expected_stq_arguments: Optional[Dict[str, Any]],
):
    @mockserver.json_handler(f'/{consumer}/v1/admin/tags/topics_permissions')
    def _topics_permissions(request):
        def are_sets_intersecting(set1, set2):
            return bool(set1 & set2)

        topics = [
            topic
            for topic in _TOPICS
            if are_sets_intersecting(
                set(topic['tags']),
                set(request_shipment.consumer.allowed_tag_names),
            )
        ]
        return {'topics': topics}

    if quota_requirements:
        quota_tools.insert_requirements(pgsql, quota_requirements)
    if quotas:
        quota_tools.insert_quotas(pgsql, quotas)

    request_json = {'shipment': request_shipment.as_request_data()}

    # check draft validation

    response = await taxi_segments_provider.post(
        '/admin/v1/shipment/check-create',
        json=request_json,
        params={'consumer': consumer},
        headers={'X-Yandex-Login': 'loginef', 'Accept-Language': language},
    )
    assert response.status_code == expected_response_http_code
    if expected_error_response:
        assert response.json() == {
            'code': expected_error_response['code'],
            'message': expected_error_response['messages'][language],
        }
    else:
        draft_data = copy.deepcopy(request_json)
        draft_data['shipment']['schedule']['start_at'] = normalized_datetime(
            request_shipment.schedule.start_at,
        ).isoformat()

        assert response.json() == {
            'data': draft_data,
            # TODO change_doc_id
        }

    # check draft application

    response = await taxi_segments_provider.post(
        '/admin/v1/shipment/create',
        json=request_json,
        params={'consumer': consumer},
        headers={'X-Yandex-Login': 'loginef', 'Accept-Language': language},
    )
    assert response.status_code == expected_response_http_code
    if expected_error_response:
        assert response.json() == {
            'code': expected_error_response['code'],
            'message': expected_error_response['messages'][language],
        }
    else:
        assert response.json() == {}

        check_tags_providers_exists(pgsql, consumer, request_shipment.name)

        db_shipment = shipment_tools.find_shipment(
            pgsql, consumer, request_shipment.name,
        )
        expected_db_shipment = shipment_tools.DbShipment.from_api_shipment(
            shipment=request_shipment,
            created_at=_NOW,
            updated_at=_NOW,
            last_modifier='loginef',
            timezone=_TZ_MOSCOW,
            status=shipment_tools.Status.NEW,
        )
        assert db_shipment == expected_db_shipment

        if request_shipment.quotas:
            db_assignments = quota_tools.get_assignments(
                pgsql, request_shipment.name, consumer,
            )
            req_quotas = request_shipment.quotas
            assert req_quotas.owner in db_assignments
            for name, assignment in req_quotas.assignments.items():
                assert (
                    quota_tools.Assignment(name=name, value=assignment)
                    in db_assignments[req_quotas.owner]
                )
            # TODO: add implicit assignments check

        if quotas:
            quotas_usage = quota_tools.get_usage(pgsql, 'efficiency')
            assert quotas_usage == [
                quota_tools.Usage(name=quota_tools.TAGS_COUNT, usage=10),
                quota_tools.Usage(name=quota_tools.TAGS_SHIPMENTS, usage=1),
            ]
    if expected_stq_arguments:
        assert stq.segments_shipment.has_calls
        stq_args = stq.segments_shipment.next_call()
        del stq_args['kwargs']['log_extra']
        assert stq_args == expected_stq_arguments
    else:
        assert not stq.segments_shipment.has_calls
