import logging

from eats_testing_simplifier_responser.generated.service.swagger import (
    requests,
)
from eats_testing_simplifier_responser.generated.service.swagger import (
    responses,
)
from eats_testing_simplifier_responser.generated.web import web_context
import eats_testing_simplifier_responser.internal.utils as utils

logger = logging.getLogger(__name__)


async def handle(
        request: requests.SearchPaymentMethods, context: web_context.Context,
) -> responses.SEARCH_PAYMENT_METHODS_RESPONSES:
    response_data = await utils.user_payment_methods(
        request.passport_uid, context,
    )
    return responses.SearchPaymentMethods200(data=response_data)
