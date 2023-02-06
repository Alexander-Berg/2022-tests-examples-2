# pylint: disable=redefined-outer-name,protected-access
from eats_retail_magnit_parser.generated.service.swagger.models import (
    api as models,
)

TASK_ID = 'task_id'
PLACE_ID = 'place_id'
ORIGIN_PLACE_ID = 'origin_place_id'
PLACE_GROUP_ID = 'place_group_id'


async def test_nomenclature(
        magnit_mocks, mds_mocks, stq_runner, procaas_parsed_mocks,
):
    await stq_runner.eats_retail_magnit_parser_prices.call(
        task_id=TASK_ID,
        args=(),
        kwargs={
            'parse_task': models.ParseTask(
                task_type='nomenclature',
                place_id=PLACE_ID,
                place_group_id=PLACE_GROUP_ID,
                forwarded_data=models._ParseTaskForwardedData(
                    origin_place_id=ORIGIN_PLACE_ID, task_uuid=TASK_ID,
                ),
            ).serialize(),
        },
    )

    assert magnit_mocks['get_token'].has_calls
    assert magnit_mocks['get_products'].has_calls
    assert mds_mocks.has_calls
    assert procaas_parsed_mocks.has_calls
