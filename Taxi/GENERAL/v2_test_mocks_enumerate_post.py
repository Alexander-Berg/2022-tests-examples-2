from admin_pipeline import common
from admin_pipeline import errors
from admin_pipeline.generated.service.swagger import requests
from admin_pipeline.generated.service.swagger import responses
from admin_pipeline.generated.web import web_context
from admin_pipeline.pipeline import dynamic_consumers
from admin_pipeline.pipeline_tests import views


@common.error_handler(
    errors.UnexpectedConsumer, responses.V2TestMocksEnumeratePost400,
)
async def handle(
        request: requests.V2TestMocksEnumeratePost,
        context: web_context.Context,
) -> responses.V2_TEST_MOCKS_ENUMERATE_POST_RESPONSES:
    # check consumer
    await dynamic_consumers.get_helper(request.consumer, context)
    response = await views.MocksView.enumerate_mocks(request.consumer, context)
    return responses.V2TestMocksEnumeratePost200(data=response)
