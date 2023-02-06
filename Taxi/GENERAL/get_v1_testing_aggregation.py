from supportai_tasks import models as db_models
from supportai_tasks.generated.service.swagger import models
from supportai_tasks.generated.service.swagger import requests
from supportai_tasks.generated.service.swagger import responses
from supportai_tasks.generated.web import web_context
from supportai_tasks.utils import testing_aggregation as test_agg


async def handle(
        request: requests.GetV1TestingAggregation,
        context: web_context.Context,
) -> responses.GET_V1_TESTING_AGGREGATION_RESPONSES:
    async with context.pg.slave_pool.acquire() as conn:
        model = db_models.TestingAggregation
        agg = await model.select_by_task_id(
            context=context, db_conn=conn, task_id=request.task_id,
        )

    if agg is None:
        return responses.GetV1TestingAggregation204()

    return responses.GetV1TestingAggregation200(
        data=models.api.TestingAggregation(
            equals_percent=test_agg.get_percent(
                agg.equal_count, agg.chat_count,
            ),
            topic_accuracy_v1=test_agg.get_percent(
                agg.topic_ok_count_v1, agg.ok_chat_count,
            ),
            topic_accuracy_v2=test_agg.get_percent(
                agg.topic_ok_count_v2, agg.ok_chat_count,
            ),
            reply_percent_v1=test_agg.get_percent(
                agg.reply_count_v1, agg.chat_count,
            ),
            reply_percent_v2=test_agg.get_percent(
                agg.reply_count_v2, agg.chat_count,
            ),
            close_percent_v1=test_agg.get_percent(
                agg.close_count_v1, agg.chat_count,
            ),
            close_percent_v2=test_agg.get_percent(
                agg.close_count_v2, agg.chat_count,
            ),
            reply_or_close_v1=test_agg.get_percent(
                agg.reply_or_close_count_v1, agg.chat_count,
            ),
            reply_or_close_v2=test_agg.get_percent(
                agg.reply_or_close_count_v2, agg.chat_count,
            ),
            topic_details=test_agg.prepare_topic_details(agg.topic_details),
        ),
    )
