from admin_pipeline import common
from admin_pipeline import errors
from admin_pipeline.generated.service.swagger import requests
from admin_pipeline.generated.service.swagger import responses
from admin_pipeline.generated.web import web_context
from admin_pipeline.pipeline import dynamic_consumers


@common.error_handler(
    errors.UnexpectedConsumer, responses.V2PipelineTestsEnumeratePost400,
)
async def handle(
        request: requests.V2PipelineTestsEnumeratePost,
        context: web_context.Context,
) -> responses.V2_PIPELINE_TESTS_ENUMERATE_POST_RESPONSES:
    # check consumer
    helper = await dynamic_consumers.get_helper(request.consumer, context)
    response = await helper.enumerate_pipeline_tests(
        request.consumer, request.pipeline_name, context,
    )
    return responses.V2PipelineTestsEnumeratePost200(data=response)
