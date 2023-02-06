from fleet_plugins_tests.generated.service.swagger import requests
from fleet_plugins_tests.generated.service.swagger import responses
from fleet_plugins_tests.generated.web import web_context


async def handle(
        request: requests.RateLimiter1, context: web_context.Context,
) -> responses.RATE_LIMITER1_RESPONSES:
    return responses.RateLimiter1200()
