import datetime

import pytest

from taxi_corp_integration_api.api.common.payment_methods import user_checkers
from test_taxi_corp_integration_api import utils
from test_taxi_corp_integration_api.test_checkers import (
    utils as checkers_utils,
)

NOW = datetime.datetime(year=2021, month=5, day=10)


@pytest.mark.parametrize(
    ['input_data', 'expected_result'],
    [
        pytest.param(
            {'data': checkers_utils.mock_prepared_data()},
            (True, ''),
            id='without user',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    user={'_id': 'user_id'},
                ),
            },
            (True, ''),
            id='client without limit',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_with_orders_limit'},
                    user={'_id': 'user_id'},
                ),
            },
            (True, ''),
            id='no daily orders',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_with_orders_limit'},
                    user={
                        '_id': 'user_id',
                        'daily_orders': [
                            {
                                'order_id': 'order_1',
                                'finish_ts': '2021-05-10T13:11:14+0300',
                            },
                            {
                                'order_id': 'order_2',
                                'finish_ts': '2021-05-12T19:41:48+0300',
                            },
                        ],
                    },
                ),
            },
            (True, ''),
            id='client limit < daily orders',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_with_orders_limit'},
                    user={
                        '_id': 'user_id',
                        'daily_orders': [
                            {
                                'order_id': 'order_1',
                                'finish_ts': '2021-05-10T13:11:14+0300',
                            },
                            {
                                'order_id': 'order_2',
                                'finish_ts': '2021-05-10T15:11:14+0300',
                            },
                            {
                                'order_id': 'order_3',
                                'finish_ts': '2021-05-12T19:41:48+0300',
                            },
                        ],
                    },
                ),
            },
            (False, 'Лимит на поездки исчерпан'),
            id='client limit < daily orders',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.config(
    CORP_CLIENTS_ORDERS_COUNT_LIMIT={'client_with_orders_limit': 2},
)
@pytest.mark.now(NOW.isoformat())
async def test_user_order_count_limit_checker(
        web_context, input_data, expected_result,
):
    checker = checkers_utils.get_checker_instance(
        user_checkers.UserOrderCountLimitChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
