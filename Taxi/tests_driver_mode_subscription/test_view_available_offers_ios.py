import enum
from typing import List
from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import offer_templates
from tests_driver_mode_subscription import scenario


class TaximeterPlatform(enum.Enum):
    IOS = 'ios'
    ANDROID = 'android'


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(patches=[mode_rules.Patch('custom_orders')]),
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_ban_ios(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
):
    profile = driver.Profile('dbid_uuid')

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(request, 'orders', mocked_time)
        return response

    scenario.Scene.mock_driver_trackstory(mockserver)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription,
        profile,
        platform=TaximeterPlatform.IOS.value,
    )
    assert response.status_code == 200
    doc = response.json()

    item_titles = []
    for offer_item_ui in doc['ui']['items']:
        item_titles.append(offer_item_ui['items'][0]['title'])

    assert item_titles == []


_VERSION_562 = '8.80 (562)'
_VERSION_600 = '9.72 (600)'


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_OFFER_TEMPLATES=(
        offer_templates.DEFAULT_OFFER_TEMPLATES
    ),
    DRIVER_MODE_SUBSCRIPTION_MODE_TEMPLATE_RELATIONS=(
        offer_templates.DEFAULT_MODE_TEMPLATE_RELATIONS
    ),
    DRIVER_MODE_SUBSCRIPTION_ENABLE_OFFERS_FOR_IOS=True,
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(patches=[mode_rules.Patch('custom_orders')]),
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='available_offers_ios_display_modes.json')
@pytest.mark.parametrize(
    'dbid_uuid, udid, position, tags, platform, version, expected_titles',
    [
        pytest.param(
            'dbid_uuid',
            'udid',
            scenario.SPB_POSITION,
            [],
            TaximeterPlatform.IOS,
            _VERSION_562,
            # We append current work mode even if unavailable
            ['За заказы'],
            id='empty_set',
        ),
        pytest.param(
            'dbid_uuid',
            'udid1',
            scenario.SPB_POSITION,
            [],
            TaximeterPlatform.IOS,
            _VERSION_562,
            ['За заказы', 'Карточка.Заголовок(default)'],
            id='match_udid',
        ),
        pytest.param(
            'dbid_uuid',
            None,
            scenario.SPB_POSITION,
            [],
            TaximeterPlatform.IOS,
            _VERSION_562,
            # We append current work mode even if unavailable
            ['За заказы'],
            id='no_udid',
        ),
        pytest.param(
            'dbid1_uuid1',
            'udid',
            scenario.SPB_POSITION,
            [],
            TaximeterPlatform.IOS,
            _VERSION_562,
            ['За заказы', 'Карточка.Заголовок(default)', 'За время'],
            id='match_dbid_uuid',
        ),
        pytest.param(
            'dbid_uuid',
            'udid',
            scenario.SPB_POSITION,
            [
                'loginef_driver',
                'discount_1000_2020_04_01_loginef_test_effdev_1040_tmp',
            ],
            TaximeterPlatform.IOS,
            _VERSION_562,
            ['За заказы', 'Карточка.Заголовок(default)', 'За время'],
            id='match_tags',
        ),
        pytest.param(
            'dbid_uuid',
            'udid',
            scenario.MOSCOW_POSITION,
            [],
            TaximeterPlatform.IOS,
            _VERSION_562,
            ['За заказы', 'Карточка.Заголовок(default)', 'За время'],
            id='match_geonodes',
        ),
        pytest.param(
            'dbid_uuid',
            'udid',
            scenario.SPB_POSITION,
            [],
            TaximeterPlatform.IOS,
            _VERSION_600,
            ['За заказы', 'Карточка.Заголовок(default)', 'За время'],
            id='match_version',
        ),
        pytest.param(
            'dbid_uuid',
            'udid',
            scenario.SPB_POSITION,
            [],
            TaximeterPlatform.ANDROID,
            _VERSION_562,
            ['За заказы', 'Карточка.Заголовок(default)', 'За время'],
            id='android',
        ),
        pytest.param(
            'dbid_uuid',
            'udid',
            None,
            [],
            TaximeterPlatform.IOS,
            _VERSION_562,
            # We append current work mode even if unavailable
            ['За заказы'],
            id='no_position',
        ),
    ],
)
async def test_ios_experiment(
        taxi_driver_mode_subscription,
        mode_rules_data,
        mode_geography_defaults,
        mockserver,
        mocked_time,
        dbid_uuid: str,
        udid: Optional[str],
        position: Optional[common.Position],
        tags: List[str],
        platform: TaximeterPlatform,
        version: str,
        expected_titles: List[str],
):
    profile = driver.Profile(dbid_uuid)

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        response = common.mode_history_response(request, 'orders', mocked_time)
        return response

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        return {
            'offers': [
                {
                    'offer_card': {
                        'title': 'За время',
                        'subtitle': 'Доступен до 2 декабря',
                        'description': 'Заработок зависит от времени работы',
                        'is_new': True,
                        'enabled': True,
                    },
                    'settings': {
                        'rule_id': 'id_rule1',
                        'shift_close_time': '00:01',
                    },
                    'offer_screen': {
                        'items': [
                            {'type': 'text', 'text': 'Подробности правила 1.'},
                        ],
                    },
                    'memo_screen': {
                        'items': [{'type': 'text', 'text': 'Memo правила 1'}],
                    },
                },
            ],
        }

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _v1_uniques(request):
        if udid:
            return {
                'uniques': [
                    {
                        'park_driver_profile_id': dbid_uuid,
                        'data': {'unique_driver_id': udid},
                    },
                ],
            }
        return {'uniques': []}

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _match_profile(request):
        return {'tags': tags}

    scenario.Scene.mock_driver_trackstory(mockserver, position)

    response = await common.get_available_offers(
        taxi_driver_mode_subscription,
        profile,
        platform=platform.value,
        version=version,
    )
    assert response.status_code == 200
    doc = response.json()

    item_titles = []

    for offer_item_ui in doc['ui']['items']:
        item_titles.append(offer_item_ui['items'][0]['title'])

    assert sorted(item_titles) == sorted(expected_titles)
