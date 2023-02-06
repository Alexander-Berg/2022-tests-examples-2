# pylint: disable=import-only-modules
import json

import pytest


PG_DRIVERS = [('driver001', 'park001'), ('driver002', 'park002')]

# data taken from
# https://kibana.taxi.tst.yandex-team.ru/app/kibana#/discover?_g=()&_a=(columns:!(_source),index:%271df0b0f0-b956-11e9-9ad8-afd09b0ebd4e%27,interval:auto,query:(language:kuery,query:%27ngroups:taxi_order-events-producer*%20and%20%22CONSUMER%20READ%22%27),sort:!(!(%27@timestamp%27,desc)))
@pytest.mark.parametrize(
    'message',
    [
        # json decode
        pytest.param(
            {
                'plan_transporting_distance_m': 36214.90557169914,
                'source_geopoint': [37.6424736597268, 55.73551995176587],
                'user_agent': (
                    'yandex-taxi/3.157.0.1040761'
                    ' Android/8.0.0 (samsung; SM-G935F)'
                ),
                'lookup_eta': 1594894371.1,
                'allowed_tariffs': {
                    '__park__': {
                        'econom': 1043.859649122807,
                        'minivan': 1370,
                        'pool': 939.6039603960396,
                        'cargo': 1615,
                        'maybach': 8897,
                        'night': 199,
                        'child_tariff': 967,
                        'comfortplus': 1410,
                        'suv': 1522,
                        'personal_driver': 2179,
                        'premium_suv': 1991,
                        'demostand': 1,
                        'business': 1270.6,
                        'selfdriving': 1,
                        'universal': 3956,
                        'cargocorp': 1531,
                        'premium_van': 16894,
                        'express': 884,
                        'vip': 1796,
                        'courier': 571,
                        'ultimate': 174,
                    },
                },
                'order_application': 'android',
                'updated': 1594894374.597,
                'status': 'cancelled',
                'status_updated': 1594894373.682,
                'created': 1594894370.1,
                'user_locale': 'ru',
                'event_index': 1,
                'nz': 'moscow',
                'order_id': '36fd8052f7643ed9882dc958cb9d8263',
                'plan_transporting_time_sec': 3415.3809259236073,
                'payment_type': 'cash',
                'event_key': 'handle_post_finish',
                'user_id': '8cd7b7bb947f42a49c4cab41feaac55d',
                'request_ip': '2a02:6b8:b010:50a3::3',
                'sp': 1.2,
                'user_phone_id': '58247911c0d947f1eef0b1bb',
                'user_uid_type': 'phonish',
                'user_uid': '4046634807',
                'source_country': 'Россия',
                'tips_type': 'percent',
                'user_tags': ['tag_for_rider_metrics', 'nastya_ok'],
                'tips_value': 0,
                'user_has_yaplus': True,
                'destinations_geopoint': [
                    [37.4051413645625, 55.9621349299721],
                ],
                'request_classes': ['econom', 'business', 'comfortplus'],
            },
        ),
        pytest.param(
            {
                'driver_position': [37.564813, 55.745659],
                'created': 1595182007.6,
                'dispatch': 'long',
                'status_updated': 1595184337.6,
                'dispatch_id': '5f148bbc7b285100388060c7',
                'user_agent': (
                    'Mozilla/5.0 (Linux; arm; Android 9; SM-J730FM)'
                    ' AppleWebKit/537.36 (KHTML, like Gecko)'
                    ' Chrome/81.0.4044.138'
                    ' YaBrowser/20.6.4.13.00 (broteam)'
                    ' SA/0 TA/7.1 Mobile Safari/537.36'
                ),
                'driver_clid': '643753730232',
                'alias': 'b16b1aad916453f5b47128c3fca78ca8',
                'lookup_eta': 1595182008.6,
                'updated': 1595184339.9550002,
                'udid': '5b05603de6c22ea2654654d3',
                'properties': ['has_order_comment', 'dispatch_long'],
                'event_key': 'handle_post_finish',
                'user_id': '671cd0cef4a247f8b908b065876975b3',
                'payment_type': 'cash',
                'plan_transporting_time_sec': 807.9679420153306,
                'source_geopoint': [37.59285072343204, 55.73545913039247],
                'billing_currency_rate': '1',
                'status': 'finished',
                'taximeter_version': '9.28 (1234)',
                'order_id': 'fd6b2527c13b5ff48a467ee96ab008f6',
                'calc_method': 'fixed',
                'cost': 294.0,
                'order_application': 'mbro_android_broteam',
                'allowed_tariffs': {
                    '__park__': {
                        'cargo': 1167.0,
                        'vip': 600.0,
                        'econom': 231.57894736842108,
                        'demostand': 1.0,
                        'suv': 400.0,
                        'comfortplus': 417.0,
                        'business': 375.6,
                    },
                },
                'time': 52,
                'driver_uuid': 'cbbb8ba87dde44e694b1046a6b36be4d',
                'paid_supply': False,
                'user_locale': 'ru',
                'db_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
                'tags': [
                    '2orders',
                    'query_rule_tag_default',
                    'HadOrdersLast30Days',
                    'OrderCompleteTagPushv2',
                    'high_activity',
                ],
                'nz': 'moscow',
                'user_phone_id': '5d31d0d291272f03f66493ca',
                'dist': 106,
                'sp': 1.2,
                'request_ip': '2a02:6b8:c0f:1813:0:42d5:837b:0',
                'event_index': 7,
                'user_uid': '4021492700',
                'taxi_status': 'complete',
                'source_country': 'Россия',
                'currency': 'RUB',
                'user_has_yaplus': False,
                'driver_license_personal_id': (
                    'e68f37c67fda47f8b8c6bb7054af3dd7'
                ),
                'request_classes': ['econom'],
                'destinations_geopoint': [
                    [37.56530594673405, 55.74553754198694],
                ],
                'performer_tariff_class': 'econom',
                'plan_transporting_distance_m': 8079.270370364189,
                'main_card_payment_id': 'cash',
            },
        ),
        pytest.param(
            {
                'main_card_payment_id': 'cash',
                'plan_transporting_distance_m': 8079.270370364189,
                'lookup_eta': 1595182008.6,
                'allowed_tariffs': {
                    '__park__': {
                        'cargo': 1167.0,
                        'vip': 600.0,
                        'econom': 231.57894736842108,
                        'demostand': 1.0,
                        'suv': 400.0,
                        'comfortplus': 417.0,
                        'business': 375.6,
                    },
                },
                'order_application': 'mbro_android_broteam',
                'updated': 1595182009.1980003,
                'status': 'pending',
                'status_updated': 1595182008.726,
                'created': 1595182007.6,
                'user_locale': 'ru',
                'event_index': 0,
                'event_reason': 'create',
                'nz': 'moscow',
                'order_id': 'fd6b2527c13b5ff48a467ee96ab008f6',
                'plan_transporting_time_sec': 807.9679420153306,
                'event_key': 'handle_default',
                'payment_type': 'cash',
                'user_id': '671cd0cef4a247f8b908b065876975b3',
                'user_has_yaplus': False,
                'destinations_geopoint': [
                    [37.56530594673405, 55.74553754198694],
                ],
                'request_classes': ['econom'],
                'user_uid': '4021492700',
                'source_country': 'Россия',
                'user_agent': (
                    'Mozilla/5.0 (Linux; arm; Android 9; SM-J730FM)'
                    ' AppleWebKit/537.36 (KHTML, like Gecko)'
                    ' Chrome/81.0.4044.138'
                    ' YaBrowser/20.6.4.13.00 (broteam)'
                    ' SA/0 TA/7.1 Mobile Safari/537.36'
                ),
                'source_geopoint': [37.59285072343204, 55.73545913039247],
                'request_ip': '2a02:6b8:c0f:1813:0:42d5:837b:0',
                'user_phone_id': '5d31d0d291272f03f66493ca',
                'sp': 1.2,
            },
        ),
    ],
)
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
async def test_order_events(taxi_driver_status, testpoint, message):
    the_cookie = 'test_cookie'

    @testpoint('logbroker_commit')
    def _commit(cookie):
        assert cookie == the_cookie

    data = {
        'consumer': 'order-events',
        'topic': '/taxi/processing/testing/order-events',
        'cookie': 'test_cookie',
    }
    if isinstance(message, dict):
        data['data'] = json.dumps(message)
    else:
        data['data'] = message

    response = await taxi_driver_status.post(
        'tests/logbroker/messages', data=json.dumps(data),
    )

    assert response.status_code == 200
    await _commit.wait_call()
