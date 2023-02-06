from eats_testing_simplifier_responser.api.create_order_handler import (
    create_order_handler,
)
from eats_testing_simplifier_responser.generated.service.swagger import models
from eats_testing_simplifier_responser.generated.service.swagger import (
    requests,
)
from eats_testing_simplifier_responser.generated.service.swagger import (
    responses,
)
from eats_testing_simplifier_responser.generated.web import web_context


async def handle(
        request: requests.CreateOrderV2, context: web_context.Context,
) -> responses.CREATE_ORDER_V2_RESPONSES:
    await create_order_handler(request, context)
    return responses.CreateOrderV2200(models.api.EmptyResponse())
