from admin_pipeline import common
from admin_pipeline import errors
from admin_pipeline.generated.service.swagger import requests
from admin_pipeline.generated.service.swagger import responses
from admin_pipeline.generated.web import web_context
from admin_pipeline.pipeline import dynamic_consumers


@common.error_handler(
    errors.UnexpectedConsumer, responses.V2PipelineTestsEnablePost400,
)
async def handle(
        request: requests.V2PipelineTestsEnablePost,
        context: web_context.Context,
) -> responses.V2_PIPELINE_TESTS_ENABLE_POST_RESPONSES:
    # check consumer
    helper = await dynamic_consumers.get_helper(request.consumer, context)
    await helper.enable_pipeline_tests(request, context)
    return responses.V2PipelineTestsEnablePost200()
