from pro_test_order_maker.generated.service.swagger import requests
from pro_test_order_maker.generated.service.swagger import responses
from pro_test_order_maker.generated.web import web_context


async def handle(
        request: requests.Ping, context: web_context.Context,
) -> responses.PING_RESPONSES:
    return responses.Ping200()
