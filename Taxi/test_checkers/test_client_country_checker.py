import decimal

import pytest

from taxi_corp_integration_api.api.common import types
from taxi_corp_integration_api.api.common.payment_methods import (
    client_checkers,
)
from test_taxi_corp_integration_api import utils
from test_taxi_corp_integration_api.test_checkers import (
    utils as checkers_utils,
)


@pytest.mark.parametrize(
    ['input_data', 'expected_result'],
    [
        pytest.param(
            {'data': checkers_utils.mock_prepared_data()},
            (True, ''),
            id='no order_info',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(),
                'order_info': types.Eats2OrderInfo(
                    order_price=decimal.Decimal(),
                    route=[],
                    country='rus',
                    currency='RUB',
                ),
            },
            (True, ''),
            id='eats order country == country',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(),
                'order_info': types.Eats2OrderInfo(
                    order_price=decimal.Decimal(),
                    route=[],
                    country='kaz',
                    currency='KZT',
                ),
            },
            (False, 'В этой стране корпоративная оплата не поддерживается'),
            id='eats order country != client country',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(),
                'order_info': types.TankerOrderInfo(
                    order_price=decimal.Decimal(),
                    country='kaz',
                    currency='KZT',
                    fuel_type='a92',
                ),
            },
            (False, 'В этой стране корпоративная оплата не поддерживается'),
            id='tanker order country != client country',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
async def test_client_balance_checker(
        web_context, input_data, expected_result,
):
    checker = checkers_utils.get_checker_instance(
        client_checkers.ClientCountryChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
