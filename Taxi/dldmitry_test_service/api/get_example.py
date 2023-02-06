from dldmitry_test_service.generated.service.swagger import models
from dldmitry_test_service.generated.service.swagger import requests
from dldmitry_test_service.generated.service.swagger import responses
from dldmitry_test_service.generated.web import web_context


async def handle(
        request: requests.GetExample, context: web_context.Context,
) -> responses.GET_EXAMPLE_RESPONSES:
    return responses.GetExample200(
        data=models.api.ExampleObject(
            name=request.name, greetings='Hello, %s!' % request.name,
        ),
    )
