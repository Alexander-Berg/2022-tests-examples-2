from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates
from tests_driver_mode_subscription import scenario


_DRIVER_FIX_OFFERS: List[Dict[str, Any]] = [
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


@pytest.fixture(name='driver_fix')
def _mock_driver_fix(mockserver):
    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        return {'offers': _DRIVER_FIX_OFFERS}


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[mode_rules.Patch(rule_name='custom_orders')],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_RULES_BLOCKING_TAGS={
        'orders': {'tags': ['freeze_orders', 'freeze_all']},
        'custom_orders': {'tags': ['freeze_custom_orders']},
        'driver_fix': {'tags': ['freeze_driver_fix']},
    },
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.parametrize(
    'driver_mode, driver_tags, driver_tags_error, '
    'expected_code, expected_offers, expected_disabled_offers',
    [
        pytest.param(
            'orders',
            [],
            None,
            200,
            ['custom_orders', 'driver_fix_id_rule1'],
            ['driver_fix_id_rule2', 'orders'],
            id='orders_default',
        ),
        pytest.param(
            'custom_orders',
            [],
            None,
            200,
            ['driver_fix_id_rule1', 'orders'],
            ['custom_orders', 'driver_fix_id_rule2'],
            id='custom_orders_default',
        ),
        pytest.param(
            'orders',
            ['freeze_custom_orders'],
            None,
            200,
            ['driver_fix_id_rule1'],
            ['custom_orders', 'driver_fix_id_rule2', 'orders'],
            id='freeze_custom_orders',
        ),
        pytest.param(
            'orders',
            ['freeze_driver_fix', 'freeze_custom_orders'],
            None,
            200,
            [],
            [
                'custom_orders',
                'driver_fix_id_rule1',
                'driver_fix_id_rule2',
                'orders',
            ],
            id='freeze_all',
        ),
        pytest.param(
            'orders',
            [],
            scenario.ServiceError.ServerError,
            500,
            [],
            [],
            id='tags_500',
        ),
        pytest.param(
            'orders',
            [],
            scenario.ServiceError.TimeoutError,
            500,
            [],
            [],
            id='tags_timeout',
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_mode_blocked_by_tag(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        driver_authorizer,
        driver_fix,
        mode_rules_data,
        mode_geography_defaults,
        driver_mode: str,
        driver_tags: List[str],
        driver_tags_error: Optional[scenario.ServiceError],
        expected_code: int,
        expected_offers: List[str],
        expected_disabled_offers: List[str],
):
    profile = driver.Profile(dbid_uuid='park_driver')
    scene = scenario.Scene(profiles={profile: driver.Mode(driver_mode)})
    scene.setup(mockserver, mocked_time, driver_authorizer)
    scene.mock_driver_tags(
        mockserver=mockserver,
        tags=driver_tags,
        service_error=driver_tags_error or scenario.ServiceError.NoError,
    )

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == expected_code
    if expected_code != 200:
        return

    doc = response.json()
    offers = []
    disabled_offers = []
    for mode, mode_doc in doc['driver_modes'].items():
        if mode_doc['ui']['accept_button']['enabled']:
            offers.append(mode)
        else:
            disabled_offers.append(mode)

    offers.sort()
    disabled_offers.sort()

    assert expected_offers == offers
    assert expected_disabled_offers == disabled_offers


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[mode_rules.Patch(rule_name='custom_orders')],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_RULES_BLOCKING_TAGS={
        'custom_orders': {
            'tags': ['freeze_custom_orders', 'freeze_all_modes'],
        },
    },
    DRIVER_MODE_SUBSCRIPTION_BLOCKING_TAGS={
        '__default__': {
            # the only key that's used for now
            'disable_button': 'offer_card.blocked.default.button',
            'message_title': 'offer_card.blocked.default.title',
            'message_body': 'offer_card.blocked.body',
        },
        'freeze_all_modes': {
            # the only key that's used for now
            'disable_button': 'offer_card.blocked.freeze.button',
            'message_title': 'offer_card.blocked.default.title',
            'message_body': 'offer_card.blocked.body',
        },
    },
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.parametrize(
    'driver_tags, enabled, disable_reason',
    [
        pytest.param(
            ['cool_guy', 'writes_in_cpp'], True, None, id='enabled_mode',
        ),
        pytest.param(
            ['freeze_custom_orders'],
            False,
            'Режим заблокирован тегом',
            id='blocked_default_message',
        ),
        pytest.param(
            ['freeze_all_modes'],
            False,
            'Режим заблокирован сильным холодом за окном',
            id='blocked_by_cold_weather',
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_reasons(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        driver_authorizer,
        driver_fix,
        mode_rules_data,
        mode_geography_defaults,
        driver_tags: List[str],
        enabled: bool,
        disable_reason: Optional[str],
):
    profile = driver.Profile(dbid_uuid='park_driver')
    scene = scenario.Scene(profiles={profile: driver.Mode('orders')})
    scene.setup(mockserver, mocked_time, driver_authorizer)
    scene.mock_driver_tags(mockserver=mockserver, tags=driver_tags)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200

    doc = response.json()
    assert 'custom_orders' in doc['driver_modes']
    button_doc = doc['driver_modes']['custom_orders']['ui']['accept_button']
    assert enabled == button_doc['enabled']
    if disable_reason:
        assert disable_reason == button_doc['title']
