import datetime

import pytest

from infra_events.common import db


async def test_c_tickets_last_check_timestamp(cron_context):
    now = datetime.datetime.fromisoformat('2020-01-01T23:59:12+03:00')

    await db.set_c_tickets_last_check_time(cron_context, now=now)
    last_check_time = await db.get_c_tickets_last_check_time(cron_context)

    assert now.timestamp() == last_check_time.timestamp()


async def test_taxirel_c_tickets_last_check_timestamp(cron_context):
    now = datetime.datetime.fromisoformat('2020-01-01T23:59:12+00:00')

    await db.set_taxirel_c_tickets_last_check_time(cron_context, now=now)
    last_check_time = await db.get_taxirel_c_tickets_last_check_time(
        cron_context,
    )

    assert now.timestamp() == last_check_time.timestamp()


async def test_insert(cron_context):
    await db.insert_events(
        context=cron_context,
        events=[
            {
                'timestamp': datetime.datetime(2020, 1, 1),
                'header': 'header',
                'body': 'body',
                'tags': ['tags'],
                'source': 'source',
                'views': ['__all__'],
            },
        ],
    )


@pytest.mark.config(INFRA_EVENTS_VIEWS=['test_eda', 'test_taxi'])
@pytest.mark.parametrize(
    ['events_filter', 'events_count'],
    [
        (
            {
                'view': 'test_eda',
                'source': None,
                'tags': None,
                'timestamp_from': datetime.datetime(
                    2020, 1, 1, tzinfo=datetime.timezone.utc,
                ),
                'timestamp_to': None,
            },
            2,
        ),
        (
            {
                'view': 'test_eda',
                'source': None,
                'tags': None,
                'timestamp_from': datetime.datetime(
                    2020, 2, 3, tzinfo=datetime.timezone.utc,
                ),
                'timestamp_to': None,
            },
            1,
        ),
        (
            {
                'view': 'test_eda',
                'source': None,
                'tags': None,
                'timestamp_from': datetime.datetime(
                    2020, 4, 4, tzinfo=datetime.timezone.utc,
                ),
                'timestamp_to': None,
            },
            0,
        ),
        (
            {
                'view': 'test_taxi',
                'source': None,
                'tags': None,
                'timestamp_from': datetime.datetime(
                    2020, 1, 1, tzinfo=datetime.timezone.utc,
                ),
                'timestamp_to': None,
            },
            1,
        ),
        (
            {
                'view': 'test_eda',
                'source': None,
                'tags': ['test_tag_0', 'test_tag_1'],
                'timestamp_from': datetime.datetime(
                    2020, 1, 1, tzinfo=datetime.timezone.utc,
                ),
                'timestamp_to': None,
            },
            1,
        ),
        (
            {
                'view': 'test_eda',
                'source': None,
                'tags': None,
                'timestamp_from': datetime.datetime(
                    2020, 1, 1, tzinfo=datetime.timezone.utc,
                ),
                'timestamp_to': datetime.datetime(
                    2020, 2, 2, tzinfo=datetime.timezone.utc,
                ),
            },
            1,
        ),
        (
            {
                'view': 'test_eda',
                'source': None,
                'tags': None,
                'timestamp_from': datetime.datetime(
                    2020, 1, 1, tzinfo=datetime.timezone.utc,
                ),
                'timestamp_to': datetime.datetime(
                    2020, 2, 2, tzinfo=datetime.timezone.utc,
                ),
            },
            1,
        ),
        (
            {
                'view': 'test_eda',
                'source': None,
                'tags': None,
                'timestamp_from': datetime.datetime(
                    2020, 1, 1, tzinfo=datetime.timezone.utc,
                ),
                'timestamp_to': datetime.datetime(
                    2020, 2, 2, tzinfo=datetime.timezone.utc,
                ),
            },
            1,
        ),
        (
            {
                'view': 'test_eda',
                'source': 'test_source_0',
                'tags': None,
                'timestamp_from': datetime.datetime(
                    2020, 1, 1, tzinfo=datetime.timezone.utc,
                ),
                'timestamp_to': None,
            },
            1,
        ),
    ],
)
async def test_filter_timestamp_from_events(
        cron_context, events_filter, events_count,
):
    await db.insert_event(
        context=cron_context,
        views=['test_eda'],
        header='test_header',
        body='test_body',
        source='test_source_0',
        tags=['test_tag_0', 'test_tag_1'],
        timestamp=datetime.datetime(2020, 2, 2, tzinfo=datetime.timezone.utc),
    )
    await db.insert_event(
        context=cron_context,
        views=['test_eda'],
        header='test_header',
        body='test_body',
        source='test_source_1',
        tags=['test_tag_0', 'test_tag_2'],
        timestamp=datetime.datetime(2020, 3, 3, tzinfo=datetime.timezone.utc),
    )
    await db.insert_event(
        context=cron_context,
        views=['test_taxi'],
        header='test_header',
        body='test_body',
        source='test_source_0',
        tags=['test_tag_0', 'test_tag_1'],
        timestamp=datetime.datetime(2020, 2, 2, tzinfo=datetime.timezone.utc),
    )

    events_cursor = db.get_events_cursor(cron_context, **events_filter)
    events = [event async for event in events_cursor]
    assert len(events) == events_count
