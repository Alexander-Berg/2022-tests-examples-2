from eats_testing_simplifier_responser.generated.service.swagger import (
    requests,
)
from eats_testing_simplifier_responser.generated.service.swagger import (
    responses,
)
from eats_testing_simplifier_responser.generated.web import web_context


async def handle(
        request: requests.Ping, context: web_context.Context,
) -> responses.PING_RESPONSES:
    return responses.Ping200()
