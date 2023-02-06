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


@pytest.mark.parametrize(
    ['input_data', 'expected_result'],
    [
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(),
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='skip check for no contracts',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {
                            'service_ids': [650],
                            'payment_type': 'postpaid',
                            'is_active': True,
                        },
                    ],
                ),
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='skip check for postpaid contract',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {
                            'service_ids': [650],
                            'payment_type': 'prepaid',
                            'is_active': True,
                            'settings': {},
                        },
                    ],
                ),
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='skip contract without prepaid_deactivate_threshold',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {
                            'service_ids': [650],
                            'payment_type': 'prepaid',
                            'is_active': True,
                            'settings': {
                                'prepaid_deactivate_threshold': '100',
                            },
                            'balance': {'operational_balance': '200'},
                        },
                    ],
                ),
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='balance > threshold',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {
                            'service_ids': [650],
                            'payment_type': 'prepaid',
                            'is_active': True,
                            'settings': {
                                'prepaid_deactivate_threshold': '100',
                            },
                            'balance': {'operational_balance': '200'},
                        },
                    ],
                    spendings=types.Spendings(
                        client=types.ClientStat(
                            balance=decimal.Decimal(55),
                            spent=decimal.Decimal(),
                        ),
                        user=None,
                        departments=None,
                    ),
                ),
                'service': consts.ServiceName.TAXI,
                'order_info': types.TaxiOrderInfo(
                    order_price=decimal.Decimal(50),
                    route=[],
                    classes=[],
                    cost_center=None,
                    cost_centers=None,
                    combo_order=None,
                ),
            },
            (False, 'Баланс клиента ниже значения порога отключения'),
            id='balance - balance_spent - order_price < threshold',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {
                            'service_ids': [636],
                            'payment_type': 'prepaid',
                            'is_active': True,
                            'settings': {
                                'prepaid_deactivate_threshold': '100',
                            },
                            'balance': {'operational_balance': '200'},
                        },
                    ],
                    client_payment_method=types.ClientPaymentMethod(
                        types.PaymentMethodType.CARD,
                        types.CardInfo('id', 'acc', 'uid'),
                    ),
                ),
                'service': consts.ServiceName.TANKER,
                'order_info': types.TankerOrderInfo(
                    order_price=decimal.Decimal(500),
                    currency='RUB',
                    country='rus',
                    fuel_type='a95',
                ),
            },
            (True, ''),
            id='balance < order_price, but pays with card',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
async def test_client_balance_checker(
        web_context, input_data, expected_result,
):
    checker = checkers_utils.get_checker_instance(
        client_checkers.ClientBalanceChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
