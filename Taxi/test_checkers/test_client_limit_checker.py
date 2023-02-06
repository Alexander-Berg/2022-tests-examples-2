import decimal

import pytest

from taxi_corp_integration_api import consts
from taxi_corp_integration_api.api.common import types
from taxi_corp_integration_api.api.common.payment_methods import (
    client_checkers,
)
from test_taxi_corp_integration_api import utils
from test_taxi_corp_integration_api.test_checkers import (
    utils as checkers_utils,
)

BASE_SPENDING = types.Spendings(
    client=types.ClientStat(
        balance=decimal.Decimal(), spent=decimal.Decimal(55),
    ),
    user=None,
    departments=None,
)
BASE_ORDER_INFO = types.TaxiOrderInfo(
    order_price=decimal.Decimal(50),
    route=[],
    classes=[],
    cost_center=None,
    cost_centers=None,
    combo_order=None,
)


@pytest.mark.parametrize(
    ['input_data', 'expected_result'],
    [
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {'service_ids': [650], 'is_active': True},
                    ],
                ),
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='skip contract without contract_limit',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {
                            'service_ids': [650],
                            'is_active': True,
                            'settings': {
                                'contract_limit': {
                                    'limit': '200',
                                    'threshold': '100',
                                },
                            },
                        },
                    ],
                ),
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='spent + order_price < limit - threshold',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {
                            'service_ids': [668],
                            'is_active': True,
                            'settings': {
                                'contract_limit': {
                                    'limit': '200',
                                    'threshold': '100',
                                },
                            },
                        },
                    ],
                    spendings=BASE_SPENDING,
                ),
                'service': consts.ServiceName.TAXI,
                'order_info': BASE_ORDER_INFO,
            },
            (True, ''),
            id='over limit for other contract',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {
                            'service_ids': [650],
                            'is_active': True,
                            'settings': {
                                'contract_limit': {
                                    'limit': '200',
                                    'threshold': '100',
                                },
                            },
                        },
                    ],
                    spendings=BASE_SPENDING,
                ),
                'service': consts.ServiceName.TAXI,
                'order_info': BASE_ORDER_INFO,
            },
            (False, 'Недостаточно денег на счёте'),
            id='spent + order_price >= limit - threshold',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
async def test_client_limit_checker(web_context, input_data, expected_result):
    checker = checkers_utils.get_checker_instance(
        client_checkers.ClientLimitChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
