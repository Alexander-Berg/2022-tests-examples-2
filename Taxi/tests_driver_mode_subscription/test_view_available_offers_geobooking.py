import copy
import datetime
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

_DRIVER_MODE_RULES = mode_rules.patched(
    patches=[
        mode_rules.Patch(
            rule_name='geobooking',
            stops_at=datetime.datetime.fromisoformat(
                '2020-05-01T05:00:00+00:00',
            ),
            features={'geobooking': {}},
        ),
        mode_rules.Patch(
            rule_name='custom_orders',
            stops_at=datetime.datetime.fromisoformat(
                '2000-05-01T05:00:00+00:00',
            ),
        ),
        mode_rules.Patch(
            rule_name='driver_fix',
            stops_at=datetime.datetime.fromisoformat(
                '2000-05-01T05:00:00+00:00',
            ),
        ),
    ],
)

_VIEW_OFFERS: List[Dict[str, Any]] = [
    {
        'offer_card': {
            'title': 'C минимальной гарантией дохода(Нет мест)',
            'description': 'Заработок зависит от времени работы',
            'is_new': False,
            'enabled': True,
        },
        'settings': {'rule_id': 'id_rule3'},
        'key_params': {
            'tariff_zone': 'test_tariff_zone',
            'subvention_geoarea': 'test_subvention_geoarea',
            'tag': 'no_free_slots_tag',
        },
        'offer_screen': {
            'items': [{'type': 'text', 'text': 'Подробности правила 2.'}],
        },
        'memo_screen': {'items': [{'type': 'text', 'text': 'Memo правила 2'}]},
    },
    {
        'offer_card': {
            'title': 'C минимальной гарантией дохода',
            'subtitle': 'Подзаголовок geobooking',
            'description': 'Заработок зависит от времени работы',
            'is_new': True,
            'enabled': True,
            'details': {
                'type': 'detail',
                'title': '17:00 - 20:00',
                'subtitle': 'Волгоград, Южный',
                'detail': '250 P/час',
            },
        },
        'settings': {'rule_id': 'id_rule1'},
        'key_params': {
            'tariff_zone': 'volgograd',
            'subvention_geoarea': 'volgograd_south',
            'tag': 'courier_geobooking_2020',
        },
        'offer_screen': {
            'items': [{'type': 'text', 'text': 'Подробности правила 1.'}],
        },
        'memo_screen': {'items': [{'type': 'text', 'text': 'Memo правила 1'}]},
    },
    {
        'offer_card': {
            'title': 'C минимальной гарантией дохода 2',
            'description': 'Заработок зависит от времени работы',
            'is_new': False,
            'enabled': True,
        },
        'settings': {'rule_id': 'id_rule2'},
        'key_params': {
            'tariff_zone': 'test_tariff_zone',
            'subvention_geoarea': 'test_subvention_geoarea',
            'tag': 'test_tag',
        },
        'offer_screen': {
            'items': [{'type': 'text', 'text': 'Подробности правила 2.'}],
        },
        'memo_screen': {'items': [{'type': 'text', 'text': 'Memo правила 2'}]},
    },
]


class GeobookingContext:
    def __init__(self):
        self.offers = _VIEW_OFFERS
        self.check_rule_id = False
        self.expected_rule_id: Optional[str] = None
        self.handler = None

    def set_offers(self, offers: List[Dict[str, Any]]):
        self.offers = offers

    def expect_rule_id(self, rule_id: Optional[str]):
        self.check_rule_id = True
        self.expected_rule_id = rule_id


@pytest.fixture(name='geobooking_context')
def _geobooking_context():
    return GeobookingContext()


@pytest.fixture(name='geobooking')
def _mock_geobooking(mockserver, geobooking_context):
    @mockserver.json_handler('/driver-fix/v1/view/geobooking_offer')
    async def _mock_view_offer(request):
        doc = request.json
        assert doc['park_id'] == 'dbid'
        assert doc['driver_profile_id'] == 'uuid'
        if geobooking_context.check_rule_id:
            if geobooking_context.expected_rule_id:
                assert 'current_mode_settings' in doc
                assert (
                    doc['current_mode_settings']['rule_id']
                    == geobooking_context.expected_rule_id
                )
            else:
                assert 'current_mode_settings' not in doc
        return {'offers': geobooking_context.offers}

    geobooking_context.handler = _mock_view_offer


def _set_mode_settings(response, rule_id):
    data = response['docs'][0]['data']
    if rule_id:
        data['settings'] = common.MODE_SETTINGS
        data['settings']['rule_id'] = rule_id


@pytest.mark.pgsql('driver_mode_subscription', files=['no_free_slots.sql'])
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.parametrize(
    'card_number, expected_ctor_json',
    [
        (0, 'expected_card_offer_selected.json'),
        (1, 'expected_card_offer_normal_free_slots.json'),
        (2, 'expected_card_offer_normal_no_free_slots.json'),
        (3, 'expected_card_offer_orders.json'),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_card_constructor(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        geobooking,
        load_json,
        card_number,
        expected_ctor_json,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(
            request, 'geobooking', mocked_time,
        )
        _set_mode_settings(response, 'id_rule1')
        return response

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200
    doc = response.json()
    card_ctor = doc['ui']['items'][card_number]

    # in this test we interest only in UI-fields
    del card_ctor['payload']

    expected_ctor = load_json(expected_ctor_json)
    assert card_ctor == expected_ctor


@pytest.mark.pgsql('driver_mode_subscription', files=['no_free_slots.sql'])
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
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
        geobooking,
        load_json,
        card_number,
        expected_ctor_json,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(
            request, 'geobooking', mocked_time,
        )
        _set_mode_settings(response, 'id_rule1')
        return response

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


@pytest.mark.pgsql('driver_mode_subscription', files=['no_free_slots.sql'])
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_geobooking_offers_sort(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        taxi_config,
        geobooking,
        geobooking_context,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(request, 'orders', mocked_time)
        return response

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200
    doc = response.json()
    expected_titles = [
        'За заказы',
        'C минимальной гарантией дохода',
        'C минимальной гарантией дохода 2',
        'C минимальной гарантией дохода(Нет мест)',
    ]

    item_titles = []

    for offer_item_ui in doc['ui']['items']:
        item_titles.append(offer_item_ui['items'][0]['title'])

    assert item_titles == expected_titles


_ROLES = [{'name': 'role0'}, {'name': 'role1'}]


@pytest.mark.pgsql('driver_mode_subscription', files=['no_free_slots.sql'])
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(rules=_DRIVER_MODE_RULES)
@pytest.mark.parametrize(
    'has_roles',
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.mode_rules(
                    rules=mode_rules.patched(
                        [
                            mode_rules.Patch(
                                rule_name='geobooking',
                                features={'geobooking': {'roles': _ROLES}},
                            ),
                        ],
                        copy.deepcopy(_DRIVER_MODE_RULES),
                    ),
                ),
            ],
        ),
        pytest.param(False),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_role_parameter(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        geobooking,
        geobooking_context,
        has_roles,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(
            request, 'geobooking', mocked_time,
        )
        _set_mode_settings(response, 'id_rule1')
        return response

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription, profile,
    )
    assert response.status_code == 200

    assert geobooking_context.handler.times_called == 1
    geobooking_request = geobooking_context.handler.next_call()['request']
    roles = geobooking_request.json.get('roles', None)
    if has_roles:
        assert roles == _ROLES
    else:
        assert roles is None
