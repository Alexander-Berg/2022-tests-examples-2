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
                'data': checkers_utils.mock_prepared_data(),
                'order_info': types.TaxiOrderInfo(
                    order_price=decimal.Decimal(),
                    route=[],
                    classes=[],
                    cost_center=None,
                    cost_centers=None,
                    combo_order=None,
                ),
            },
            (True, ''),
            id='no zone',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    zone_status=types.ZoneStatus.OK,
                    zone=types.TariffSetting(
                        home_zone='',
                        is_corp_paymentmethod=True,
                        tariffs={},
                        tanker_keys={},
                        country='',
                        tz='',
                        driver_change_cost=None,
                    ),
                ),
                'order_info': types.TaxiOrderInfo(
                    order_price=decimal.Decimal(),
                    route=[],
                    classes=[],
                    cost_center=None,
                    cost_centers=None,
                    combo_order=None,
                ),
            },
            (True, ''),
            id='no classes',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_categories=['econom'],
                    zone_status=types.ZoneStatus.OK,
                    zone=types.TariffSetting(
                        home_zone='',
                        is_corp_paymentmethod=True,
                        tariffs={'econom': True},
                        tanker_keys={},
                        country='',
                        tz='',
                        driver_change_cost=None,
                    ),
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
            id='with classes and zone classes',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_categories=['econom'],
                    zone_status=types.ZoneStatus.OK,
                    zone=types.TariffSetting(
                        home_zone='',
                        is_corp_paymentmethod=True,
                        tariffs={},
                        tanker_keys={},
                        country='',
                        tz='',
                        driver_change_cost=None,
                    ),
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
            (
                False,
                'Запрещён заказ по корпоративным '
                'счетам по этим тарифам: Эконом',
            ),
            id='with classes and no zone classes',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
async def test_zone_corp_classes_checker(
        web_context, input_data, expected_result,
):
    checker = checkers_utils.get_checker_instance(
        client_checkers.ZoneCorpClassesChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
