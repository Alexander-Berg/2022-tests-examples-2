import datetime
import decimal

import pytest

from taxi_corp_integration_api import consts
from taxi_corp_integration_api.api.common import types
from taxi_corp_integration_api.api.common.payment_methods import user_checkers
from test_taxi_corp_integration_api import utils
from test_taxi_corp_integration_api.test_checkers import (
    utils as checkers_utils,
)

NOW = datetime.datetime(year=2021, month=5, day=10, hour=5)

BASE_ZONE = types.TariffSetting(
    home_zone='',
    is_corp_paymentmethod=True,
    tariffs={},
    tanker_keys={},
    country='',
    tz='Europe/Moscow',
    driver_change_cost=None,
)
BASE_RESTRICTIONS = [
    {
        'days': ['th', 'sa', 'fr'],
        'start_time': '00:00:00',
        'end_time': '10:00:00',
        'type': 'weekly_date',
    },
    {
        'days': ['mo'],
        'start_time': '00:00:00',
        'end_time': '20:00:00',
        'type': 'weekly_date',
    },
]


@pytest.mark.parametrize(
    ['input_data', 'expected_result'],
    [
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    zone_status=types.ZoneStatus.NO_ZONE,
                ),
            },
            (True, ''),
            id='no zone, skip',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id', 'features': ['restrictions']},
                    zone_status=types.ZoneStatus.OK,
                    zone=BASE_ZONE,
                ),
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='no restrictions',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id', 'features': ['restrictions']},
                    limit={'time_restrictions': BASE_RESTRICTIONS},
                    zone_status=types.ZoneStatus.OK,
                    zone=BASE_ZONE,
                ),
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.TAXI,
            },
            (True, ''),
            id='one appropriate restriction',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id', 'features': ['restrictions']},
                    limit={'time_restrictions': [BASE_RESTRICTIONS[0]]},
                    zone_status=types.ZoneStatus.OK,
                    zone=BASE_ZONE,
                ),
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.TAXI,
            },
            (False, 'error.time_is_not_permitted'),
            id='only failed restriction',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id', 'features': ['restrictions']},
                    limit={'time_restrictions': BASE_RESTRICTIONS},
                    zone_status=types.ZoneStatus.OK,
                    zone=BASE_ZONE,
                ),
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.EATS2,
            },
            (True, ''),
            id='one appropriate restriction (eats)',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id', 'features': ['restrictions']},
                    limit={'time_restrictions': [BASE_RESTRICTIONS[0]]},
                    zone_status=types.ZoneStatus.OK,
                    zone=BASE_ZONE,
                ),
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.EATS2,
            },
            (False, 'Оплата заказа в это время недоступна'),
            id='only failed restriction (eats)',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    client={'_id': 'client_id', 'features': ['restrictions']},
                    limit={'time_restrictions': [BASE_RESTRICTIONS[0]]},
                    zone_status=types.ZoneStatus.ERROR,
                    order_info=types.Eats2OrderInfo(
                        order_price=decimal.Decimal(),
                        currency='RUB',
                        country='rus',
                        route=[
                            types.GeoPoint(geopoint=[37.676062, 55.743145]),
                        ],
                    ),
                ),
                'source_app': 'yataxi_application',
                'service': consts.ServiceName.EATS2,
            },
            (False, 'Оплата заказа в это время недоступна'),
            id='only failed restriction, nearestzone not found (eats)',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.now(NOW.isoformat())
async def test_zone_weekly_restrictions_checker(
        web_context, input_data, expected_result,
):
    checker = checkers_utils.get_checker_instance(
        user_checkers.ZoneWeeklyRestrictionsChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
