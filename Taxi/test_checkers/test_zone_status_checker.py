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
            {
                'data': checkers_utils.mock_prepared_data(
                    zone_status=types.ZoneStatus.OK,
                ),
            },
            (True, ''),
            id='zone_status OK',
        ),
        pytest.param(
            {
                'data': checkers_utils.mock_prepared_data(
                    zone_status=types.ZoneStatus.ERROR,
                ),
            },
            (False, 'Зона недоступна'),
            id='zone_status ERROR',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
async def test_zone_status_checker(web_context, input_data, expected_result):
    checker = checkers_utils.get_checker_instance(
        client_checkers.ZoneStatusChecker, web_context, **input_data,
    )

    assert await checker.check() == expected_result
