import datetime
from typing import List
from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import geography_tools
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates
from tests_driver_mode_subscription import scenario

_PAST = datetime.datetime.fromisoformat('2019-05-01T11:00:00+03:00')

_NORMAL_DELAY = 238
_ONE_RULE_DELAY = 600
_PROVIDER_FAIL_DELAY = 100
_NO_OFFERS_DELAY = 1800
_ONE_RULE_DELAY_WITH_BROKEN_TARIFF_ZONE = 400


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_AVAILABLE_OFFERS_POLLING_DELAYS={
        'normal_delay_s': _NORMAL_DELAY,
        'current_mode_has_no_offers_delay_s': _NO_OFFERS_DELAY,
        'one_rule_available_delay_s': _ONE_RULE_DELAY,
        'offer_provider_fail_delay_s': _PROVIDER_FAIL_DELAY,
    },
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
    DRIVER_MODE_GEOGRAPHY_DEFAULTS={
        'work_modes_available_by_default': [
            'orders',
            'driver_fix',
            'custom_orders',
        ],
    },
)
@pytest.mark.parametrize(
    'current_work_mode, expected_polling_delay, mode_geography_configuration, '
    'driver_position',
    [
        pytest.param(
            'orders',
            str(_NORMAL_DELAY),
            None,
            None,
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        patches=[
                            mode_rules.Patch('driver_fix', stops_at=_PAST),
                        ],
                    ),
                ),
            ],
            id='many_offers',
        ),
        pytest.param(
            'orders',
            str(_ONE_RULE_DELAY),
            None,
            None,
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        patches=[
                            mode_rules.Patch('driver_fix', stops_at=_PAST),
                            mode_rules.Patch('custom_orders', stops_at=_PAST),
                        ],
                    ),
                ),
            ],
            id='one_rule',
        ),
        pytest.param(
            'orders',
            str(_NORMAL_DELAY),
            None,
            None,
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        patches=[
                            mode_rules.Patch('driver_fix', stops_at=_PAST),
                            mode_rules.Patch('custom_orders', stops_at=_PAST),
                        ],
                    ),
                ),
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_AVAILABLE_OFFERS_POLLING_DELAYS={
                        'normal_delay_s': _NORMAL_DELAY,
                        'current_mode_has_no_offers_delay_s': _NO_OFFERS_DELAY,
                        'offer_provider_fail_delay_s': _PROVIDER_FAIL_DELAY,
                    },
                ),
            ],
            id='one_offer_no_config',
        ),
        pytest.param(
            'uberdriver',
            str(_NO_OFFERS_DELAY),
            None,
            None,
            marks=[
                pytest.mark.mode_rules(rules=mode_rules.default_mode_rules()),
            ],
            id='no_offers',
        ),
        pytest.param(
            'orders',
            str(_PROVIDER_FAIL_DELAY),
            None,
            None,
            marks=[
                pytest.mark.mode_rules(rules=mode_rules.default_mode_rules()),
            ],
            id='some_providers_failed_1_offer',
        ),
        pytest.param(
            'orders',
            str(_ONE_RULE_DELAY),
            [
                # Disable root, enable moscow
                geography_tools.ModeGeographyConfiguration(
                    'test_rule', 'br_root', False,
                ),
                geography_tools.ModeGeographyConfiguration(
                    'test_rule', 'br_moscow', True,
                ),
            ],
            None,
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        patches=[
                            mode_rules.Patch('driver_fix', stops_at=_PAST),
                            mode_rules.Patch('custom_orders', stops_at=_PAST),
                            mode_rules.Patch('test_rule'),
                        ],
                    ),
                ),
            ],
            id='one_offer_with_broken_position_but_no_config',
        ),
        pytest.param(
            'orders',
            str(_ONE_RULE_DELAY_WITH_BROKEN_TARIFF_ZONE),
            [
                # Disable root, enable moscow
                geography_tools.ModeGeographyConfiguration(
                    'test_rule', 'br_root', False,
                ),
                geography_tools.ModeGeographyConfiguration(
                    'test_rule', 'br_moscow', True,
                ),
            ],
            None,
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        patches=[
                            mode_rules.Patch('driver_fix', stops_at=_PAST),
                            mode_rules.Patch('custom_orders', stops_at=_PAST),
                            mode_rules.Patch('test_rule'),
                        ],
                    ),
                ),
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_AVAILABLE_OFFERS_POLLING_DELAYS={
                        'normal_delay_s': _NORMAL_DELAY,
                        'current_mode_has_no_offers_delay_s': _NO_OFFERS_DELAY,
                        'one_rule_available_delay_s': _ONE_RULE_DELAY,
                        'offer_provider_fail_delay_s': _PROVIDER_FAIL_DELAY,
                        'one_rule_available_but_no_tariff_zone_delay_s': (
                            _ONE_RULE_DELAY_WITH_BROKEN_TARIFF_ZONE
                        ),
                    },
                ),
            ],
            id='one_offer_with_broken_position_using_delay_from_config',
        ),
        pytest.param(
            'orders',
            str(_ONE_RULE_DELAY),
            [
                # Disable root, enable moscow
                geography_tools.ModeGeographyConfiguration(
                    'test_rule', 'br_root', False,
                ),
                geography_tools.ModeGeographyConfiguration(
                    'test_rule', 'br_moscow', True,
                ),
            ],
            scenario.SAMARA_POSITION,
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        patches=[
                            mode_rules.Patch('driver_fix', stops_at=_PAST),
                            mode_rules.Patch('custom_orders', stops_at=_PAST),
                            mode_rules.Patch('test_rule'),
                        ],
                    ),
                ),
                pytest.mark.config(
                    DRIVER_MODE_SUBSCRIPTION_AVAILABLE_OFFERS_POLLING_DELAYS={
                        'normal_delay_s': _NORMAL_DELAY,
                        'current_mode_has_no_offers_delay_s': _NO_OFFERS_DELAY,
                        'one_rule_available_delay_s': _ONE_RULE_DELAY,
                        'offer_provider_fail_delay_s': _PROVIDER_FAIL_DELAY,
                        'one_rule_available_but_no_tariff_zone_delay_s': (
                            _ONE_RULE_DELAY_WITH_BROKEN_TARIFF_ZONE
                        ),
                    },
                ),
            ],
            id='one_offer_with_correct_position_and_geo',
        ),
    ],
)
async def test_custom_polling_delay(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mockserver,
        pgsql,
        current_work_mode: str,
        expected_polling_delay: str,
        mode_geography_configuration: Optional[
            List[geography_tools.ModeGeographyConfiguration]
        ],
        driver_position: Optional[common.Position],
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        return {
            'docs': [
                {
                    'kind': 'driver_mode_subscription',
                    'external_event_ref': 'idempotency',
                    'event_at': '2019-05-01T12:00:00+0300',
                    'data': {
                        'driver': {
                            'park_id': 'park_id_0',
                            'driver_profile_id': 'uuid',
                        },
                        'mode': current_work_mode,
                    },
                },
            ],
            'cursor': common.MODE_HISTORY_CURSOR,
        }

    if mode_geography_configuration is not None:
        geography_tools.insert_mode_geography(
            mode_geography_configuration, pgsql,
        )

    # for test with failed provider
    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        raise mockserver.TimeoutError()

    # for test with one available offer and one failed geo
    scenario.Scene.mock_driver_trackstory(mockserver, driver_position)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200
    assert response.headers['X-Polling-Delay'] == expected_polling_delay
