import datetime
import json

import bson
import pytest


async def test_lookup_contractor_base(stq_runner, mockserver, mocked_time):
    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/new_driver_found',
    )
    def order_core_event(request):
        body = bson.BSON.decode(request.get_data())
        assert (
            body['extra_update']['$push']['aliases']['id']
            == body['extra_update']['$push']['candidates']['alias_id']
        )
        body['extra_update']['$push']['aliases']['id'] = None
        body['extra_update']['$push']['candidates']['alias_id'] = None
        body['extra_update']['$push']['candidates']['created'] = None
        body['extra_update']['$push']['candidates']['driver_eta'] = None
        body['extra_update']['$push']['candidates']['dbcar_id'] = None
        assert body == {
            'fields': [],
            'extra_update': {
                '$inc': {'lookup.version': 1},
                '$push': {
                    'aliases': {
                        'due': datetime.datetime(2021, 7, 14, 8, 58, 36),
                        'due_optimistic': None,
                        'generation': 1,
                        'id': None,
                    },
                    'candidates': {
                        'adjusted_point': {
                            'avg_speed': 35,
                            'direction': 214,
                            'geopoint': [37.8954151234, 55.4183979995],
                            'time': 1533817820,
                        },
                        'alias_id': None,
                        'ar': 1,
                        'autoaccept': None,
                        'car_color': 'Red',
                        'car_color_code': 'red_code',
                        'car_model': 'BMW X2',
                        'car_number': 'А100ВR777',
                        'ci': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                        'cr': 1,
                        'created': None,
                        'driver_eta': None,
                        'db_id': '7f74df331eb04ad78bc2ff25ff88a8f2',
                        'dbcar_id': None,
                        'discount': {},
                        'dist': 125,
                        'dp_values': {'c': 0},
                        'driver_classes': ['econom', 'business'],
                        'driver_id': '12345_4bb5a0018d9641c681c1a854b21ec9ab',
                        'driver_license': (
                            'number-67666d1b64314ff4a8d82ee89cd9d111'
                        ),
                        'driver_license_personal_id': (
                            '67666d1b64314ff4a8d82ee89cd9d111'
                        ),
                        'driver_metrics': {
                            'activity': 100,
                            'activity_blocking': {
                                'activity_threshold': 30,
                                'duration_sec': 3600,
                            },
                            'activity_prediction': {'c': 0},
                            'dispatch': None,
                            'id': None,
                            'properties': None,
                            'type': 'fallback',
                        },
                        'driver_points': 100,
                        'first_name': 'Maxim',
                        'gprs_time': 20.0,
                        'hiring_date': None,
                        'hiring_type': 'type',
                        'is': True,
                        'line_dist': 26292,
                        'metrica_device_id': '112233',
                        'name': 'Urev Maxim Dmitrievich',
                        'order_allowed_classes': ['econom'],
                        'paid_supply': False,
                        'phone': 'number-+799999999',
                        'phone_personal_id': '+799999999',
                        'point': [37.642907, 55.735141],
                        'rd': True,
                        'tags': ['tag0', 'tag1', 'tag2', 'tag3'],
                        'tariff_class': 'econom',
                        'tariff_currency': 'RUB',
                        'tariff_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                        'taximeter_version': '9.07 (1234)',
                        'time': 18,
                        'udid': '5dcbf13eb8e3f87968f01111',
                        'z': [],
                        'push_on_driver_arriving_send_at_eta': None,
                        'push_on_driver_arriving_sent': None,
                    },
                },
                '$set': {'lookup.state.wave': 3},
            },
            'filter': {'lookup.version': 11, 'status': 'pending'},
        }

        return mockserver.make_response('', 200)

    now_time = datetime.datetime(
        2021, 7, 14, 8, 57, 36, tzinfo=datetime.timezone.utc,
    )
    mocked_time.set(now_time)
    await stq_runner.lookup_contractor.call(
        task_id='order_id', args=[], kwargs={'order_id': 'id'},
    )
    assert order_core_event.has_calls


async def test_lookup_contractor_not_found(
        stq_runner, mockserver, mocked_time,
):
    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        body = json.loads(request.get_data())
        body['excluded_car_numbers'] = None
        body['excluded_ids'] = None
        body['excluded_license_ids'] = None
        assert body == {
            'allowed_classes': ['econom'],
            'destination': [37.73, 55.98],
            'excluded_car_numbers': None,
            'excluded_ids': None,
            'excluded_license_ids': None,
            'lookup': {
                'generation': 1,
                'start_eta': 1618493536.187,
                'version': 11,
                'wave': 3,
            },
            'order': {
                'application': 'iphone',
                '_type': 'soon',
                'calc': {'distance': 67165.26606464389, 'time': 7324},
                'city': 'Москва',
                'created': 1618493534.778,
                'fixed_price': {'price': 1114},
                'pricing_data': {'user': {'data': {'country_code2': 'RU'}}},
                'nearest_zone': 'moscow',
                'personal_phone_id': '84132b2eff22428db748939484e1236d',
                'request': {
                    'class': ['econom'],
                    'comment': '',
                    'destinations': [
                        {
                            'country': 'Россия',
                            'description': 'Московская область, ' 'Россия',
                            'extra_data': {
                                'contact_phone_id': '5cd413ead253f1c435a87c28',
                            },
                            'fullname': 'Россия, Московская ' 'область',
                            'geopoint': [37.73, 55.98],
                            'locality': 'деревня Пирогово',
                            'metrica_method': 'suggest',
                            'object_type': 'другое',
                            'premisenumber': '_',
                            'short_text': 'Садовая улица',
                            'thoroughfare': 'Садовая улица',
                            'type': 'address',
                        },
                    ],
                    'due': 1618494360.0,
                    'lookup_ttl': 600,
                    'offer': '44eea40718d42a5ae59dfc1830ed0db2',
                    'requirements': {'door_to_door': True},
                    'source': {
                        'geopoint': [37.6, 55.5],
                        'object_type': 'другое',
                    },
                    'source_geoareas': [
                        'reposition_discount_B',
                        'vidnoe_activation',
                        'vidnoe',
                        'moscow',
                        'vidnoe_transfer',
                    ],
                    'surge_price': 1.3,
                },
                'user_agent': (
                    'ru.yandex.ytaxi/600.32.0.125308 (iPhone; iPhone12,1; '
                    'iOS 14.4.2; Darwin)'
                ),
                'user_id': 'bbc4f82b95ac4001820142043fb1a420',
                'user_phone_id': '5bfd522c8566ffb1421d643c',
                'user_tags': [
                    'meta_core_user',
                    'chatterbox_tag_rider_double_pay',
                    'comfortplus_msc_032020_2w15p5t',
                    'crm_hub_push_finished_in_lavka_zone_msc',
                    'logistics_plus_exp_frequent_user',
                    'has_logistic_trip',
                    'chatterbox_tag_prem_cash_cashless_tag',
                    'chatterbox_tag_super_ultima',
                ],
                'user_uid': '279056117',
                'using_new_pricing': True,
            },
            'order_id': '78bd637369c82cb687f6a8651b5cda8d',
            'payment_method': 'card',
            'payment_tech': {'type': 'card'},
            'point': [37.6, 55.5],
            'requirements': {'door_to_door': True},
            'timeout': 2000,
            'zone_id': 'moscow',
        }
        return mockserver.make_response(
            '{"candidates":[]}', 200, content_type='application/json',
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def order_core_set(request):
        body = bson.BSON.decode(request.get_data())
        assert body == {
            'fields': [],
            'filter': {'lookup.version': 11, 'status': 'pending'},
            'revision': {'version': 1},
            'update': {
                '$inc': {'lookup.version': 1},
                '$set': {'lookup.state.wave': 3},
            },
        }
        return mockserver.make_response('', 200)

    now_time = datetime.datetime(
        2021, 7, 14, 8, 57, 36, tzinfo=datetime.timezone.utc,
    )
    mocked_time.set(now_time)
    await stq_runner.lookup_contractor.call(
        task_id='order_id', args=[], kwargs={'order_id': 'id'},
    )
    assert order_core_set.has_calls


@pytest.mark.config(LOOKUP_EXPIRE_ORDER={'limit_of_candidates_on_order': 5})
async def test_lookup_contractor_candidate_limit(
        stq_runner, mockserver, mocked_time,
):
    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        assert False, 'Shoudnot be called'

    @mockserver.json_handler('/order-core/internal/processing/v1/event/expire')
    def order_core_event(request):
        body = bson.BSON.decode(request.get_data())
        assert body == {
            'fields': [],
            'filter': {'status': 'pending'},
            'event_extra_payload': {
                's': 'finished',
                't': 'expired',
                'r': 'reach limit of candidates on order',
            },
            'extra_update': {
                '$set': {
                    'order.status': 'finished',
                    'order.status_updated': datetime.datetime(
                        2021, 7, 14, 8, 57, 36,
                    ),
                    'order.taxi_status': 'expired',
                    'order.user_fraud': False,
                    'status': 'finished',
                },
            },
        }
        return {}

    now_time = datetime.datetime(
        2021, 7, 14, 8, 57, 36, tzinfo=datetime.timezone.utc,
    )
    mocked_time.set(now_time)
    await stq_runner.lookup_contractor.call(
        task_id='order_id', args=[], kwargs={'order_id': 'id'},
    )
    assert order_core_event.has_calls
