import pytest

from taxi_corp_integration_api.api.common import types
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
            id='no zone',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    zone_status=types.ZoneStatus.OK,
                    zone=types.TariffSetting(
                        home_zone='',
                        is_corp_paymentmethod=True,
                        tariffs={},
                        tanker_keys={},
                        country='rus',
                        tz='',
                        driver_change_cost=None,
                    ),
                ),
            },
            (True, ''),
            id='with zone_status and zone',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    zone_status=types.ZoneStatus.OK,
                    zone=types.TariffSetting(
                        home_zone='',
                        is_corp_paymentmethod=False,
                        tariffs={},
                        tanker_keys={},
                        country='arm',
                        tz='',
                        driver_change_cost=None,
                    ),
                ),
            },
            (False, 'Страна клиента не совпадает со страной заказа'),
            id='countries not equal',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
async def test_zone_country_checker(web_context, input_data, expected_result):
    checker = checkers_utils.get_checker_instance(
        client_checkers.ZoneCountryChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
