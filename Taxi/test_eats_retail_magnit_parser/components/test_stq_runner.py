# pylint: disable=redefined-outer-name,protected-access
import pytest

from eats_integration_menu_schema import parser_tools

from eats_retail_magnit_parser.generated.service.swagger.models import (
    api as models,
)

TASK_ID = 'task_id'
PLACE_ID = 'place_id'
ORIGIN_PLACE_ID = 'origin_place_id'
PLACE_GROUP_ID = 'place_group_id'


@pytest.mark.parametrize(
    'task_type',
    [
        parser_tools.TaskType.AVAILABILITY,
        parser_tools.TaskType.STOCK,
        parser_tools.TaskType.NOMENCLATURE,
        parser_tools.TaskType.PRICE,
    ],
)
async def test_stq_queue_has_calls(web_context, task_type, stq):
    queues = {
        parser_tools.TaskType.AVAILABILITY: (
            stq.eats_retail_magnit_parser_availability
        ),
        parser_tools.TaskType.STOCK: (stq.eats_retail_magnit_parser_stocks),
        parser_tools.TaskType.NOMENCLATURE: (
            stq.eats_retail_magnit_parser_nomenclature
        ),
        parser_tools.TaskType.PRICE: (stq.eats_retail_magnit_parser_prices),
    }
    await web_context.stq_runner.run_task(
        models.ParseTask(
            task_type=task_type.value,
            place_id=PLACE_ID,
            place_group_id=PLACE_GROUP_ID,
            forwarded_data=models._ParseTaskForwardedData(
                origin_place_id=ORIGIN_PLACE_ID, stock_reset_limit=0,
            ),
        ),
    )
    assert queues[task_type].has_calls
