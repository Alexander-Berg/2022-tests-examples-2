from example_service.generated.service.swagger import requests
from example_service.generated.service.swagger import responses
from example_service.generated.web import web_context


async def handle(
        request: requests.TvmTestingGet, context: web_context.Context,
) -> responses.TVM_TESTING_GET_RESPONSES:
    return responses.TvmTestingGet200()
