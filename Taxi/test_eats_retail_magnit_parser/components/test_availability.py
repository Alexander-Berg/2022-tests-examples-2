# pylint: disable=redefined-outer-name,protected-access,unused-variable
import pytest

from taxi.stq import async_worker_ng

from eats_retail_magnit_parser.components.workers.magnit import workers
from eats_retail_magnit_parser.generated.service.swagger.models import (
    api as models,
)
from eats_retail_magnit_parser.stq import workers as stq_workers

TASK_ID = 'task_id'
PLACE_ID = 'place_id'
PLACE_GROUP_ID = 'place_group_id'


async def test_availability(
        magnit_mocks, mds_mocks, stq_runner, procaas_parsed_mocks,
):
    await stq_runner.eats_retail_magnit_parser_availability.call(
        task_id=TASK_ID,
        args=(),
        kwargs={
            'parse_task': models.ParseTask(
                task_type='availability',
                place_id=PLACE_ID,
                place_group_id=PLACE_GROUP_ID,
                forwarded_data=models._ParseTaskForwardedData(
                    origin_place_id='origin_place_id',
                    stock_reset_limit=0,
                    task_uuid=TASK_ID,
                ),
            ).serialize(),
        },
    )

    assert magnit_mocks['get_stock'].has_calls
    assert mds_mocks.has_calls
    assert procaas_parsed_mocks.has_calls


async def test_availability_with_stock_reset_limit(
        magnit_mocks, mds_mocks, stq_runner, procaas_parsed_mocks,
):
    await stq_runner.eats_retail_magnit_parser_availability.call(
        task_id=TASK_ID,
        args=(),
        kwargs={
            'parse_task': models.ParseTask(
                task_type='availability',
                place_id=PLACE_ID,
                place_group_id=PLACE_GROUP_ID,
                forwarded_data=models._ParseTaskForwardedData(
                    origin_place_id='origin_place_id_reset_stock_limit_10',
                    stock_reset_limit=10,
                    task_uuid=TASK_ID,
                ),
            ).serialize(),
        },
    )

    assert magnit_mocks['get_stock'].has_calls
    assert mds_mocks.has_calls
    assert procaas_parsed_mocks.has_calls


@pytest.mark.config(
    EATS_RETAIL_MAGNIT_PARSER_RETRIES_SETTINGS={'availability': 2},
)
async def test_availability_parsing_fails_if_will_be_retried(
        mockserver, stq3_context,
):
    @mockserver.handler(r'/stores/(?P<place_id>\w+)/stock', regex=True)
    def get_stock(request, place_id):
        return mockserver.make_response('', 500)

    with pytest.raises(workers.MagnitDataError):
        await stq_workers.task(
            stq3_context,
            async_worker_ng.TaskInfo(
                id=1, exec_tries=0, queue='queue_name', reschedule_counter=0,
            ),
            parse_task=models.ParseTask(
                task_type='availability',
                place_id=PLACE_ID,
                place_group_id=PLACE_GROUP_ID,
                forwarded_data=models._ParseTaskForwardedData(
                    origin_place_id='origin_place_id_reset_stock_limit_10',
                    stock_reset_limit=0,
                    task_uuid=TASK_ID,
                ),
            ).serialize(),
        )


async def test_availability_parsing_not_fails_if_retries_exceeded(
        mockserver, stq3_context,
):
    @mockserver.handler(r'/stores/(?P<place_id>\w+)/stock', regex=True)
    def get_stock(request, place_id):
        return mockserver.make_response('', 500)

    await stq_workers.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=1, exec_tries=0, queue='queue_name', reschedule_counter=0,
        ),
        parse_task=models.ParseTask(
            task_type='availability',
            place_id=PLACE_ID,
            place_group_id=PLACE_GROUP_ID,
            forwarded_data=models._ParseTaskForwardedData(
                origin_place_id='origin_place_id_reset_stock_limit_10',
                stock_reset_limit=0,
                task_uuid=TASK_ID,
            ),
        ).serialize(),
    )
