import datetime

from aiohttp import web
# pylint: disable=redefined-outer-name
import pytest

from feeds_admin.models import run_history
from feeds_admin.views import publication
from test_feeds_admin import const


NOW = datetime.datetime(2018, 1, 2, 4, 0)


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_default.sql'])
@pytest.mark.parametrize(
    ['feed_id', 'feed_status'], [(const.UUID_1, 'created')],
)
async def test_feed_get(stq_runner, stq3_context, feed_id, feed_status):
    async with stq3_context.pg.master_pool.acquire() as conn:
        publication_data = await publication.get(
            feed_id, None, conn=conn, context=stq3_context,
        )
    assert publication_data.feed.status.value == feed_status
    assert publication_data.run.status == run_history.Status.PLANNED


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_manual.sql'])
@pytest.mark.config(
    FEEDS_ADMIN_PUBLISH_TASK_SETTINGS={'retries': 5, 'batch_size': 5000},
    TVM_RULES=[
        {'dst': 'driver-wall', 'src': 'feeds-admin'},
        {'dst': 'stq-agent', 'src': 'feeds-admin'},
    ],
)
@pytest.mark.parametrize(
    ['feed_id', 'run_id', 'should_fail'],
    [
        (const.UUID_1, 1, False),
        (const.UUID_2, 2, False),
        (const.UUID_3, 3, True),
        (const.UUID_4, 4, False),
    ],
)
async def test_feed_admin_send_manual_task(
        stq_runner,
        stq3_context,
        patch,
        mock_driver_wall,
        feed_id,
        run_id,
        should_fail,
):
    @mock_driver_wall('/internal/driver-wall/v1/add')
    async def handler(request):  # pylint: disable=W0612
        assert request.json['id'].split('_')[0] == feed_id
        return web.json_response({'id': request.json['id']})

    @mock_driver_wall('/internal/driver-wall/v1/remove')
    async def handler_remove(request):  # pylint: disable=W0612
        assert should_fail
        assert request.json['request_ids'] == [f'{feed_id}_{run_id}']
        return web.json_response({'success': True})

    @patch('taxi.util.dates.utcnow')
    def utcnow():  # pylint: disable=W0612
        return NOW

    @patch('feeds_admin.stq.feeds_admin_send._is_expired')
    def _is_expired(*args):  # pylint: disable=W0612
        return False

    @patch('feeds_admin.models.run_history.Run.mark_failed')
    def mark_failed(*args):  # pylint: disable=W0612
        assert should_fail

    await stq_runner.feeds_admin_send.call(args=(feed_id,), exec_tries=0)


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_feeds.sql'])
@pytest.mark.config(
    TVM_RULES=[
        {'dst': 'driver-wall', 'src': 'feeds-admin'},
        {'dst': 'stq-agent', 'src': 'feeds-admin'},
    ],
    FEEDS_SERVICES={
        'service': {
            'description': 'test',
            'feed_count': 10,
            'max_feed_ttl_hours': 24,
            'polling_delay_sec': 60,
        },
    },
)
@pytest.mark.parametrize(
    ['feed_id', 'run_id', 'removed'],
    [
        (const.UUID_1, 1, ['page:removed']),
        (const.UUID_2, 2, None),
        (const.UUID_3, 3, None),
    ],
)
async def test_feed_admin_send_task_though_feeds(
        stq_runner, stq3_context, patch, mock_feeds, feed_id, run_id, removed,
):
    @mock_feeds('/v1/batch/create')
    async def handler_add(request):  # pylint: disable=W0612
        assert request.json['items'][0]['request_id'].split('_')[0] == str(
            feed_id,
        )
        assert request.json['items'][0]['payload']['text'] == 'foo'
        assert request.json['items'][0]['service']
        return web.json_response(
            data={
                'items': [
                    {
                        'service': request.json['items'][0]['service'],
                        'feed_ids': {
                            request.json['items'][0][
                                'service'
                            ]: 'feeds_feed_id',
                        },
                        'filtered': [],
                    },
                ],
            },
        )

    @mock_feeds('/v1/batch/remove')
    async def handler_remove(request):  # pylint: disable=W0612
        assert removed
        assert set(request.json['items'][0]['channels']) == set(removed)

        return web.json_response({'statuses': {}})

    @patch('taxi.util.dates.utcnow')
    def utcnow():  # pylint: disable=W0612
        return NOW

    @patch('feeds_admin.stq.feeds_admin_send._is_expired')
    def _is_expired(*args):  # pylint: disable=W0612
        return False

    await stq_runner.feeds_admin_send.call(
        args=(feed_id, run_id), exec_tries=0,
    )
