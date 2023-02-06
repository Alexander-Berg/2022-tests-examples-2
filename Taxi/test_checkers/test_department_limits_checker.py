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
            {'data': checkers_utils.mock_prepared_data()},
            (True, ''),
            id='without departments limits',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    department_limits={
                        'dep_1': types.DepartmentBudget(decimal.Decimal(100)),
                        'dep_2': types.DepartmentBudget(decimal.Decimal(50)),
                    },
                    spendings=types.Spendings(
                        client=None,
                        user=None,
                        departments={
                            'dep_1': decimal.Decimal(30),
                            'dep_2': decimal.Decimal(30),
                        },
                    ),
                ),
            },
            (True, ''),
            id='department spending OK',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    department_limits={
                        'dep_1': types.DepartmentBudget(decimal.Decimal(100)),
                        'dep_2': types.DepartmentBudget(decimal.Decimal(50)),
                    },
                    spendings=types.Spendings(
                        client=None, user=None, departments=None,
                    ),
                ),
            },
            (True, ''),
            id='no department spending',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    department_limits={
                        'dep_1': types.DepartmentBudget(decimal.Decimal(100)),
                        'dep_2': types.DepartmentBudget(decimal.Decimal(50)),
                    },
                    spendings=types.Spendings(
                        client=None,
                        user=None,
                        departments={
                            'dep_1': decimal.Decimal(30),
                            'dep_2': decimal.Decimal(70),
                        },
                    ),
                ),
            },
            (False, 'Недостаточно денег на счёте'),
            id='dep_2 out of limit',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
async def test_departments_limit_checker(
        web_context, input_data, expected_result,
):
    checker = checkers_utils.get_checker_instance(
        user_checkers.DepartmentLimitsChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
