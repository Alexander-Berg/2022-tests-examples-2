import datetime as dt
from typing import Any
from typing import Dict

import pytest
import pytz

from tests_segments_provider import shipment_tools


def get_datetime_msk(
        year: int, month: int, day: int, hour: int, minute: int, second: int,
):
    return dt.datetime(
        year, month, day, hour, minute, second, tzinfo=pytz.UTC,
    ).astimezone(pytz.timezone('Europe/Moscow'))


_CREATED_AT = get_datetime_msk(2021, 12, 14, 12, 0, 0)
_UPDATED_AT = get_datetime_msk(2021, 12, 14, 13, 0, 0)
_START_AT = get_datetime_msk(2021, 12, 14, 14, 0, 0)


@pytest.mark.pgsql(
    'segments_provider',
    queries=[
        shipment_tools.get_shipment_insert_query(
            'tags',
            shipment_tools.DbShipment(
                name='shipment_name',
                ticket='A-1',
                maintainers=['developer', 'analyst'],
                is_enabled=True,
                labels=['SQLv1', 'unimportant', 'driver-tags'],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT,
                    unit=shipment_tools.UnitOfTime.HOURS,
                    count=2,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1, 'SELECT \'1\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    ['tag1', 'tag2'], 'udid',
                ),
                created_at=_CREATED_AT,
                updated_at=_UPDATED_AT,
                status=shipment_tools.Status.READY,
            ),
        ),
    ],
)
async def test_not_found(taxi_segments_provider):
    response = await taxi_segments_provider.get(
        f'/admin/v1/shipment?consumer=tags&name=unknown_name',
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'SHIPMENT_NOT_FOUND',
        'message': 'Shipment "unknown_name" for consumer "tags" not found',
    }


@pytest.mark.pgsql(
    'segments_provider',
    queries=[
        shipment_tools.get_shipment_insert_query(
            'tags',
            shipment_tools.DbShipment(
                name='shipment_name',
                ticket='A-1',
                maintainers=['developer', 'analyst'],
                is_enabled=True,
                labels=['SQLv1', 'unimportant', 'driver-tags'],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT,
                    unit=shipment_tools.UnitOfTime.HOURS,
                    count=2,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.SQLv1, 'SELECT \'1\' as tag;',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    ['tag1', 'tag2'], 'udid',
                ),
                created_at=_CREATED_AT,
                updated_at=_UPDATED_AT,
                status=shipment_tools.Status.READY,
            ),
        ),
        shipment_tools.get_shipment_insert_query(
            'passenger-tags',
            shipment_tools.DbShipment(
                name='shipment_name',
                ticket='A-2',
                maintainers=['developer'],
                is_enabled=False,
                labels=['CLICKHOUSE', 'passenger-tags'],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT,
                    unit=shipment_tools.UnitOfTime.SECONDS,
                    count=3600,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.CLICKHOUSE, 'SELECT 2',
                ),
                consumer=shipment_tools.TagsConsumerSettings(['tag3']),
                created_at=_CREATED_AT,
                updated_at=_UPDATED_AT,
                status=shipment_tools.Status.READY,
            ),
        ),
        shipment_tools.get_shipment_insert_query(
            'passenger-tags',
            shipment_tools.DbShipment(
                name='shipment_wo_labels_and_maintainers',
                ticket='A-2',
                maintainers=[],
                is_enabled=False,
                labels=[],
                schedule=shipment_tools.Schedule(
                    start_at=_START_AT,
                    unit=shipment_tools.UnitOfTime.SECONDS,
                    count=3600,
                ),
                source=shipment_tools.YqlQuery(
                    shipment_tools.YqlSyntax.CLICKHOUSE, 'SELECT 2',
                ),
                consumer=shipment_tools.TagsConsumerSettings(['tag3']),
                created_at=_CREATED_AT,
                updated_at=_UPDATED_AT,
                status=shipment_tools.Status.READY,
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'consumer, shipment_name, expected_data',
    [
        pytest.param(
            'tags',
            'shipment_name',
            {
                'name': 'shipment_name',
                'ticket': 'A-1',
                'maintainers': [{'login': 'analyst'}, {'login': 'developer'}],
                'is_enabled': True,
                'labels': [
                    {'name': 'SQLv1'},
                    {'name': 'driver-tags'},
                    {'name': 'unimportant'},
                ],
                'schedule': {
                    'type': 'periodic',
                    'start_at': '2021-12-14T14:00:00+00:00',
                    'period': {'unit': 'hours', 'count': 2},
                },
                'source': {'syntax': 'SQLv1', 'query': 'SELECT \'1\' as tag;'},
                'consumer': {
                    'allowed_tag_names': ['tag1', 'tag2'],
                    'entity_type': 'udid',
                },
            },
            id='tags_consumer',
        ),
        pytest.param(
            'passenger-tags',
            'shipment_name',
            {
                'name': 'shipment_name',
                'ticket': 'A-2',
                'maintainers': [{'login': 'developer'}],
                'is_enabled': False,
                'labels': [{'name': 'CLICKHOUSE'}, {'name': 'passenger-tags'}],
                'schedule': {
                    'type': 'periodic',
                    'start_at': '2021-12-14T14:00:00+00:00',
                    'period': {'unit': 'seconds', 'count': 3600},
                },
                'source': {'syntax': 'CLICKHOUSE', 'query': 'SELECT 2'},
                'consumer': {'allowed_tag_names': ['tag3']},
            },
            id='passenger_tags_consumer',
        ),
        pytest.param(
            'passenger-tags',
            'shipment_wo_labels_and_maintainers',
            {
                'name': 'shipment_wo_labels_and_maintainers',
                'ticket': 'A-2',
                'maintainers': [],
                'is_enabled': False,
                'labels': [],
                'schedule': {
                    'type': 'periodic',
                    'start_at': '2021-12-14T14:00:00+00:00',
                    'period': {'unit': 'seconds', 'count': 3600},
                },
                'source': {'syntax': 'CLICKHOUSE', 'query': 'SELECT 2'},
                'consumer': {'allowed_tag_names': ['tag3']},
            },
            id='passenger_tags_consumer',
        ),
    ],
)
async def test_shipment_get(
        taxi_segments_provider,
        consumer: str,
        shipment_name: str,
        expected_data: Dict[str, Any],
):
    response = await taxi_segments_provider.get(
        f'/admin/v1/shipment?consumer={consumer}&name={shipment_name}',
    )
    assert response.status_code == 200
    assert response.json() == {'shipment': expected_data}
