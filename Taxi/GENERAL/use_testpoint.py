from taxi.pytest_plugins.blacksuite import testpoint

from example_service.generated.service.swagger import requests
from example_service.generated.service.swagger import responses
from example_service.generated.web import web_context


async def handle(
        request: requests.UseTestpoint, context: web_context.Context,
) -> responses.USE_TESTPOINT_RESPONSES:
    await testpoint.add(
        'some_testpoint_name', {'name': 'John', 'surname': 'Wick'},
    )
    return responses.UseTestpoint200()
