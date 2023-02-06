# type: ignore

import decimal

import pytest

from taxi_corp_integration_api import consts
from taxi_corp_integration_api.api.common import types
from taxi_corp_integration_api.api.common.payment_methods import user_checkers
from test_taxi_corp_integration_api import utils
from test_taxi_corp_integration_api.test_checkers import (
    utils as checkers_utils,
)

DEFAULT_LIMIT = {
    'limits': {
        'orders_cost': {'value': '500', 'period': 'month'},
        'orders_amount': {'value': 5, 'period': 'day'},
    },
}
ZERO_SPENDING = types.UserStat(orders_count=0, orders_spent=0)
DEFAULT_SPENDING = types.UserStat(
    orders_count=3, orders_spent=decimal.Decimal(200),
)


@pytest.mark.parametrize(
    ['input_data', 'expected_result'],
    [
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(),
                'source_app': 'corpweb',
            },
            (True, ''),
            id='skip for cabinet only from corpweb',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id', 'features': ['ride_limits']},
                    spendings=types.Spendings(
                        client=None,
                        user={None: ZERO_SPENDING},
                        departments=None,
                    ),
                ),
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='without limit and spending',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id', 'features': ['ride_limits']},
                    limit=DEFAULT_LIMIT,
                    spendings=types.Spendings(
                        client=None,
                        user={
                            'month': DEFAULT_SPENDING,
                            'day': DEFAULT_SPENDING,
                            None: ZERO_SPENDING,
                        },
                        departments=None,
                    ),
                ),
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='spent < limit, orders count < limit',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id', 'features': ['ride_limits']},
                    limit=DEFAULT_LIMIT,
                    spendings=types.Spendings(
                        client=None,
                        user={
                            'month': types.UserStat(
                                orders_count=3,
                                orders_spent=decimal.Decimal(600),
                            ),
                            'day': DEFAULT_SPENDING,
                            None: ZERO_SPENDING,
                        },
                        departments=None,
                    ),
                ),
                'service': consts.ServiceName.TAXI,
            },
            (False, 'Недостаточно денег на счёте'),
            id='spent > limit',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id', 'features': ['ride_limits']},
                    limit=DEFAULT_LIMIT,
                    spendings=types.Spendings(
                        client=None,
                        user={
                            'month': DEFAULT_SPENDING,
                            'day': types.UserStat(
                                orders_count=7,
                                orders_spent=decimal.Decimal(200),
                            ),
                            None: ZERO_SPENDING,
                        },
                        departments=None,
                    ),
                ),
                'service': consts.ServiceName.TAXI,
            },
            (False, 'Недостаточно денег на счёте'),
            id='orders count > limit',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    limit=DEFAULT_LIMIT,
                    spendings=types.Spendings(
                        client=None,
                        user={
                            'month': DEFAULT_SPENDING,
                            'day': DEFAULT_SPENDING,
                            None: ZERO_SPENDING,
                        },
                        departments=None,
                    ),
                ),
                'service': consts.ServiceName.EATS2,
            },
            (True, ''),
            id='spent < limit, orders count < limit (eats)',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    limit=DEFAULT_LIMIT,
                    spendings=types.Spendings(
                        client=None,
                        user={
                            'month': DEFAULT_SPENDING,
                            'day': DEFAULT_SPENDING,
                            None: ZERO_SPENDING,
                        },
                        departments=None,
                    ),
                ),
                'order_info': types.Eats2OrderInfo(
                    order_price=decimal.Decimal(100),
                    route=[],
                    currency='RUB',
                    country='rus',
                ),
                'service': consts.ServiceName.EATS2,
            },
            (True, ''),
            id='spent < limit, orders count < limit (eats with order_info)',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    limit=DEFAULT_LIMIT,
                    spendings=types.Spendings(
                        client=None,
                        user={
                            'month': DEFAULT_SPENDING,
                            'day': DEFAULT_SPENDING,
                            None: ZERO_SPENDING,
                        },
                        departments=None,
                    ),
                ),
                'order_info': types.Eats2OrderInfo(
                    order_price=decimal.Decimal(350),
                    route=[],
                    currency='RUB',
                    country='rus',
                ),
                'service': consts.ServiceName.EATS2,
            },
            (False, 'Сумма заказа превышает доступный лимит'),
            id='spent > limit (eats with order_info)',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
async def test_user_mixed_limits_checker(
        web_context, input_data, expected_result,
):
    checker = checkers_utils.get_checker_instance(
        user_checkers.UserMixedLimitsChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
