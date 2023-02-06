# pylint: disable=too-many-lines
# pylint: disable=import-only-modules
# mypy: ignore-errors
import json
from json import JSONDecodeError
import logging
from typing import Union

from eats_testing_simplifier_responser.generated.service.swagger import models
from eats_testing_simplifier_responser.generated.service.swagger import (
    requests,
)
from eats_testing_simplifier_responser.generated.service.swagger import (
    responses,
)
from eats_testing_simplifier_responser.generated.web import web_context

logger = logging.getLogger(__name__)


async def create_order_handler(
        request: Union[requests.CreateOrder, requests.CreateOrderV2],
        context: web_context.Context,
):
    logger.info('handling order - %s', request.body.id)
    try:
        data_from_x_eats_testing_mock = json.loads(
            str(request.x_eats_testing_mock_bypass),
        )
        logger.info(
            'x_eats_testing_mock_bypass value %s',
            data_from_x_eats_testing_mock,
        )
        if 'not_enough_funds' in data_from_x_eats_testing_mock.values():
            status, action = 'rejected', 'purchase'
        elif 'processing_error' in data_from_x_eats_testing_mock.values():
            status, action = 'confirmed', 'debt'
        elif 'success' in data_from_x_eats_testing_mock.values():
            status, action = 'confirmed', 'purchase'
    except JSONDecodeError:
        logger.info(
            'No x_eats_testing_mock_bypass headers in request for order - %s',
            request.body.id,
        )
        status, action = 'confirmed', 'purchase'
    kwargs = {
        'action': action,
        'status': status,
        'revision': request.body.revision,
        'order_id': request.body.id,
    }

    if action == 'debt':
        kwargs.update(
            {'meta': ([{'discriminator': 'debt_type', 'value': 'auto'}])},
        )
    await context.stq.eda_order_processing_payment_events_callback.call(
        task_id=str(request.body.id) + '_1', kwargs=kwargs,
    )
    logger.info(
        'Task of order %s with kwargs %s put to stq',
        request.body.id,
        str(kwargs),
    )
    return responses.CreateOrder200(models.api.EmptyResponse())
