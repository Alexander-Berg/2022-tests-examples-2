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
                    client={'_id': 'client_id', 'country': 'arm'},
                ),
            },
            (True, ''),
            id='skip pm billing check for arm',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={
                        '_id': 'client_id',
                        'country': 'rus',
                        'services': {'taxi': {'is_test': True}},
                    },
                ),
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='test client',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {'service_ids': [650], 'is_active': True},
                    ],
                ),
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='active contract 650',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {'service_ids': [1181, 1183], 'is_active': True},
                    ],
                ),
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='active contract without_vat',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {'service_ids': [650], 'is_active': False},
                    ],
                ),
                'service': consts.ServiceName.TAXI,
            },
            (False, 'Ваш корпоративный счет больше недоступен'),
            id='inactive contract',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client_contracts=[
                        {'service_ids': [668], 'is_active': True},
                    ],
                ),
                'service': consts.ServiceName.TAXI,
            },
            (False, 'Ваш корпоративный счет больше недоступен'),
            id='no contract for taxi service',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(),
                'service': consts.ServiceName.TAXI,
            },
            (False, 'Ваш корпоративный счет больше недоступен'),
            id='without any contract',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.config(
    CORP_COUNTRIES_SUPPORTED={
        'rus': {},
        'arm': {'skip_pm_billing_check': True},
    },
)
async def test_billing_contract_checker(
        web_context, input_data, expected_result,
):

    checker = checkers_utils.get_checker_instance(
        client_checkers.BillingContractChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
