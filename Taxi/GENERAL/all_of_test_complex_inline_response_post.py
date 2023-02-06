import json

from example_service.generated.service.swagger import requests
from example_service.generated.service.swagger import responses
from example_service.generated.web import web_context


async def handle(
        request: requests.AllOfTestComplexInlineResponsePost,
        context: web_context.Context,
) -> responses.ALL_OF_TEST_COMPLEX_INLINE_RESPONSE_POST_RESPONSES:
    return responses.AllOfTestComplexInlineResponsePost200(
        responses.AllOfTestComplexInlineResponsePost200.Body.deserialize(
            json.loads(request.body),
        ),
    )
