import pytest


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
    ('affiliation_id', 'active',
     'park_id', 'local_driver_id',
     'driver_park_id', 'driver_id',
     'creator_uid', '2020-01-01+00')
        """,
    ],
)
async def test_ok(web_app_client, driver_auth_headers):
    response = await web_app_client.get(
        '/driver/v1/periodic-payments/affiliations/is-rentier',
        headers=driver_auth_headers,
    )
    assert response.status == 200

    assert await response.json() == {'is_rentier': True}


async def test_not_ok(web_app_client, driver_auth_headers):
    response = await web_app_client.get(
        '/driver/v1/periodic-payments/affiliations/is-rentier',
        headers=driver_auth_headers,
    )
    assert response.status == 200

    assert await response.json() == {'is_rentier': False}
