from example_service.generated.service.swagger import requests
from example_service.generated.service.swagger import responses
from example_service.generated.web import web_context


async def handle(
        request: requests.AllOfTestLinkToExternalDefinitionsPost,
        context: web_context.Context,
) -> responses.ALL_OF_TEST_LINK_TO_EXTERNAL_DEFINITIONS_POST_RESPONSES:
    return responses.AllOfTestLinkToExternalDefinitionsPost200(
        f'{request.body.name}: {request.body.age}',
    )
