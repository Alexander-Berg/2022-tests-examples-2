from fleet_plugins_tests.generated.service.swagger import requests
from fleet_plugins_tests.generated.service.swagger import responses
from fleet_plugins_tests.generated.web import web_context


async def handle(
        request: requests.TvmUserEnabled, context: web_context.Context,
) -> responses.TVM_USER_ENABLED_RESPONSES:

    assert request.middlewares.tvm.user_info

    return responses.TvmUserEnabled200()
