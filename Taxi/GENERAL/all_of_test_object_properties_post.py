from example_service.generated.service.swagger import models
from example_service.generated.service.swagger import requests
from example_service.generated.service.swagger import responses
from example_service.generated.web import web_context


async def handle(
        request: requests.AllOfTestObjectPropertiesPost,
        context: web_context.Context,
) -> responses.ALL_OF_TEST_OBJECT_PROPERTIES_POST_RESPONSES:
    assert isinstance(request.body.mix, models.api.MixedNameAgeObject)
    return responses.AllOfTestObjectPropertiesPost200()
