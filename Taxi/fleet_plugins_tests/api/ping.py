from fleet_plugins_tests.generated.service.swagger import requests
from fleet_plugins_tests.generated.service.swagger import responses
from fleet_plugins_tests.generated.web import web_context


async def handle(
        request: requests.Ping, context: web_context.Context,
) -> responses.PING_RESPONSES:
    return responses.Ping200()
