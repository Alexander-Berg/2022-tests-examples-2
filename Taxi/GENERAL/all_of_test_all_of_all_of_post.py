from example_service.generated.service.swagger import requests
from example_service.generated.service.swagger import responses
from example_service.generated.web import web_context


async def handle(
        request: requests.AllOfTestAllOfAllOfPost,
        context: web_context.Context,
) -> responses.ALL_OF_TEST_ALL_OF_ALL_OF_POST_RESPONSES:
    return responses.AllOfTestAllOfAllOfPost200(
        request.body.name + str(request.body.age) + request.body.suffix,
    )
