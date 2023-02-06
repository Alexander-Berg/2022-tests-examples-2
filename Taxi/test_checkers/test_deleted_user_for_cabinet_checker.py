# type: ignore

import pytest

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
            id='no user',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    user={'_id': 'user_id'},
                ),
            },
            (True, ''),
            id='not deleted user',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    user={'_id': 'user_id', 'is_deleted': True},
                ),
                'source_app': 'yataxi_application',
            },
            (True, ''),
            id='skip check for yataxi_application',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    user={'_id': 'user_id', 'is_deleted': True},
                ),
                'source_app': 'corpweb',
            },
            (False, 'Пользователь удален'),
            id='deleted user from corpweb',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
async def test_deleted_user_for_cabinet_checker(
        web_context, input_data, expected_result,
):
    checker = checkers_utils.get_checker_instance(
        user_checkers.DeletedUserForCabinetChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
