from clownductor.generated.service.swagger import models
from clownductor.generated.service.swagger import requests
from clownductor.generated.service.swagger import responses
from clownductor.generated.web import web_context
from clownductor.internal.utils import task_processor


async def handle(
        request: requests.PostGenerateTestingDeployMessage,
        context: web_context.Context,
) -> responses.POST_GENERATE_TESTING_DEPLOY_MESSAGE_RESPONSES:
    body = request.body.serialize()
    meta_task = task_processor.MetaTask(**body)
    response = await task_processor.update_cube(
        context, meta_task, 'GenerateTestingDeployMessage',
    )
    model_response = models.api.PostGenerateTestingDeployMessageResponse
    return responses.PostGenerateTestingDeployMessage200(
        model_response.deserialize(response.serialize()),
    )
