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
            {
                'data': checkers_utils.mock_prepared_data(
                    client_categories=['econom', 'vip'],
                ),
                'order_info': types.TaxiOrderInfo(
                    order_price=decimal.Decimal(),
                    route=[],
                    classes=['econom'],
                    cost_center=None,
                    cost_centers=None,
                    combo_order=None,
                ),
            },
            (True, ''),
            id='request class in client_categories',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_categories=['econom', 'vip'],
                ),
                'order_info': types.TaxiOrderInfo(
                    order_price=decimal.Decimal(),
                    route=[],
                    classes=['business'],
                    cost_center=None,
                    cost_centers=None,
                    combo_order=None,
                ),
            },
            (False, 'Комфорт недоступны'),
            id='request class in client_categories',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
async def test_corp_classes_checker(web_context, input_data, expected_result):
    checker = checkers_utils.get_checker_instance(
        client_checkers.CorpClassesChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
