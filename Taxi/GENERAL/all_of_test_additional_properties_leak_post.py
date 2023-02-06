from example_service.generated.service.swagger import requests
from example_service.generated.service.swagger import responses
from example_service.generated.web import web_context


async def handle(
        request: requests.AllOfTestAdditionalPropertiesLeakPost,
        context: web_context.Context,
) -> responses.ALL_OF_TEST_ADDITIONAL_PROPERTIES_LEAK_POST_RESPONSES:
    return responses.AllOfTestAdditionalPropertiesLeakPost200(
        data=request.body.inner.name or '',
    )
