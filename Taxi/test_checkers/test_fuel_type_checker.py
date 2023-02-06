import decimal

import pytest

from taxi.util import context_timings
from taxi.util import performance

from taxi_corp_integration_api import consts
from taxi_corp_integration_api.api.common import types
from taxi_corp_integration_api.api.common.payment_methods import user_checkers
from test_taxi_corp_integration_api import utils
from test_taxi_corp_integration_api.test_checkers import (
    utils as checkers_utils,
)

BASE_LIMIT = {'fuel_types': ['a92', 'a95']}
BASE_TANKER_ORDER_INFO = types.TankerOrderInfo(
    order_price=decimal.Decimal(),
    country='rus',
    currency='RUB',
    fuel_type='a92',
)


@pytest.mark.parametrize(
    ['input_data', 'expected_result'],
    [
        pytest.param(
            {'data': checkers_utils.mock_prepared_data(limit=BASE_LIMIT)},
            (True, ''),
            id='no order_info',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(),
                'order_info': BASE_TANKER_ORDER_INFO,
                'source_app': None,
                'service': consts.ServiceName.TANKER,
            },
            (True, ''),
            id='no fuel restrictions',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(limit=BASE_LIMIT),
                'order_info': BASE_TANKER_ORDER_INFO,
                'source_app': None,
                'service': consts.ServiceName.TANKER,
            },
            (True, ''),
            id='matches restrictions',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(limit=BASE_LIMIT),
                'order_info': types.TankerOrderInfo(
                    order_price=decimal.Decimal(),
                    country='rus',
                    currency='RUB',
                    fuel_type='a100',
                ),
                'source_app': None,
                'service': consts.ServiceName.TANKER,
            },
            (False, 'error.fuel_type_is_not_permitted'),
            id='doesnt match restrictions',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
async def test_fuel_type_checker(
        web_context, patch, input_data, expected_result,
):
    time_storage = performance.TimeStorage('fuel_type_restrictions')
    context_timings.time_storage.set(time_storage)

    checker = checkers_utils.get_checker_instance(
        user_checkers.FuelTypeChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
