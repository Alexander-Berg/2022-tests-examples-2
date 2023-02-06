import pytest

from taxi.stq import async_worker_ng

from eats_integration_workers.stq import availability
from eats_integration_workers.stq import nomenclature
from eats_integration_workers.stq import price
from eats_integration_workers.stq import stocks


@pytest.mark.parametrize(
    'max_task_retries, count_calls, mapping_name',
    [
        (0, 0, 'stocks'),
        (3, 3, 'stocks'),
        (0, 0, 'price'),
        (3, 3, 'price'),
        (0, 0, 'availability'),
        (3, 3, 'availability'),
        (0, 0, 'nomenclature'),
        (3, 3, 'nomenclature'),
    ],
)
async def test_retries_stq_workres(
        stq3_context,
        patch,
        stq_runner,
        max_task_retries,
        count_calls,
        mapping_name,
):
    stq3_context.config.EATS_INTEGRATION_WORKERS_RETRIES_SETTINGS = (  # noqa: F401,E501
        {
            'metro_stock_worker': max_task_retries,
            'metro_price_worker': max_task_retries,
            'metro_nomenclature_worker': max_task_retries,
            'metro_availability_worker': max_task_retries,
        }
    )
    mapping_tasks = {
        'availability': availability.task,
        'nomenclature': nomenclature.task,
        'stocks': stocks.task,
        'price': price.task,
    }

    @patch(f'eats_integration_workers.stq.workers.worker_task')
    async def tasks_call(*args, **kwargs):
        raise Exception(f'Test task {mapping_name} exception')

    task_info = async_worker_ng.TaskInfo(
        id='1', exec_tries=0, reschedule_counter=1, queue='',
    )

    kwargs = {
        'id': 'place_id',
        'place_id': 'place_id',
        'external_id': 123,
        'brand_id': 'brand_id',
        'stock_reset_limit': 1,
        'dev_filter': 'dev_filter',
        'parser_name': 'metro',
        'integration_task_id': 'task_id',
    }

    while True:
        try:
            handler = mapping_tasks.get(mapping_name)
            await handler(stq3_context, task_info, **kwargs)
        except Exception:  # pylint: disable=W0703
            task_info = async_worker_ng.TaskInfo(
                id='1',
                exec_tries=task_info.exec_tries + 1,
                reschedule_counter=1,
                queue='',
            )
            continue
        assert len(tasks_call.calls) == count_calls
        break
