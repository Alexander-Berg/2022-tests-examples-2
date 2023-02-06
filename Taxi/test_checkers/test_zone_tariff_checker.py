import pytest

from taxi_corp_integration_api.api.common import types
from taxi_corp_integration_api.api.common.payment_methods import (
    client_checkers,
)
from test_taxi_corp_integration_api import utils
from test_taxi_corp_integration_api.test_checkers import (
    utils as checkers_utils,
)

BASE_ZONE = types.TariffSetting(
    home_zone='kzn',
    is_corp_paymentmethod=True,
    tariffs={},
    tanker_keys={},
    country='',
    tz='',
    driver_change_cost=None,
)


@pytest.mark.parametrize(
    ['input_data', 'zones', 'expected_result'],
    [
        pytest.param(
            {'data': checkers_utils.mock_prepared_data()},
            {},
            (True, ''),
            id='without zone',
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
            {},
            (True, ''),
            id='without decoupling experiment',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id_6', 'country': 'rus'},
                    client_tariff_plan_series_id='series_id',
                    zone_status=types.ZoneStatus.OK,
                    zone=BASE_ZONE,
                ),
            },
            {'kzn': {}},
            (True, ''),
            id='home_zone in tariff plan',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id_6', 'country': 'rus'},
                    client_tariff_plan_series_id='series_id',
                    zone_status=types.ZoneStatus.OK,
                    zone=BASE_ZONE,
                ),
            },
            {},
            (False, 'Не задан тариф для зоны'),
            id='home_zone not in tariff plan',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
async def test_zone_tariff_checker(
        web_context,
        patch,
        exp3_decoupling_mock,
        input_data,
        zones,
        expected_result,
):
    @patch(
        'taxi_corp_integration_api.caches.corp_tariff_plans_cache.'
        'Cache.get_by_series_id',
    )
    async def _get_by_series_id(*args, **kwargs):
        return {'disable_tariff_fallback': True, 'zones': zones}

    checker = checkers_utils.get_checker_instance(
        client_checkers.ZoneTariffChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
