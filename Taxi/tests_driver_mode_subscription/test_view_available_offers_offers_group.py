from typing import List

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates
from tests_driver_mode_subscription import scenario


_DBID = 'testparkid'
_UUID = 'testdriverprofileid'

_OFFER_CARD_TITLE = 'offer_card_title'
_OFFER_CARD_SUBTITLE = 'offer_card_subtitle'
_OFFER_CARD_DESCRIPTION = 'offer_card_description'
_OFFER_HEADER = 'offer_header'
_OFFER_TEXT = 'offer_text'
_MEMO_HEADER = 'memo_header'
_MEMO_TEXT = 'memo_text'


@pytest.mark.mode_rules(
    rules=mode_rules.patched([mode_rules.Patch(rule_name='uberdriver')]),
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_AVAILABLE_OFFERS_POLLING_DELAYS={
        'normal_delay_s': 600,
        'current_mode_has_no_offers_delay_s': 123,
        'offer_provider_fail_delay_s': 600,
    },
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_available_offers_current_mode_without_offers(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
):
    profile = driver.Profile(f'{_DBID}_{_UUID}')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(
            request, 'uberdriver', mocked_time,
        )
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        return {'offers': []}

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )

    assert response.status_code == 200

    doc = response.json()
    assert not doc['ui']['items']
    assert doc['driver_modes'] == {}
    assert response.headers['X-Polling-Delay'] == '123'


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.parametrize(
    'expected_items_ids',
    (
        pytest.param(
            ['orders', 'custom_orders'],
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        [
                            mode_rules.Patch(
                                rule_name='custom_orders', offers_group='taxi',
                            ),
                        ],
                    ),
                ),
            ],
            id='mode with offers',
        ),
        pytest.param(
            ['orders'],
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        [
                            mode_rules.Patch(
                                rule_name='custom_orders',
                                offers_group='no_group',
                            ),
                        ],
                    ),
                ),
            ],
            id='mode without offers',
        ),
    ),
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_available_offers_mode_with_no_offers_excluded(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        expected_items_ids: List[str],
):
    profile = driver.Profile(f'{_DBID}_{_UUID}')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(request, 'orders', mocked_time)
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        return {'offers': []}

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )

    assert response.status_code == 200
    doc = response.json()

    item_ids = []

    for offer_item_ui in doc['ui']['items']:
        item_ids.append(offer_item_ui['id'])

    assert item_ids == expected_items_ids


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(rule_name='eda_orders', offers_group='eda'),
            mode_rules.Patch(
                rule_name='eda_custom_orders', offers_group='eda',
            ),
        ],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS={
        'by_mode_class': {},
        'by_work_mode': {
            'orders': 'orders_template',
            'driver_fix': 'driver_fix_template',
            'custom_orders': 'orders_template',
            'geobooking': 'geobooking_template',
            'eda_orders': 'orders_template',
            'eda_custom_orders': 'orders_template',
        },
    },
)
@pytest.mark.parametrize(
    'current_mode, expected_items_ids',
    (
        pytest.param('orders', ['orders', 'custom_orders'], id='taxi group'),
        pytest.param(
            'eda_orders', ['eda_orders', 'eda_custom_orders'], id='eda group',
        ),
    ),
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_available_offers_groups(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        current_mode: str,
        expected_items_ids: List[str],
):
    profile = driver.Profile(f'{_DBID}_{_UUID}')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(
            request, current_mode, mocked_time,
        )
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        return {'offers': []}

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )

    assert response.status_code == 200
    doc = response.json()

    item_ids = []

    for offer_item_ui in doc['ui']['items']:
        item_ids.append(offer_item_ui['id'])

    assert item_ids == expected_items_ids
