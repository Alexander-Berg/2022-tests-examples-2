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
    ('record_id1', 'accepted',
     'park_id1', 'local_driver_id1',
     'original_driver_park_id1', 'original_driver_id1',
     'creator_uid', '2020-01-01+00', '2020-01-01+00'),
    ('record_id2', 'new',
     'park_id2', 'local_driver_id2',
     'original_driver_park_id2', 'original_driver_id2',
     'creator_uid', '2020-01-01+00', '2020-01-01+00')
        """,
    ],
)
async def test_cancel(web_app_client, web_context: wc.Context):
    response404 = await web_app_client.post(
        '/v1/park/affiliations/cancel',
        params={'record_id': 'missing_record_id', 'park_id': 'park_id1'},
    )
    assert response404.status == 404

    response409 = await web_app_client.post(
        '/v1/park/affiliations/cancel',
        params={'record_id': 'record_id1', 'park_id': 'park_id1'},
    )
    assert response409.status == 409

    response200 = await web_app_client.post(
        '/v1/park/affiliations/cancel',
        params={'record_id': 'record_id2', 'park_id': 'park_id2'},
    )
    assert response200.status == 200
