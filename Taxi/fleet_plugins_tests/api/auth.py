from fleet_plugins_tests.generated.service.swagger import requests
from fleet_plugins_tests.generated.service.swagger import responses
from fleet_plugins_tests.generated.service.swagger.models import api
from fleet_plugins_tests.generated.web import web_context
from fleet_plugins_tests.generated.web.fleet_common.services import auth


async def handle(
        request: requests.Auth, context: web_context.Context,
) -> responses.AUTH_RESPONSES:
    fleet_user = await auth.run(
        req_params=request.middlewares.fleet_auth_request.get_params(),
        context=context,
        log_extra=request.log_extra,
    )

    return responses.Auth200(
        data=api.AuthResponse(
            park_id=fleet_user.park.id,
            login=fleet_user.passport_user.login,
            parks=[
                api.Api7Park(id=park.id, name=park.name)
                for park in fleet_user.api7_parks
            ]
            if fleet_user.api7_parks
            else [],
        ),
    )
