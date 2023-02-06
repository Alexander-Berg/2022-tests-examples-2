import datetime as dt

import pytest

from tests_segments_provider import shipment_tools

_NOW = dt.datetime.now()


@pytest.mark.pgsql(
    'segments_provider',
    queries=[
        shipment_tools.get_shipment_insert_query(
            'tags',
            shipment_tools.DbShipment(
                name='shipment-name',
                ticket='A-1',
                maintainers=['developer', 'analyst'],
                is_enabled=True,
                labels=[],
                schedule=shipment_tools.Schedule(
                    start_at=_NOW,
                    unit=shipment_tools.UnitOfTime.HOURS,
                    count=1,
                ),
                source=shipment_tools.YqlQuery(
                    syntax=shipment_tools.YqlSyntax.SQLv1, query='SELECT 1',
                ),
                consumer=shipment_tools.TagsConsumerSettings(
                    allowed_tag_names=[],
                ),
                created_at=_NOW,
                updated_at=_NOW,
                status=shipment_tools.Status.READY,
                last_modifier='loginef',
            ),
        ),
        shipment_tools.get_consumer_insert_query('discounts'),
    ],
)
async def test_suggest_users(taxi_segments_provider):
    response = await taxi_segments_provider.get('/admin/v1/users')
    assert response.status_code == 200
    assert response.json() == {
        'users': [
            {'login': 'analyst'},
            {'login': 'developer'},
            {'login': 'loginef'},
        ],
    }
