# pylint: disable=too-many-lines
# pylint: disable=import-only-modules
# mypy: ignore-errors


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
        request: requests.CreateOrder, context: web_context.Context,
) -> responses.CREATE_ORDER_RESPONSES:
    await create_order_handler(request, context)
    return responses.CreateOrder200(models.api.EmptyResponse())
