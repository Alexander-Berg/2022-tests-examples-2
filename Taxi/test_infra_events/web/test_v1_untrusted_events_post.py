import datetime

import bson
import pytest

from infra_events.common import db

INFRA_EVENTS_VIEWS = {'test_view': {'release_schedule': 'default'}}


@pytest.mark.config(INFRA_EVENTS_VIEWS=INFRA_EVENTS_VIEWS)
async def test_v1_untrusted_events_post(web_context, web_app_client):
    response = await web_app_client.post(
        '/v1/untrusted-events',
        json={
            'events': [
                {
                    'timestamp': '2020-01-01T00:00:00+00:00',
                    'header': 'header',
                    'body': 'body',
                    'tags': ['test_tag'],
                    'views': ['test_view'],
                },
            ],
        },
        headers={'X-YaTaxi-Api-Key': 'test_token'},
    )
    assert response.status == 200
    events_ids = (await response.json())['events_ids']
    event = await db.find_event(
        web_context, event_id=bson.ObjectId(events_ids[0]),
    )
    del event['_id']
    assert event == {
        'timestamp': datetime.datetime(2020, 1, 1),
        'header': 'header',
        'body': 'body',
        'tags': ['test_tag'],
        'source': 'untrusted-service-input',
        'views': ['test_view'],
    }


@pytest.mark.config(INFRA_EVENTS_VIEWS=INFRA_EVENTS_VIEWS)
async def test_v1_untrusted_events_post_no_ts_no_tags_no_body(
        web_context, web_app_client,
):
    response = await web_app_client.post(
        '/v1/untrusted-events',
        json={'events': [{'header': 'header', 'views': ['test_view']}]},
        headers={'X-YaTaxi-Api-Key': 'test_token'},
    )
    assert response.status == 200
    events_ids = (await response.json())['events_ids']
    event = await db.find_event(
        web_context, event_id=bson.ObjectId(events_ids[0]),
    )
    del event['_id']
    del event['timestamp']
    assert event == {
        'header': 'header',
        'body': None,
        'tags': [],
        'source': 'untrusted-service-input',
        'views': ['test_view'],
    }
