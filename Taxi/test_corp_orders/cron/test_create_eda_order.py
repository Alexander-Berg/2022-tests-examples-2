# pylint: disable=redefined-outer-name
import pytest

from corp_orders.crontasks import create_eda_order
from corp_orders.generated.cron import run_cron
from corp_orders.internal import base_context


# put config in separate parametrize
@pytest.mark.parametrize(
    ['fixture_name', 'expected_stq_tasks', 'expected_cursor'],
    [
        pytest.param(
            'topics_1.json',
            2,
            'cursor',
            marks=pytest.mark.config(
                CORP_USE_CORP_ORDERS_SIDE_SYNC_LIMIT=True,
            ),
        ),
        pytest.param(
            'topics_1.json',
            2,
            'cursor',
            marks=pytest.mark.config(
                CORP_USE_CORP_ORDERS_SIDE_SYNC_LIMIT=False,
            ),
        ),
        pytest.param(
            'topics_2.json',
            0,
            'cursor',
            marks=pytest.mark.config(
                CORP_USE_CORP_ORDERS_SIDE_SYNC_LIMIT=True,
            ),
        ),
        pytest.param(
            'topics_2.json',
            0,
            'cursor',
            marks=pytest.mark.config(
                CORP_USE_CORP_ORDERS_SIDE_SYNC_LIMIT=False,
            ),
        ),
    ],
)
async def test_create_eda_order(
        mockserver,
        cron_context,
        load_json,
        fixture_name,
        expected_stq_tasks,
        expected_cursor,
):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    async def _queue(request, queue_name):
        pass

    @mockserver.json_handler('/corp-billing-events/v1/events/journal/topics')
    async def _events_journal_full(request):
        if 'cursor' in request.json:
            # simulte empty topics list from billing-events
            response = {'changed_topics': [], 'cursor': 'cursor'}
        else:
            response = load_json(fixture_name)['events/journal/topics']
        return mockserver.make_response(
            status=200, json=response, headers={'X-Polling-Delay-Ms': '2000'},
        )

    @mockserver.json_handler('/corp-billing-events/v1/topics/compact')
    async def _topics_compact(request):
        return load_json(fixture_name)['topics/compact']

    await run_cron.main(['corp_orders.crontasks.create_eda_order', '-t', '0'])

    ctx = base_context.Context(cron_context, 'test_create_eda_order', {})

    query = ctx.generated.postgres_queries['fetch_eda_cursor.sql']
    master_pool = ctx.generated.pg.master[0]
    async with master_pool.acquire() as conn:
        cursor = await conn.fetch(query)

    assert cursor[0]['cursor'] == expected_cursor
    assert _queue.times_called == expected_stq_tasks


@pytest.mark.parametrize(
    ['static_name', 'expected_topics', 'expected_cursor'],
    [
        pytest.param(
            'changed_topics_1.json', ['order_id_1', 'order_id_2'], 'cursor_11',
        ),
        pytest.param(
            'changed_topics_2.json',
            ['order_id_3', 'order_id_5', 'order_id_6', 'order_id_7'],
            'cursor_2',
        ),
    ],
)
@pytest.mark.config(CORP_ORDERS_EDA_SYNC_LIMIT=3)
async def test_use_corp_orders_side_chunking(
        mockserver,
        cron_context,
        load_json,
        static_name,
        expected_topics,
        expected_cursor,
):
    @mockserver.json_handler('/corp-billing-events/v1/events/journal/topics')
    async def _events_journal_full(request):
        if 'cursor' in request.json:
            # simulte empty topics list from billing-events
            response = {'changed_topics': [], 'cursor': 'cursor_11'}
        else:
            response = load_json(static_name)['events/journal/topics']
        return mockserver.make_response(
            status=200, json=response, headers={'X-Polling-Delay-Ms': '2000'},
        )

    result = await create_eda_order.fetch_topics(cron_context)

    result_topics = [
        topic.topic.external_ref for topic in result.changed_topics
    ]
    assert result_topics == expected_topics
    assert result.cursor == expected_cursor
