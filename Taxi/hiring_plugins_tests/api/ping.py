from hiring_plugins_tests.generated.service.swagger import models
from hiring_plugins_tests.generated.service.swagger import requests
from hiring_plugins_tests.generated.service.swagger import responses
from hiring_plugins_tests.generated.web import web_context


async def handle(
        data: requests.Ping, context: web_context.Context,
) -> responses.PING_RESPONSES:
    if not context.forms_cache_on_start.ready:
        return responses.Ping500(
            data=models.api.PingResponse500(
                code='FORM_NOT_LOADED',
                message='Unable to process requests due form not loaded',
            ),
        )
    return responses.Ping200(data=models.api.EmptyObject())
