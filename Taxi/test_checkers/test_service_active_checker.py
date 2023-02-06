import pytest

from taxi_corp_integration_api import consts
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
                'data': checkers_utils.mock_prepared_data(
                    client={
                        '_id': 'client_id',
                        'services': {
                            'taxi': {'is_active': True, 'is_visible': True},
                        },
                    },
                ),
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='is_active and is_visible',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={
                        '_id': 'client_id',
                        'services': {'taxi': {'is_active': True}},
                    },
                ),
                'service': consts.ServiceName.TAXI,
            },
            (False, 'Сервис отключен'),
            id='is_active but not is_visible',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
async def test_service_active_checker(
        web_context, input_data, expected_result,
):
    checker = checkers_utils.get_checker_instance(
        client_checkers.ServiceActiveChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
