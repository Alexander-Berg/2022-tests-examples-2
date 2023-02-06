# pylint: disable=redefined-outer-name,protected-access
import json

from eats_retail_magnit_parser.generated.service.swagger.models import (
    api as models,
)

TASK_ID = 'task_id'
PLACE_ID = 'place_id'
ORIGIN_PLACE_ID = 'origin_place_id'
PLACE_GROUP_ID = 'place_group_id'


async def test_should_set_cache(
        magnit_mocks,
        mds_mocks,
        stq_runner,
        procaas_parsed_mocks,
        redis_store,
        load_json,
):
    await stq_runner.eats_retail_magnit_parser_stocks.call(
        task_id=TASK_ID,
        args=(),
        kwargs={
            'parse_task': models.ParseTask(
                task_type='stock',
                place_id=PLACE_ID,
                place_group_id=PLACE_GROUP_ID,
                forwarded_data=models._ParseTaskForwardedData(
                    origin_place_id=ORIGIN_PLACE_ID,
                    stock_reset_limit=0,
                    task_uuid=TASK_ID,
                ),
            ).serialize(),
        },
    )

    assert magnit_mocks['get_token'].has_calls
    assert magnit_mocks['get_stock'].has_calls
    assert mds_mocks.has_calls
    assert procaas_parsed_mocks.has_calls

    actual_cache = json.loads(redis_store.get(f'stock_{ORIGIN_PLACE_ID}'))
    expected_cache = load_json('test_request_stocks.json')
    assert actual_cache == expected_cache


async def test_should_get_from_cache(
        magnit_mocks,
        mds_mocks,
        stq_runner,
        procaas_parsed_mocks,
        redis_store,
        load_json,
):
    cache = load_json('test_request_stocks.json')
    redis_store.set(f'stock_{ORIGIN_PLACE_ID}', json.dumps(cache))

    await stq_runner.eats_retail_magnit_parser_stocks.call(
        task_id=TASK_ID,
        args=(),
        kwargs={
            'parse_task': models.ParseTask(
                task_type='stock',
                place_id=PLACE_ID,
                place_group_id=PLACE_GROUP_ID,
                forwarded_data=models._ParseTaskForwardedData(
                    origin_place_id=ORIGIN_PLACE_ID,
                    stock_reset_limit=0,
                    task_uuid=TASK_ID,
                ),
            ).serialize(),
        },
    )

    assert not magnit_mocks['get_token'].has_calls
    assert not magnit_mocks['get_stock'].has_calls
    assert mds_mocks.has_calls
    assert procaas_parsed_mocks.has_calls

    actual_cache = json.loads(redis_store.get(f'stock_{ORIGIN_PLACE_ID}'))
    assert actual_cache == cache
