import generated.clients.cargo_claims as cargo_claims_client
import generated.models.cargo_claims as cargo_claims_module

from pro_test_order_maker.generated.service.swagger import requests
from pro_test_order_maker.generated.service.swagger import responses
import pro_test_order_maker.generated.service.swagger.models.api as api_module
from pro_test_order_maker.generated.web import web_context


async def handle(
        request: requests.DriverV1CargoOrderStatusPost,
        context: web_context.Context,
) -> responses.DRIVER_V1_CARGO_ORDER_STATUS_POST_RESPONSES:
    status = await context.clients.cargo_claims.get_cut_claim(
        claim_id=request.body.claim_id,
    )
    if status.body.status in ('new', 'estimating'):
        return responses.DriverV1CargoOrderStatusPost200(
            api_module.V1CargoOrderStatusResponse(
                status='waiting',
                message=f'Claim status is {status.body.status}',
            ),
        )
    if status.body.status != 'ready_for_approval':
        return responses.DriverV1CargoOrderStatusPost200(
            api_module.V1CargoOrderStatusResponse(
                status='failed',
                message=f'Claim status is {status.body.status}',
            ),
        )

    try:
        await context.clients.cargo_claims.v2_admin_claim_courier_post(
            cargo_claims_module.ClaimCourierPostRequest(
                claim_id=request.body.claim_id,
                courier_id=f'{request.body.park_id}_{request.body.driver_id}',
                revision=1,
            ),
        )
    except cargo_claims_client.V2AdminClaimCourierPost409:
        pass  # performer is set already

    await context.clients.cargo_claims.integration_v2_claims_accept(
        accept_language='ru',
        claim_id=request.body.claim_id,
        x_b2_b_client_id='b8cfabb9d01d48079e35655c253035a9',
        x_cargo_api_prefix='/api/b2b/cargo-claims/',
        body=cargo_claims_module.ChangeStatusRequest(version=1),
    )

    return responses.DriverV1CargoOrderStatusPost200(
        api_module.V1CargoOrderStatusResponse(status='ok'),
    )
