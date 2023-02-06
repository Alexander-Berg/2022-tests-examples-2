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
            id='old limits, skip check',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id', 'features': ['new_limits']},
                ),
            },
            (True, ''),
            id='without user',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id', 'features': ['new_limits']},
                    user={'_id': 'user_id', 'is_active': True},
                ),
            },
            (True, ''),
            id='active user',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id', 'features': ['new_limits']},
                    user={'_id': 'user_id', 'is_active': False},
                ),
            },
            (False, 'Пользователь неактивен'),
            id='inactive user',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
async def test_user_active_checker(web_context, input_data, expected_result):
    checker = checkers_utils.get_checker_instance(
        user_checkers.UserActiveChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
