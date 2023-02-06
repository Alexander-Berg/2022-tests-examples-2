from fleet_plugins_tests.generated.service.swagger import requests
from fleet_plugins_tests.generated.service.swagger import responses
from fleet_plugins_tests.generated.web import web_context
from fleet_plugins_tests.generated.web.fleet_error_response import (
    plugin as exceptions,
)


async def handle(
        request: requests.FleetErrorResponse429Internal,
        context: web_context.Context,
) -> responses.FLEET_ERROR_RESPONSE429_INTERNAL_RESPONSES:
    if request.throw_429:
        raise exceptions.HTTPTooManyRequests()

    return responses.FleetErrorResponse429Internal200()
