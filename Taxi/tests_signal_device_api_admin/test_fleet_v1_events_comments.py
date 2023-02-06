import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'event_id, code',
    [('34b3d7ec-30f6-43cf-94a8-911bc8fe404c', 200), ('xxx-not-exists', 404)],
)
async def test_add_comment(
        taxi_signal_device_api_admin, event_id, code, pgsql, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(),
                    'specifications': ['signalq'],
                },
            ],
        }

    response = await taxi_signal_device_api_admin.post(
        f'fleet/signal-device-api-admin/v1/events/comments',
        json={'text': 'resolved_with_driver'},
        params={'event_id': event_id},
        headers={
            **web_common.PARTNER_HEADERS_1,
            'X-Park-Id': 'p1',
            'X-Idempotency-Token': 'adsdsads41ddsad1521',
        },
    )
    assert response.status_code == code, response.text
    if code == 200:
        assert response.json()['text'] == 'resolved_with_driver'
        db = pgsql['signal_device_api_meta_db'].cursor()
        db.execute(
            f"""SELECT "text" FROM signal_device_api.events_comments
                WHERE event_id='{event_id}'
            """,
        )
        assert list(db)[0][0] == 'resolved_with_driver'


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
async def test_add_idempotency(
        taxi_signal_device_api_admin, pgsql, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(),
                    'specifications': ['signalq'],
                },
            ],
        }

    event_id = '34b3d7ec-30f6-43cf-94a8-911bc8fe404c'
    response = await taxi_signal_device_api_admin.post(
        f'fleet/signal-device-api-admin/v1/events/comments',
        json={'text': 'resolved_with_driver'},
        params={'event_id': event_id},
        headers={
            **web_common.PARTNER_HEADERS_1,
            'X-Park-Id': 'p1',
            'X-Idempotency-Token': 'adsdsads41ddsad1521',
        },
    )
    assert response.status_code == 200, response.text
    response = await taxi_signal_device_api_admin.post(
        f'fleet/signal-device-api-admin/v1/events/comments',
        json={'text': 'resolved_with_driver'},
        params={'event_id': event_id},
        headers={
            **web_common.PARTNER_HEADERS_1,
            'X-Park-Id': 'p1',
            'X-Idempotency-Token': '999998sxxxxfd1521',
        },
    )
    assert response.status_code == 200, response.text

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        f"""SELECT COUNT(1) FROM signal_device_api.events_comments
            WHERE event_id='{event_id}'
        """,
    )
    assert list(db)[0][0] == 1


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'event_id, comments',
    [
        (
            '44b3d7ec-30f6-43cf-94a8-911bc8fe404c',
            [
                {
                    'created_at': '2020-08-11T15:00:00+00:00',
                    'text': 'lol, kek, ti uvolen',
                    'id': '2',
                },
                {
                    'created_at': '2020-08-08T15:00:00+00:00',
                    'text': 'privet!',
                    'id': '1',
                },
            ],
        ),
        ('xxx-not-exists', []),
    ],
)
async def test_get_comments(
        taxi_signal_device_api_admin, event_id, comments, pgsql, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(),
                    'specifications': ['signalq'],
                },
            ],
        }

    response = await taxi_signal_device_api_admin.get(
        f'fleet/signal-device-api-admin/v1/events/comments',
        params={'event_id': event_id},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'comments': comments}


@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_DEMO_SETTINGS_V2={
        'timings': {
            'working_day_start': 8,
            'working_day_end': 20,
            'working_days_amount': 7,
        },
        'comments': ['Комментарий 1', 'Комментарий 2', 'Комментарий 3'],
        'media': {'__default__': {}},
        'devices': [],
        'events': web_common.DEMO_EVENTS,
        'vehicles': [],
        'groups': [],
        'drivers': [],
    },
)
@pytest.mark.parametrize(
    'event_id, comments_amount',
    [
        pytest.param('e2', 3, id='event with comments'),
        pytest.param('e1', 0, id='event without comments'),
    ],
)
async def test_demo_get_comments(
        taxi_signal_device_api_admin,
        event_id,
        comments_amount,
        pgsql,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info('no such park'),
                    'specifications': ['taxi'],
                },
            ],
        }

    response = await taxi_signal_device_api_admin.get(
        f'fleet/signal-device-api-admin/v1/events/comments',
        params={
            'event_id': utils.get_encoded_events_cursor(
                '2020-02-27T13:02:00+00:00', event_id,
            ),
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no such park'},
    )
    assert response.status_code == 200, response.text
    assert len(response.json()['comments']) == comments_amount
    if comments_amount != 0:
        assert [
            comment['text'] for comment in response.json()['comments']
        ] == ['Комментарий 1', 'Комментарий 2', 'Комментарий 3']
