import asyncio

import pytest


async def make_stq_tasks(stq_runner, input_for_task):
    await stq_runner.logistic_platform_processing_execute_platform_events_by_order.call(  # noqa E501
        **input_for_task,
    )


INPUTS = [
    dict(
        task_id='id',
        kwargs={
            'external_order_id': '00000000',
            'operator_id': '123',
            'cluster_id': 'main_cluster',
        },
        expect_fail=False,
    ),
    dict(
        task_id='id1',
        kwargs={
            'external_order_id': '00000001',
            'operator_id': '123',
            'cluster_id': 'main_cluster',
        },
        expect_fail=True,
    ),
]


@pytest.mark.config(
    LOGISTIC_PLATFORM_PROCESSING_BATCHER_SETTINGS={
        '__default__': {'max_batch_delay': 10000, 'max_batch_size': 2},
    },
)
async def test_execute_platform_events_one_fail(mockserver, stq_runner):
    @mockserver.json_handler(
        '/logistic-platform-uservices/'
        + 'api/platform/operator/process_operator_events',
    )
    def mock_server_main(request):
        return {'message': 'OK', 'not_processed_orders_ids': ['00000001']}

    tasks = [make_stq_tasks(stq_runner, task) for task in INPUTS]

    await asyncio.gather(*tasks)

    assert mock_server_main.times_called == 1
