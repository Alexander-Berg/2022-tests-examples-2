import datetime

from generated.models import fleet_transactions_api as fta_model

from fleet_plugins_tests.generated.service.swagger import requests
from fleet_plugins_tests.generated.service.swagger import responses
from fleet_plugins_tests.generated.web import web_context


async def handle(
        request: requests.FleetErrorResponse429External,
        context: web_context.Context,
) -> responses.FLEET_ERROR_RESPONSE429_EXTERNAL_RESPONSES:
    await context.clients.fleet_transactions_api.v1_parks_driver_profiles_balances_list_post(  # noqa: E501
        body=fta_model.ParksDriverProfilesBalancesListRequest(
            query=fta_model.ParksDriverProfilesBalancesListQuery(
                park=fta_model.ParksDriverProfilesBalancesListQueryPark(
                    id='park_id_0',
                    driver_profile=fta_model.ParksBalancesListQueryParkDriverProfile(  # noqa: E501
                        ids=['driver_id_0'],
                    ),
                ),
                balance=fta_model.ParksBalancesListQueryBalance(
                    group_ids=['cash_collected'],
                    accrued_ats=[
                        datetime.datetime.now() - datetime.timedelta(60),
                        datetime.datetime.now(),
                    ],
                ),
            ),
        ),
    )

    return responses.FleetErrorResponse429External200()
