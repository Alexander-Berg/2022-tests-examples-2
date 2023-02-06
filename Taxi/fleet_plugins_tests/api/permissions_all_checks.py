from fleet_plugins_tests.generated.service.swagger import requests
from fleet_plugins_tests.generated.service.swagger import responses
from fleet_plugins_tests.generated.web import web_context
from fleet_plugins_tests.generated.web.fleet_common.services import auth
from fleet_plugins_tests.generated.web.fleet_common.services import (
    permissions as permissions_service,
)


async def handle(
        request: requests.PermissionsAllChecks, context: web_context.Context,
) -> responses.PERMISSIONS_ALL_CHECKS_RESPONSES:
    fleet_user = await auth.run(
        req_params=request.middlewares.fleet_auth_request.get_params(),
        context=context,
        with_api7_user=True,
        log_extra=request.log_extra,
    )

    permissions_ = await permissions_service.get_permissions(
        context=context, fleet_user=fleet_user, log_extra=request.log_extra,
    )

    permissions = permissions_.data

    assert len(permissions) == 1
    assert permissions.pop() == 'bug_send'

    return responses.PermissionsAllChecks200()
