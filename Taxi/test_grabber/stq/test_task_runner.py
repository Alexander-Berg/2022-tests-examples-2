import datetime

import aiohttp
import bson
import pytest

from grabber.common import data_request_storage
from grabber.common import tasks_storage
from grabber.stq.tasks import task_runner


@pytest.fixture
def archive_service(mockserver):  # pylint: disable=W0621
    @mockserver.json_handler('/archive-api/archive/order')
    def order(request):  # pylint: disable=W0612
        order_doc = {
            'performer': {
                'uuid': 'adasdasd',
                'taxi_alias': {'id': 'sdasdassd'},
            },
            'statistics': {
                'start_transporting_time': datetime.datetime(
                    2018, 1, 28, 12, 8, 48,
                ),
                'complete_time': datetime.datetime(2018, 1, 28, 12, 8, 48),
            },
        }

        return aiohttp.web.Response(
            body=bson.BSON.encode({'doc': order_doc}),
            headers={'Content-Type': 'application/bson'},
        )


async def test_task_run(
        stq3_context, pgsql, archive_service,
):  # pylint: disable=W0621
    # pass
    pgsql['grabber'].cursor().execute(
        'INSERT '
        'INTO grabber.tasks (task_id, order_id)'
        'VALUES (\'task_id\', \'order_id\')',
    )  # noqa E501

    pgsql['grabber'].cursor().execute(
        'INSERT '
        'INTO grabber.data_requests (request_id, task_id, data_type, data_filter)'  # noqa E501
        'VALUES (\'request_id\', \'task_id\', \'driver_timeline\',  \'"{\\"x\\": 1}"\')',  # noqa E501
    )

    await task_runner.run(stq3_context, 'task_id')
    task = await tasks_storage.get_task(stq3_context, 'task_id')
    assert task
    data_requests_with_metrica = await data_request_storage.get_data_requests(
        stq3_context, task.task_id,
    )
    assert data_requests_with_metrica

    await task_runner.run(stq3_context, 'task_id')
