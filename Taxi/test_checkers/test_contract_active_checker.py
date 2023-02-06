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
                'data': checkers_utils.mock_prepared_data(),
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='client without contract',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {
                            'service_ids': [650],
                            'is_active': True,
                            'settings': {'is_active': True},
                        },
                    ],
                ),
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='active contract',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {
                            'service_ids': [668],
                            'is_active': True,
                            'settings': {'is_active': False},
                        },
                    ],
                ),
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='disabled other contract',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {
                            'service_ids': [650],
                            'is_active': True,
                            'settings': {'is_active': False},
                        },
                    ],
                ),
                'service': consts.ServiceName.TAXI,
            },
            (False, 'Корпоративный контракт отключен'),
            id='disabled contract',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
async def test_contract_active_checker(
        web_context, input_data, expected_result,
):
    checker = checkers_utils.get_checker_instance(
        client_checkers.ContractActiveChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
