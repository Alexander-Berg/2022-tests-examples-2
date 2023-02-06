import pytest

from fleet_rent.entities import park as park_entities
from fleet_rent.generated.web import web_context as wc


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
    INSERT INTO rent.affiliations
    (record_id, state,
     park_id, local_driver_id,
     original_driver_park_id, original_driver_id,
     creator_uid, created_at_tz)
    VALUES
    ('affiliation_id', 'new',
     'park_id', 'local_driver_id',
     'driver_park_id', 'driver_id',
     'creator_uid', '2020-01-01+00')
        """,
    ],
)
async def test_details(
        web_app_client, web_context: wc.Context, driver_auth_headers, patch,
):
    @patch('fleet_rent.services.park_info.ParkInfoService.get_park_info')
    async def _get_park_info_b(park_id: str):
        return park_entities.Park(
            id=park_id, name='name', clid='clid', owner=None, tz_offset=3,
        )

    response404 = await web_app_client.get(
        '/driver/v1/periodic-payments/affiliations/details',
        params={'affiliation_id': 'bad_id'},
        headers=driver_auth_headers,
    )
    assert response404.status == 404

    response200 = await web_app_client.get(
        '/driver/v1/periodic-payments/affiliations/details',
        params={'affiliation_id': 'affiliation_id'},
        headers=driver_auth_headers,
    )
    assert response200.status == 200

    assert await response200.json() == {
        'id': 'affiliation_id',
        'state': 'new',
        'items': [
            {
                'type': 'detail',
                'title': 'Park name',
                'subtitle': 'name',
                'reverse': True,
                'horizontal_divider_type': 'bottom_gap',
            },
            # Owner is configured, but missing in source, so item is skipped
        ],
    }
