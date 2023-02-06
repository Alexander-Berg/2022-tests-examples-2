import datetime as dt
from typing import Any
from typing import Dict
from typing import List

import pytest
import pytz

from tests_segments_provider import shipment_tools

_TZ_MOSCOW = pytz.timezone('Europe/Moscow')

_START_AT = dt.datetime(2021, 12, 14, 17, 0, 0).astimezone(_TZ_MOSCOW)

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


def mock_topics_permissions(mockserver, allowed_tag_names: List[str]):
    @mockserver.json_handler('/tags/v1/admin/tags/topics_permissions')
    def topics_permissions(request):
        def are_sets_intersecting(set1, set2):
            return bool(set1 & set2)

        topics = [
            topic
            for topic in _TOPICS
            if are_sets_intersecting(
                set(topic['tags']), set(allowed_tag_names),
            )
        ]
        return {'topics': topics}

    return topics_permissions


@pytest.mark.pgsql(
    'segments_provider',
    queries=[shipment_tools.get_consumer_insert_query('tags')],
)
@pytest.mark.parametrize(
    'request_shipment, expected_decision, expected_hints',
    [
        pytest.param(
            shipment_tools.Shipment(
                name=' shipment, Карл',
                ticket='A-3',
                maintainers=['loginef'],
                is_enabled=False,
                labels=['SQLv1', 'tags', 'unimportant'],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT,
                    unit=shipment_tools.UnitOfTime.SECONDS,
                    count=2000,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.CLICKHOUSE,
                    '[_INSERT_HERE_]SELECT \'2\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    [_TAG_3, _TAG_4], 'dbid_uuid',
                ),
            ),
            'rejected',
            [
                {
                    'name': 'name',
                    'level': 'error',
                    'hint': (
                        'Shipment name " shipment, Карл" does not match '
                        'pattern. It can contain latin characters, digits, '
                        'hyphens and underscores only'
                    ),
                },
                {
                    'name': 'source.syntax',
                    'level': 'error',
                    'hint': 'CHYT queries support not implemented',
                },
            ],
            id='name_and_syntax',
        ),
    ],
)
async def test_shipment_review_create(
        taxi_segments_provider,
        mockserver,
        request_shipment: shipment_tools.Shipment,
        expected_decision: str,
        expected_hints: List[Dict[str, Any]],
):
    mock_topics_permissions(
        mockserver, request_shipment.consumer.allowed_tag_names,
    )

    response = await taxi_segments_provider.post(
        '/admin/v1/shipment/review?consumer=tags',
        json={'shipment': request_shipment.as_request_data()},
        headers={'X-Yandex-Login': 'loginef', 'Accept-Language': 'ru'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'decision': 'denied',
        'is_audit_required': False,
        'audit_groups': [],
        'fields': expected_hints,
    }


@pytest.mark.pgsql(
    'segments_provider',
    queries=[
        shipment_tools.get_consumer_insert_query('tags'),
        shipment_tools.get_shipment_insert_query(
            'tags',
            shipment_tools.DbShipment(
                name='shipment_name',
                ticket='A-4',
                maintainers=['loginef'],
                is_enabled=True,
                labels=['SQLv1', 'tags', 'unimportant'],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT,
                    unit=shipment_tools.UnitOfTime.SECONDS,
                    count=2001,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1,
                    '[_INSERT_HERE_]SELECT \'3\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    [_TAG_1, _TAG_2], 'dbid_uuid',
                ),
                created_at=_START_AT,
                updated_at=_START_AT,
                status=shipment_tools.Status.READY,
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'request_shipment, expected_decision, expected_hints',
    [
        pytest.param(
            shipment_tools.Shipment(
                name='shipment_name',
                ticket='A-3',
                maintainers=['loginef'],
                is_enabled=False,
                labels=['SQLv1', 'tags', 'unimportant'],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT,
                    unit=shipment_tools.UnitOfTime.SECONDS,
                    count=2000,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.CLICKHOUSE,
                    '[_INSERT_HERE_]SELECT \'2\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    [_TAG_3, _TAG_4], 'dbid_uuid',
                ),
            ),
            'rejected',
            [
                {
                    'name': 'source.syntax',
                    'level': 'error',
                    'hint': 'Syntax changing not supported',
                },
                {
                    'name': 'source.syntax',
                    'level': 'error',
                    'hint': 'CHYT queries support not implemented',
                },
            ],
            id='name_and_syntax',
        ),
    ],
)
async def test_shipment_review_edit(
        taxi_segments_provider,
        mockserver,
        request_shipment: shipment_tools.Shipment,
        expected_decision: str,
        expected_hints: List[Dict[str, Any]],
):
    mock_topics_permissions(
        mockserver, request_shipment.consumer.allowed_tag_names,
    )

    response = await taxi_segments_provider.post(
        '/admin/v1/shipment/review?consumer=tags',
        json={'shipment': request_shipment.as_request_data()},
        headers={'X-Yandex-Login': 'loginef', 'Accept-Language': 'ru'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'decision': 'denied',
        'is_audit_required': False,
        'audit_groups': [],
        'fields': expected_hints,
    }


@pytest.mark.pgsql(
    'segments_provider',
    queries=[shipment_tools.get_consumer_insert_query('tags')],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(id='create'),
        pytest.param(
            marks=[
                pytest.mark.pgsql(
                    'segments_provider',
                    queries=[
                        shipment_tools.get_shipment_insert_query(
                            'tags',
                            shipment_tools.DbShipment(
                                name='shipment_name',
                                ticket='A-4',
                                maintainers=['loginef'],
                                is_enabled=True,
                                labels=['SQLv1', 'tags', 'unimportant'],
                                schedule=shipment_tools.Schedule(
                                    start_at=_START_AT,
                                    unit=shipment_tools.UnitOfTime.SECONDS,
                                    count=2001,
                                ),
                                source=shipment_tools.YqlQuery(
                                    shipment_tools.YqlSyntax.SQLv1,
                                    '[_INSERT_HERE_]SELECT \'3\' as tag;',
                                ),
                                consumer=shipment_tools.TagsConsumerSettings(
                                    [_TAG_1, _TAG_2], 'dbid_uuid',
                                ),
                                created_at=_START_AT,
                                updated_at=_START_AT,
                                status=shipment_tools.Status.READY,
                            ),
                        ),
                    ],
                ),
            ],
            id='edit',
        ),
    ],
)
@pytest.mark.parametrize(
    'request_shipment, expected_decision, expected_hints',
    [
        pytest.param(
            shipment_tools.Shipment(
                name='shipment_name',
                ticket='A-3',
                maintainers=['loginef'],
                is_enabled=True,
                labels=['SQLv1', 'tags', 'unimportant'],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT,
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
            'allowed',
            [],
            id='allowed',
        ),
        pytest.param(
            shipment_tools.Shipment(
                name='shipment_name',
                ticket='A-3',
                maintainers=['loginef'],
                is_enabled=True,
                labels=['SQLv1', 'tags', 'unimportant'],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT,
                    unit=shipment_tools.UnitOfTime.SECONDS,
                    count=2000,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1, 'SELECT \'2\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    [_TAG_5, _TAG_4], 'dbid_uuid_clid_phid',
                ),
            ),
            'denied',
            [
                {
                    'name': 'source.query',
                    'level': 'error',
                    'hint': 'No placeholder [_INSERT_HERE_]',
                },
                {
                    'name': 'consumer.entity_type',
                    'level': 'error',
                    'hint': (
                        'Invalid entity type \'dbid_uuid_clid_phid\' for '
                        'consumer tags'
                    ),
                },
                {
                    'name': 'consumer.allowed_tag_names',
                    'level': 'error',
                    'hint': 'Denied topics access: topic2',
                },
            ],
            id='denied',
        ),
    ],
)
async def test_shipment_review(
        taxi_segments_provider,
        mockserver,
        request_shipment: shipment_tools.Shipment,
        expected_decision: str,
        expected_hints: List[Dict[str, Any]],
):
    mock_topics_permissions(
        mockserver, request_shipment.consumer.allowed_tag_names,
    )

    response = await taxi_segments_provider.post(
        '/admin/v1/shipment/review?consumer=tags',
        json={'shipment': request_shipment.as_request_data()},
        headers={'X-Yandex-Login': 'loginef', 'Accept-Language': 'en'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'decision': expected_decision,
        'is_audit_required': False,
        'audit_groups': [],
        'fields': expected_hints,
    }
