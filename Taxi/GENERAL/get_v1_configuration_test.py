from supportai_lib.utils import postgres

from supportai_tasks import models as db_models
from supportai_tasks.generated.service.swagger import models
from supportai_tasks.generated.service.swagger import requests
from supportai_tasks.generated.service.swagger import responses
from supportai_tasks.generated.web import web_context
from supportai_tasks.models import api_converters


async def handle(
        request: requests.GetV1ConfigurationTest, context: web_context.Context,
) -> responses.GET_V1_CONFIGURATION_TEST_RESPONSES:
    async with context.pg.slave_pool.acquire() as conn:
        model = db_models.ConfigurationTest
        configuration_tests = await model.select_by_task_id(
            context=context,
            db_conn=conn,
            task_id=request.task_id,
            offset=request.offset,
            limit=request.limit,
            is_equal=request.is_equal,
        )

        query, args = context.sqlt.configuration_test_count(
            task_id=request.task_id, is_equal=request.is_equal,
        )

        _rows_count = await postgres.fetch(conn, query, args)

        total_records = _rows_count[0]['count']

    return responses.GetV1ConfigurationTest200(
        data=models.api.ConfigurationTestResponse(
            test_records=list(
                map(
                    api_converters.db_conftest_to_api_conftest,
                    configuration_tests,
                ),
            ),
            total_records=total_records,
        ),
    )
