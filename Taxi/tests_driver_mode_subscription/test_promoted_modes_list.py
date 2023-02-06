import datetime as dt
from typing import Any
from typing import Dict
from typing import List

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scenario

_LONG_AGO = dt.datetime.fromisoformat('2020-01-01T08:00:00+03:00')
_NOW = dt.datetime.fromisoformat('2020-04-04T08:00:00+03:00')

_PROMO_TITLE = 'Новый режим дохода «За время»'
_PROMO_SUBTITLE = 'Доход не зависит от числа заказов и известен заранее.'


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[
            mode_rules.Patch('duplicated_mode'),
            mode_rules.Patch('blocked_mode'),
            mode_rules.Patch(
                'unavailable_mode', condition={'any_of': ['missing_tag']},
            ),
            mode_rules.Patch('driver_fix', stops_at=_LONG_AGO),
            mode_rules.Patch('not_expired_mode'),
            mode_rules.Patch('expired_mode'),
            mode_rules.Patch('not_started_mode'),
            mode_rules.Patch('conditional_mode_1'),
            mode_rules.Patch('conditional_mode_2'),
            mode_rules.Patch('conditional_mode_3'),
            mode_rules.Patch('conditional_mode_4'),
            mode_rules.Patch('broken_tankerkeys_mode'),
        ],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_RULES_BLOCKING_TAGS={
        'blocked_mode': {'tags': ['blocking_tag']},
    },
    DRIVER_MODE_SUBSCRIPTION_PROMO_V2={
        'promoted_modes': [
            {
                'work_mode': 'orders',
                'title_tanker_key': 'promo.title',
                'text_tanker_key': 'promo.description',
                'deeplink_target': 'offer_screen',
                'banner_type': 'default',
            },
            {
                'work_mode': 'duplicated_mode',
                'title_tanker_key': 'promo.title',
                'text_tanker_key': 'promo.description',
                'deeplink_target': 'offer_screen',
                'banner_type': 'default',
            },
            {
                'work_mode': 'duplicated_mode',
                'title_tanker_key': 'promo.title',
                'text_tanker_key': 'promo.description_for_test',
                'deeplink_target': 'offer_screen',
                'banner_type': 'default',
            },
            {
                'work_mode': 'blocked_mode',
                'title_tanker_key': 'promo.title',
                'text_tanker_key': 'promo.description',
                'deeplink_target': 'offers_list',
                'banner_type': 'big_money',
            },
            {
                'work_mode': 'unavailable_mode',
                'title_tanker_key': 'promo.title',
                'text_tanker_key': 'promo.description',
                'deeplink_target': 'offer_screen',
                'banner_type': 'default',
            },
            {
                'work_mode': 'not_expired_mode',
                'title_tanker_key': 'promo.title',
                'text_tanker_key': 'promo.description',
                'deeplink_target': 'offer_screen',
                'banner_type': 'default',
                'start_at': '2020-04-04T07:59:00+03:00',
                'stop_at': '2020-04-04T08:01:00+03:00',
            },
            {
                'work_mode': 'expired_mode',
                'title_tanker_key': 'promo.title',
                'text_tanker_key': 'promo.description',
                'deeplink_target': 'offer_screen',
                'banner_type': 'default',
                'start_at': '2020-04-04T07:58:00+03:00',
                'stop_at': '2020-04-04T07:59:00+03:00',
            },
            {
                'work_mode': 'not_started_mode',
                'title_tanker_key': 'promo.title',
                'text_tanker_key': 'promo.description',
                'deeplink_target': 'offer_screen',
                'banner_type': 'default',
                'start_at': '2020-04-04T08:01:00+03:00',
                'stop_at': '2020-04-04T08:02:00+03:00',
            },
            {
                'work_mode': 'conditional_mode_1',
                'title_tanker_key': 'promo.title',
                'text_tanker_key': 'promo.description',
                'deeplink_target': 'offer_screen',
                'banner_type': 'default',
                'condition': {
                    'and': [
                        {'all_of': ['tag1', 'tag2']},
                        {'any_of': ['tag3', 'tag4']},
                        {'none_of': ['tag5', 'tag6']},
                    ],
                },
            },
            {
                'work_mode': 'conditional_mode_2',
                'title_tanker_key': 'promo.title',
                'text_tanker_key': 'promo.description',
                'deeplink_target': 'offer_screen',
                'banner_type': 'default',
                'condition': {
                    'or': [
                        {'all_of': ['tag5']},  # not satisfied
                        {'any_of': ['tag5']},  # not satisfied
                        {'none_of': ['tag1']},  # not satisfied
                    ],
                },
            },
            {
                'work_mode': 'conditional_mode_3',
                'title_tanker_key': 'promo.title',
                'text_tanker_key': 'promo.description',
                'deeplink_target': 'offer_screen',
                'banner_type': 'default',
                'condition': {
                    'or': [
                        {'all_of': ['tag5', 'tag6']},  # not satisfied
                        {'any_of': ['tag4']},  # not satisfied
                        {'none_of': ['tag5', 'tag6']},
                    ],
                },
            },
            {
                'work_mode': 'conditional_mode_4',
                'title_tanker_key': 'promo.title',
                'text_tanker_key': 'promo.description',
                'deeplink_target': 'offer_screen',
                'banner_type': 'default',
                'condition': {
                    'and': [
                        {'all_of': ['tag1', 'tag2']},
                        {'any_of': ['tag3', 'tag4']},
                        {'none_of': ['tag5', 'tag3']},  # not satisfied
                    ],
                },
            },
            {
                'work_mode': 'broken_tankerkeys_mode',
                'title_tanker_key': 'promo.title',
                'text_tanker_key': 'promo.not_existing_key',
                'deeplink_target': 'offer_screen',
                'banner_type': 'default',
            },
            # All keys here are corect, but it's the second matching mode
            # So we aren't expecting to see this promo
            {
                'work_mode': 'broken_tankerkeys_mode',
                'title_tanker_key': 'promo.title',
                'text_tanker_key': 'promo.description',
                'deeplink_target': 'offer_screen',
                'banner_type': 'default',
            },
        ],
    },
)
@pytest.mark.now(_NOW.isoformat())
async def test_promoted_modes_list(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        mode_rules_data,
        mode_geography_defaults,
):
    profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene({profile: driver.Mode('orders')})
    scene.setup(mockserver, mocked_time)

    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _driver_tags_handler(request):
        return {'tags': ['blocking_tag', 'tag1', 'tag2', 'tag3', 'tag7']}

    response = await taxi_driver_mode_subscription.get(
        'v1/promoted-modes-list',
        params={
            'lat': scenario.SAMARA_POSITION.lat,
            'lon': scenario.SAMARA_POSITION.lon,
            'tz': 'Europe/Samara',
            'park_id': 'dbid0',
            'driver_profile_id': 'uuid0',
        },
        headers={
            'Accept-Language': 'ru',
            'X-Ya-Service-Ticket': common.MOCK_TICKET,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'promoted_modes': [
            {
                'title': _PROMO_TITLE,
                'subtitle': _PROMO_SUBTITLE,
                'offer_id': 'orders',
                'banner_type': 'default',
            },
            {
                'title': _PROMO_TITLE,
                'subtitle': _PROMO_SUBTITLE,
                'offer_id': 'duplicated_mode',
                'banner_type': 'default',
            },
            {
                'title': _PROMO_TITLE,
                'subtitle': _PROMO_SUBTITLE,
                'banner_type': 'big_money',
            },  # blocked
            {
                'title': _PROMO_TITLE,
                'subtitle': _PROMO_SUBTITLE,
                'offer_id': 'not_expired_mode',
                'banner_type': 'default',
            },
            {
                'title': _PROMO_TITLE,
                'subtitle': _PROMO_SUBTITLE,
                'offer_id': 'conditional_mode_1',
                'banner_type': 'default',
            },
            {
                'title': _PROMO_TITLE,
                'subtitle': _PROMO_SUBTITLE,
                'offer_id': 'conditional_mode_3',
                'banner_type': 'default',
            },
        ],
    }


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


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[
            mode_rules.Patch('driver_fix', stops_at=_LONG_AGO),
            mode_rules.Patch(
                'driver_fix_one_offer',
                features={'driver_fix': {'roles': [{'name': 'one_offer'}]}},
            ),
            mode_rules.Patch(
                'driver_fix_two_offers',
                features={'driver_fix': {'roles': [{'name': 'two_offers'}]}},
            ),
        ],
    ),
)
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_PROMO_V2={
        'promoted_modes': [
            {
                'work_mode': 'driver_fix_one_offer',
                'title_tanker_key': 'promo.title',
                'text_tanker_key': 'promo.description',
                'deeplink_target': 'offer_screen',
                'banner_type': 'default',
            },
            {
                'work_mode': 'driver_fix_two_offers',
                'title_tanker_key': 'promo.title',
                'text_tanker_key': 'promo.description',
                'deeplink_target': 'offer_screen',
                'banner_type': 'default',
            },
        ],
    },
)
@pytest.mark.now('2020-04-04T08:00:00+0300')
async def test_single_offer_deeplink(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        mode_rules_data,
        mode_geography_defaults,
):
    profile = driver.Profile('dbid0_uuid0')
    scene = scenario.Scene({profile: driver.Mode('orders')})
    scene.setup(mockserver, mocked_time)

    @mockserver.json_handler('/driver-fix/v1/view/offer')
    async def _mock_view_offer(request):
        offers_count = (
            2 if request.json['roles'] == [{'name': 'two_offers'}] else 1
        )
        return {'offers': _VIEW_OFFERS[:offers_count]}

    response = await taxi_driver_mode_subscription.get(
        'v1/promoted-modes-list',
        params={
            'lat': scenario.SAMARA_POSITION.lat,
            'lon': scenario.SAMARA_POSITION.lon,
            'tz': 'Europe/Samara',
            'park_id': 'dbid0',
            'driver_profile_id': 'uuid0',
        },
        headers={
            'Accept-Language': 'ru',
            'X-Ya-Service-Ticket': common.MOCK_TICKET,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'promoted_modes': [
            {
                'title': _PROMO_TITLE,
                'subtitle': _PROMO_SUBTITLE,
                'offer_id': 'driver_fix_one_offer_id_rule1',
                'banner_type': 'default',
            },
            {
                'title': _PROMO_TITLE,
                'subtitle': _PROMO_SUBTITLE,
                'banner_type': 'default',
            },
        ],
    }
