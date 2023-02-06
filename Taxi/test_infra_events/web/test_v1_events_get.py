import datetime

import pytest

from infra_events.common import db

INFRA_EVENTS_VIEWS = {
    'test_view_0': {'release_schedule': 'default'},
    'test_view_1': {'release_schedule': 'default'},
}


@pytest.mark.config(INFRA_EVENTS_VIEWS=INFRA_EVENTS_VIEWS)
@pytest.mark.parametrize(
    ['params', 'status_code', 'response_len'],
    [
        ({'timestamp_from': '2020-01-01T00:00:00'}, 400, 0),
        ({'view': 'test_view_0'}, 400, 0),
        (
            {'view': 'test_view', 'timestamp_from': '2020-01-01T00:00:00'},
            400,
            0,
        ),
        (
            {'view': 'test_view_0', 'timestamp_from': '2020-02-02T00:00:00'},
            200,
            1,
        ),
        (
            {'view': 'test_view_1', 'timestamp_from': '2020-01-01T00:00:00'},
            200,
            1,
        ),
        (
            {'view': 'test_view_0', 'timestamp_from': '2020-03-03T00:00:00'},
            200,
            0,
        ),
        (
            {'view': 'test_view_1', 'timestamp_from': '2020-01-01T00:00:00'},
            200,
            1,
        ),
        (
            {
                'view': 'test_view_0',
                'timestamp_from': '2020-01-01T00:00:00',
                'source': 'not_found',
            },
            200,
            0,
        ),
        (
            {
                'view': 'test_view_0',
                'timestamp_from': '2020-01-02T00:00:00',
                'timestamp_to': '2020-02-01T00:00:00',
            },
            200,
            0,
        ),
    ],
)
async def test_v1_events_get(
        mockserver,
        web_context,
        web_app_client,
        params,
        status_code,
        response_len,
):
    await db.insert_event(
        context=web_context,
        views=['test_view_0'],
        header='header',
        body='body',
        source='test',
        timestamp=datetime.datetime(2020, 2, 2, tzinfo=datetime.timezone.utc),
    )
    await db.insert_event(
        context=web_context,
        views=['__all__'],
        header='header',
        body='body',
        source='test',
        timestamp=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),
    )
    response = await web_app_client.get('/v1/events', params=params)
    assert response.status == status_code
    if response.status == 200:
        response_data = await response.json()
        assert len(response_data['events']) == response_len
