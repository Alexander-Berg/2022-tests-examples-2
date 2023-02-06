import pytest

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
                        'billing_id': '9075720',
                    },
                ),
            },
            (True, ''),
            id='client with correct billing_id',
        ),
        pytest.param(
            {'data': checkers_utils.mock_prepared_data()},
            (False, 'Ваш корпоративный счет не найден'),
            id='client does not have billing_id',
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
async def test_billing_id_checker(web_context, input_data, expected_result):
    checker = checkers_utils.get_checker_instance(
        client_checkers.BillingIdChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
