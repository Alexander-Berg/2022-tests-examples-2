import datetime

import pytest

from infra_events.common import db

INFRA_EVENTS_VIEWS = {'test_view': {'release_schedule': 'default'}}


@pytest.mark.config(INFRA_EVENTS_VIEWS=INFRA_EVENTS_VIEWS)
async def test_admin_v1_event_put(mockserver, web_context, web_app_client):
    inserted = await db.insert_event(
        context=web_context,
        views=['test_view'],
        header='header',
        body='body',
        source='test',
        timestamp=datetime.datetime(2020, 2, 2, tzinfo=datetime.timezone.utc),
    )
    inserted_id = inserted.inserted_id

    response = await web_app_client.put(
        '/admin/v1/event',
        headers={'X-Yandex-Login': 'tester1'},
        json={
            'id': str(inserted_id),
            'view': 'test_view',
            'timestamp': '2020-01-01T00:00:00+00:00',
        },
    )
    assert response.status == 200
    updated_event = await db.find_event(web_context, event_id=inserted_id)
    assert updated_event['timestamp'] == datetime.datetime(2020, 1, 1)
