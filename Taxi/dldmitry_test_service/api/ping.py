from dldmitry_test_service.generated.service.swagger import requests
from dldmitry_test_service.generated.service.swagger import responses
from dldmitry_test_service.generated.web import web_context


async def handle(
        request: requests.Ping, context: web_context.Context,
) -> responses.PING_RESPONSES:
    return responses.Ping200()
