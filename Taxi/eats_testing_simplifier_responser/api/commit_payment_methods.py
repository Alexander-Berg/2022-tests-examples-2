import json
import logging

from eats_testing_simplifier_responser.generated.service.swagger import models
from eats_testing_simplifier_responser.generated.service.swagger import (
    requests,
)
from eats_testing_simplifier_responser.generated.service.swagger import (
    responses,
)
from eats_testing_simplifier_responser.generated.web import web_context

logger = logging.getLogger(__name__)


async def handle(
        request: requests.CommitPaymentMethods, context: web_context.Context,
) -> responses.COMMIT_PAYMENT_METHODS_RESPONSES:
    payment_methods = [
        {'id': method.id, 'enable': method.enable}
        for method in request.body.payment_methods
    ]
    record_for_insert = [
        request.body.mock_usage,
        json.dumps(payment_methods),
        request.body.uid,
    ]
    async with context.pg.master_pool.acquire(
            log_extra=request.log_extra,
    ) as conn:
        query = (
            'SELECT * from '
            'eats_testing_simplifier_responser.users_payments_methods '
            'where passport_uid = $1'
        )
        is_record_exists = await conn.fetch(query, request.body.uid)

        if is_record_exists:
            logger.info(
                'Trying to update record with passport_uid = %s',
                request.body.uid,
            )
            query = (
                'UPDATE '
                'eats_testing_simplifier_responser.users_payments_methods '
                'set mock_usage = $1, '
                'payment_methods = $2 WHERE passport_uid = $3'
            )
            await conn.execute(query, *record_for_insert)

            return responses.CommitPaymentMethods200(
                models.api.EmptyResponse(),
            )

        logger.info(
            'Trying to insert record with passport_uid = %s', request.body.uid,
        )
        query = (
            'INSERT INTO '
            'eats_testing_simplifier_responser.users_payments_methods '
            'VALUES ($3,$1,$2)'
        )
        await conn.execute(query, *record_for_insert)

        return responses.CommitPaymentMethods200(models.api.EmptyResponse())
