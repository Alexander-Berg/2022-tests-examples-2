import hiring_forms_lib

from hiring_plugins_tests.generated.service.swagger import models
from hiring_plugins_tests.generated.service.swagger import requests
from hiring_plugins_tests.generated.service.swagger import responses
from hiring_plugins_tests.generated.web import web_context


async def handle(
        data: requests.ValidateForm, context: web_context.Context,
) -> responses.VALIDATE_FORM_RESPONSES:
    try:
        context.forms_cache_on_start.from_request(
            data.body.fields, log_extra=data.log_extra,
        )
    except hiring_forms_lib.exceptions.InvalidForm as exc:
        return responses.ValidateForm400(data=exc.response_object)
    else:
        return responses.ValidateForm200(data=models.api.EmptyObject())
