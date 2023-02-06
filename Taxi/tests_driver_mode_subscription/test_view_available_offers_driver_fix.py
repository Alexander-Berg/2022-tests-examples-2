import datetime
from typing import Any
from typing import Dict
from typing import List

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates
from tests_driver_mode_subscription import scenario

_DRIVER_MODE_RULES = mode_rules.default_mode_rules()

_ROLE_NAME = 'role0'

_VIEW_OFFERS: List[Dict[str, Any]] = [
    {
        'offer_card': {
            'title': 'За время',
            'subtitle': 'Доступен до 2 декабря',
            'description': 'Заработок зависит от времени работы',
            'is_new': True,
            'enabled': True,
        },
        'settings': {'rule_id': 'id_rule1', 'shift_close_time': '00:01'},
        'offer_screen': {
            'items': [{'type': 'text', 'text': 'Подробности правила 1.'}],
        },
        'memo_screen': {'items': [{'type': 'text', 'text': 'Memo правила 1'}]},
    },
    {
        'offer_card': {
            'title': 'За время',
            'subtitle': 'Был доступен до 15 ноября',
            'description': 'Заработок зависит от времени работы',
            'is_new': False,
            'enabled': False,
            'disable_reason': 'Был доступен до 15 ноября',
        },
        'settings': {'rule_id': 'id_rule2', 'shift_close_time': '00:02'},
        'offer_screen': {
            'items': [{'type': 'text', 'text': 'Подробности правила 2.'}],
        },
        'memo_screen': {'items': [{'type': 'text', 'text': 'Memo правила 2'}]},
    },
]

_DRIVER_FIX_SETTINGS = {
    'rule_id': 'id_rule1',
    'shift_close_time': '00:00:00+03:00',
}


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[
            mode_rules.Patch(
                rule_name='driver_fix',
                starts_at=datetime.datetime.fromisoformat(
                    '2020-05-01T05:00:00+00:00',
                ),
                features={'driver_fix': {'roles': [{'name': _ROLE_NAME}]}},
            ),
        ],
    ),
)
@pytest.mark.now('2020-05-05T05:00:00+00:00')
async def test_view_offer_driver_fix_role_parameter(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
):
    profile = driver.Profile('dbid_uuid')

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
    assert _mock_view_offer.has_calls

    request = _mock_view_offer.next_call()['request']
    roles = request.json['roles']
    assert len(roles) == 1
    assert roles[0]['name'] == _ROLE_NAME


@pytest.mark.now('2020-05-05T05:00:00+00:00')
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[
            mode_rules.Patch(
                rule_name='driver_fix',
                starts_at=datetime.datetime.fromisoformat(
                    '2020-05-01T05:00:00+00:00',
                ),
                features={'driver_fix': {'roles': [{'name': _ROLE_NAME}]}},
            ),
        ],
        rules=_DRIVER_MODE_RULES,
    ),
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_AVAILABLE_OFFERS_POLLING_DELAYS={
        'normal_delay_s': 600,
        'current_mode_has_no_offers_delay_s': 600,
        'offer_provider_fail_delay_s': 123,
    },
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.parametrize(
    'current_mode, expected_code, expect_polling_delay',
    [
        pytest.param(
            'orders', 200, 20, id='current mode has not driver-fix feature',
        ),
        pytest.param(
            'driver_fix', 500, 20, id='current mode has driver-fix feature',
        ),
    ],
)
async def test_view_offer_driver_fix_failed(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        current_mode: str,
        expected_code: int,
        expect_polling_delay: int,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(
            request, current_mode, mocked_time,
        )
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        raise mockserver.TimeoutError()

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.headers['X-Polling-Delay'] == '123'

    assert _mock_view_offer.has_calls


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.now('2020-05-05T05:00:00+00:00')
async def test_view_offer_driver_fix_timezone(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
):
    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(request, 'orders', mocked_time)
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        return {'offers': []}

    profile = driver.Profile('dbid_uuid')

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await taxi_driver_mode_subscription.get(
        'v1/view/available_offers',
        params={'lon': '131.8', 'lat': '43.1', 'tz': 'Europe/Moscow'},
        headers={
            **common.get_api_v1_headers(profile),
            'Accept-Language': 'ru',
        },
    )
    assert response.status_code == 200

    assert _mock_view_offer.has_calls
    request = _mock_view_offer.next_call()['request']
    assert request.args['tz'] == 'Europe/Moscow'


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[
            mode_rules.Patch(
                rule_name='driver_fix',
                offers_group='no_group',
                features={'driver_fix': {}},
            ),
        ],
    ),
)
@pytest.mark.now('2020-05-01T12:00:00+0300')
async def test_available_offers_driver_fix_without_group_selected(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        load_json,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(
            request,
            'driver_fix',
            mocked_time,
            mode_settings=_DRIVER_FIX_SETTINGS,
        )
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        return {'offers': _VIEW_OFFERS}

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200
    doc = response.json()

    driver_fix_selected_card_ctor = doc['ui']['items'][0]
    orders_card_ctor = doc['ui']['items'][1]

    assert driver_fix_selected_card_ctor == load_json(
        'expected_no_group_offer_card.json',
    )

    assert doc['driver_modes']['driver_fix_id_rule1'] == load_json(
        'expected_no_group_driver_modes_item.json',
    )

    assert orders_card_ctor == load_json(
        'expected_no_group_orders_offer_card.json',
    )

    assert doc['driver_modes']['orders'] == load_json(
        'expected_no_group_orders_driver_modes_item.json',
    )

    assert len(doc['ui']['items']) == 2


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[
            mode_rules.Patch(
                rule_name='driver_fix',
                stops_at=datetime.datetime.fromisoformat(
                    '2020-05-01T05:00:00+00:00',
                ),
                features={'driver_fix': {}},
            ),
            mode_rules.Patch(
                rule_name='custom_orders',
                stops_at=datetime.datetime.fromisoformat(
                    '2000-05-01T05:00:00+00:00',
                ),
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    'card_number, expected_ctor_json',
    [
        (0, 'expected_card_offer_selected.json'),
        (1, 'expected_card_offer_orders.json'),
    ],
)
@pytest.mark.now('2020-06-01T12:00:00+0300')
async def test_show_only_selected_offer_when_mode_unavailable(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        load_json,
        card_number,
        expected_ctor_json,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(
            request,
            'driver_fix',
            mocked_time,
            mode_settings=_DRIVER_FIX_SETTINGS,
        )
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        return {'offers': _VIEW_OFFERS}

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200
    doc = response.json()
    card_ctor = doc['ui']['items'][card_number]

    assert len(doc['ui']['items']) == 2

    # in this test we interest only in UI-fields
    del card_ctor['payload']

    expected_ctor = load_json(expected_ctor_json)
    assert card_ctor == expected_ctor
