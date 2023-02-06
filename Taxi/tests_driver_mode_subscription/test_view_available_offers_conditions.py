from typing import Any
from typing import Dict
from typing import List

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates
from tests_driver_mode_subscription import scenario


_DBID = 'testparkid'
_UUID = 'testprofileid'


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.parametrize(
    'current_mode, condition, expected_items_ids, expect_driver_tags_calls',
    [
        pytest.param(
            'orders',
            {'none_of': ['tag1']},
            ['orders', 'custom_orders'],
            1,
            id='good',
        ),
        pytest.param('orders', {'none_of': ['tag3']}, ['orders'], 1, id='bad'),
        pytest.param(
            'orders',
            None,
            ['orders', 'custom_orders'],
            0,
            id='no rules with condition, so no driver-tags call',
        ),
        pytest.param(
            'custom_orders',
            {'none_of': ['tag3']},
            ['custom_orders', 'orders'],
            1,
            id='current mode always shown',
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_conditions(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        current_mode: str,
        condition: Dict[str, Any],
        expected_items_ids: List[str],
        expect_driver_tags_calls: int,
):
    profile = driver.Profile(f'{_DBID}_{_UUID}')

    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched_mode_rules(
            rule_name='custom_orders', condition=condition,
        ),
    )

    mode_geography_defaults.set_all_modes_available()

    driver_mock = common.make_driver_tags_mock(
        mockserver, ['tag3'], _DBID, _UUID,
    )

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

    assert driver_mock.times_called == expect_driver_tags_calls

    assert response.status_code == 200
    doc = response.json()

    item_ids = []

    for offer_item_ui in doc['ui']['items']:
        item_ids.append(offer_item_ui['id'])

    assert item_ids == expected_items_ids


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched_mode_rules(
        rule_name='custom_orders', condition={'none_of': ['tag3']},
    ),
)
@pytest.mark.parametrize(
    'driver_tags_error',
    [
        pytest.param(
            common.ServiceError.TimeoutError, id='driver-tags timeout',
        ),
        pytest.param(
            common.ServiceError.ServerError, id='driver-tags server error',
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_driver_tags_fail(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        driver_tags_error: common.ServiceError,
):
    profile = driver.Profile(f'{_DBID}_{_UUID}')

    driver_mock = common.make_driver_tags_mock(
        mockserver, ['tag3'], _DBID, _UUID, driver_tags_error,
    )

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

    assert driver_mock.times_called == 3

    assert response.status_code == 500

    response_body = response.json()
    assert response_body['code'] == '500'
    assert not response_body['message']
    assert 'details' not in response_body
