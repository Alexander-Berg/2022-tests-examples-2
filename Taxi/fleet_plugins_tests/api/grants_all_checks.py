from fleet_plugins_tests.generated.service.swagger import requests
from fleet_plugins_tests.generated.service.swagger import responses
from fleet_plugins_tests.generated.web import web_context
from fleet_plugins_tests.generated.web.fleet_common import entities
from fleet_plugins_tests.generated.web.fleet_common import enums
from fleet_plugins_tests.generated.web.fleet_common.services import auth
from fleet_plugins_tests.generated.web.fleet_common.services import (
    grants as grants_service,
)
from fleet_plugins_tests.generated.web.fleet_common.utils import exceptions


async def handle(
        request: requests.GrantsAllChecks, context: web_context.Context,
) -> responses.GRANTS_ALL_CHECKS_RESPONSES:

    fleet_user = await auth.run(
        req_params=request.middlewares.fleet_auth_request.get_params(),
        context=context,
        with_api7_user=True,
        log_extra=request.log_extra,
    )

    await _assert_get_grants(
        context=context, fleet_user=fleet_user, log_extra=request.log_extra,
    )

    await _assert_is_allowed(
        context=context, fleet_user=fleet_user, log_extra=request.log_extra,
    )

    await _assert_check_grant(
        context=context, fleet_user=fleet_user, log_extra=request.log_extra,
    )

    return responses.GrantsAllChecks200()


async def _assert_get_grants(
        context: web_context.Context,
        fleet_user: entities.FleetUser,
        log_extra: dict,
) -> None:
    grants_collection = await grants_service.get_grants(
        context=context, fleet_user=fleet_user, log_extra=log_extra,
    )

    grants = list(grants_collection.data)

    assert len(grants) == 1
    assert grants[0] == enums.Grant.DriverReadCommon.value


async def _assert_is_allowed(
        context: web_context.Context,
        fleet_user: entities.FleetUser,
        log_extra: dict,
) -> None:
    assert await grants_service.is_allowed(
        context=context,
        fleet_user=fleet_user,
        grant=enums.Grant.DriverReadCommon,
        log_extra=log_extra,
    )


async def _assert_check_grant(
        context: web_context.Context,
        fleet_user: entities.FleetUser,
        log_extra: dict,
) -> None:
    try:
        await grants_service.check_grant(
            context=context,
            fleet_user=fleet_user,
            grant=enums.Grant.CarReadCommon,
            log_extra=log_extra,
        )
    except exceptions.NoGrants:
        assert True

    try:
        await grants_service.check_grant(
            context=context,
            fleet_user=fleet_user,
            grant=enums.Grant.DriverReadCommon,
            log_extra=log_extra,
        )
    except exceptions.NoGrants:
        pass
    else:
        assert False
