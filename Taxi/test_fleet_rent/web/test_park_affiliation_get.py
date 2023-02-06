import pytest

from fleet_rent.generated.web import web_context as wc


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
    INSERT INTO rent.affiliations
    (record_id, state,
     park_id, local_driver_id,
     original_driver_park_id, original_driver_id,
     creator_uid, created_at_tz, modified_at_tz)
    VALUES
    ('record_id', 'park_recalled',
     'park_id', 'local_driver_id',
     'original_driver_park_id', 'original_driver_id',
     'creator_uid', '2020-01-01+00', '2020-01-01+00')
        """,
    ],
)
async def test_get(web_app_client, web_context: wc.Context):
    response404 = await web_app_client.get(
        '/v1/park/affiliations',
        params={'record_id': 'missing_record_id', 'park_id': 'owner_park_id'},
    )
    assert response404.status == 404

    response200 = await web_app_client.get(
        '/v1/park/affiliations',
        params={'record_id': 'record_id', 'park_id': 'park_id'},
    )
    assert response200.status == 200
    data = await response200.json()
    assert data == {
        'record_id': 'record_id',
        'park_id': 'park_id',
        'local_driver_id': 'local_driver_id',
        'original_driver_park_id': 'original_driver_park_id',
        'original_driver_id': 'original_driver_id',
        'creator_uid': 'creator_uid',
        'created_at': '2020-01-01T03:00:00+03:00',
        'modified_at': '2020-01-01T03:00:00+03:00',
        'state': 'park_recalled',
    }
