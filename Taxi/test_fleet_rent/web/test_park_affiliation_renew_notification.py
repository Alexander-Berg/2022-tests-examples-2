import datetime

import pytest

from testsuite.utils import http


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
    ('record_id1', 'new',
     'park_id1', 'local_driver_id1',
     'OriginalDriverParkId1', 'OriginalDriverId1',
     'creator_uid', '2020-01-01+00', '2020-01-01+00'),
    ('record_id2', 'active',
     'park_id2', 'local_driver_id2',
     'original_driver_park_id2', 'original_driver_id2',
     'creator_uid', '2020-01-01+00', '2020-01-01+00')
        """,
        """
    INSERT INTO rent.affiliation_notifications
    (affiliation_id, notified_at_tz)
    VALUES ('record_id1', '2020-01-01+00')
        """,
    ],
)
@pytest.mark.config(
    FLEET_RENT_DRIVER_NOTIFICATIONS_V2={
        '__default__': {'timeout': '10d'},
        'new_affiliation': {'timeout': '1h'},
    },
)
async def test_renew(
        web_app_client, patch, mock_client_notify, mock_load_park_info,
):
    @mock_client_notify('/v2/push')
    async def _push(request: http.Request):
        return {'notification_id': '1'}

    response404 = await web_app_client.post(
        '/v1/park/affiliations/renew-notification',
        params={'record_id': 'missing_record_id', 'park_id': 'park_id1'},
    )
    assert response404.status == 404

    response400_1 = await web_app_client.post(
        '/v1/park/affiliations/renew-notification',
        params={'record_id': 'record_id2', 'park_id': 'park_id2'},
    )
    assert response400_1.status == 400
    assert await response400_1.json() == {
        'code': 'invalid_state_to_renotify',
        'message': 'Cant notify driver of an affiliation in this state',
        'details': {'current_state': 'active'},
    }

    @patch('datetime.datetime.now')
    def _now1(*args, **kwargs):
        return datetime.datetime(
            2020, 1, 1, 0, 30, tzinfo=datetime.timezone.utc,
        )

    response400_2 = await web_app_client.post(
        '/v1/park/affiliations/renew-notification',
        params={'record_id': 'record_id1', 'park_id': 'park_id1'},
    )
    assert response400_2.status == 400
    assert await response400_2.json() == {
        'code': 'too_soon_to_renotify',
        'message': 'Wait to notify driver',
        'details': {'seconds_left': 1800.0},
    }

    @patch('datetime.datetime.now')
    def _now2(*args, **kwargs):
        return datetime.datetime(
            2020, 1, 1, 1, 1, tzinfo=datetime.timezone.utc,
        )

    response200 = await web_app_client.post(
        '/v1/park/affiliations/renew-notification',
        params={'record_id': 'record_id1', 'park_id': 'park_id1'},
    )
    assert response200.status == 200
