from fleet_plugins_tests.generated.service.swagger import requests
from fleet_plugins_tests.generated.service.swagger import responses
from fleet_plugins_tests.generated.web import web_context
from fleet_plugins_tests.generated.web.fleet_common.services import auth


async def handle(
        request: requests.AuthWithUser, context: web_context.Context,
) -> responses.AUTH_WITH_USER_RESPONSES:
    await auth.run(
        req_params=request.middlewares.fleet_auth_request.get_params(),
        context=context,
        with_api7_user=True,
        log_extra=request.log_extra,
    )

    return responses.AuthWithUser200()
