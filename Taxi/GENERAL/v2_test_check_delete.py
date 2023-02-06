from admin_pipeline import common
from admin_pipeline import errors
from admin_pipeline.generated.service.swagger import requests
from admin_pipeline.generated.service.swagger import responses
from admin_pipeline.generated.web import web_context
from admin_pipeline.pipeline import dynamic_consumers
from admin_pipeline.pipeline_tests import views


@common.error_handler(
    errors.UnexpectedConsumer, responses.V2TestCheckDelete400,
)
async def handle(
        request: requests.V2TestCheckDelete, context: web_context.Context,
) -> responses.V2_TEST_CHECK_DELETE_RESPONSES:
    # check consumer
    await dynamic_consumers.get_helper(request.consumer, context)
    await views.ChecksView.delete(request, context)
    return responses.V2TestCheckDelete200()
