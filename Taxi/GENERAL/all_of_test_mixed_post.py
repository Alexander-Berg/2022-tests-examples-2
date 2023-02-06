from example_service import utils
from example_service.generated.service.swagger import requests
from example_service.generated.service.swagger import responses
from example_service.generated.web import web_context


async def handle(
        request: requests.AllOfTestMixedPost, context: web_context.Context,
) -> responses.ALL_OF_TEST_MIXED_POST_RESPONSES:
    return responses.AllOfTestMixedPost200(
        utils.concat_name_and_age(request.body),
    )
