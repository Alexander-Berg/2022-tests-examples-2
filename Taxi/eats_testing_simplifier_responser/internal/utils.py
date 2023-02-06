import json
import logging
import typing as t

from taxi.pg import exceptions as taxi_pg_exceptions

import eats_testing_simplifier_responser.generated.service.swagger.models.api as models  # noqa: E501 line too long
from eats_testing_simplifier_responser.generated.web import web_context

logger = logging.getLogger(__name__)


async def user_payment_methods(
        passport_uid: str, context: web_context.Context,
) -> models.UserPaymentMethodsAvailability:

    logger.info('Try to fetch records for passport_uid = %s', passport_uid)
    async with context.pg.slave_pool.acquire() as conn:
        try:
            query, binds = context.sqlt.payment_methods_get_by_passport_uid(
                passport_uid,
            )
            result = await conn.fetchrow(query, *binds)
        except taxi_pg_exceptions.BaseError as exc:
            logger.exception(f'Some exception occured: {exc}')
            raise Exception(f'Some exception occured: {exc}')

    if not result:
        logger.info('Not found record in DB')
        payment_methods_from_config: t.List = context.config.EATS_TESTING_SIMPLIFIER_RESPONSER_DEFAULT_PAYMENT_METHODS_NEW[  # noqa: E501 line too long
            'default_payment_methods'
        ]
        payment_methods = [
            {'enable': method['availability']['available'], 'id': method['id']}
            for method in payment_methods_from_config
            if method['is_default'] is True
        ]
        mock_usage = (
            context.config.EATS_TESTING_SIMPLIFIER_RESPONSER_DEFAULT_MOCK_USAGE[  # noqa: E501 line too long
                'mock_usage_enabled_by_default'
            ]
        )

    else:
        payment_methods = json.loads((result['payment_methods']))
        mock_usage = bool(result['mock_usage'])

    response_data = models.UserPaymentMethodsAvailability(
        mock_usage=mock_usage,
        uid=passport_uid,
        payment_methods=[
            models.PaymentMethodAvailabilityState(
                enable=methods['enable'], id=methods['id'],
            )
            for methods in payment_methods
        ],
    )
    logger.info('Users payment methods -= %s', str(response_data))

    return response_data
