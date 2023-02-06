# type: ignore

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
            id='no user',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id', 'features': ['ride_limits']},
                    user={'_id': 'user_id'},
                ),
            },
            (True, ''),
            id='ride_limits feature, skip this check',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    user={'_id': 'user_id'},
                ),
                'source_app': 'corpweb',
            },
            (True, ''),
            id='allow is_cabinet_only for corpweb',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    user={
                        '_id': 'user_id',
                        'stat': {'2021-05': {'spent_with_vat': 500000}},
                    },
                    limit={'limits': {'orders_cost': None}},
                ),
                'source_app': 'yataxi_application',
            },
            (True, ''),
            id='infinity limit',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    user={'_id': 'user_id', 'stat': {}},
                    limit={'limits': {'orders_cost': {'value': 100}}},
                ),
                'source_app': 'yataxi_application',
            },
            (True, ''),
            id='zero spending',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    user={
                        '_id': 'user_id',
                        'stat': {'2021-05': {'spent_with_vat': 500000}},
                    },
                    limit={'limits': {'orders_cost': {'value': 100}}},
                ),
                'source_app': 'yataxi_application',
            },
            (True, ''),
            id='spent_with_vat < limit',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    user={
                        '_id': 'user_id',
                        'stat': {'2021-05': {'spent_with_vat': 1200000}},
                    },
                    limit={'limits': {'orders_cost': {'value': 100}}},
                ),
                'source_app': 'yataxi_application',
            },
            (False, 'Недостаточно денег на счёте'),
            id='spent_with_vat > limit',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.now(NOW.isoformat())
async def test_user_limit_checker(web_context, input_data, expected_result):
    checker = checkers_utils.get_checker_instance(
        user_checkers.UserLimitChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
