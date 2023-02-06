# pylint: disable=redefined-outer-name,protected-access
import pytest

from taxi.stq import async_worker_ng

from eats_retail_magnit_parser.components.workers.magnit import workers
from eats_retail_magnit_parser.generated.service.swagger.models import (
    api as models,
)
from eats_retail_magnit_parser.stq import workers as workers_stq

TASK_ID = 'task_id'
PLACE_ID = 'place_id'
ORIGIN_PLACE_ID = 'origin_place_id'
PLACE_GROUP_ID = 'place_group_id'


@pytest.mark.config(
    EATS_RETAIL_MAGNIT_PARSER_RETRIES_SETTINGS={'stock': 2, 'availability': 2},
)
@pytest.mark.parametrize('task_type', ['stock', 'availability'])
async def test_should_fail_with_zero_stocks(
        magnit_mocks, stq3_context, task_type,
):
    with pytest.raises(workers.MagnitDataError):
        await workers_stq.task(
            stq3_context,
            async_worker_ng.TaskInfo(
                id=None, exec_tries=0, reschedule_counter=0, queue='',
            ),
            parse_task=models.ParseTask(
                task_type=task_type,
                place_id=PLACE_ID,
                place_group_id=PLACE_GROUP_ID,
                forwarded_data=models._ParseTaskForwardedData(
                    origin_place_id=ORIGIN_PLACE_ID,
                    stock_reset_limit=0,
                    task_uuid=TASK_ID,
                ),
            ).serialize(),
        )
