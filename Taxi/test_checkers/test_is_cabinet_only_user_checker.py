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
            {
                'data': checkers_utils.mock_prepared_data(),
                'source_app': 'cargo',
            },
            (True, ''),
            id='skip for cargo',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    limit={'_id': 'limit_id'},
                ),
                'source_app': 'yataxi_application',
            },
            (True, ''),
            id='is not cabinet only',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(),
                'source_app': 'corpweb',
            },
            (True, ''),
            id='skip for corpweb',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(),
                'source_app': 'yataxi_application',
            },
            (False, 'Заказ возможен только из корпоративного кабинета'),
            id='reject cabinet only from yataxi_application',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.config(CORP_SOURCES_NO_USER=['cargo'])
async def test_is_cabinet_only_user_checker(
        web_context, input_data, expected_result,
):
    checker = checkers_utils.get_checker_instance(
        user_checkers.IsCabinetOnlyUserChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
