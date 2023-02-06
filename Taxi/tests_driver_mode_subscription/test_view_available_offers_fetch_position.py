from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates
from tests_driver_mode_subscription import scenario

_DRIVER_MODE_RULES = mode_rules.default_mode_rules()


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
    DRIVER_MODE_SUBSCRIPTION_QUERY_POSITIONS_PARAMS={
        'fallback_on': True,
        'max_age_s': 180,
        'max_retries': 3,
        'source': 'raw_or_adjusted',
        'timeout_ms': 50,
        'max_historic_age_h': 123,
    },
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.now('2020-05-05T05:00:00+00:00')
@pytest.mark.parametrize(
    'driver_trackstory_position, client_position, expected_position',
    [
        pytest.param(
            scenario.MOSCOW_POSITION,
            scenario.PERM_POSITION,
            scenario.MOSCOW_POSITION,
            id='prefer trackstory position',
        ),
        pytest.param(
            None,
            scenario.PERM_POSITION,
            scenario.PERM_POSITION,
            id='use client position',
        ),
        pytest.param(
            scenario.PERM_POSITION,
            None,
            scenario.PERM_POSITION,
            id='use trackstory position',
        ),
    ],
)
async def test_view_offer_position_pass(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        driver_trackstory_position: Optional[common.Position],
        client_position: Optional[common.Position],
        expected_position: common.Position,
):
    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(request, 'orders', mocked_time)
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        return {'offers': []}

    profile = driver.Profile('dbid_uuid')

    trackstory_mock = scenario.Scene.mock_driver_trackstory(
        mockserver, driver_trackstory_position,
    )

    response = await common.get_available_offers(
        taxi_driver_mode_subscription,
        profile,
        client_position=client_position,
    )

    assert response.status_code == 200

    assert _mock_view_offer.has_calls
    request = _mock_view_offer.next_call()['request']
    assert float(request.args['lon']) == expected_position.lon
    assert float(request.args['lat']) == expected_position.lat

    actual_trackstory_request = trackstory_mock.next_call()['request'].json
    # using historic age
    assert actual_trackstory_request['max_age'] == 442800
