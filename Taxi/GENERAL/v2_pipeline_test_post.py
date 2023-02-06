from admin_pipeline import common
from admin_pipeline import errors
from admin_pipeline.generated.service.swagger import requests
from admin_pipeline.generated.service.swagger import responses
from admin_pipeline.generated.service.swagger.models import api
from admin_pipeline.generated.web import web_context
from admin_pipeline.pipeline import dynamic_consumers


@common.error_handler(
    errors.UnexpectedConsumer, responses.V2PipelineTestPost400,
)
async def handle(
        request: requests.V2PipelineTestPost, context: web_context.Context,
) -> responses.V2_PIPELINE_TEST_POST_RESPONSES:
    helper = await dynamic_consumers.get_helper(request.consumer, context)
    return responses.V2PipelineTestPost200(
        api.PipelineTestResultsResponse(
            tests_results=await helper.test_pipeline_request(request, context),
        ),
    )
