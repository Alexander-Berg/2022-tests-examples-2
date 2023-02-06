# pylint: disable-all
# mypy: ignore-errors
# flake8: noqa
from typing import Dict

from eats_testing_simplifier_responser.generated.service.swagger import (
    requests,
)
from eats_testing_simplifier_responser.generated.service.swagger import (
    responses,
)
from eats_testing_simplifier_responser.generated.service.swagger.models.api import (
    ListPaymentMethods,
    PaymentMethods,
)
from eats_testing_simplifier_responser.generated.web import web_context


async def handle(
        request: requests.ListPaymentMethods, context: web_context.Context,
) -> responses.LIST_PAYMENT_METHODS_RESPONSES:
    payment_methods_from_config: Dict = context.config.EATS_TESTING_SIMPLIFIER_RESPONSER_DEFAULT_PAYMENT_METHODS_NEW[
        'default_payment_methods'
    ]
    response = []

    for payment_type in payment_methods_from_config:
        _id = payment_type.get('id', None)
        _type = payment_type.get('type', None)
        name = payment_type.get('name', _type)
        response.append(PaymentMethods(id=_id, type=_type, title=name))
    return responses.ListPaymentMethods200(data=ListPaymentMethods(response))
