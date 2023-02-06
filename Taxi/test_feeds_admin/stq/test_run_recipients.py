from aiohttp import web
# pylint: disable=redefined-outer-name
import pytest

from test_feeds_admin import const


@pytest.mark.now('2019-12-01T3:00:00')
@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_run_recipients.sql'])
@pytest.mark.config(
    FEEDS_ADMIN_PUBLISH_TASK_SETTINGS={'retries': 5, 'batch_size': 5000},
    TVM_RULES=[
        {'dst': 'driver-wall', 'src': 'feeds-admin'},
        {'dst': 'stq-agent', 'src': 'feeds-admin'},
    ],
)
async def test_feed_manual_recipients_for_run(
        stq_runner, stq3_context, patch, mock_driver_wall,
):
    @mock_driver_wall('/internal/driver-wall/v1/add')
    async def handler(request):  # pylint: disable=W0612
        assert request.json['id'] == f'{const.UUID_1}_1'
        assert request.json['template']['text'] == 'foo'
        return web.json_response({'id': f'{const.UUID_1}_1'})

    @patch('feeds_admin.stq.feeds_admin_send._is_expired')
    def _is_expired(*args):  # pylint: disable=W0612
        return False

    await stq_runner.feeds_admin_send.call(
        args=(const.UUID_1,), kwargs={'run_id': 1},
    )
