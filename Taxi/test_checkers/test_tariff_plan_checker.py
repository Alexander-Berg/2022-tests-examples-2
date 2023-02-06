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
            {'data': checkers_utils.mock_prepared_data()},
            (True, ''),
            id='without decoupling experiment',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id_6', 'country': 'rus'},
                    client_tariff_plan_series_id='test_series_id',
                ),
            },
            (True, ''),
            id='decoupling experiment',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id_6', 'country': 'rus'},
                ),
            },
            (False, 'Не задан тарифный план'),
            id='decoupling experiment without client_tariff_plan_series_id',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
async def test_tariff_plan_checker(
        web_context, exp3_decoupling_mock, input_data, expected_result,
):
    checker = checkers_utils.get_checker_instance(
        client_checkers.TariffPlanChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
