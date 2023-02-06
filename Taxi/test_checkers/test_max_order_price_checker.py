import decimal

import pytest

from taxi_corp_integration_api.api.common import types
from taxi_corp_integration_api.api.common.payment_methods import user_checkers
from test_taxi_corp_integration_api import utils
from test_taxi_corp_integration_api.test_checkers import (
    utils as checkers_utils,
)


@pytest.mark.parametrize(
    ['input_data', 'expected_result'],
    [
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(),
                'order_info': types.TaxiOrderInfo(
                    order_price=decimal.Decimal(200),
                    route=[],
                    classes=[],
                    cost_center=None,
                    cost_centers=None,
                    combo_order=None,
                ),
            },
            (True, ''),
            id='order_price < price limit',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id_2'},
                ),
                'order_info': types.TaxiOrderInfo(
                    order_price=decimal.Decimal(500),
                    route=[],
                    classes=[],
                    cost_center=None,
                    cost_centers=None,
                    combo_order=None,
                ),
            },
            (True, ''),
            id='no restriction for client',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(),
                'order_info': types.TaxiOrderInfo(
                    order_price=decimal.Decimal(500),
                    route=[],
                    classes=[],
                    cost_center=None,
                    cost_centers=None,
                    combo_order=None,
                ),
            },
            (False, 'Сумма поездки превышает максимальную стоимость'),
            id='order_price > price limit',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.config(
    CORP_LIMIT_ORDER_PRICE=[{'client_id': 'client_id', 'max_order_sum': 400}],
)
async def test_max_order_price_checker(
        web_context, input_data, expected_result,
):
    checker = checkers_utils.get_checker_instance(
        user_checkers.MaxOrderPriceChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
