# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import copy
import json
import math
import urlparse
import uuid

import bson
import pytest

from taxi import config
from taxi.core import async
from taxi.core import db
from taxi.external import experiments3
from taxi.external import pymlaas
from taxi.external import support_info
from taxi.external import zendesk
from taxi.internal import dbh
from taxi.internal import driver_manager
from taxi.internal import experiment_manager
from taxi.internal import feedback_manager
from taxi.internal.order_kit import feedback_report

TICKET_FORM_ID = 152345
UUID = '00000000000040008000000000000000'


@pytest.fixture
def mock_uuid_uuid4(monkeypatch, mock):
    @mock
    def _dummy_uuid4():
        return uuid.UUID(int=0, version=4)

    monkeypatch.setattr(uuid, 'uuid4', _dummy_uuid4)


@pytest.fixture(autouse=True)
def patch_support_chat_ml_request_id(patch):
    @patch('taxi.internal.user_support_chat.get_ml_request_id')
    @async.inline_callbacks
    def get_ml_request_id(phone_id, platform, log_extra):
        yield async.return_value(UUID)


@pytest.fixture(autouse=True)
def patch_userapi_phone_id(patch):
    @patch('taxi.internal.userapi.get_user_phone')
    @async.inline_callbacks
    def impl(
            phone_id,
            primary_replica=False,
            fields=None,
            log_extra=None,
    ):
        doc = yield dbh.user_phones.Doc.find_one_by_id(
            phone_id,
            secondary=not primary_replica,
            fields=fields,
        )
        async.return_value(doc)


@pytest.fixture(autouse=True)
def patch_userapi_get_user_emails(patch):
    @patch('taxi.external.userapi.get_user_emails')
    @async.inline_callbacks
    def mock_userapi(
            brand,
            email_ids=None,
            phone_ids=None,
            yandex_uids=None,
            fields=None,
            primary_replica=False,
            log_extra=None,
    ):
        phone_id = phone_ids[0]
        email_id = phone_id[-1:]
        yield async.return_value(
            [
                {
                    'id': phone_id,
                    'phone_id': phone_id,
                    'confirmed': True,
                    'confirmation_code': 'code{}'.format(email_id),
                    'personal_email_id':
                        'personal_email_id{}'.format(email_id),
                },
            ],
        )


@pytest.fixture(autouse=True)
def patch_personal_retrieve(patch):
    @patch('taxi.external.personal.retrieve')
    @async.inline_callbacks
    def mock_personal(data_type, request_id, log_extra=None, **kwargs):
        email_id = request_id[-1:]
        yield async.return_value(
            {
                'id': request_id,
                'email': 'email{}'.format(email_id),
            },
        )


@pytest.fixture
def mock_get_urgency(monkeypatch, mock):
    @mock
    @async.inline_callbacks
    def _dummy_get_urgency(request_data, log_extra=None):
        yield
        text = request_data['comment'].strip()
        if text == 'морозно хорошо':
            async.return_value(0.7)
        if text == 'ужасно морозно':
            async.return_value(0.9)
        if text == 'ужасно':
            async.return_value(0.8)
        async.return_value(0.2)

    monkeypatch.setattr(
        pymlaas,
        'urgent_comments_detection',
        _dummy_get_urgency
    )
    return _dummy_get_urgency


@pytest.fixture
def mock_get_readonly(patch):
    @patch('taxi.external.pymlaas.client_tickets_read_only')
    @async.inline_callbacks
    def _dummy_need_response(data, log_extra=None):
        yield
        assert data['comment'] is not None
        comment = data['comment'].strip()
        if comment == 'спасибо':
            async.return_value(True)
        async.return_value(False)

    return _dummy_need_response


@pytest.fixture
def mock_experiments3(patch):
    @patch('taxi.external.experiments3.get_values')
    @async.inline_callbacks
    def _dummy_get_values(consumer, args, **kwargs):
        yield
        assert consumer == 'stq/zendesk_ticket'
        async.return_value([
            experiments3.ExperimentsValue(
                feedback_report.SHOW_CALL_ME_BACK_OPTION,
                {'enabled': False},
            ),
        ])
    return _dummy_get_values


@pytest.fixture
def mock_tags(areq_request):
    def request(method, url, **kwargs):
        assert method == 'POST'
        assert url.endswith('/v1/match')

        entity_id = kwargs['json']['entities'][0]['id']
        if entity_id == 'bad_user_phone_id':
            tags = None
        elif entity_id in ['user_phone_id', 'user_phone_id_urgent']:
            tags = ['business_client']
        else:
            tags = []
        assert entity_id
        return areq_request.response(
            200,
            body=json.dumps(
                {
                    'entities': [
                        {
                            'tags': tags,
                        }
                    ],
                }
            )
        )
    areq_request(request)
    return request


@pytest.fixture
def mock_driver_tags(areq_request):
    def request(method, url, **kwargs):
        assert method == 'POST'
        assert url.endswith('/v1/drivers/match/profile')

        uuid = kwargs['json']['uuid']
        if uuid == 'driver':
            tags = ['vip', 'blogger', 'other']
        elif uuid == 'baddriver':
            tags = None
        else:
            tags = []
        return areq_request.response(
            200,
            body=json.dumps({'tags': tags})
        )
    areq_request(request)
    return request


@pytest.fixture
def mock_detect_language(patch):
    def _get_detect_language(language):
        @patch('taxi.external.translate.detect_language')
        @async.inline_callbacks
        def detect_language(text, log_extra=None):
            yield
            assert text
            async.return_value(language)
        return detect_language

    return _get_detect_language


@pytest.fixture(autouse=True)
def mock_meta_from_support_info(patch, request):
    if 'no_mock_support_info_meta' in request.keywords:
        return

    @patch('taxi.internal.order_kit.feedback_report.get_chatterbox_fields_from_py3')
    @async.inline_callbacks
    def _dummy_get_fields(*args, **kwargs):
        yield async.return_value({})


@pytest.fixture
def zclient(monkeypatch):

    class Client(object):
        def __init__(self):
            self.id = None
            self.tickets = {}

    zclient = Client()

    def get_zendesk_client(id):
        zclient.id = id
        return zclient

    monkeypatch.setattr(
        zendesk, 'get_zendesk_client_by_id', get_zendesk_client
    )

    return zclient


class MockClient:
    def __init__(self, id):
        self.id = id

    def search(self, *args, **kwargs):
        return []


translations = [
    ('tariff', 'detailed.minutes', 'ru', u'%(value).0f мин'),
    ('tariff', 'detailed.minute', 'ru', u'%(value).0f мин'),
    ('tariff', 'detailed.hour', 'ru', u'%(value).0f ч'),
    ('tariff', 'detailed.hours', 'ru', u'%(value).0f ч'),
    ('tariff', 'detailed.kilometers_meters', 'ru', u'%(value).3f км'),
    ('tariff', 'detailed.kilometers', 'ru', u'%(value).3f км'),
    ('tariff', 'detailed.kilometer', 'ru', u'%(value).3f км'),
    ('client_messages', 'feedback_choice.low_rating_reason.nochange',
     'ru', u'Не было сдачи'),
    ('client_messages', 'feedback_choice.low_rating_reason.car_condition',
     'ru', u'Состояние автомобиля'),
    ('client_messages', 'feedback_choice.low_rating_reason.driverlate',
     'ru', u'Водитель опоздал'),
    ('client_messages', 'feedback_choice.low_rating_reason.rudedriver',
     'ru', u'Грубый водитель'),
    ('client_messages', 'feedback_choice.low_rating_reason.smellycar',
     'ru', u'Запах в машине'),
    ('client_messages', 'feedback_choice.low_rating_reason.badroute',
     'ru', u'Ездил кругами'),
    ('client_messages', 'feedback_choice.low_rating_reason.notrip',
     'ru', u'Поездки не было'),
    ('client_messages', 'feedback_choice.cancelled_reason.usererror',
     'ru', u'Заказал по ошибке'),
    ('client_messages', 'feedback_choice.cancelled_reason.droveaway',
     'ru', u'Водитель ехал в другую сторону'),
    ('client_messages', 'feedback_choice.cancelled_reason.driverrequest',
     'ru', u'Водитель попросил отменить'),
    ('client_messages', 'feedback_choice.badge_label.bad_driving',
     'ru', u'Небезопасное вождение'),
    ('client_messages', 'feedback_choice.badge_label.pleasant_music',
     'ru', u'Приятная музыка'),
]


feedback_badges_mapping = {
    'feedback_badges': [
        {
            "label": "feedback_choice.badge_label.bad_driving",
            "name": "bad_driving"
        },
        {
            "label": "feedback_choice.badge_label.pleasant_music",
            "name": "music"
        },
    ]
}


@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(_fill=False)
def test_feedback_ctx_defaults():
    ctx = feedback_report.FeedbackContext()
    assert not ctx.driver_id
    assert not ctx.driver_license
    assert not ctx.driver_payment_claims_count
    assert not ctx.driver_phone
    assert not ctx.driver_rating
    assert not ctx.driver_tickets_count
    assert not ctx.fixed_price
    assert not ctx.fixed_price_broken
    assert not ctx.has_driver_info
    assert not ctx.has_order_info
    assert not ctx.has_user_info
    assert not ctx.house_was_mentioned
    assert not ctx.payment_type
    assert not ctx.ride_cost
    assert not ctx.statistics
    assert not ctx.tariff_category
    assert not ctx.user_payment_claims_count


@pytest.mark.parametrize('zendesk_id,user_type,report_kwargs,expected_result',
    [(
        'yataxi',
        'general',
        {
            'park_email': 'park@park.ru',
            'call_requested': True,
            'order_pre_distance': '15 км',
            'order_pre_time': '25 мин',
            'order_pre_cost': 500,
            'waiting_cost': 100,
            'waiting_time': 25,
            'order_currency': 'руб',
            'real_order_id': 'order_id',
            'order_timestamp': '12:20',
            'calc_way': '',
            'precomment': '',
            'coupon': False,
            'coupon_used': False,
            'point_b_changed': False,
            'point_a': '',
            'points_b': 'Test address',
            'real_point_b': 'Test address',
            'transactions': '',
            'app_version': '3.87.951',
            'user_phone': '+79250000000',
            'driver_license': '111',
            'driver_phone': '',
            'fixed_price': '',
            'order_cost': 333,
            'order_date': '10.10',
            'tariff': 'econom',
            'user_platform': 'iphone',
            'comment': '',
            'driver_track': [],
            'city': 'Нижний новгород',
            'payment_type': 'cash',
            'user_locale': 'en',
            'paid_cancel_tag': False
        },
        {
            'user_phone': '+79250000000',
            'order_date': '10.10',
            'order_time': '12:20',
            'tariff': 'econom',
            'user_type': 'пользователь',
            'payment_type': 'способ_оплаты_нал',
            'call_requested': True,
            'park_email': 'park@park.ru',
            'user_platform': 'iphone',
            'client_thematic': 'клиент_отзыв_из_приложения',
            'order_id': 'order_id',
            'city': 'нижний_новгород',
            'language': 'язык_английский',
            'driver_license': '111',
            'order_cost': 333,
            'driver_phone': '',
            'app_version': '3.87.951',
            'fixed_price': '',
            'order_pre_distance': '15 км',
            'order_pre_time': '25 мин',
            'order_pre_cost': 500,
            'waiting_cost': 100,
            'waiting_time': 25,
            'order_currency': 'руб',
            'calc_way': '',
            'precomment': '',
            'comment': '',
            'coupon': False,
            'coupon_used': False,
            'point_b_changed': False,
            'point_a': '',
            'points_b': 'Test address',
            'real_point_b': 'Test address',
            'transactions': '',
            'driver_track': [],
            'user_locale': 'en',
            'paid_cancel_tag': False
        },
    ),
    (
        'yataxi',
        'vip',
        {
            'order_pre_distance': '17 км',
            'order_pre_time': '14 мин',
            'order_pre_cost': 500,
            'waiting_cost': 44,
            'waiting_time': 251,
            'order_currency': 'руб',
            'real_order_id': 'order_id_2',
            'order_timestamp': '13:45',
            'calc_way': 'taximeter',
            'precomment': 'test',
            'coupon': True,
            'coupon_used': True,
            'point_b_changed': True,
            'point_a': 'Test',
            'points_b': 'Test address; Test address 2',
            'real_point_b': 'Test address',
            'transactions': 'tran_1500_RUB_HOLD_INIT',
            'app_version': '3.38.4261',
            'user_phone': '+79250000001',
            'driver_license': '222',
            'driver_phone': '+791111111',
            'park_phone': '+7999',
            'fixed_price': 149,
            'order_cost': 250,
            'order_date': '19.07',
            'tariff': 'comfortplus',
            'user_platform': 'android',
            'comment': 'comm',
            'park_email': 'park@park1.ru',
            'call_requested': False,
            'driver_track': [
                'test'
            ],
            'city': 'Ростёв-на-Дону',
            'payment_type': 'card',
            'user_locale': 'ru',
            'paid_cancel_tag': True
        },
        {
            'user_phone': '+79250000001',
            'order_date': '19.07',
            'order_time': '13:45',
            'tariff': 'comfortplus',
            'user_type': 'vip-пользователь',
            'payment_type': 'способ_оплаты_карта',
            'call_requested': False,
            'park_email': 'park@park1.ru',
            'user_platform': 'android',
            'client_thematic': 'клиент_платная_отмена',
            'order_id': 'order_id_2',
            'city': 'ростев_на_дону',
            'language': 'язык_русский',
            'driver_license': '222',
            'order_cost': 250,
            'driver_phone': '+791111111',
            'park_phone': '+7999',
            'app_version': '3.38.4261',
            'fixed_price': 149,
            'calc_way': 'taximeter',
            'precomment': 'test',
            'coupon': True,
            'coupon_used': True,
            'point_b_changed': True,
            'point_a': 'Test',
            'points_b': 'Test address; Test address 2',
            'real_point_b': 'Test address',
            'transactions': 'tran_1500_RUB_HOLD_INIT',
            'comment': 'comm',
            'order_currency': 'руб',
            'order_pre_distance': '17 км',
            'order_pre_time': '14 мин',
            'order_pre_cost': 500,
            'waiting_cost': 44,
            'waiting_time': 251,
            'driver_track': [
                'test'
            ],
            'user_locale': 'ru',
            'paid_cancel_tag': True
        }
    ),
    (
            'yutaxi',
            'vip',
            {
                'order_pre_distance': '17 км',
                'order_pre_time': '14 мин',
                'order_pre_cost': 500,
                'waiting_cost': 44,
                'waiting_time': 251,
                'order_currency': 'руб',
                'real_order_id': 'order_id_2',
                'order_timestamp': '13:45',
                'calc_way': 'taximeter',
                'precomment': 'test',
                'coupon': True,
                'coupon_used': True,
                'point_b_changed': True,
                'point_a': 'Test',
                'points_b': 'Test address; Test address 2',
                'real_point_b': 'Test address',
                'transactions': 'tran_1500_RUB_HOLD_INIT',
                'app_version': '3.38.4261',
                'user_phone': '+79250000001',
                'driver_license': '222',
                'driver_phone': '+791111111',
                'fixed_price': 149,
                'order_cost': 250,
                'order_date': '19.07',
                'tariff': 'comfortplus',
                'user_platform': 'android',
                'comment': 'comm',
                'park_email': 'park@park1.ru',
                'call_requested': False,
                'driver_track': {
                    'track': [
                        {
                            'bearing': -1,
                            'timestamp': 1528547772,
                            'end': True,
                            'speed': 21.25,
                            'point': [51.9444694519043, 47.160884857177734]
                        }
                    ]
                },
                'city': 'Ростёв-на-Дону',
                'payment_type': 'card',
                'user_locale': 'ru',
                'paid_cancel_tag': True
            },
            {
                'user_phone': '+79250000001',
                'order_date': '19.07',
                'order_time': '13:45',
                'tariff': 'comfortplus',
                'user_type': 'vip-пользователь',
                'payment_type': 'способ_оплаты_карта',
                'call_requested': False,
                'park_email': 'park@park1.ru',
                'user_platform': 'android',
                'client_thematic': 'клиент_платная_отмена',
                'order_id': 'order_id_2',
                'city': 'ростев_на_дону',
                'language': 'язык_русский',
                'driver_license': '222',
                'order_cost': 250,
                'driver_phone': '+791111111',
                'app_version': '3.38.4261',
                'fixed_price': 149,
                'calc_way': 'taximeter',
                'precomment': 'test',
                'coupon': True,
                'coupon_used': True,
                'point_b_changed': True,
                'point_a': 'Test',
                'points_b': 'Test address; Test address 2',
                'real_point_b': 'Test address',
                'transactions': 'tran_1500_RUB_HOLD_INIT',
                'comment': 'comm',
                'order_currency': 'руб',
                'order_pre_distance': '17 км',
                'order_pre_time': '14 мин',
                'order_pre_cost': 500,
                'waiting_cost': 44,
                'waiting_time': 251,
                'driver_track': {
                    'track': [
                        {
                            'bearing': -1,
                            'timestamp': 1528547772,
                            'end': True,
                            'speed': 21.25,
                            'point': [51.9444694519043, 47.160884857177734]
                        }
                    ]
                },
                'user_locale': 'ru',
                'paid_cancel_tag': True
            }
    )
])
@pytest.mark.filldb(_fill=True)
@pytest.inline_callbacks
@pytest.mark.config(ZENDESK_PAID_CANCEL_TICKETS_ENABLED=True)
@pytest.mark.config(FEEDBACK_BADGES_MAPPING=feedback_badges_mapping)
def test_get_custom_fields(zendesk_id, user_type, report_kwargs,
                           expected_result):
    custom_fields = yield feedback_report.get_custom_fields(
        zendesk_id, user_type, copy.deepcopy(report_kwargs), True
    )

    assert custom_fields == expected_result


@pytest.mark.parametrize('order_proc_id,order,user_phone_doc,user_doc,city,'
                         'statistics,driver,park,expected_result', [
    (
        'order_id1',
        {
            'billing_tech': {
                'transactions': [
                    {
                        'sum': {
                            'ride': 100000
                        },
                        'status': 'HOLD_INIT'
                    }
                ]
            }
        },
        {
            'phone': '+79250000001'
        },
        {
            'application': 'iphone',
            'application_version': '3.85.124'
        },
        {
            'tz': 'Europe/Moscow'
        },
        {},
        {
            'uuid': 'driver1',
            'db_id': 'pid1'
        },
        {},
        {
            'car_number': '-',
            'city': 'Moscow',
            'comment': '-',
            'driver_license': '-',
            'driver_phone': '-',
            'driver_name': '',
            'clid': '',
            'park_phone': '-',
            'park_name': '',
            'taximeter_version': '',
            'order_id': 'order',
            'rating': '-',
            'whats_wrong': '-',
            'order_cost': 0,
            'order_time': 0,
            'order_distance': '0.000 км',
            'order_currency': 'RUB',
            'order_pre_cost': 0,
            'order_pre_distance': '0.000 км',
            'order_pre_time': 0,
            'surge': '',
            'cancel_time': '-',
            'cancel_distance': '-',
            'precomment': 'precomment',
            'calc_way': '',
            'waiting_time': '-',
            'waiting_cost': 0,
            'waiting': 'Нет',
            'waiting_bool': False,
            'fixed_price': '',
            'app_version': '3.85.124',
            'call_requested': False,
            'coupon': False,
            'coupon_used': False,
            'order_date': '01.01',
            'order_timestamp': '13:15',
            'order_due_time': 1514790917,
            'real_order_id': 'order_id1',
            'point_a': 'Москва, Красная площадь',
            'points_b': 'Москва, Льва Толстого 14',
            'real_point_b': 'Москва, Льва Толстого 14',
            'user_phone': '+79250000001',
            'user_platform': 'iphone',
            'point_b_changed': False,
            'tariff': '',
            'transactions': 'tran_10.0_RUB_HOLD_INIT',
            'complete_rides': 0,
            'user_email': 'email1',
            'user_locale': '',
            'payment_type': None,
            'park_db_id': 'pid1',
            'driver_id': 'park_driver1',
            'driver_uuid': 'driver1',
            'user_id': 'user_id1',
            'user_phone_id': 'user_phone_id1',
            'urgency_probability': '',
            'order_pre_time_raw': 0,
            'cancel_time_raw': None,
            'order_pre_distance_raw': 0,
            'order_distance_raw': 0,
            'application_platform': None,
            'baby_seat_services': False,
            'cancel_distance_raw': 0,
            'cost_paid_supply': 0,
            'coupon_use_value': 0,
            'dif_ordercost_surge_surgecharge': 0.0,
            'difference_fact_estimated_cost': 0,
            'driver_late_time': 0,
            'driver_waiting_time': 0,
            'waiting_time_raw_minutes': 0,
            'final_ride_duration': 0,
            'final_transaction_status': 'hold_fail',
            'fixed_price_order_flg': False,
            'order_date_ymd': '2018-01-01',
            'order_pre_time_raw_minutes': 0,
            'paid_supply': False,
            'success_order_flg': False,
            'surge_order_flg': False,
            'transportation_animals': False,
            'park_email': 'devnull@yandex.ru',
            'zone': '',
        }
    ),
    (
        'order_id2',
        {
            'billing_tech': {
                'transactions': [
                    {
                        'sum': {
                            'ride': 100000
                        },
                        'status': 'hold_fail'
                    },
                    {
                        'sum': {
                            'ride': 1230000
                        },
                        'status': 'clear_success'
                    }
                ]
            }
        },
        {
            'phone': '+79250000001'
        },
        {
            'application': 'android',
            'application_version': '3.45.124'
        },
        {
            'tz': 'Europe/Moscow'
        },
        {
            'statistics.travel_time': 5000,
            'statistics.travel_distance': 5654,
            'statistics.cancel_time': 300,
            'statistics.cancel_distance': 6700.0,
        },
        {
            'phone': '+4997771122',
            'uuid': 'driver2',
            'db_id': 'pid2'
        },
        {
            '_id': 'park_id',
            'phone': '+7999'
        },
        {
            'car_number': 'АА111А77',
            'city': 'Moscow',
            'comment': 'ругался матом',
            'driver_license': 'права',
            'driver_phone': '+4997771122',
            'driver_name': '',
            'clid': 'park_id',
            'park_phone': '+7999',
            'park_name': '',
            'taximeter_version': '',
            'order_id': 'order',
            'rating': 2,
            'whats_wrong': 'Небезопасное вождение, Грубый водитель',
            'order_cost': 1134,
            'order_time': '1 ч 23 мин',
            'order_distance': '5.000 км',
            'order_currency': 'RUB',
            'order_pre_cost': 1031.196,
            'order_pre_distance': '5.000 км',
            'order_pre_time': '16 мин',
            'surge': 1.2,
            'cancel_time': '5 мин',
            'cancel_distance': '6.700 км',
            'precomment': 'text',
            'calc_way': 'fixed',
            'waiting_time': '10 мин',
            'waiting_cost': 25,
            'waiting': 'Да',
            'waiting_bool': True,
            'fixed_price': 1000,
            'app_version': '3.45.124',
            'call_requested': True,
            'coupon': True,
            'coupon_used': True,
            'order_date': '-',
            'order_timestamp': '-',
            'order_due_time': None,
            'real_order_id': 'order_id2',
            'point_a': 'Яндекс',
            'points_b': 'Аврора; Роза',
            'real_point_b': 'Аврора',
            'user_phone': '+79250000001',
            'user_platform': 'android',
            'point_b_changed': False,
            'tariff': 'econom',
            'transactions': 'tran_10.0_RUB_hold_fail;'
                            'tran_123.0_RUB_clear_success',
            'complete_rides': 0,
            'user_email': 'email2',
            'user_locale': '',
            'payment_type': None,
            'park_db_id': 'pid2',
            'driver_id': 'park_driver2',
            'driver_uuid': 'driver2',
            'user_id': 'user_id2',
            'user_phone_id': 'user_phone_id2',
            'urgency_probability': '',
            'order_pre_time_raw': 1000,
            'cancel_time_raw': 300,
            'order_pre_distance_raw': 5000,
            'order_distance_raw': 5654,
            'application_platform': None,
            'baby_seat_services': False,
            'cancel_distance_raw': 6700.0,
            'cost_paid_supply': 0,
            'coupon_use_value': 100,
            'dif_ordercost_surge_surgecharge': 945.0,
            'difference_fact_estimated_cost': 134,
            'driver_late_time': 0,
            'driver_waiting_time': 0,
            'waiting_time_raw_minutes': 10,
            'final_ride_duration': 5000 / 60.,
            'final_transaction_status': 'clear_success',
            'fixed_price_order_flg': True,
            'order_date_ymd': None,
            'order_pre_time_raw_minutes': 1000 / 60.,
            'paid_supply': False,
            'success_order_flg': False,
            'surge_order_flg': True,
            'transportation_animals': False,
            'park_email': 'devnull@yandex.ru',
            'zone': '',
        },
    ),
    (
        'order_with_cost_included_coupon',
        {
            'billing_tech': {
                'transactions': [
                    {
                        'sum': {
                            'ride': 100000
                        },
                        'status': 'hold_fail'
                    },
                    {
                        'sum': {
                            'ride': 1230000
                        },
                        'status': 'clear_success'
                    }
                ]
            }
        },
        {
            'phone': '+79250000001'
        },
        {
            'application': 'android',
            'application_version': '3.45.124'
        },
        {
            'tz': 'Europe/Moscow'
        },
        {
            'statistics.travel_time': 5000,
            'statistics.travel_distance': 5654,
            'statistics.cancel_time': 300,
            'statistics.cancel_distance': 6700.0,
        },
        {
            'phone': '+4997771122',
            'uuid': 'driver2',
            'db_id': 'pid2'
        },
        {
            '_id': 'park_id',
            'phone': '+7999'
        },
        {
            'car_number': 'АА111А77',
            'city': 'Moscow',
            'comment': 'ругался матом',
            'driver_license': 'права',
            'driver_phone': '+4997771122',
            'driver_name': '',
            'clid': 'park_id',
            'park_phone': '+7999',
            'park_name': '',
            'taximeter_version': '',
            'order_id': 'order',
            'rating': 2,
            'whats_wrong': 'Небезопасное вождение, Грубый водитель',
            'order_cost': 1134,
            'order_time': '1 ч 23 мин',
            'order_distance': '5.000 км',
            'order_currency': 'RUB',
            'order_pre_cost': 1031.196,
            'order_pre_distance': '5.000 км',
            'order_pre_time': '16 мин',
            'surge': 1.1,
            'cancel_time': '5 мин',
            'cancel_distance': '6.700 км',
            'precomment': 'text',
            'calc_way': 'fixed',
            'waiting_time': '10 мин',
            'waiting_cost': 25,
            'waiting': 'Да',
            'waiting_bool': True,
            'fixed_price': 1000,
            'app_version': '3.45.124',
            'call_requested': True,
            'coupon': True,
            'coupon_used': True,
            'order_date': '-',
            'order_timestamp': '-',
            'order_due_time': None,
            'real_order_id': 'order_with_cost_included_coupon',
            'point_a': 'Яндекс',
            'points_b': 'Аврора; Роза',
            'real_point_b': 'Аврора',
            'user_phone': '+79250000001',
            'user_platform': 'android',
            'point_b_changed': False,
            'tariff': 'econom',
            'transactions': 'tran_10.0_RUB_hold_fail;'
                            'tran_123.0_RUB_clear_success',
            'complete_rides': 0,
            'user_email': 'email2',
            'user_locale': '',
            'payment_type': None,
            'park_db_id': 'pid2',
            'driver_id': 'park_driver2',
            'driver_uuid': 'driver2',
            'user_id': 'user_id2',
            'user_phone_id': 'user_phone_id2',
            'urgency_probability': '',
            'order_pre_time_raw': 1000,
            'cancel_time_raw': 300,
            'order_pre_distance_raw': 5000,
            'order_distance_raw': 5654,
            'application_platform': None,
            'baby_seat_services': False,
            'cancel_distance_raw': 6700.0,
            'cost_paid_supply': 0,
            'coupon_use_value': 100,
            'dif_ordercost_surge_surgecharge': 124.0,
            'difference_fact_estimated_cost': 134,
            'driver_late_time': 0,
            'driver_waiting_time': 0,
            'waiting_time_raw_minutes': 10,
            'final_ride_duration': 5000 / 60.,
            'final_transaction_status': 'clear_success',
            'fixed_price_order_flg': True,
            'order_date_ymd': None,
            'order_pre_time_raw_minutes': 1000 / 60.,
            'paid_supply': False,
            'success_order_flg': False,
            'surge_order_flg': True,
            'transportation_animals': False,
            'park_email': 'devnull@yandex.ru',
            'zone': '',
        },
    ),
    (
        'order_without_final_cost',
        {
            'billing_tech': {
                'transactions': [
                    {
                        'sum': {
                            'ride': 100000
                        },
                        'status': 'hold_fail'
                    },
                    {
                        'sum': {
                            'ride': 1230000
                        },
                        'status': 'clear_success'
                    }
                ]
            }
        },
        {
            'phone': '+79250000001'
        },
        {
            'application': 'android',
            'application_version': '3.45.124'
        },
        {
            'tz': 'Europe/Moscow'
        },
        {
            'statistics.travel_time': 5000,
            'statistics.travel_distance': 5654,
            'statistics.cancel_time': 300,
            'statistics.cancel_distance': 6700.0,
        },
        {
            'phone': '+4997771122',
            'uuid': 'driver2',
            'db_id': 'pid2'
        },
        {
            '_id': 'park_id',
            'phone': '+7999'
        },
        {
            'car_number': 'АА111А77',
            'city': 'Moscow',
            'comment': 'ругался матом',
            'driver_license': 'права',
            'driver_phone': '+4997771122',
            'driver_name': '',
            'clid': 'park_id',
            'park_phone': '+7999',
            'park_name': '',
            'taximeter_version': '',
            'order_id': 'order',
            'rating': 2,
            'whats_wrong': 'Небезопасное вождение, Грубый водитель',
            'order_cost': 1134,
            'order_time': '1 ч 23 мин',
            'order_distance': '5.000 км',
            'order_currency': 'RUB',
            'order_pre_cost': 1031.196,
            'order_pre_distance': '5.000 км',
            'order_pre_time': '16 мин',
            'surge': 1.1,
            'cancel_time': '5 мин',
            'cancel_distance': '6.700 км',
            'precomment': 'text',
            'calc_way': 'fixed',
            'waiting_time': '10 мин',
            'waiting_cost': 25,
            'waiting': 'Да',
            'waiting_bool': True,
            'fixed_price': 1000,
            'app_version': '3.45.124',
            'call_requested': True,
            'coupon': False,
            'coupon_use_value': 0,
            'coupon_used': False,
            'order_date': '-',
            'order_timestamp': '-',
            'order_due_time': None,
            'real_order_id': 'order_without_final_cost',
            'point_a': 'Яндекс',
            'points_b': 'Аврора; Роза',
            'real_point_b': 'Аврора',
            'user_phone': '+79250000001',
            'user_platform': 'android',
            'point_b_changed': False,
            'tariff': 'econom',
            'transactions': 'tran_10.0_RUB_hold_fail;'
                            'tran_123.0_RUB_clear_success',
            'complete_rides': 0,
            'user_email': 'email2',
            'user_locale': '',
            'payment_type': None,
            'park_db_id': 'pid2',
            'driver_id': 'park_driver2',
            'driver_uuid': 'driver2',
            'user_id': 'user_id2',
            'user_phone_id': 'user_phone_id2',
            'urgency_probability': '',
            'order_pre_time_raw': 1000,
            'cancel_time_raw': 300,
            'order_pre_distance_raw': 5000,
            'order_distance_raw': 5654,
            'application_platform': None,
            'baby_seat_services': False,
            'cancel_distance_raw': 6700.0,
            'cost_paid_supply': 0,
            'dif_ordercost_surge_surgecharge': 124.0,
            'difference_fact_estimated_cost': 134,
            'driver_late_time': 0,
            'driver_waiting_time': 0,
            'waiting_time_raw_minutes': 10,
            'final_ride_duration': 5000 / 60.,
            'final_transaction_status': 'clear_success',
            'fixed_price_order_flg': True,
            'order_date_ymd': None,
            'order_pre_time_raw_minutes': 1000 / 60.,
            'paid_supply': False,
            'success_order_flg': False,
            'surge_order_flg': True,
            'transportation_animals': False,
            'park_email': 'devnull@yandex.ru',
            'zone': '',
        },
    ),
])
@pytest.inline_callbacks
@pytest.mark.translations(translations)
@pytest.mark.config(FEEDBACK_BADGES_MAPPING=feedback_badges_mapping,
                    USE_FEEDBACK_API_FOR_ZENDESK_REPORT=True)
@pytest.mark.filldb(order_proc='for_email', users='for_email')
def test_get_email_body_kwargs(patch,
                               feedback_retrieve_from_proc,
                               passenger_feedback_retrieve_from_proc,
                               order_proc_id, order, user_phone_doc,
                               user_doc, city, statistics, driver, park,
                               expected_result):

    @patch('taxi.internal.order_kit.positions_handler.get_destination_address')
    @async.inline_callbacks
    def get_destination(order_proc):
        yield async.return_value((
            '', '', order_proc.order.request.destinations[0].full_text, ''
        ))

    @patch('taxi.external.geotracks.get_driver_track')
    @async.inline_callbacks
    def get_geotrack(driver_id, db, start_time,
                     end_time, verbose, log_extra=None):
        yield async.return_value({'track': []})

    class MockContext(feedback_report.FeedbackContext):

        @property
        def statistics(self):
            return statistics

    ctx = MockContext()
    ctx.city = dbh.cities.Doc(city)
    ctx.order = dbh.orders.Doc(order)
    ctx.user_phone_doc = dbh.user_phones.Doc(user_phone_doc)
    ctx.user_doc = dbh.users.Doc(user_doc)
    ctx.order_id = order_proc_id
    order_proc = dbh.order_proc.Doc(
        (yield db.order_proc.find_one(order_proc_id))
    )
    ctx.order_proc = order_proc

    for feedback in (ctx.order_proc.order.feedback, None):
        yield feedback_report.fetch_feedback(ctx, feedback=feedback)
        captions = yield feedback_report.get_order_reason_captions(
            feedback=ctx.feedback, locale='ru',
        )
        ctx.order_reason_captions = captions
        ctx.driver = dbh.drivers.Doc(driver)
        ctx.park = dbh.parks.Doc(park)
        ctx.user_email = yield feedback_report.get_email_by_user_id(
            ctx.order_proc.order.user_id,
        )
        kwargs = yield feedback_report.get_report_kwargs(ctx)
        assert kwargs == expected_result, str(feedback)


@pytest.mark.parametrize('order_proc_id,order,city,'
                         'statistics,expected_result', [
    (
        'order_id_ml',
        {
            'billing_tech': {
                'transactions': [
                    {
                        'sum': {
                            'ride': 100000
                        },
                        'status': 'hold_fail'
                    },
                    {
                        'sum': {
                            'ride': 1230000
                        },
                        'status': 'clear_success'
                    },
                    {
                        'sum': {
                            'ride': 50000
                        },
                        'status': 'hold_fail'
                    }
                ]
            },
            'application': 'iphone',
            'payment_tech': {
                'type': 'card',
                'finish_handled': True
            },
        },
        {
            'tz': 'Europe/Moscow'
        },
        {
            'statistics.travel_time': 5000,
            'statistics.travel_distance': 5654,
            'statistics.cancel_time': 300,
            'statistics.cancel_distance': 6700.0,
            'statistics.driver_delay': 598,
            'statistics.start_waiting_time': datetime.datetime(
                2018, 12, 10, 12, 8, 29
            ),
            'statistics.start_transporting_time': datetime.datetime(
                2018, 12, 10, 12, 28, 29
            )
        },
        {
            'application_platform': 'iphone',
            'baby_seat_services': True,
            'cancel_distance_raw': 6700.0,
            'cost_paid_supply': 100,
            'coupon_use_value': 100,
            'dif_ordercost_surge_surgecharge': 845.0,
            'difference_fact_estimated_cost': 134,
            'driver_late_time': 598 / 60.,
            'driver_waiting_time': 20,
            'final_ride_duration': 5000 / 60.,
            'final_transaction_status': 'clear_success',
            'fixed_price_order_flg': True,
            'order_date_ymd': '2018-12-10',
            'order_pre_time_raw_minutes': 1000 / 60.,
            'paid_supply': True,
            'success_order_flg': True,
            'surge_order_flg': True,
            'transportation_animals': True,
            'coupon_used': True,
            'tariff': 'econom',
            'payment_type': 'способ_оплаты_карта',
            'complete_rides': 0,
            'city': 'москва',
            'order_cost': 1134,
            'order_pre_cost': 1131.196,
            'order_pre_distance_raw': 5000,
            'order_distance_raw': 5654,
            'points_b': 'Аврора; Роза',
            'real_point_b': 'Аврора',
            'waiting_cost': 25,
            'waiting_time_raw_minutes': 10,
            'fixed_price': 1000,
            'point_b_changed': False,
            'park_email': 'devnull@yandex.ru',
        }
    ),
])
@pytest.inline_callbacks
@pytest.mark.translations(translations)
@pytest.mark.config(FEEDBACK_BADGES_MAPPING=feedback_badges_mapping,
                    USE_FEEDBACK_API_FOR_ZENDESK_REPORT=True)
@pytest.mark.filldb(_fill=True)
def test_get_kwargs_for_ml_autoreply(patch,
                                     feedback_retrieve_from_proc,
                                     passenger_feedback_retrieve_from_proc,
                                     order_proc_id, order, city, statistics,
                                     expected_result):

    @patch('taxi.internal.order_kit.positions_handler.get_destination_address')
    @async.inline_callbacks
    def get_destination(order_proc):
        yield async.return_value((
            '', '', order_proc.order.request.destinations[0].full_text, ''
        ))

    @patch('taxi.external.geotracks.get_driver_track')
    @async.inline_callbacks
    def get_geotrack(driver_id, db, start_time,
                     end_time, verbose, log_extra=None):
        yield async.return_value({'track': []})

    class MockContext(feedback_report.FeedbackContext):

        @property
        def statistics(self):
            return statistics

    ctx = MockContext()
    ctx.city = dbh.cities.Doc(city)
    ctx.order = dbh.orders.Doc(order)
    ctx.order_id = order_proc_id
    ctx.zclient = MockClient('yataxi')
    ctx.user_phone_doc = yield dbh.user_phones.Doc.find_one_by_id(
        'user_phone_id'
    )
    order_proc = dbh.order_proc.Doc(
        (yield db.order_proc.find_one(order_proc_id))
    )
    ctx.order_proc = order_proc
    ctx.user_type = feedback_report.USER_TYPE_GENERAL
    for feedback in (ctx.order_proc.order.feedback, None):
        yield feedback_report.fetch_feedback(ctx, feedback=feedback)
    yield set_chatterbox_fields(ctx)
    assert expected_result.viewitems() <= ctx.chatterbox_fields.viewitems()


@pytest.mark.parametrize('order_id,user_phone_id,attributes,statistics,'
                         'zendesk_id,ticket_expected', [
    (
        'order_id_1',
        'user_phone_id',
        {
            'bad_route': (True, True),
            'driver_late': True,
            'short_notrip': True,
            'nochange': False,
            'bad_driving': False,
        },
        {
            "statistics.travel_time": 564.1,
            "statistics.travel_distance": 25012.0,
            "statistics.cancel_time": 300,
            "statistics.cancel_distance": 4500.0,
            "statistics.driver_delay": 1000,
            "statistics.start_waiting_time": datetime.datetime(
                2015, 7, 30, 15, 28, 29
            ),
            "statistics.start_transporting_time": datetime.datetime(
                2015, 7, 30, 15, 34, 29
            )
        },
        'yataxi',
        {
            'ticket': {
                'requester': {
                    'name': '79000000000',
                    'email': '79000000000@taxi.yandex.ru'
                },
                'subject': 'Яндекс.Такси (Moscow). Отзыв по заказу order.',
                'comment': 'Предварительная стоимость: 5000 руб (25.000 км/ 8 мин)\n'
                           'Итоговая стоимость: 8000 руб (25.012 км/ 9 мин)\n'
                           'Оценка пользователя: 2\n'
                           'Комментарий пользователя: ругался матом\n'
                           'Что было не так: Ездил кругами, Водитель опоздал, Грубый водитель\n\n'
                           'Госномер автомобиля: АА111А77\n'
                           'Номер ВУ водителя: права\n'
                           'Номер телефона водителя: +74997771122\n'
                           'Сурдж: 2\n'
                           'Ожидание: 8 мин\n'
                           'Пожелания: text\n'
                           'Время отмены: 5 мин\n'
                           'Расстояние в момент отмены: 4.500 км\n'
                           'Фиксированная стоимость поездки: 500 руб\n'
                           'Способ расчёта: fixed\n'
                           'Была указана точка Б: Да\n'
                           'Стоимость поездки завышена на 60%\n'
                           'Минуты ожидания: 6 мин\n'
                           'Платные услуги: animal - 100.0 Rub, seat - 200.0 Rub\n'
                           'Машина была подана позже на: 16 мин',
            }
        }
    ),
    (
        'order_id_2',
        'user_phone_id',
        {
            'bad_route': (False, False),
            'driver_late': False,
            'short_notrip': False,
            'nochange': False,
            'bad_driving': False,
        },
        {
            "statistics.travel_time": 564.1,
            "statistics.travel_distance": 25012.0,
            "statistics.driver_delay": 1000,
            "statistics.start_waiting_time": datetime.datetime(
                2015, 7, 30, 15, 28, 29
            ),
            "statistics.start_transporting_time": datetime.datetime(
                2015, 7, 30, 15, 34, 29
            )
        },
        'yataxi',
        {
            'ticket': {
                'requester': {
                    'name': '79000000000',
                    'email': '79000000000@taxi.yandex.ru'
                },
                'subject': 'Яндекс.Такси (Moscow). Отзыв по заказу order.',
                'comment': 'Предварительная стоимость: 3000.0 руб (25.000 км/ 8 мин)\n'
                           'Итоговая стоимость: 4000 руб (25.012 км/ 9 мин)\n'
                           'Оценка пользователя: 3\n'
                           'Комментарий пользователя: ужасно\n'
                           'Что было не так: Водитель попросил отменить, '
                           'Водитель ехал в другую сторону, Заказал по ошибке\n\n'
                           'Госномер автомобиля: АА111А77\n'
                           'Номер ВУ водителя: права\n'
                           'Номер телефона водителя: +74997771122\n'
                           'Сурдж: 1.5\n'
                           'Ожидание: -\n'
                           'Пожелания: \n'
                           'Время отмены: -\n'
                           'Расстояние в момент отмены: -\n'
                           'Фиксированная стоимость поездки:  руб\n'
                           'Способ расчёта: taximeter\n'
            }
        }
    ),
    (
            'order_id_1',
            'user_phone_id',
            {
                'bad_route': (True, True),
                'driver_late': True,
                'short_notrip': True,
                'nochange': False,
                'bad_driving': False,
            },
            {
                "statistics.travel_time": 564.1,
                "statistics.travel_distance": 25012.0,
                "statistics.cancel_time": 300,
                "statistics.cancel_distance": 4500.0,
                "statistics.driver_delay": 1000,
                "statistics.start_waiting_time": datetime.datetime(
                    2015, 7, 30, 15, 28, 29
                ),
                "statistics.start_transporting_time": datetime.datetime(
                    2015, 7, 30, 15, 34, 29
                )
            },
            'yutaxi',
            {
                'ticket': {
                    'requester': {
                        'name': '79000000000',
                        'email': '79000000000@taxi.yuber.ru'
                    },
                    'subject': 'Такси (Moscow). Отзыв по заказу order.',
                    'comment': 'Предварительная стоимость: 5000 руб (25.000 км/ 8 мин)\n'
                               'Итоговая стоимость: 8000 руб (25.012 км/ 9 мин)\n'
                               'Оценка пользователя: 2\n'
                               'Комментарий пользователя: ругался матом\n'
                               'Что было не так: Ездил кругами, Водитель опоздал, Грубый водитель\n\n'
                               'Госномер автомобиля: АА111А77\n'
                               'Номер ВУ водителя: права\n'
                               'Номер телефона водителя: +74997771122\n'
                               'Сурдж: 2\n'
                               'Ожидание: 8 мин\n'
                               'Пожелания: text\n'
                               'Время отмены: 5 мин\n'
                               'Расстояние в момент отмены: 4.500 км\n'
                               'Фиксированная стоимость поездки: 500 руб\n'
                               'Способ расчёта: fixed\n'
                               'Была указана точка Б: Да\n'
                               'Стоимость поездки завышена на 60%\n'
                               'Минуты ожидания: 6 мин\n'
                               'Платные услуги: animal - 100.0 Rub, seat - 200.0 Rub\n'
                               'Машина была подана позже на: 16 мин',
                }
            }
    ),
])
@pytest.inline_callbacks
@pytest.mark.filldb(_fill=True)
@pytest.mark.translations(translations)
@pytest.mark.config(FEEDBACK_BADGES_MAPPING=feedback_badges_mapping)
def test_make_zendesk_ticket(patch, order_id, user_phone_id, attributes, statistics,
                             zendesk_id, ticket_expected, mock_driver_tags,
                             areq_request):

    @patch('taxi.internal.order_kit.positions_handler.get_destination_address')
    @async.inline_callbacks
    def get_destination(order_proc):
        yield async.return_value((
            '', '', order_proc.order.request.destinations[0].full_text, ''
        ))

    @patch('taxi.internal.driver_manager._set_brand_model')
    def _set_brand_model(brand, model, car_doc):
        car_doc['brand'] = brand
        car_doc['model'] = model

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    @patch('taxi.external.geotracks.get_driver_track')
    @async.inline_callbacks
    def get_geotrack(driver_id, db, start_time,
                     end_time, verbose, log_extra=None):
        yield async.return_value({'track': []})

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))
        if url == "http://personal.taxi.yandex.net/v1/phones/find":
            phone = kwargs['json']['value']
            response = {'value': phone, 'id': 'id_' + phone}
            return areq_request.response(200, body=json.dumps(response))

    class MockContext(feedback_report.FeedbackContext):
        @property
        def statistics(self):
            return statistics

    ctx = MockContext()
    ctx.zclient = MockClient(zendesk_id)
    ctx.order_id = order_id
    ctx.order = yield dbh.orders.Doc.find_one_by_id(order_id)
    ctx.order_proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    ctx.user_doc = yield dbh.users.Doc({})
    ctx.user_phone_doc = yield dbh.user_phones.Doc.find_one_by_id(user_phone_id)
    ctx.attributes = attributes
    ctx.driver = yield driver_manager.get_doc(ctx.order_proc.chosen_candidate.driver_id, 'test_make_zendesk_ticket')
    ctx.city = yield dbh.cities.Doc.find_one_by_id(
        ctx.order_proc.order.city_id,
        fields=[dbh.cities.Doc.tz],
        secondary=True
    )

    try:
        ctx.tariff = yield dbh.tariffs.Doc.find_one_or_not_found(
            query={
                dbh.tariffs.Doc.categories.tariff_id:
                    ctx.order_proc.chosen_candidate.category_id
            },
            fields=[
                'categories.$',
                dbh.tariffs.Doc.home_zone
            ],
            secondary=True
        )
    except dbh.tariffs.NotFound:
        pass
    yield feedback_report.fetch_feedback(ctx)
    readonly = yield feedback_report._check_ticket_readonly(
        ctx, 'general', [],
    )
    captions = yield feedback_report.get_order_reason_captions(
        ctx.feedback, locale=feedback_report.TICKET_LOCALE,
    )
    ctx.order_reason_captions = captions
    ctx.report_kwargs = yield feedback_report.get_report_kwargs(ctx)
    ctx.user_type = feedback_report.USER_TYPE_GENERAL

    ticket, _ = yield feedback_report._create_zendesk_ticket(
        ctx, user_experiments3={}, ticket_readonly=readonly,
    )
    assert ticket['ticket']['comment'] == ticket_expected['ticket']['comment']
    assert ticket['ticket']['subject'] == ticket_expected['ticket']['subject']
    assert ticket['ticket']['requester'] == ticket_expected['ticket']['requester']
    assert ticket['ticket']['ticket_form_id'] == TICKET_FORM_ID


@pytest.mark.parametrize('order_proc,comment_expected', [
    (
        {
            '_id': 'order_id',
            'candidates': [
                {},
                {},
                {
                    'db_id': 'ext_park', 'alias_id': 'ext_order',
                    'driver_id': 'park_driver'
                }
            ],
            'performer': {'candidate_index': 2, 'park_id': 'clid'}
        },
        'Заказ в Такси: https://ymsh-admin.mobile.yandex-team.ru/'
        '?order_id=order_id\n'
        'Заказ в Таксометре: https://taximeter-admin.taxi.yandex-team.ru/redirect/to/order'
        '?db=ext_park&order=ext_order\n'
        'Платежи: https://ymsh-admin.mobile.yandex-team.ru/'
        '?payments_order_id=order_id\n'
        'Поездки пользователя: None\n'
        'Логи: https://ymsh-admin.mobile.yandex-team.ru/'
        '?log_order_id=order_id\n'
        'Водители: https://ymsh-admin.mobile.yandex-team.ru/'
        '?driver_id=park_driver\n'
    )
])
@pytest.inline_callbacks
def test_comment_links_block(order_proc, comment_expected):
    ctx = feedback_report.FeedbackContext()
    ctx.order_proc = dbh.order_proc.Doc(order_proc)
    comment = yield feedback_report._comment_links_block(ctx)
    assert comment == comment_expected


@pytest.mark.parametrize('choices,driver_delay,expected_result', [
    (['rudedriver'], 630, False),
    (['driverlate'], 630, True),
    (['driverlate'], 400, False),
    (['driverlate'], None, False),
])
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_driver_delay(choices, driver_delay, expected_result):
    driver_late = yield feedback_report.is_driver_late(choices, driver_delay)
    assert driver_late == expected_result


@pytest.mark.parametrize('order_proc,choices,expected_result', [
    (
        {
            '_id': 'order_id_1',
            "changes": {
                "objects": []
            },
            'order': {
                'calc': {
                    'allowed_tariffs': {
                        'park': {
                            'econom': 859.33
                        }
                    }
                },
                'request': {
                  'destinations': []
                },
                'cost': 0,
            },
            'candidates': [{'tariff_class': 'econom'}],
            'performer': {'candidate_index': 0}
        },
        ['rudedriver'],
        (False, False)
    ),
    (
        {
            '_id': 'order_id_2',
            "changes": {
                "objects": []
            },
            'order': {
                'calc': {
                    'allowed_tariffs': {
                        'park': {
                            'vip': 859.33
                        }
                    }
                },
                'request': {
                    'destinations': []
                },
                'cost': 0,
            },
            'candidates': [{'tariff_class': 'vip'}],
            'performer': {'candidate_index': 0}
        },
        ['badroute'],
        (False, False)
    ),
    (
        {
            '_id': 'order_id_3',
            "changes": {
                "objects": []
            },
            'order': {
                'calc': {
                    'allowed_tariffs': {
                        'park': {
                            'comfortplus': 859.33
                        }
                    }
                },
                'request': {
                    'destinations': []
                },
                'cost': 900,
            },
            'candidates': [{'tariff_class': 'comfortplus'}],
            'performer': {'candidate_index': 0}
        },
        ['badroute'],
        (True, False)
    ),
    (
        {
            '_id': 'order_id_4',
            "changes": {
                "objects": []
            },
            'order': {
                'calc': {
                    'allowed_tariffs': {
                        'park': {
                            'business': 859.33
                        }
                    }
                },
                'request': {
                    'destinations': ['dest']
                },
                'cost': 900,
            },
            'candidates': [
                {'tariff_class': 'econom'}, {'tariff_class': 'business'}
            ],
            'performer': {'candidate_index': 1}
        },
        ['badroute'],
        (False, True)
    ),
    (
        {
            '_id': 'order_id_5',
            "changes": {
                "objects": []
            },
            'order': {
                'calc': {
                    'allowed_tariffs': {
                        'park': {
                            'econom': 859.33
                        }
                    }
                },
                'request': {
                    'destinations': ['dest']
                },
                'cost': 2000,
            },
            'candidates': [{'tariff_class': 'econom'}],
            'performer': {'candidate_index': 0}
        },
        ['badroute'],
        (True, True)
    ),
    (
        {
            '_id': 'order_id_6',
            "changes": {
                "objects": [
                    {
                        "n": "destinations",
                        "vl": []
                    },
                    {
                        "n": "destinations",
                        "vl": ["new destination"]
                    }
                ]
            },
            'order': {
                'calc': {
                    'allowed_tariffs': {
                        'park': {
                            'econom': 859.33
                        }
                    }
                },
                'request': {
                    'destinations': []
                },
                'cost': 2000,
            },
            'candidates': [{'tariff_class': 'econom'}],
            'performer': {'candidate_index': 0}
        },
        ['badroute'],
        (True, False)
    ),
    (
        {
            '_id': 'order_id_7',
            "changes": {
                "objects": [
                    {
                        "n": "destinations",
                        "vl": [],
                    },
                    {
                        "n": "destinations",
                        "vl": ["new destination"],
                    }
                ]
            },
            'order': {
                'calc': {
                    'allowed_tariffs': {
                        'park': {
                            'econom': 859.33
                        }
                    }
                },
                'request': {
                    'destinations': ['dest']
                },
                'cost': 900
            },
            'candidates': [{'tariff_class': 'econom'}],
            'performer': {'candidate_index': None}
        },
        ['badroute'],
        (True, False)
    ),
])
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_bad_route(order_proc, choices, expected_result):
    order_proc = dbh.order_proc.Doc(order_proc)
    driver_late = yield feedback_report.is_bad_route(order_proc, choices)
    assert driver_late == expected_result


@pytest.mark.parametrize('choices,expected_result', [
    (
        ['rudedriver'],
        False
    ),
    (
        ['nochange'],
        True
    ),
    (
        [],
        False
    ),
    (
        ['rudedriver', 'nochange'],
        True
    ),
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_nochange(choices, expected_result):
    no_change = feedback_report.is_nochange(choices)
    assert no_change == expected_result


@pytest.mark.parametrize('choices,expected_result', [
    (
        ['droveaway'],
        True
    ),
    (
        ['droveaway', 'usererror'],
        True
    ),
    (
        [],
        False
    ),
    (
        ['driverrequest'],
        False
    ),
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_drove_away(choices, expected_result):
    no_change = feedback_report.is_drove_away(choices)
    assert no_change == expected_result


@pytest.mark.parametrize('choices,expected_result', [
    (
        ['droveaway'],
        False
    ),
    (
        ['driverrequest', 'usererror'],
        True
    ),
    (
        [],
        False
    ),
    (
        ['usererror'],
        False
    ),
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_driver_request(choices, expected_result):
    driver_request = feedback_report.is_driver_request(choices)
    assert driver_request == expected_result


@pytest.mark.parametrize('order,travel_time,expected_result', [
    (
        {
            '_id': 'order_id',
            'payment_tech': {'type': dbh.orders.PAYMENT_TYPE_CARD},
            'status': 'finished',
            'taxi_status': 'complete',
        },
        50,
        True
    ),
    (
        {
            '_id': 'order_id',
            'payment_tech': {'type': dbh.orders.PAYMENT_TYPE_CARD},
            'status': 'finished',
            'taxi_status': 'failed',
        },
        50,
        False
    ),
    (
        {
            '_id': 'order_id',
            'payment_tech': {'type': dbh.orders.PAYMENT_TYPE_CARD},
            'status': 'finished',
            'taxi_status': 'complete',
        },
        100,
        False
    ),
    (
        {
            '_id': 'order_id',
            'payment_tech': {'type': dbh.orders.PAYMENT_TYPE_CARD},
            'status': 'pending',
            'taxi_status': 'complete',
        },
        50,
        False
    ),
    (
        {
            '_id': 'order_id',
            'payment_tech': {'type': dbh.orders.PAYMENT_TYPE_CARD},
            'status': 'pending',
            'taxi_status': 'complete',
        },
        None,
        False,
    ),
    (
        {
            '_id': 'order_id',
            'payment_tech': {'type': dbh.orders.PAYMENT_TYPE_CASH},
            'status': 'finished',
            'taxi_status': 'complete',
        },
        40,
        False,
    ),
])
@pytest.mark.translations(translations)
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_short_ride(order, travel_time, expected_result):
    order = dbh.orders.Doc(order)
    short_trip = yield feedback_report._is_short_notrip(order, travel_time)
    assert short_trip == expected_result


@pytest.mark.parametrize('report,feedback,expected_result', [
    (
        {
            'comment': 'text',
            'rating': 3,
            'call_requested': False,
            'choices': {}
        },
        {
            'msg': 'text',
            'rating': 3,
            'c': False,
            'choices': {
                'low_rating_reason': ['driverlate']
            }
        },
        (False, True, False)
    ),
    (
        {
            'comment': 'text',
            'rating': 3,
            'call_requested': False,
            'choices': {
                'cancelled_reasons': ['usererror']
            }
        },
        {
            'msg': 'new_text',
            'rating': 3,
            'c': False,
            'choices': {
                'low_rating_reason': ['driverlate']
            }
        },
        (True, True, False)
    ),
    (
        {
            'comment': 'new_text',
            'rating': 3,
            'call_requested': False,
            'choices': {
                'low_rating_reason': ['driverlate']
            }
        },
        {
            'msg': 'new_text',
            'rating': 3,
            'c': True,
            'choices': {
                'low_rating_reason': ['driverlate']
            }
        },
        (False, True, True)
    ),
    (
        {
            'comment': '',
            'rating': 3,
            'call_requested': False,
            'choices': {
                'low_rating_reason': ['driverlate', 'smellycar']
            }
        },
        {
            'rating': 3,
            'c': False,
            'choices': {
                'low_rating_reason': ['driverlate', 'smellycar']
            }
        },
        (False, False, False)
    ),
    (
        {
            'rating': 3,
            'call_requested': True,
            'choices': {
                'low_rating_reason': ['driverlate', 'smellycar']
            }
        },
        {
            'msg': '',
            'rating': 3,
            'c': False,
            'choices': {
                'low_rating_reason': ['driverlate', 'smellycar'],
                'cancelled_reason': ['usererror']
            }
        },
        (False, True, False)
    ),
    (
        {
            'comment': 'Text',
            'rating': 3,
            'call_requested': False,
            'choices': {
                'low_rating_reason': ['driverlate', 'smellycar']
            }
        },
        {
            'msg': '',
            'rating': 4,
            'c': False,
            'choices': {
                'low_rating_reason': ['driverlate', 'smellycar'],
            }
        },
        (True, True, False)
    ),
    (
        {
            'comment': 'Text',
            'rating': 3,
            'call_requested': False,
        },
        {
            'msg': '',
            'rating': 3,
            'c': True,
            'choices': {
                'low_rating_reason': ['driverlate', 'smellycar'],
            }
        },
        (True, True, True)
    ),
    (
        {
            'comment': 'Text',
            'rating': 3,
            'call_requested': False,
            'choices': {
                'low_rating_reason': ['driverlate', 'smellycar']
            }
        },
        {
            'msg': '',
            'rating': 3,
            'c': False,
        },
        (True, True, False)
    ),
    (
        {
            'comment': 'Text',
            'rating': 3,
            'call_requested': False,
            'choices': {
                'low_rating_reason': ['driverlate', 'smellycar']
            }
        },
        {
            'msg': '',
            'rating': 3,
            'c': False,
            'choices': {
                'low_rating_reason': ['driverlate', 'smellycar', 'badroute'],
            }
        },
        (True, True, False)
    ),
])
@pytest.mark.filldb(_fill=False)
def test_compare_report(report, feedback, expected_result):
    text_changed, params_changed, call = feedback_report._compare_report(
        report, feedback_manager.FeedbackStorage(feedback, new_style=False)
    )
    assert text_changed == expected_result[0]
    assert params_changed == expected_result[1]
    assert call == expected_result[2]


@pytest.mark.filldb(_fill=True)
@pytest.mark.async('blocking')
@pytest.inline_callbacks
def test_no_performer_fetch():
    ctx = feedback_report.FeedbackContext()
    ctx.order_id = 'order_id'
    res = yield feedback_report.fetch_data_for_ride_feedback(ctx)
    assert ctx.has_order_info
    assert not ctx.driver_id
    assert not res


@pytest.mark.filldb(_fill=True)
@pytest.mark.config(
    FEEDBACK_ENABLE_CHECK_KEYWORDS=True,
    USE_FEEDBACK_API_FOR_ZENDESK_REPORT=True,
    FEEDBACK_FALSE_URGENT_WORDS=['мороз'],
    FEEDBACK_COUNTRIES_ML_CHECK_URGENCY=['rus'],
)
@pytest.mark.parametrize(
    'order_id,result,user_country,expected_urgency',
    [
        ('order_id_urgent', True, 'blr', None),
        ('order_id_not_urgent', False, 'blr', None),
        ('order_id_urgent', True, 'blr', None),
        ('order_id_not_urgent', False, 'blr', None),
        ('order_id_urgent', True, 'rus', 0.8),
        ('order_id_not_urgent', False, 'rus', 0.2),
        ('order_id_urgent', True, 'rus', 0.8),
        ('order_id_false_urgent', False, 'rus', 0.2),
        ('order_id_still_urgent', True, 'rus', 0.8),
        ('order_id_not_urgent', False, 'rus', 0.2),
        ('order_id_urgent_with_keywords', True, 'rus', 0.2),
    ],
)
@pytest.mark.translations(translations)
@pytest.inline_callbacks
def test_check_keywords_urgent(feedback_retrieve_from_proc,
                               passenger_feedback_retrieve_from_proc,
                               order_id, result, user_country,
                               expected_urgency, mock_get_urgency,
                               mock_detect_language):
    mocked_detect_language = mock_detect_language('ru')
    ctx = feedback_report.FeedbackContext()
    ctx.order_id = order_id
    ctx.zclient = MockClient('yataxi')
    ctx.user_type = feedback_report.USER_TYPE_CORP
    yield feedback_report.fetch_data_for_ride_feedback(ctx)
    ctx.user_country = user_country

    ml_check_countries = yield config.FEEDBACK_COUNTRIES_ML_CHECK_URGENCY.get()

    for feedback in (ctx.order_proc.order.feedback, None):
        yield feedback_report.fetch_feedback(ctx, feedback=feedback)
        yield set_chatterbox_fields(ctx)
        yield feedback_report.fetch_urgent_and_payment(ctx)
        assert ctx.urgent == result

        assert ctx.chatterbox_fields['urgency_probability'] == str(expected_urgency or '')
        assert ctx.ml_urgency == expected_urgency

        if ctx.user_country in ml_check_countries:
            detect_language_called = mocked_detect_language.calls[0]['kwargs']
            assert detect_language_called['text'] == ctx.feedback.comment

            request_data = mock_get_urgency.calls[0]['kwargs']['request_data']
            assert request_data['comment'] == ctx.feedback.comment
            assert request_data['request_id'] == '{}_None'.format(order_id)
            # mocked_detect_language has returned 'ru'
            assert request_data['comment_language'] == 'ru'
        else:
            assert mock_get_urgency.call is None


@pytest.mark.filldb(_fill=True)
@pytest.mark.config(
    USE_FEEDBACK_API_FOR_ZENDESK_REPORT=True,
    FEEDBACK_FALSE_URGENT_WORDS=['мороз'],
    FEEDBACK_COUNTRIES_ML_CHECK_URGENCY=['rus'],
)
@pytest.mark.parametrize(
    'percentage,order_id,predicted_class,expected_urgent,'
    'expected_false_urgent,expected_use_routing,expected_pymlaas,'
    'expected_translate',
    [
        (
            100, 'order_id_urgent', 'car_accident', True, False, True, False,
            True,
        ),
        (
            100, 'order_id_urgent', 'lost_item_first', True, False, True,
            False, True,
        ),
        (
            100, 'order_id_urgent', 'lost_item_second', True, False, True,
            False, True,
        ),
        (
            100, 'order_id_urgent', 'urgent', True, False, True, False, True,
        ),
        (
            100, 'order_id_urgent', 'urgent_finance', True, False, True, False,
            True,
        ),
        (
            100, 'order_id_urgent', 'other', False, False, True, False, True,
        ),
        (
            100, 'order_id_false_urgent', 'urgent', True, False, True, False,
            True,
        ),
        (
            100, 'order_id_false_urgent', 'other', False, True, True, False,
            True,
        ),
        (
            100, 'order_id_empty_comment', None, False, False, None, False,
            False,
        ),
        (
            0, 'order_id_urgent', None, False, False, None, True, True,
        ),
        (
            0, 'order_id_empty_comment', None, False, False, None, False,
            False,
        ),
    ],
)
@pytest.mark.translations(translations)
@pytest.inline_callbacks
def test_client_tickets_routing(feedback_retrieve_from_proc,
                                passenger_feedback_retrieve_from_proc,
                                percentage,
                                order_id, predicted_class, expected_urgent,
                                expected_false_urgent, expected_use_routing,
                                expected_pymlaas, expected_translate,
                                areq_request, mock_detect_language):
    yield config.FEEDBACK_CLIENT_TICKETS_ROUTING_PERCENTAGE.save(percentage)
    mocked_detect_language = mock_detect_language('ru')

    @areq_request
    def request(method, url, **kwargs):
        if url.endswith('/client_tickets_routing/v1'):
            response = {
                'ml_class_name': 'ml_class',
                'urgent_keywords_triggered': True,
                'lost_item_second_keywords_triggered': True,
                'probabilities': [0.0, 0.5, 1.0],
            }
            if 'мороз' in kwargs['json']['comment']:
                response['predicted_class_name'] = 'urgent'
            else:
                response['predicted_class_name'] = predicted_class
            return areq_request.response(
                200,
                body=json.dumps(response)
            )
        return areq_request.response(
            200,
            body=json.dumps({'urgency_probability': 0})
        )

    ctx = feedback_report.FeedbackContext()
    ctx.ml_request_id = uuid.uuid4().hex
    ctx.order_id = order_id
    ctx.zclient = MockClient('yataxi')
    ctx.user_type = feedback_report.USER_TYPE_CORP
    yield feedback_report.fetch_data_for_ride_feedback(ctx)
    ctx.user_country = 'rus'

    for feedback in (ctx.order_proc.order.feedback, None):
        yield feedback_report.fetch_feedback(ctx, feedback=feedback)
        yield set_chatterbox_fields(ctx)
        yield feedback_report.fetch_urgent_and_payment(ctx)
        assert ctx.urgent == expected_urgent
        assert ctx.false_urgent == expected_false_urgent
        assert ctx.use_client_tickets_routing_ml == expected_use_routing

        excluded_args = [
            ('POST', 'http://experiments3.taxi.yandex.net/v1/experiments')
        ]
        request_calls = [
            request_call for request_call in request.calls
            if request_call['args'] not in excluded_args
        ]
        if expected_pymlaas:
            assert request_calls[0]['args'] == (
                'POST', 'http://pyml.test.url/urgent_comments_detection',
            )
        elif expected_use_routing is not None:
            assert ctx.use_client_tickets_routing_ml
            assert ctx.urgent_keywords_triggered
            assert ctx.lost_item_second_keywords_triggered
            assert request_calls[0]['args'] == (
                'POST', 'http://plotva-ml.test.url/client_tickets_routing/v1',
            )
            request_data = request_calls[0]['kwargs']['json']
            assert request_data['comment'] == ctx.feedback.comment
            assert request_data['comment_language'] == 'ru'
            assert (
                    ctx.chatterbox_fields['predicted_class_name'] ==
                    predicted_class
            )
            assert ctx.chatterbox_fields['ml_class_name'] == 'ml_class'
            assert ctx.chatterbox_fields['ml_class_probabilities'] == [
                0.0, 0.5, 1.0,
            ]

            assert ctx.ml_request_id == UUID
        else:
            assert not request_calls

        if expected_translate:
            detect_language_called = mocked_detect_language.calls[0]['kwargs']
            assert detect_language_called['text'] == ctx.feedback.comment
        else:
            assert not mocked_detect_language.calls


@pytest.mark.config(
    FEEDBACK_ENABLE_CHECK_KEYWORDS=True,
    FEEDBACK_URGENT_KEYWORDS_BY_LANG={
        'fi': ['fin_urgent'], 'ru': ['ужасно'],
    },
    FEEDBACK_PAYMENT_KEYWORDS_BY_LANG={
        'fi': ['fin_payment'], 'ru': ['оплата'],
    },
    FEEDBACK_URGENT_KEYWORDS=['ург_дефолт_keyword'],
    FEEDBACK_PAYMENT_KEYWORDS=['оплата_дефолт_keyword'],
    FEEDBACK_BADGES_MAPPING=feedback_badges_mapping,
    FEEDBACK_CHECK_KEYWORDS_BY_LANG=['fin'],
    FEEDBACK_COUNTRIES_ML_CHECK_URGENCY=[],  # will not go to check ml urgency
)
@pytest.mark.translations(translations)
@pytest.mark.parametrize(
    'use_default_languages,comment,country,urgent,payment,urgent_langs,'
    'payment_langs,result_tags',
    (
        (True, 'без ключевых слов =(', 'fin', False, False, [], [], []),
        (True, 'fin_urgent', 'fin',
         True, False, ['fi'], [],
         ['клиент_urgent', 'подозрение_urgent', 'urgent_fi',
          'need_response_before_ml']),
        (
            True,
            'fin_urgent и ужасно', 'fin',
            True, False, ['ru', 'fi'], [],
            ['клиент_urgent', 'подозрение_urgent', 'urgent_ru', 'urgent_fi',
             'need_response_before_ml'],
        ),
        (
            True,
            'fin_payment', 'fin',
            False, True, [], ['fi'],
            ['клиент_оплата', 'подозрение_оплата', 'оплата_fi',
             'need_response_before_ml'],
        ),
        (
            True,
            'fin_urgent,ужасно fin_payment', 'fin',
            True, True, ['ru', 'fi'], ['fi'],
            # if has urgent and has payment => urgent tags'il win
            ['клиент_urgent', 'подозрение_urgent', 'urgent_ru', 'urgent_fi',
             'need_response_before_ml']),
        # if country not in FEEDBACK_CHECK_KEYWORDS_BY_LANG,
        # we'il use default_config instead lang_config
        (
            True,
            'fin_urgent,ужасно fin_payment', 'rus',
            False, False, [], [],
            [],
        ),
        (
            True,
            'ург_дефолт_keyword и оплата_дефолт_keyword', 'rus',
            True, True, [], [],
            ['клиент_urgent', 'подозрение_urgent', 'need_response_before_ml'],
        ),
        (False, 'без ключевых слов =(', 'fin', False, False, [], [], []),
        (False, 'fin_urgent', 'fin',
         True, False, ['fi'], [],
         ['клиент_urgent', 'подозрение_urgent', 'urgent_fi',
          'need_response_before_ml']),
        (
            False,
            'fin_urgent и ужасно', 'fin',
            True, False, ['fi'], [],
            ['клиент_urgent', 'подозрение_urgent', 'urgent_fi',
             'need_response_before_ml'],
        ),
        (
            False,
            'fin_payment', 'fin',
            False, True, [], ['fi'],
            ['клиент_оплата', 'подозрение_оплата', 'оплата_fi',
             'need_response_before_ml'],
        ),
        (
            False,
            'fin_urgent,ужасно fin_payment', 'fin',
            True, True, ['fi'], ['fi'],
            # if has urgent and has payment => urgent tags'il win
            ['клиент_urgent', 'подозрение_urgent', 'urgent_fi',
             'need_response_before_ml']),
        (
            False,
            'fin_payment и оплата', 'fin',
            False, True, [], ['fi'],
            ['клиент_оплата', 'подозрение_оплата', 'оплата_fi',
             'need_response_before_ml'],
        ),
        (
            False,
            'оплата', 'fin',
            False, False, [], [],
            [],
        ),
        # if country not in FEEDBACK_CHECK_KEYWORDS_BY_LANG,
        # we'il use default_config instead lang_config
        (
            False,
            'fin_urgent,ужасно fin_payment', 'rus',
            False, False, [], [],
            [],
        ),
        (
            False,
            'ург_дефолт_keyword и оплата_дефолт_keyword', 'rus',
            True, True, [], [],
            ['клиент_urgent', 'подозрение_urgent', 'need_response_before_ml'],
        ),
    ),
)
@pytest.inline_callbacks
@pytest.mark.filldb(_fill=True)
def test_check_urgent_and_payment(
        feedback_retrieve_from_proc,
        passenger_feedback_retrieve_from_proc, mock_get_urgency,
        use_default_languages, comment, country, urgent, payment,
        urgent_langs, payment_langs, result_tags, mock_detect_language,
):
    mock_detect_language('fi')
    yield config.FEEDBACK_USE_DEFAULT_LANGUAGES.save(use_default_languages)
    ctx = feedback_report.FeedbackContext()
    ctx.order_id = 'order_id_urgent_and_payment'
    ctx.zclient = MockClient('yataxi')
    yield feedback_report.fetch_data_for_ride_feedback(ctx)
    yield feedback_report.fetch_feedback(
        ctx, feedback=ctx.order_proc.order.feedback,
    )
    yield feedback_report.fetch_extended_info(ctx)

    ctx.feedback._data['msg'] = comment
    ctx.user_country = country
    ctx.user_type = feedback_report.USER_TYPE_CORP
    yield set_chatterbox_fields(ctx)
    yield feedback_report.fetch_urgent_and_payment(ctx)

    assert ctx.urgent == urgent
    assert ctx.payment == payment
    assert ctx.urgent_langs == urgent_langs
    assert ctx.payment_langs == payment_langs
    ctx.user_type = feedback_report.USER_TYPE_GENERAL

    yield feedback_report._need_create_report(
        ctx, order_experiments=[],
    )
    ticket, _ = yield feedback_report._create_zendesk_ticket(
        ctx,
        user_experiments3={},
        ticket_readonly=False,
    )

    assert ticket['ticket']['tags'] == result_tags


@pytest.mark.filldb(_fill=True)
@pytest.mark.config(
    FEEDBACK_URGENT_SHORTLIST=['ужасно'],
    FEEDBACK_COUNTRIES_ML_CHECK_URGENCY=['rus'],
)
@pytest.mark.parametrize(
    'order_id,result',
    [
        ('order_id_urgent', True),
        ('order_id_not_urgent', False)
    ],
)
@pytest.mark.translations(translations)
@pytest.inline_callbacks
def test_shortlist(feedback_retrieve_from_proc,
                   passenger_feedback_retrieve_from_proc, order_id, result,
                   mock_detect_language, mock_get_urgency):
    mock_detect_language('ru')
    ctx = feedback_report.FeedbackContext()
    ctx.order_id = order_id
    ctx.zclient = MockClient('yataxi')
    ctx.user_type = feedback_report.USER_TYPE_CORP
    yield feedback_report.fetch_data_for_ride_feedback(ctx)
    ctx.user_country = 'rus'  # for checking urgency in ml

    for feedback in (ctx.order_proc.order.feedback, None):
        yield feedback_report.fetch_feedback(ctx, feedback=feedback)
        yield set_chatterbox_fields(ctx)
        yield feedback_report.fetch_urgent_and_payment(ctx)
        assert mock_get_urgency.call['kwargs']['request_data']['comment'] == (
                ctx.feedback.comment or ''
        )
        assert ctx.urgent == result


@pytest.mark.filldb(_fill=True)
@pytest.mark.config(
    FEEDBACK_ENABLE_CHECK_KEYWORDS=True,
    USE_FEEDBACK_API_FOR_ZENDESK_REPORT=True,
    FEEDBACK_COUNTRIES_ML_CHECK_URGENCY=['rus'],
)
@pytest.mark.parametrize(
    'order_id,result',
    [
        ('order_id_urgent', True),
        ('order_id_not_urgent', False)
    ],
)
@pytest.inline_callbacks
def test_check_urgent_ml_fallback(feedback_retrieve_from_proc,
                                  passenger_feedback_retrieve_from_proc,
                                  order_id,
                                  result, monkeypatch, mock,
                                  mock_detect_language):
    mock_detect_language('ru')

    @async.inline_callbacks
    def _dummy_get_urgency(request_data, log_extra=None):
        yield
        raise RuntimeError('AHAHA LOL!11')

    original_check_keywords = feedback_report.check_keywords

    @mock
    @async.inline_callbacks
    def _dummy_check_keywords(*args, **kwargs):
        result = yield original_check_keywords(*args, **kwargs)
        async.return_value(result)

    monkeypatch.setattr(
        pymlaas,
        'urgent_comments_detection',
        _dummy_get_urgency
    )
    monkeypatch.setattr(
        feedback_report,
        'check_keywords',
        _dummy_check_keywords,
    )

    ctx = feedback_report.FeedbackContext()
    ctx.order_id = order_id
    ctx.user_country = 'rus'  # will check urgency in ml
    yield feedback_report.fetch_data_for_ride_feedback(ctx)

    for feedback in (ctx.order_proc.order.feedback, None):
        yield feedback_report.fetch_feedback(ctx, feedback=feedback)
        yield feedback_report.fetch_urgent_and_payment(ctx)
        check_keywords_calls = _dummy_check_keywords.calls
        assert check_keywords_calls
        assert ctx.urgent == result


@pytest.mark.parametrize('order_id,user_phone_id,is_need', [
    (
        'order_id_1',
        'user_phone_id',
        True
    ),
    (
        'order_id_not_feedback',
        'user_phone_id',
        False
    ),
    (
        'order_id_empty_feedback',
        'user_phone_id',
        False
    ),
])
@pytest.inline_callbacks
@pytest.mark.filldb(_fill=True)
def test_need_report(patch, order_id, user_phone_id, is_need):

    class MockContext(feedback_report.FeedbackContext):

        @property
        def statistics(self):
            stat = {
                "statistics.travel_time": 564.1,
                "statistics.travel_distance": 25012.0,
                "statistics.cancel_time": 300,
                "statistics.cancel_distance": 4500.0,
                "statistics.driver_delay": 1000,
                "statistics.start_waiting_time": datetime.datetime(
                    2015, 7, 30, 15, 28, 29
                ),
                "statistics.start_transporting_time": datetime.datetime(
                    2015, 7, 30, 15, 34, 29
                )
            }
            return stat

    ctx = MockContext()
    ctx.order_id = order_id
    ctx.order = yield dbh.orders.Doc.find_one_by_id(order_id)
    ctx.order_proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    ctx.user_doc = yield dbh.users.Doc({})
    ctx.user_phone_doc = yield dbh.user_phones.Doc.find_one_by_id(user_phone_id)
    yield feedback_report.fetch_feedback(ctx)
    ctx.user_type = feedback_report.USER_TYPE_GENERAL

    result, _ = yield feedback_report._need_create_report(
        ctx, order_experiments=[],
    )
    assert result == is_need


@pytest.mark.parametrize(
    'order_id, order_experiments, rules, expected_readonly',
    [
        (
            'order_id_empty_feedback',
            [],
            [],
            True,
        ),
        (
            'order_id_empty_comment',
            [],
            [],
            True,
        ),
        (
            'order_id_empty_comment',
            [],
            [
                {
                    'percentage': 100,
                    'tariff': ['econom'],
                    'need_comment': True,
                },
            ],
            True,
        ),
        (
            'order_id_empty_comment',
            [],
            [
                {
                    'percentage': 100,
                    'tariff': ['econom'],
                },
            ],
            False,
        ),
        (
            'order_id_econom',
            [],
            [
                {
                    'percentage': 100,
                    'tariff': ['econom'],
                    'max_rating': 3,
                },
            ],
            True,
        ),
        (
            'order_id_econom',
            [],
            [
                {
                    'percentage': 100,
                    'tariff': ['comfortplus'],
                },
            ],
            True,
        ),
        (
            'order_id_econom',
            [],
            [
                {
                    'percentage': 100,
                    'tariff': ['econom'],
                },
            ],
            False,
        ),
        (
            'order_id_corp',
            [],
            [],
            True,
        ),
        (
            'order_id_corp',
            [],
            [
                {
                    'percentage': 100,
                    'user_type': 'corp',
                },
            ],
            False,
        ),
        (
            'order_id_vip',
            [],
            [],
            True,
        ),
        (
            'order_id_vip',
            [],
            [
                {
                    'percentage': 100,
                    'user_type': 'vip',
                },
            ],
            False,
        ),
        (
            'order_id_elite',
            [],
            [],
            True,
        ),
        (
            'order_id_elite',
            [],
            [
                {
                    'percentage': 100,
                    'user_type': 'elite',
                },
            ],
            False,
        ),
        (
            'order_from_Baku',
            [],
            [
                {
                    'percentage': 100,
                    'order_experiment': 'disable_readonly',
                },
            ],
            True,
        ),
        (
            'order_from_Baku',
            ['disable_readonly'],
            [
                {
                    'percentage': 100,
                    'order_experiment': 'disable_readonly',
                },
            ],
            False,
        ),
        (
            'order_from_Baku',
            [],
            [
                {
                    'percentage': 100,
                    'country': 'rus',
                },
            ],
            True,
        ),
        (
            'order_from_Baku',
            [],
            [
                {
                    'percentage': 100,
                    'country': 'aze',
                },
            ],
            False,
        ),
        (
            'order_id_econom',
            [],
            [
                {
                    'percentage': 100,
                    'tariff': 'econom',
                    'feedback_report_conditions': True,
                },
            ],
            True,
        ),
        (
            'order_id_econom',
            [],
            [
                {
                    'percentage': 100,
                    'tariff': 'econom',
                },
            ],
            False,
        ),
        (
            'order_id_econom',
            [],
            [
                {
                    'percentage': 100,
                    'tariff': 'econom',
                    'feedback_report_conditions': False,
                },
            ],
            False,
        ),
        (
            'order_from_New_York',
            [],
            [],
            True,
        ),
        (
            'order_from_New_York',
            [],
            [
                {
                    'percentage': 100,
                    'feedback_report_conditions': True,
                }
            ],
            False,
        ),
        (
            'order_from_New_York',
            [],
            [
                {
                    'percentage': 100,
                    'language': 'ru',
                }
            ],
            False,
        ),
        (
            'order_from_New_York',
            [],
            [
                {
                    'percentage': 100,
                    'language': 'en',
                }
            ],
            True,
        ),
        (
            'order_from_New_York',
            [],
            [
                {
                    'percentage': 100,
                    'language': ['en', 'ru'],
                }
            ],
            False,
        ),
        (
            'order_from_New_York',
            [],
            [
                {
                    'percentage': 100,
                    'language': ['en'],
                }
            ],
            True,
        ),
    ],
)
@pytest.inline_callbacks
@pytest.mark.filldb(_fill=True)
def test_disable_readonly_config(order_id, order_experiments, zclient,
                                 mock_detect_language, rules,
                                 expected_readonly, areq_request):
    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    mock_detect_language('ru')
    yield config.CHATTERBOX_DISABLE_READONLY_RULES.save(rules)
    ctx = feedback_report.FeedbackContext()
    ctx.order_id = order_id
    ctx.zclient = zclient
    yield feedback_report.fetch_data_for_ride_feedback(ctx)
    yield feedback_report.fetch_feedback(ctx)
    yield feedback_report.fetch_extended_info(ctx)
    ctx.user_type = yield feedback_report.get_user_type(
        order=ctx.order,
        order_proc=ctx.order_proc,
        user_phone_doc=ctx.user_phone_doc,
    )
    _, readonly = yield feedback_report._need_create_report(
        ctx, order_experiments=order_experiments,
    )
    assert readonly == expected_readonly
    assert ctx.disable_readonly == (not expected_readonly)


@pytest.mark.parametrize(
    'order_id,expected_readonly,expected_readonly_args',
    [
        (
            'order_id_econom',
            True,
            (
                {
                    'comment': 'почти все клево',
                    'order_pre_time': 100,
                    'order_pre_distance': 1.5,
                    'order_distance': 2.0,
                },
            ),
        ),
        (
            'order_id_ml_not_readonly',
            False,
            (
                {
                    'comment': 'спасибо',
                    'order_pre_time': 100,
                    'order_pre_distance': 1.5,
                    'order_distance': 2.0,
                },
            ),
        ),
    ]
)
@pytest.mark.config(
    FEEDBACK_COUNTRIES_ML_CHECK_URGENCY=['rus'],
    FEEDBACK_READONLY_ML_LANGUAGES=['ru'],
)
@pytest.inline_callbacks
@pytest.mark.filldb(_fill=True)
def test_ml_disable_readonly(mock_get_readonly, mock_get_urgency,
                             order_id, expected_readonly, mock_detect_language,
                             expected_readonly_args):
    mock_detect_language('ru')
    ctx = feedback_report.FeedbackContext()
    ctx.order_id = order_id
    yield feedback_report.fetch_data_for_ride_feedback(ctx)
    yield feedback_report.fetch_feedback(ctx)
    ctx.user_country = 'rus'  # we will check urgency in ml
    yield feedback_report.fetch_urgent_and_payment(ctx)
    ctx.user_type = yield feedback_report.get_user_type(
        order=ctx.order,
        order_proc=ctx.order_proc,
        user_phone_doc=ctx.user_phone_doc,
    )
    _, readonly = yield feedback_report._need_create_report(
        ctx, order_experiments=[],
    )

    ctx.chatterbox_fields = {
        'order_pre_time': '1 мин',
        'order_pre_time_raw': 100,
        'order_pre_distance': '1.5 км',
        'order_pre_distance_raw': 1500,
        'order_distance': '2 км',
        'order_distance_raw': 2000,
        'cancel_time': '-',
        'cancel_time_raw': None,
    }
    readonly = yield feedback_report._ml_disable_readonly(ctx)
    assert readonly == expected_readonly
    if expected_readonly_args is None:
        assert not mock_get_readonly.calls
    else:
        assert (
            mock_get_readonly.calls[0]['args'] == expected_readonly_args
        )


@pytest.mark.parametrize(
    'order_id,expected_readonly',
    [
        (
            'order_id_ml_not_readonly',
            False,
        ),
        (
            'order_id_empty_comment',
            True,
        ),
    ]
)
@pytest.mark.config(
    FEEDBACK_ENABLE_ML_READONLY=True,
    FEEDBACK_READONLY_ML_LANGUAGES=['ru'],
)
@pytest.inline_callbacks
@pytest.mark.filldb(_fill=True)
def test_ml_disable_readonly_fallback(monkeypatch, order_id,
                                      expected_readonly, mock_detect_language):
    mock_detect_language('ru')

    @async.inline_callbacks
    def _dummy_need_response(comment):
        yield
        raise RuntimeError('AHAHA LOL!!1')

    monkeypatch.setattr(
        pymlaas,
        'client_tickets_read_only',
        _dummy_need_response,
    )

    ctx = feedback_report.FeedbackContext()
    ctx.order_id = order_id
    yield feedback_report.fetch_data_for_ride_feedback(ctx)
    yield feedback_report.fetch_feedback(ctx)
    ctx.chatterbox_fields = {'some': 'data'}
    readonly = yield feedback_report._ml_disable_readonly(ctx)
    assert readonly == expected_readonly


@pytest.inline_callbacks
def test_create_zendesk_private_comment():
    ctx = feedback_report.FeedbackContext()
    ctx.zclient = MockClient('yataxi')

    comment = yield feedback_report.create_zendesk_private_comment(ctx)
    assert comment == {
        'ticket': {
            'comment': {
                'public': False,
                'body': '',
                'author_id': 2780965569
            }
        }
    }


@pytest.mark.translations(translations)
@pytest.inline_callbacks
@pytest.mark.filldb(_fill=True)
def test_missing_city():
    ctx = feedback_report.FeedbackContext()
    ctx.order_id = 'order_from_Baku'
    ctx.zclient = MockClient('yataxi')

    yield feedback_report.fetch_data_for_ride_feedback(ctx)
    yield feedback_report.fetch_feedback(ctx)
    yield feedback_report.fetch_extended_info(ctx)
    kwargs = yield feedback_report._get_kwargs_from_order_proc(ctx.order_proc, ctx)
    assert kwargs['order_date'] != '-'


@pytest.mark.translations(translations)
@pytest.inline_callbacks
@pytest.mark.filldb(_fill=True)
def test_nan_pre_time():
    ctx = feedback_report.FeedbackContext()
    ctx.order_id = 'order_from_Baku'
    ctx.zclient = MockClient('yataxi')

    yield feedback_report.fetch_data_for_ride_feedback(ctx)
    yield feedback_report.fetch_feedback(ctx)
    yield feedback_report.fetch_extended_info(ctx)
    kwargs = yield feedback_report._get_kwargs_from_order_proc(ctx.order_proc, ctx)
    assert kwargs['order_pre_time'] == 0
    assert math.isnan(kwargs['order_pre_time_raw'])
    assert math.isnan(kwargs['order_pre_time_raw_minutes'])


@pytest.mark.parametrize(
    'order_id, user_country, experiments3, driver_tags_enabled,'
    'support_info_percentage, client_routing_percentage, tags',
    [
        (
            'order_from_Baku',
            'blr',  # will not check ml urgency
            {},
            False,
            0,
            0,
            [
                'readonly',
                'приятная_музыка',
                'мультизаказ_эксперимент',
            ]
        ),
        (
            'order_from_New_York',
            'blr',
            {},
            True,
            0,
            0,
            [
                'небезопасное_вождение',
                'yandex-team',
                'taxi-staff',
                'disable_readonly',
                'need_response_before_ml',
                'driver_tag_vip',
                'driver_tag_blogger',
            ]
        ),
        (
            'order_id_BAD_LICENSE',
            'blr',
            {},
            True,
            0,
            0,
            [
                'небезопасное_вождение',
                'yandex-team',
                'taxi-staff',
                'disable_readonly',
                'need_response_before_ml',
            ]
        ),
        (
            'order_from_New_York',
            'blr',
            {},
            False,
            0,
            0,
            [
                'небезопасное_вождение',
                'yandex-team',
                'taxi-staff',
                'disable_readonly',
                'need_response_before_ml',
            ]
        ),
        (
            'order_id_call_requested',
            'blr',
            {},
            False,
            0,
            0,
            [
                'небезопасное_вождение',
                'yandex-team',
                'taxi-staff',
                'disable_readonly',
                'need_response_before_ml'
            ]
        ),
        (
            'order_id_econom',
            'blr',
            {
                feedback_report.SHOW_CALL_ME_BACK_OPTION: {
                    'enabled': False,
                    'add_tags': ['dont_show_call_me_back'],
                },
            },
            False,
            0,
            0,
            [
                'readonly',
                'приятная_музыка',
                'use_ml_readonly',
                'мультизаказ_эксперимент',
                'dont_show_call_me_back',
            ]
        ),
        (
            'order_id_ml_not_readonly',
            'blr',
            {feedback_report.SHOW_CALL_ME_BACK_OPTION: {'enabled': False}},
            False,
            0,
            0,
            [
                'use_ml_readonly',
            ]
        ),
        (
            'order_id_ml_not_readonly',
            'blr',
            {},
            False,
            0,
            0,
            [
                'readonly',
            ]
        ),
        (
            'order_id_ultimate',
            'blr',
            {feedback_report.SHOW_CALL_ME_BACK_OPTION: {'enabled': False}},
            False,
            0,
            0,
            [
                'приятная_музыка',
                'disable_readonly',
                'need_response_before_ml',
                'мультизаказ_эксперимент',
            ]
        ),
        (
            'order_id_zero_cost',
            'blr',
            {feedback_report.SHOW_CALL_ME_BACK_OPTION: {'enabled': False}},
            False,
            0,
            0,
            [
                'readonly',
                'приятная_музыка',
                'мультизаказ_эксперимент',
            ]
        ),
        (
            'order_id_urgent_zero_cost',
            'rus',  # will check ml urgency
            {feedback_report.SHOW_CALL_ME_BACK_OPTION: {'enabled': False}},
            False,
            0,
            0,
            [
                'грубый_водитель',
                'клиент_urgent',
                'подозрение_urgent',
                'use_urgent_ml',
                'need_response_before_ml',
            ]
        ),
        (
            'order_from_yauber',
            'blr',
            {},
            False,
            0,
            0,
            [
                'небезопасное_вождение',
                'uber',
                'yauber',
                'yandex-team',
                'taxi-staff',
                'disable_readonly',
                'need_response_before_ml',
            ]
        ),
        (
            'order_from_uber',
            'blr',
            {},
            False,
            0,
            0,
            [
                'небезопасное_вождение',
                'uber',
                'yandex-team',
                'taxi-staff',
                'disable_readonly',
                'need_response_before_ml',
            ]
        ),
        (
            'order_id_urgent',
            'blr',
            {},
            False,
            0,
            0,
            [
                'readonly',
                'грубый_водитель'
            ],
        ),
        (
            'order_id_urgent',
            'rus',
            {},
            False,
            0,
            0,
            [
                'грубый_водитель',
                'клиент_urgent',
                'подозрение_urgent',
                'use_urgent_ml',
                'need_response_before_ml',
            ],
        ),
        (
            'order_id_false_urgent',
            'rus',
            {},
            False,
            0,
            0,
            [
                'readonly',
                'грубый_водитель',
                'use_urgent_ml',
                'false_urgent'
            ],
        ),
        (
            'order_id_still_urgent',
            'rus',
            {},
            False,
            0,
            0,
            [
                'грубый_водитель',
                'клиент_urgent',
                'подозрение_urgent',
                'use_urgent_ml',
                'need_response_before_ml',
            ],
        ),
        (
            'order_id_urgent',
            'blr',
            {},
            True,
            0,
            0,
            [
                'readonly',
                'грубый_водитель',
                'business_client'
            ],
        ),
        (
            'order_id_urgent',
            'rus',
            {},
            False,
            0,
            100,
            [
                'грубый_водитель',
                'клиент_urgent',
                'подозрение_urgent',
                'use_client_tickets_routing_ml',
                'urgent_keywords_triggered',
                'lost_item_second_keywords_triggered',
                'need_response_before_ml',
            ],
        ),
        (
            'order_id_false_urgent',
            'rus',
            {},
            False,
            0,
            100,
            [
                'readonly',
                'грубый_водитель',
                'use_client_tickets_routing_ml',
                'urgent_keywords_triggered',
                'lost_item_second_keywords_triggered',
                'false_urgent'
            ],
        ),
        (
            'order_id_still_urgent',
            'rus',
            {},
            False,
            0,
            100,
            [
                'грубый_водитель',
                'клиент_urgent',
                'подозрение_urgent',
                'use_client_tickets_routing_ml',
                'urgent_keywords_triggered',
                'lost_item_second_keywords_triggered',
                'need_response_before_ml',
            ],
        ),
        (
            'order_id_urgent',
            'blr',
            {},
            True,
            0,
            100,
            [
                'readonly',
                'грубый_водитель',
                'business_client'
            ],
        ),
        (
            'order_id_bad_user_phone',
            'blr',
            {},
            True,
            0,
            0,
            [
                'readonly',
                'грубый_водитель',
            ],
        ),
        (
            'order_id_urgent',
            'rus',
            {},
            True,
            0,
            0,
            [
                'грубый_водитель',
                'клиент_urgent',
                'подозрение_urgent',
                'use_urgent_ml',
                'need_response_before_ml',
                'business_client'
            ],
        ),
        (
            'order_id_false_urgent',
            'rus',
            {},
            True,
            0,
            0,
            [
                'readonly',
                'грубый_водитель',
                'use_urgent_ml',
                'false_urgent',
                'business_client'
            ],
        ),
        (
            'order_id_still_urgent',
            'rus',
            {},
            True,
            0,
            0,
            [
                'грубый_водитель',
                'клиент_urgent',
                'подозрение_urgent',
                'use_urgent_ml',
                'need_response_before_ml',
                'business_client'
            ],
        ),
        (
            'order_id_elite',
            'blr',
            {},
            False,
            0,
            0,
            [
                'приятная_музыка',
                'elite',
                'disable_readonly',
                'need_response_before_ml',
                'мультизаказ_эксперимент',
            ],
        ),
        (
            'order_id_no_driver',
            'blr',
            {},
            True,
            0,
            0,
            [
                'readonly',
                'грубый_водитель',
                'business_client'
            ],
        ),
        (
            'order_by_corp_with_corp_payment',
            'blr',
            {},
            False,
            0,
            0,
            [
                'readonly',
                'Корпоративный_пользователь',
            ]
        ),
        (
            'order_by_corp_with_not_corp_payment',
            'blr',
            {},
            False,
            0,
            0,
            [
                'readonly',
            ]
        ),
        (
            'order_from_New_York',
            'rus',
            {},
            True,
            100,
            0,
            [
                'небезопасное_вождение',
                'yandex-team',
                'taxi-staff',
                'use_urgent_ml',
                'disable_readonly',
                'need_response_before_ml',
                'use_meta_from_support_info',
                'driver_tag_vip',
                'driver_tag_blogger',
            ],
        ),
    ]
)
@pytest.mark.translations(translations)
@pytest.inline_callbacks
@pytest.mark.filldb(_fill=True)
@pytest.mark.config(
    FEEDBACK_BADGES_MAPPING=feedback_badges_mapping,
    USE_FEEDBACK_API_FOR_ZENDESK_REPORT=True,
    FEEDBACK_COUNTRIES_ML_CHECK_URGENCY=['rus'],
    CHATTERBOX_DISABLE_READONLY_RULES=[
        {
            'percentage': 100,
            'feedback_report_conditions': True,
        },
        {
            'percentage': 100,
            'user_type': 'elite',
        },
        {
            'percentage': 100,
            'tariff': ['ultimate'],
        },
    ],
    FEEDBACK_FALSE_URGENT_WORDS=['мороз'],
    FEEDBACK_ALLOWED_DRIVER_TAGS=['vip', 'blogger', 'ultima'],
    FEEDBACK_ENABLE_ML_READONLY=True,
    FEEDBACK_READONLY_ML_LANGUAGES=['ru', ''],
)
def test_tags(feedback_retrieve_from_proc,
              passenger_feedback_retrieve_from_proc, order_id, user_country,
              experiments3, driver_tags_enabled, support_info_percentage,
              client_routing_percentage, tags, mock_get_urgency, mock_tags, mock_driver_tags,
              mock_get_readonly, mock_detect_language, zclient, areq_request):
    mock_detect_language('ru')

    @areq_request
    def request(method, url, **kwargs):
        if url.endswith('/client_tickets_routing/v1'):
            text = kwargs['json']['comment'].strip()
            response = {
                'ml_class_name': 'ml_class',
                'urgent_keywords_triggered': True,
                'lost_item_second_keywords_triggered': True,
                'probabilities': [0.0, 0.5, 1.0],
            }
            if text in ['морозно хорошо', 'ужасно морозно', 'ужасно']:
                response['predicted_class_name'] = 'urgent'
            else:
                response['predicted_class_name'] = 'other'
            return areq_request.response(
                200,
                body=json.dumps(response)
            )
        if url.endswith('v1/enrich_meta/'):
            return areq_request.response(
                200,
                body=json.dumps(
                    {
                        'metadata': {
                            'order_id': order_id,
                            'some': 'meta',
                        },
                        'status': 'ok',
                    },
                ),
            )
        if url.endswith('/v1/match'):
            return mock_tags(method, url, **kwargs)
        if url.endswith('/v1/drivers/match/profile'):
            return mock_driver_tags(method, url, **kwargs)
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))
        assert False, 'url ' + url + ' is not mocked'

    yield config.FEEDBACK_SUPPORT_INFO_META_PERCENTAGE.save(
        support_info_percentage,
    )
    yield config.FEEDBACK_EXTERNAL_TAGS_ENABLED.save(driver_tags_enabled)
    yield config.FEEDBACK_CLIENT_TICKETS_ROUTING_PERCENTAGE.save(
        client_routing_percentage,
    )
    ctx = feedback_report.FeedbackContext()
    ctx.order_id = order_id
    ctx.zclient = zclient
    ctx.zclient.id = 'yataxi'

    yield feedback_report.fetch_data_for_ride_feedback(ctx)

    for feedback in (ctx.order_proc.order.feedback, None):
        yield feedback_report.fetch_feedback(ctx, feedback=feedback)
        yield feedback_report.fetch_extended_info(ctx)
        ctx.user_type = yield feedback_report.get_user_type(
            order=ctx.order,
            order_proc=ctx.order_proc,
            user_phone_doc=ctx.user_phone_doc,
        )
        yield set_chatterbox_fields(ctx)
        # checking ml urgency in config.FEEDBACK_COUNTRIES_ML_CHECK_URGENCY
        ctx.user_country = user_country
        yield feedback_report.fetch_urgent_and_payment(ctx)

        _, readonly = (
            yield feedback_report._need_create_report(
                ctx, order_experiments=[],
            )
        )
        yield gather_ctx_data(ctx)

        ticket, _ = yield feedback_report._create_zendesk_ticket(
            ctx, user_experiments3=experiments3, ticket_readonly=readonly,
        )
        assert ticket['ticket']['tags'] == tags


@pytest.mark.parametrize(
    [
        'support_info_percentage',
        'support_info_status',
        'support_info_response',
        'expected_exception',
        'expected_chatterbox_fields',
        'expected_get_additional_meta',
    ],
    [
        (
            0,
            None,
            None,
            None,
            {
                'real_point_b': None,
                'order_pre_cost': 2500,
                'order_pre_distance': '25.000 км',
                'comment': 'feedback comment',
                'user_phone_id': 'user_phone_id_staff',
                'driver_id': 'park_driver',
                'driver_uuid': 'driver',
                'driver_name': '',
                'surge': '',
                'app_version': '3.83.0',
                'taximeter_version': '8.66',
                'payment_type': 'способ_оплаты_нал',
                'cancel_distance': '-',
                'user_locale': '',
                'waiting_cost': 0,
                'ticket_subject': 'Яндекс.Такси (new_york). '
                                  'Отзыв по заказу order_from_New_York.',
                'fixed_price': '',
                'clid': 'park',
                'park_db_id': 'dbid123',
                'park_name': 'park_name',
                'park_phone': '-',
                'points_b': '',
                'point_b_changed': False,
                'cancel_time': '-',
                'driver_phone': '+74997771122',
                'call_requested': False,
                'tariff': 'comfortplus',
                'rating': 3,
                'order_id': 'order_from_New_York',
                'order_time': '18:28',
                'order_due_time': 1438259309,
                'user_id': 'user_id_urgent',
                'calc_way': '',
                'waiting_time': '-',
                'car_number': 'AA111A77',
                'user_email': '',
                'driver_license': 'BLOGGER_LICENSE',
                'order_pre_time': '8 мин',
                'transactions': '',
                'order_cost': 4000,
                'order_distance': '0.000 км',
                'whats_wrong': 'Небезопасное вождение',
                'coupon': False,
                'point_a': '',
                'order_date': '30.07',
                'city': 'new_york',
                'waiting': 'Нет',
                'waiting_bool': False,
                'user_phone': '+7999999992',
                'user_platform': 'iphone',
                'coupon_used': False,
                'complete_rides': 0,
                'precomment': '',
                'order_currency': 'RUB',
                'language': None,
                'order_alias_id': 'order',
                'user_type': 'пользователь',
                'country': 'rus',
                'phone_type': 'yandex',
                'urgency_probability': '',
                'zendesk_profile': 'yataxi',
                'order_pre_time_raw': 500,
                'cancel_time_raw': None,
                'order_pre_distance_raw': 25000,
                'order_distance_raw': 0,
                'application_platform': None,
                'baby_seat_services': False,
                'cancel_distance_raw': 0,
                'cost_paid_supply': 0,
                'coupon_use_value': 0,
                'dif_ordercost_surge_surgecharge': 4000.0,
                'difference_fact_estimated_cost': 1500,
                'driver_late_time': 0,
                'driver_waiting_time': 0,
                'waiting_time_raw_minutes': 0,
                'final_ride_duration': 0,
                'final_transaction_status': 'hold_fail',
                'fixed_price_order_flg': False,
                'order_date_ymd': '2015-07-30',
                'order_pre_time_raw_minutes': 500 / 60.,
                'paid_supply': False,
                'success_order_flg': False,
                'surge_order_flg': False,
                'transportation_animals': False,
                'park_email': 'park@park.ru',
                'zone': '',
                'comment_language': 'ru',
            },
            None,
        ),
        (
            100,
            200,
            {
                'metadata': {
                    'order_id': 'order_from_New_York',
                    'country': 'blr',
                    'some': 'meta',
                    'user_id': 'user_id_urgent',
                },
                'status': 'ok',
            },
            None,
            {
                'ticket_subject': '\u042f\u043d\u0434\u0435\u043a\u0441.'
                                  '\u0422\u0430\u043a\u0441\u0438 (new_york). '
                                  '\u041e\u0442\u0437\u044b\u0432 '
                                  '\u043f\u043e \u0437\u0430\u043a\u0430'
                                  '\u0437\u0443 order_from_New_York.',
                'order_id': 'order_from_New_York',
                'country': 'blr',
                'some': 'meta',
                'call_requested': False,
                'comment': 'feedback comment',
                'language': None,
                'comment_language': 'ru',
                'rating': 3,
                'real_point_b': None,
                'urgency_probability': '',
                'user_email': '',
                'whats_wrong': 'Небезопасное вождение',
                'zendesk_profile': 'yataxi',
                'user_id': 'user_id_urgent',
            },
            {
                'headers': {},
                'json': {
                    'metadata': {
                        'order_id': 'order_from_New_York',
                        'country': 'rus',
                        'phone_type': 'yandex',
                        'user_phone': '+7999999992',
                        'driver_uuid': 'driver',
                        'user_id': 'user_id_urgent',
                    },
                    'suppress_conflict': True,
                },
                'log_extra': None,
            },
        ),
        (
            100,
            200,
            {
                'metadata': {},
                'status': 'no_data',
            },
            None,
            {
                'ticket_subject': '\u042f\u043d\u0434\u0435\u043a\u0441.'
                                  '\u0422\u0430\u043a\u0441\u0438 (new_york). '
                                  '\u041e\u0442\u0437\u044b\u0432 '
                                  '\u043f\u043e \u0437\u0430\u043a\u0430'
                                  '\u0437\u0443 order_from_New_York.',
                'order_id': 'order_from_New_York',
                'country': 'rus',
                'call_requested': False,
                'comment': 'feedback comment',
                'language': None,
                'comment_language': 'ru',
                'rating': 3,
                'real_point_b': None,
                'urgency_probability': '',
                'user_email': '',
                'whats_wrong': 'Небезопасное вождение',
                'zendesk_profile': 'yataxi',
                'phone_type': 'yandex',
                'user_phone': '+7999999992',
                'driver_uuid': 'driver',
                'user_id': 'user_id_urgent',
            },
            {
                'headers': {},
                'json': {
                    'metadata': {
                        'order_id': 'order_from_New_York',
                        'country': 'rus',
                        'phone_type': 'yandex',
                        'user_phone': '+7999999992',
                        'driver_uuid': 'driver',
                        'user_id': 'user_id_urgent',
                    },
                    'suppress_conflict': True,
                },
                'log_extra': None,
            },
        ),
        (
            100,
            400,
            {
                'metadata': {},
                'status': 'no_data',
            },
            support_info.SupportInfoBadRequestError,
            None,
            None,
        ),
    ],
)
@pytest.mark.translations(translations)
@pytest.inline_callbacks
@pytest.mark.filldb(_fill=True)
@pytest.mark.config(FEEDBACK_BADGES_MAPPING=feedback_badges_mapping)
@pytest.mark.no_mock_support_info_meta
def test_custom_fields(
        patch,
        areq_request,
        mock_driver_tags,
        support_info_percentage,
        support_info_status,
        support_info_response,
        expected_exception,
        expected_chatterbox_fields,
        expected_get_additional_meta,
        mock_detect_language
):
    mock_detect_language('ru')

    yield config.FEEDBACK_SUPPORT_INFO_META_PERCENTAGE.save(
        support_info_percentage,
    )

    @areq_request
    def request(method, url, **kwargs):
        if url.endswith('v1/enrich_meta/'):
            return areq_request.response(
                support_info_status,
                body=json.dumps(
                    support_info_response or {'status': 'ok', 'metadata': {}}
                )
            )
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))
        return mock_driver_tags(method, url, **kwargs)

    @patch('taxi.internal.driver_manager._set_brand_model')
    def _set_brand_model(brand, model, car_doc):
        car_doc['brand'] = brand
        car_doc['model'] = model

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    ctx = feedback_report.FeedbackContext()
    ctx.order_id = 'order_from_New_York'
    ctx.zclient = MockClient('yataxi')
    ctx.user_type = feedback_report.USER_TYPE_GENERAL

    if expected_exception is not None:
        with pytest.raises(expected_exception):
            yield gather_ctx_data(ctx)
        async.return_value()

    yield gather_ctx_data(ctx)

    _, readonly = yield feedback_report._need_create_report(
        ctx, order_experiments=[],
    )
    ticket, _ = yield feedback_report._create_zendesk_ticket(
        ctx, user_experiments3={}, ticket_readonly=readonly,
    )

    assert sorted(
        ticket['ticket']['custom_fields'], key=lambda field: field['id']
    ) == sorted([
        {u'id': 360000220925, u'value': u'feedback comment'},
        {u'id': 360000014145, u'value': 3},
        {u'id': 45318305, u'value': u''},
        {u'id': 360000217829, u'value': False},
        {u'id': 32670029, u'value': u'+7999999992'},
        {u'id': 27946649, u'value': u'пользователь'},
        {u'id': 360000012929, u'value': u'Небезопасное вождение'},
        {u'id': 360000220985, u'value': 2500},
        {u'id': 38797505, u'value': u'BLOGGER_LICENSE'},
        {u'id': 360000217809, u'value': 0},
        {u'id': 27279269, u'value': u'new_york'},
        {u'id': 360000217849, u'value': False},
        {u'id': 360000221025, u'value': u''},
        {u'id': 360000217909, u'value': u''},
        {u'id': 360000221005, u'value': u''},
        {u'id': 39674429, u'value': u'iphone'},
        {u'id': 45414685, u'value': u'Нет'},
        {u'id': 360000217769, u'value': u''},
        {u'id': 45249665, u'value': u'3.83.0'},
        {u'id': 360000220945, u'value': u'25.000 км'},
        {u'id': 360000015609, u'value': u'-'},
        {u'id': 34109165, u'value': '18:28'},
        {u'id': 360000220905, u'value': u''},
        {u'id': 38647729, u'value': u'order_from_New_York'},
        {u'id': 28015529, u'value': u'AA111A77'},
        {u'id': 360000353349, u'value': u''},
        {u'id': 360000015629, u'value': u'-'},
        {u'id': 360000220965, u'value': u'8 мин'},
        {u'id': 34109145, u'value': '30.07'},
        {u'id': 33990269, u'value': u'comfortplus'},
        {u'id': 360000217889, u'value': None},
        {u'id': 44183605, u'value': None},
        {u'id': 45234829, u'value': u'+74997771122'},
        {u'id': 360000217869, u'value': False},
        {u'id': 45557885, u'value': u'-'},
        {u'id': 43458949, u'value': 4000},
        {u'id': 35941509, u'value': 'способ_оплаты_нал'},
        {u'id': 35937589, u'value': False},
        {u'id': 360000217789, u'value': u'-'},
        {u'id': 45557125, u'value': u''},
        {u'id': 38859069, u'value': u'park@park.ru'},
    ], key=lambda field: field['id'])

    assert ctx.chatterbox_fields == expected_chatterbox_fields

    if not support_info_percentage:
        return

    if expected_get_additional_meta is None:
        assert not request.calls
    else:
        calls = request.calls
        call = [c['kwargs'] for c in calls
                if c['args'][1] == 'http://support-info.taxi.yandex.net/v1/enrich_meta/']
        assert call[0] == expected_get_additional_meta


@pytest.mark.parametrize(
    [
        'order_id',
        'support_info_response',
        'expected_chatterbox_fields',
    ],
    [
        (
            'order_for_extra_meta',
            {
                'metadata': {
                    'order_id': 'order_for_extra_meta',
                    'user_locale': 'ru',
                },
                'status': 'ok',
            },
            {
                'ticket_subject': '\u042f\u043d\u0434\u0435\u043a\u0441.'
                                  '\u0422\u0430\u043a\u0441\u0438 (new_york). '
                                  '\u041e\u0442\u0437\u044b\u0432 '
                                  '\u043f\u043e \u0437\u0430\u043a\u0430'
                                  '\u0437\u0443 order_for_extra_meta.',
                'order_id': 'order_for_extra_meta',
                'call_requested': False,
                'comment': 'feedback comment',
                'language': 'язык_русский',
                'user_locale': 'ru',
                'comment_language': 'ru',
                'rating': 3,
                'real_point_b': 'Москва, Льва Толстого 14',
                'urgency_probability': '',
                'user_email': 'email1',
                'whats_wrong': 'Небезопасное вождение',
                'zendesk_profile': 'yataxi',
            },
        )
    ]
)
@pytest.mark.translations(translations)
@pytest.inline_callbacks
@pytest.mark.filldb(_fill=True)
@pytest.mark.config(FEEDBACK_BADGES_MAPPING=feedback_badges_mapping)
@pytest.mark.no_mock_support_info_meta
def test_chatterbox_extra_fields(
        patch,
        areq_request,
        mock_driver_tags,
        order_id,
        support_info_response,
        expected_chatterbox_fields,
        mock_detect_language
):
    mock_detect_language('ru')

    yield config.FEEDBACK_SUPPORT_INFO_META_PERCENTAGE.save(100)

    @patch('taxi.internal.order_kit.positions_handler.get_destination_address')
    @async.inline_callbacks
    def get_destination(order_proc):
        yield async.return_value((
            '', '', order_proc.order.request.destinations[0].full_text, ''
        ))

    @patch('taxi.external.geotracks.get_driver_track')
    @async.inline_callbacks
    def get_geotrack(driver_id, db, start_time,
                     end_time, verbose, log_extra=None):
        yield async.return_value({'track': []})

    @patch('taxi.internal.driver_manager._set_brand_model')
    def _set_brand_model(brand, model, car_doc):
        car_doc['brand'] = brand
        car_doc['model'] = model

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    @areq_request
    def request(method, url, **kwargs):
        if url.endswith('v1/enrich_meta/'):
            return areq_request.response(
                200,
                body=json.dumps(support_info_response)
            )
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))
        return mock_driver_tags(method, url, **kwargs)

    ctx = feedback_report.FeedbackContext()
    ctx.order_id = order_id
    ctx.zclient = MockClient('yataxi')
    ctx.user_type = feedback_report.USER_TYPE_GENERAL

    yield gather_ctx_data(ctx)
    assert ctx.chatterbox_fields == expected_chatterbox_fields


@pytest.mark.parametrize(
    'order_id, feedback_type, message, message_hash,'
    'expected_experiments3_args',
    [
        (
            'order_id_1', 'after_ride', 'ругался матом',
            'a8595f7679ca0499feb221a68d755247e8605599',
            [
                {
                    'name': 'phone_id',
                    'type': 'string',
                    'value': 'user_phone_id',
                },
                {
                    'name': 'application',
                    'type': 'application',
                    'value': 'android',
                },
                {
                    'name': 'version',
                    'type': 'application_version',
                    'value': '7.0.1',
                },
                {
                    'name': 'country',
                    'type': 'string',
                },
            ],
        ),
        (
            'order_id_ml_not_readonly', 'after_ride', 'спасибо',
            '00f66d0ba9b2500ac35fc14bed3d439bcda82dcf',
            [
                {
                    'name': 'phone_id',
                    'type': 'string',
                    'value': 'user_phone_id',
                },
                {
                    'name': 'application',
                    'type': 'application',
                    'value': 'android',
                },
                {
                    'name': 'version',
                    'type': 'application_version',
                    'value': '7.0.1',
                },
                {
                    'name': 'country',
                    'type': 'string',
                },
            ],
        ),
        (
            'order_id_no_version', 'after_ride', 'ругался матом',
            'a8595f7679ca0499feb221a68d755247e8605599',
            None,
        ),
    ]
)
@pytest.mark.translations(translations)
@pytest.inline_callbacks
@pytest.mark.filldb(_fill=True)
@pytest.mark.config(FEEDBACK_ENABLE_CHECK_KEYWORDS=True)
@pytest.mark.config(
    FEEDBACK_BADGES_MAPPING=feedback_badges_mapping,
    FEEDBACK_EXTERNAL_TAGS_ENABLED=True,
    FEEDBACK_ENABLE_ML_READONLY=True,
    FEEDBACK_READONLY_ML_LANGUAGES=['ru', ''],
    CHATTERBOX_DISABLE_READONLY_RULES=[
        {
            'percentage': 100,
            'feedback_report_conditions': True
        },
    ],
)
@pytest.mark.asyncenv('async')
@pytest.mark.usefixtures('mock_get_urgency')
def test_feedback_report_chat_with_api(
        zclient, patch, areq_request, mock_tags, mock_driver_tags, mock_experiments3,
        mock_get_readonly, order_id, feedback_type, message, message_hash,
        expected_experiments3_args, mock_detect_language
):
    mock_detect_language('ru')

    order_proc = yield feedback_report.fetch_order_proc_doc(order_id)
    country = yield feedback_report.get_user_country(
        order_proc.order.nearest_zone
    )

    message_1_id = '{}_{}'.format(
        order_id, message_hash,
    )
    message_2_id = 'order_id_2_071018a55b820745e32fadb3a7a9b5e5bdd37ed2'
    message_3_id = 'order_id_2_4b9709cf0dddb6ab990e19862eff5315073a3d80'
    message_4_id = 'order_id_2_fa495f5ac822ee8fdb567bf300ccfc9685eff0d9'

    @patch('taxi.internal.experiment_manager.get_experiments')
    @patch('taxi.internal.experiment_manager.get_experiments_for_user')
    def get_experiments(doc1, doc2, log_extra=None):
        return ['user_chat', 'feedback_user_chat', 'use_support_chat_api']

    @patch('taxi.internal.user_manager.user_support_chat')
    def user_support_chat(*args, **kwargs):
        return True

    @patch('taxi.external.tvm.get_ticket')
    @async.inline_callbacks
    def get_ticket(src_service_name, dst_service_name, log_extra=None):
        assert src_service_name == 'stq'
        assert dst_service_name in ['support_chat', 'chatterbox', 'tags']
        yield async.return_value('test_ticket')

    @patch('taxi.internal.order_kit.positions_handler.get_destination_address')
    @async.inline_callbacks
    def get_destination(order_proc):
        yield async.return_value((
            '', '', order_proc.order.request.destinations[0].full_text, ''
        ))

    @patch('taxi.external.geotracks.get_driver_track')
    @async.inline_callbacks
    def get_geotrack(driver_id, db, start_time,
                     end_time, verbose, log_extra=None):
        yield async.return_value({'track': []})

    @areq_request
    def requests_request(method, url, **kwargs):
        if 'driver-tags.taxi.yandex.net' in url:
            return mock_driver_tags(method, url, **kwargs)
        if 'tags.taxi.yandex.net' in url:
            return mock_tags(method, url, **kwargs)
        assert method == 'POST'
        parsed_url = urlparse.urlparse(url)
        request = kwargs['json']
        if 'support-chat' in url:
            assert url.startswith('http://support-chat.taxi.yandex.net')
            if 'add_update' in url:
                chat_id = parsed_url.path.split('/')[3]
                assert request['update_metadata']['author_id'] == 'STUB_ID'
                assert request['update_metadata']['ticket_id'] == 1
                db.user_chat_messages._collection.update(
                    {
                        '_id': bson.ObjectId(chat_id)
                    },
                    {
                        '$set': {
                            'author_id': 'STUB_ID',
                            'ticket_id': 1
                        }
                    }
                )
                return areq_request.response(200, body=json.dumps({}))
            else:
                if request['request_id'] in message_1_id:
                    assert request['metadata']['user_locale'] == 'ru'
                    assert request['metadata']['user_country'] == 'kaz'
                    assert request['metadata']['tags'] == ['business_client']
                    assert (
                        request['message']['metadata']['order_id'] == order_id
                    )
                else:
                    assert request['metadata']['user_locale'] == ''
                    assert request['metadata']['user_country'] == ''
                    assert request['metadata']['tags'] == ['business_client']
                    assert request['message']['metadata']['order_id'] == 'order_id_2'
                assert request['owner']['platform'] == 'android'
                assert request['metadata']['user_application'] == 'android'
                assert request['message']['metadata']['source'] == 'report'
                assert request['message']['metadata']['driver_id'] == 'park_driver'
                assert request['message']['metadata']['driver_uuid'] == 'driver'
                assert request['message']['metadata']['park_db_id'] == 'dbid123'
                assert request['message']['metadata']['order_alias_id'] == 'order'
                chat_doc, _ = dbh.user_chat_messages.Doc.open_new_chat(
                    request['metadata']['user_id'],
                    request['owner']['id'],
                    request['request_id'],
                    request['message']['text'],
                    request['metadata']['user_locale']
                ).result
                result = {
                    'id': str(chat_doc.pk),
                    'metadata': {
                        'ticket_id': chat_doc.get('ticket_id'),
                        'author_id': chat_doc.get('author_id')
                    }
                }
                return areq_request.response(
                    200, body=json.dumps(result)
                )
        if 'chatterbox' in url:
            chatterbox_field_names = (
                'driver_id', 'order_id', 'order_alias_id', 'park_db_id',
                'user_id', 'user_phone', 'user_phone_id', 'park_phone',
            )
            assert url == 'http://chatterbox.taxi.yandex.net/v1/tasks'
            assert request['type'] == 'chat'
            assert 'metadata' in request
            meta = request['metadata']['update_meta']
            tags = request['metadata']['update_tags']
            meta_values = {}
            for item in meta:
                assert item['change_type'] == 'set'
                if item['field_name'] == 'zendesk_profile':
                    assert item['value'] == 'yataxi'
                if item['field_name'] in chatterbox_field_names:
                    meta_values[item['field_name']] = item['value']
            if meta_values['order_id'] == 'order_id_1':
                assert meta_values == {
                    'order_id': 'order_id_1',
                    'order_alias_id': 'order',
                    'driver_id': 'park_driver',
                    'park_db_id': 'dbid123',
                    'user_id': 'user_id',
                    'user_phone_id': 'user_phone_id',
                    'user_phone': '+79000000000'
                }
            elif meta_values['order_id'] == 'order_id_2':
                assert meta_values == {
                    'order_id': 'order_id_2',
                    'order_alias_id': 'order',
                    'driver_id': 'park_driver',
                    'park_db_id': 'dbid123',
                    'user_id': 'user_id',
                    'user_phone_id': 'user_phone_id',
                    'user_phone': '+79000000000'
                }
            tags_values = []
            for item in tags:
                assert item['change_type'] == 'add'
                tags_values.append(item['tag'])
            assert 'chat_draft' in tags_values
            assert not 'readonly' in tags_values
            assert 'chat' in tags_values
            result = {
                'id': 'chatterbox_id',
                'status': 'new'
            }
            return areq_request.response(200, body=json.dumps(result))
        if 'forms/fos' in url:
            assert method == 'POST'
            assert url == 'http://support-info.taxi.yandex.net/v1/forms/fos'
            return areq_request.response(200, body=json.dumps({}))
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))
        return result

    def check_chat(chat):
        assert 'ticket_id' not in chat
        assert 'author_id' not in chat

    @patch('taxi_stq._client.put')
    def put(queue=None, eta=None, task_id=None, args=None, kwargs=None):
        pass

    yield feedback_report.create_zendesk_ticket(
        order_id, feedback_type=feedback_type
    )

    chat = yield db.user_chat_messages.find_one({
        'user_phone_id': 'user_phone_id'
    })
    assert chat['messages'][-1]['id'] == message_1_id
    assert chat['messages'][-1]['message'] == message
    check_chat(chat)

    yield feedback_report.create_zendesk_ticket(
        order_id, feedback_type=feedback_type
    )
    check_chat(chat)

    yield feedback_report.create_zendesk_ticket(
        'order_id_2', feedback_type='ride'
    )

    chat = yield db.user_chat_messages.find_one({
        'user_phone_id': 'user_phone_id'
    })
    assert chat['messages'][-1]['id'] == message_2_id
    assert chat['messages'][-1]['message'] == 'ужасно'
    assert len(chat['messages']) == 2
    check_chat(chat)

    yield feedback_report.create_zendesk_ticket(
        'order_id_2', feedback_type='ride'
    )
    chat = yield db.user_chat_messages.find_one({
        'user_phone_id': 'user_phone_id'
    })
    assert chat['messages'][-1]['id'] == message_2_id
    assert chat['messages'][-1]['message'] == 'ужасно'
    assert len(chat['messages']) == 2
    check_chat(chat)

    feedback = {
        'msg': 'текст',
        'c': True
    }

    yield feedback_report.create_zendesk_ticket(
        'order_id_2', feedback=feedback, feedback_type='ride',
    )
    chat = yield db.user_chat_messages.find_one({
        'user_phone_id': 'user_phone_id'
    })
    assert chat['messages'][-1]['id'] == message_3_id
    assert chat['messages'][-1]['message'] == 'текст'
    assert len(chat['messages']) == 3

    feedback['choices'] = {
        'low_rating_reason': ['longwait']
    }

    yield feedback_report.create_zendesk_ticket(
        'order_id_2', feedback=feedback, feedback_type='ride',
    )
    chat = yield db.user_chat_messages.find_one({
        'user_phone_id': 'user_phone_id'
    })
    assert chat['messages'][-1]['id'] == message_3_id
    assert chat['messages'][-1]['message'] == 'текст'
    assert len(chat['messages']) == 3

    feedback = {
        'msg': 'новый текст',
        'c': True
    }

    yield feedback_report.create_zendesk_ticket(
        'order_id_2', feedback=feedback, feedback_type='ride',
    )
    chat = yield db.user_chat_messages.find_one({
        'user_phone_id': 'user_phone_id'
    })
    assert chat['messages'][-1]['id'] == message_4_id
    assert chat['messages'][-1]['message'] == 'новый текст'
    assert len(chat['messages']) == 4

    feedback['rating'] = 5

    yield feedback_report.create_zendesk_ticket(
        'order_id_2', feedback=feedback, feedback_type='ride',
    )

    chat = yield db.user_chat_messages.find_one({
        'user_phone_id': 'user_phone_id'
    })
    assert chat['messages'][-1]['id'] == message_4_id
    assert chat['messages'][-1]['message'] == 'новый текст'
    assert len(chat['messages']) == 4

    if expected_experiments3_args:
        experiments3_calls = mock_experiments3.calls
        assert experiments3_calls
        args = experiments3_calls[0]['args'][1]
        assert len(args) == len(expected_experiments3_args)
        for arg, expected_arg in zip(args, expected_experiments3_args):
            if expected_arg['name'] == 'country':
                expected_arg['value'] = country
            for key, value in expected_arg.items():
                assert getattr(arg, key) == value


@pytest.mark.parametrize(
    'order_id, expected_support_info_calls',
    [
        (
            'order_id_1',
            [
                {
                    'user_platform': 'android',
                    'user_phone': '+79000000000',
                    'message_text': 'test',
                    'request_id': 'order_id_1_'
                                  'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3',
                    'country': 'kaz',
                    'zone': 'astana',
                    'order_id': 'order_id_1',
                    'tags': ['non-call-center-tag'],
                },
                {
                    'user_platform': 'android',
                    'user_phone': '+79000000000',
                    'message_text': 'test',
                    'request_id': 'order_id_1_'
                                  'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3',
                    'country': 'kaz',
                    'zone': 'astana',
                    'order_id': 'order_id_1',
                    'tags': ['non-call-center-tag'],
                },
                {
                    'user_platform': 'android',
                    'user_phone': '+79000000000',
                    'message_text': 'test_1',
                    'request_id': 'order_id_1_'
                                  '5629ddd238a3e934cfa4af81e239ec8e73c58ace',
                    'country': 'kaz',
                    'zone': 'astana',
                    'order_id': 'order_id_1',
                    'tags': ['non-call-center-tag'],
                }
            ]
        ),
        (
            'order_id_urgent',
            [
                {
                    'user_platform': 'iphone',
                    'user_phone': '+7999999999',
                    'message_text': 'test',
                    'request_id': 'order_id_urgent_'
                                  'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3',
                    'country': 'rus',
                    'zone': 'moscow',
                    'order_id': 'order_id_urgent',
                    'tags': ['non-call-center-tag'],
                },
                {
                    'user_platform': 'iphone',
                    'user_phone': '+7999999999',
                    'message_text': 'test',
                    'request_id': 'order_id_urgent_'
                                  'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3',
                    'country': 'rus',
                    'zone': 'moscow',
                    'order_id': 'order_id_urgent',
                    'tags': ['non-call-center-tag'],
                },
                {
                    'user_platform': 'iphone',
                    'user_phone': '+7999999999',
                    'message_text': 'test_1',
                    'request_id': 'order_id_urgent_'
                                  '5629ddd238a3e934cfa4af81e239ec8e73c58ace',
                    'country': 'rus',
                    'zone': 'moscow',
                    'order_id': 'order_id_urgent',
                    'tags': ['non-call-center-tag'],
                }
            ]
        )
    ]
)
@pytest.mark.translations(translations)
@pytest.inline_callbacks
@pytest.mark.filldb(_fill=True)
@pytest.mark.config(
    FEEDBACK_ENABLE_CHECK_KEYWORDS=True,
    FEEDBACK_BADGES_MAPPING=feedback_badges_mapping,
    STARTRACK_READONLY_QUEUE_BY_PROFILE={
        'yutaxi': 'YUTAXIREADONLY',
        'yataxi': 'YATAXIREADONLY',
    },
    USER_CHAT_VERSION_SUPPORTED=[],
)
def test_feedback_report_sms_tickets(zclient, patch, monkeypatch, order_id,
                                     expected_support_info_calls,
                                     mock_get_urgency, mock_experiments3,
                                     areq_request):

    def get_experiments(doc1, doc2, log_extra=None):
        return []

    monkeypatch.setattr(
        experiment_manager,
        'get_experiments_for_user',
        get_experiments
    )

    monkeypatch.setattr(
        experiment_manager,
        'get_experiments',
        get_experiments
    )

    call_counter = 0

    @patch('taxi_stq._client.put')
    def put(queue=None, eta=None, task_id=None, args=None, kwargs=None):
        pass

    @patch('taxi.external.translate.detect_language')
    @async.inline_callbacks
    def detect_language(text, log_extra=None):
        assert text
        yield async.return_value('ru')

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))
        if 'driver-tags.taxi.yandex.net' in url:
            return mock_driver_tags(method, url, **kwargs)
        assert method == 'POST'
        assert url == 'http://support-info.taxi.yandex.net/v1/forms/fos'
        assert kwargs['json'] == expected_support_info_calls[call_counter]
        return areq_request.response(200, body=json.dumps({}))

    @patch('taxi.internal.order_kit.positions_handler.get_destination_address')
    @async.inline_callbacks
    def get_destination(order_proc):
        yield async.return_value((
            '', '', '', ''
        ))

    @patch('taxi.external.geotracks.get_driver_track')
    @async.inline_callbacks
    def get_geotrack(driver_id, db, start_time,
                     end_time, verbose, log_extra=None):
        yield async.return_value({'track': []})

    @patch('taxi.internal.driver_manager._set_brand_model')
    def _set_brand_model(brand, model, car_doc):
        car_doc['brand'] = brand
        car_doc['model'] = model

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    feedback = {
        'msg': 'test',
        'rating': 5,
        'c': True,
    }
    yield feedback_report.create_zendesk_ticket(
        order_id, feedback_type='after_ride', feedback=feedback
    )
    call_counter += 1
    assert not put.calls

    yield feedback_report.create_zendesk_ticket(
        order_id, feedback_type='after_ride', feedback=feedback
    )
    call_counter += 1
    assert not put.calls

    feedback = {
        'msg': 'test_1',
        'rating': 4,
        'choices': {
            'low_rating_reason': ['smellycar']
        },
        'c': True,
    }
    yield feedback_report.create_zendesk_ticket(
        order_id, feedback_type='after_ride', feedback=feedback
    )
    assert not put.calls

    assert mock_experiments3.calls


@pytest.mark.parametrize(
    'nearest_zone,expected_result',
    [
        (
            'moscow',
            'rus'
        ),
        (
            'abidjan',
            'civ',
        ),
        (
            'astana',
            'kaz',
        ),
        (
            '',
            None
        )
    ]
)
@pytest.inline_callbacks
@pytest.mark.filldb(_fill=True)
def test_feedback_report_get_user_country(nearest_zone, expected_result):
    result = yield feedback_report.get_user_country(nearest_zone)
    assert result == expected_result


@pytest.mark.parametrize(
    'user_id, expected_experiments3',
    [
        (
            'user_id',
            {'show_call_me_back_option': {'enabled': False}},
        ),
        (
            'user_id_no_version',
            {},
        ),
        (
            'user_id_no_app',
            {},
        ),
    ],
)
@pytest.inline_callbacks
def test_get_user_experiments3(mock_experiments3, user_id,
                               expected_experiments3):
    ctx = feedback_report.FeedbackContext()
    ctx.order_id = 'order_id'
    ctx.order = yield dbh.orders.Doc.find_one_by_id(ctx.order_id)
    ctx.order_proc = yield dbh.order_proc.Doc.find_one_by_id(ctx.order_id)
    ctx.user_doc = yield dbh.users.Doc.find_one_by_id(user_id)
    ctx.user_phone_doc = (
        yield dbh.user_phones.Doc.find_one_by_id('user_phone_id')
    )
    user_experiments3 = yield feedback_report._get_user_experiments3(ctx)
    assert user_experiments3 == expected_experiments3


@pytest.mark.parametrize(
    'order_id, user_country, language, expected_requests_count, rate,'
    'expected_is_readonly',
    [
        (
            'order_id_ultimate',
            'blr',
            'ru',
            0,
            4,
            True,
        ),
        (
            'order_id_ultimate',
            'blr',
            'ru',
            0,
            2,
            False,
        ),
        (
            'order_id_ultimate',
            'rus',
            'язык_анимешников',
            1,
            2,
            False,
        ),
        (
            'order_id_ultimate',
            'rus',
            'язык_анимешников',
            1,
            4,
            False,
        ),
    ]
)
@pytest.mark.translations(translations)
@pytest.inline_callbacks
@pytest.mark.filldb(_fill=True)
@pytest.mark.config(
    FEEDBACK_BADGES_MAPPING=feedback_badges_mapping,
    USE_FEEDBACK_API_FOR_ZENDESK_REPORT=True,
    FEEDBACK_COUNTRIES_ML_CHECK_URGENCY=['rus'],
    FEEDBACK_FALSE_URGENT_WORDS=['мороз'],
    FEEDBACK_ALLOWED_DRIVER_TAGS=['vip', 'blogger', 'ultima'],
    FEEDBACK_ENABLE_ML_READONLY=True,
    FEEDBACK_READONLY_ML_LANGUAGES=['язык_анимешников'],
)
def test_forbidden_language(feedback_retrieve_from_proc,
                            passenger_feedback_retrieve_from_proc, order_id,
                            user_country,
                            mock_get_urgency, mock_driver_tags,
                            expected_requests_count, rate, language, patch,
                            expected_is_readonly):

    @patch('taxi.external.pymlaas.client_tickets_read_only')
    @async.inline_callbacks
    def _client_tickets_read_only(*args, **kwargs):
        return True

    @patch('taxi.external.translate.detect_language')
    @async.inline_callbacks
    def detect_language(text, log_extra=None):
        assert text
        yield async.return_value(language)

    ctx = feedback_report.FeedbackContext()
    ctx.order_id = order_id
    ctx.zclient = zclient
    ctx.zclient.id = 'yataxi'

    yield feedback_report.fetch_data_for_ride_feedback(ctx)

    feedback = ctx.order_proc.order.feedback
    yield feedback_report.fetch_feedback(ctx, feedback=feedback)
    yield feedback_report.fetch_extended_info(ctx)
    ctx.user_type = yield feedback_report.get_user_type(
        order=ctx.order,
        order_proc=ctx.order_proc,
        user_phone_doc=ctx.user_phone_doc,
    )
    yield set_chatterbox_fields(ctx)
    # checking ml urgency in config.FEEDBACK_COUNTRIES_ML_CHECK_URGENCY
    ctx.user_country = user_country
    yield feedback_report.fetch_urgent_and_payment(ctx)

    _, readonly = (
        yield feedback_report._need_create_report(
            ctx, order_experiments=[],
        )
    )
    experiment3 = {
        feedback_report.SHOW_CALL_ME_BACK_OPTION: {'enabled': False}
    }
    yield gather_ctx_data(ctx)
    ctx.feedback._data['rating'] = rate
    ticket, ticket_readonly = yield feedback_report._create_zendesk_ticket(
        ctx, user_experiments3=experiment3, ticket_readonly=readonly,
    )
    assert ticket_readonly == expected_is_readonly
    assert len(_client_tickets_read_only.calls) == expected_requests_count


@pytest.mark.config(
    FEEDBACK_BADGES_MAPPING=feedback_badges_mapping,
    STARTRACK_READONLY_QUEUE_BY_PROFILE={
        'yataxi': 'YATAXIREADONLY',
        'yutaxi': 'YUTAXIREADONLY',
    },
)
@pytest.mark.translations(translations)
@pytest.mark.parametrize(
    'order_id,expected_stq_put',
    [
        (
            'order_id_1',
            {
                'args': (
                    'order_id_1_a94a8fe5ccb19ba61c4c0873d391e987982fbbd3',
                    'test',
                    ['readonly'],
                    {
                        'app_version': '7.0.1',
                        'application_platform': None,
                        'baby_seat_services': False,
                        'calc_way': 'fixed',
                        'call_requested': False,
                        'cancel_distance': '-',
                        'cancel_distance_raw': 0,
                        'cancel_time': '-',
                        'cancel_time_raw': None,
                        'car_number': '\u0410\u0410111\u041077',
                        'city': 'moscow',
                        'clid': 'park',
                        'comment': 'test',
                        'complete_rides': 0,
                        'cost_paid_supply': 0,
                        'country': 'kaz',
                        'coupon': False,
                        'coupon_use_value': 0,
                        'coupon_used': False,
                        'dif_ordercost_surge_surgecharge': 4000.0,
                        'difference_fact_estimated_cost': 7500,
                        'driver_id': 'park_driver',
                        'driver_late_time': 0.0,
                        'driver_license': '\u043f\u0440\u0430\u0432\u0430',
                        'driver_name': '',
                        'driver_phone': '-',
                        'driver_uuid': 'driver',
                        'driver_waiting_time': 0,
                        'final_ride_duration': 0.0,
                        'final_transaction_status': 'hold_fail',
                        'fixed_price': 500,
                        'fixed_price_order_flg': True,
                        'language': '\u044f\u0437\u044b\u043a_\u0440\u0443'
                                    '\u0441\u0441\u043a\u0438\u0439',
                        'order_alias_id': 'order',
                        'order_cost': 8000,
                        'order_currency': '\u0440\u0443\u0431',
                        'order_date': '30.07',
                        'order_date_ymd': '2015-07-30',
                        'order_distance': '0.000 \u043a\u043c',
                        'order_distance_raw': 0,
                        'order_due_time': 1438259309,
                        'order_id': 'order_id_1',
                        'order_pre_cost': 5000,
                        'order_pre_distance': '25.000 \u043a\u043c',
                        'order_pre_distance_raw': 25000,
                        'order_pre_time': '8 \u043c\u0438\u043d',
                        'order_pre_time_raw': 500,
                        'order_pre_time_raw_minutes': 8.333333333333334,
                        'order_time': '18:28',
                        'paid_cancel_tag': False,
                        'paid_supply': False,
                        'park_db_id': 'dbid123',
                        'park_email': 'park@park.ru',
                        'park_name': 'park_name',
                        'park_phone': '-',
                        'payment_type': '\u0441\u043f\u043e\u0441\u043e'
                                        '\u0431_\u043e\u043f\u043b\u0430'
                                        '\u0442\u044b_\u043d\u0430\u043b',
                        'phone_type': 'yandex',
                        'point_a': '',
                        'point_b_changed': False,
                        'points_b': 'address',
                        'precomment': 'text',
                        'rating': 5,
                        'real_point_b': None,
                        'success_order_flg': True,
                        'surge': 2,
                        'surge_order_flg': True,
                        'tariff': 'comfortplus',
                        'taximeter_version': '8.66',
                        'ticket_subject': '\u042f\u043d\u0434\u0435\u043a'
                                          '\u0441.\u0422\u0430\u043a\u0441'
                                          '\u0438 (moscow). \u041e\u0442'
                                          '\u0437\u044b\u0432 \u043f\u043e'
                                          ' \u0437\u0430\u043a\u0430\u0437'
                                          '\u0443 order_id_1.',
                        'transactions': '',
                        'transportation_animals': False,
                        'urgency_probability': '',
                        'user_email': '',
                        'user_id': 'user_id',
                        'user_locale': 'ru',
                        'user_phone': '+79000000000',
                        'user_phone_id': 'user_phone_id',
                        'user_platform': 'android',
                        'user_type': '\u043f\u043e\u043b\u044c\u0437\u043e'
                                     '\u0432\u0430\u0442\u0435\u043b\u044c',
                        'waiting': '\u0414\u0430',
                        'waiting_bool': True,
                        'waiting_cost': 0,
                        'waiting_time': '8 \u043c\u0438\u043d',
                        'waiting_time_raw_minutes': 8.333333333333334,
                        'whats_wrong': '-',
                        'zendesk_profile': 'yataxi',
                        'zone': 'astana',
                        'ml_request_id': UUID,
                    },
                ),
                'eta': None,
                'kwargs': {
                    'log_extra': {
                        'extdict': {'order_id': 'order_id_1'}
                    }
                },
                'queue': 'support_info_readonly_ticket',
                'task_id': u'order_id_1_'
                           u'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3',
            },
        ),
        (
            'order_from_Baku',
            {
                'task_id': u'order_from_Baku_'
                           u'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3',
                'queue': 'support_info_readonly_ticket',
                'args': (
                    'order_from_Baku_a94a8fe5ccb19ba61c4c0873d391e987982fbbd3',
                    'test',
                    [
                        'readonly',
                        'мультизаказ_эксперимент',
                    ],
                    {
                        'comment': 'test',
                        'rating': 5,
                        'fixed_price': '',
                        'taximeter_version': '',
                        'coupon': False,
                        'user_phone': '+7123456789',
                        'cancel_distance': '-',
                        'user_type': '\u043f\u043e\u043b\u044c\u0437\u043e'
                                     '\u0432\u0430\u0442\u0435\u043b\u044c',
                        'whats_wrong': '-',
                        'order_pre_cost': 2500,
                        'clid': '',
                        'driver_id': '',
                        'ticket_subject': '\u0422\u0430\u043a\u0441\u0438 '
                                          '(baku). \u041e\u0442\u0437\u044b'
                                          '\u0432 \u043f\u043e \u0437\u0430'
                                          '\u043a\u0430\u0437\u0443 '
                                          'order_from_Baku.',
                        'driver_license': '\u043f\u0440\u0430\u0432\u0430',
                        'waiting_cost': 0,
                        'order_currency': 'RUB',
                        'zendesk_profile': 'yutaxi',
                        'city': 'baku',
                        'user_id': 'user_id_urgent',
                        'waiting': '\u041d\u0435\u0442',
                        'waiting_bool': False,
                        'coupon_used': False,
                        'points_b': '',
                        'calc_way': '',
                        'point_a': '',
                        'user_platform': 'iphone',
                        'order_cost': 4000,
                        'precomment': '',
                        'order_alias_id': 'order',
                        'app_version': '3.83.0',
                        'order_pre_distance': '25.000 \u043a\u043c',
                        'payment_type': None,
                        'cancel_time': '-',
                        'order_distance': '0.000 \u043a\u043c',
                        'order_time': '18:28',
                        'transactions': '',
                        'order_id': 'order_from_Baku',
                        'park_db_id': '',
                        'point_b_changed': False,
                        'car_number': '\u0410\u0410111\u041077',
                        'order_distance_raw': 0,
                        'user_locale': '',
                        'urgency_probability': '',
                        'order_due_time': 1438259309,
                        'order_pre_distance_raw': 25000,
                        'order_pre_time': 0,
                        'order_date': '30.07',
                        'tariff': 'comfortplus',
                        'real_point_b': None,
                        'park_name': '',
                        'language': None,
                        'driver_phone': '-',
                        'country': 'aze',
                        'surge': '',
                        'driver_uuid': '',
                        'cancel_time_raw': None,
                        'park_phone': '-',
                        'driver_name': '',
                        'user_phone_id': 'user_phone_id_corp',
                        'call_requested': False,
                        'complete_rides': 0,
                        'phone_type': 'yandex',
                        'user_email': '',
                        'waiting_time': '-',
                        'application_platform': None,
                        'baby_seat_services': False,
                        'cancel_distance_raw': 0,
                        'coupon_use_value': 0,
                        'dif_ordercost_surge_surgecharge': 4000.0,
                        'difference_fact_estimated_cost': 1500,
                        'driver_waiting_time': 0,
                        'final_ride_duration': 0.0,
                        'final_transaction_status': 'hold_fail',
                        'fixed_price_order_flg': False,
                        'order_date_ymd': '2015-07-30',
                        'paid_supply': False,
                        'success_order_flg': False,
                        'surge_order_flg': False,
                        'transportation_animals': False,
                        'waiting_time_raw_minutes': 0.0,
                        'cost_paid_supply': 0,
                        'driver_late_time': 0.0,
                        'park_email': 'devnull@yandex.ru',
                        'zone': 'baku',
                        'ml_request_id': UUID,
                    },
                ),
                'kwargs': {
                    'log_extra': {
                        'extdict': {'order_id': 'order_from_Baku'}
                    },
                },
                'eta': None,
            }
        ),
    ],
)
@pytest.inline_callbacks
def test_readonly(zclient, patch, mock_experiments3, mock_uuid_uuid4,
                  order_id, expected_stq_put, areq_request):

    @patch('taxi_stq._client.put')
    def put(queue=None, eta=None, task_id=None, args=None, kwargs=None):
        pass

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    feedback = {
        'msg': 'test',
        'rating': 5
    }
    yield feedback_report.create_zendesk_ticket(
        order_id, feedback_type='after_ride', feedback=feedback
    )

    if expected_stq_put is not None:
        stq_put_call = put.calls[0]
        import pprint
        pprint.pprint(stq_put_call)
        assert expected_stq_put == stq_put_call
    report = yield db.feedback_reports.find_one({
        'order_id': order_id
    })
    assert report['status'] == 'commented'


@async.inline_callbacks
def gather_ctx_data(ctx):
    yield feedback_report.fetch_data_for_ride_feedback(ctx)
    yield feedback_report.fetch_feedback(ctx)
    yield feedback_report.fetch_extended_info(ctx)

    ctx.order_reason_captions = yield feedback_report.get_order_reason_captions(
        ctx.feedback, locale=feedback_report.TICKET_LOCALE,
    )
    ctx.user_type = yield feedback_report.get_user_type(
        order=ctx.order,
        order_proc=ctx.order_proc,
        user_phone_doc=ctx.user_phone_doc,
    )
    yield set_chatterbox_fields(ctx)


@async.inline_callbacks
def set_chatterbox_fields(ctx):
    """
    set chatterbox_fields in ctx

    it is required before running fetch_urgent_and_payment
    """
    ctx.report_kwargs = yield feedback_report.get_report_kwargs(ctx)
    ctx.custom_fields = yield feedback_report.get_custom_fields(
        ctx.zclient.id,
        user_type=ctx.user_type,
        report_kwargs=ctx.report_kwargs,
        is_from_feedback=True,
    )
    ctx.chatterbox_fields = yield feedback_report.get_chatterbox_fields(
        ctx, zendesk_id=ctx.zclient.id, is_from_feedback=True
    )
    subject, _ = yield feedback_report.get_ticket_comment(ctx)
    ctx.chatterbox_fields['ticket_subject'] = subject
    assert ctx.chatterbox_fields
