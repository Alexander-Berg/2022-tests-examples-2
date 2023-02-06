from example_service.generated.service.swagger import requests
from example_service.generated.service.swagger import responses
from example_service.generated.web import web_context


async def handle(
        request: requests.AllOfTestComplexInlinePost,
        context: web_context.Context,
) -> responses.ALL_OF_TEST_COMPLEX_INLINE_POST_RESPONSES:
    inline = request.body.inline

    return responses.AllOfTestComplexInlinePost200(
        inline.name
        + str(inline.day.number)
        + inline.day.week
        + str(inline.age),
    )
