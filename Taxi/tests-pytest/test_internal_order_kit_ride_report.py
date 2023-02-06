# -*- coding: utf-8 -*-

import datetime
import json

import pytest

from taxi import config
from taxi.core import async
from taxi.external import experiments3
from taxi.internal import dbh
from taxi.internal.order_kit import const
from taxi.internal.order_kit import ride_report
from taxi.internal.email_sender import sticker
from taxi.internal.email_sender import stq_task

from cardstorage_mock import mock_cardstorage


@pytest.fixture(autouse=True)
def patch_corp_users(patch):
    @patch('taxi.external.corp_users.v2_users_get')
    def _mock_v2_users_get(user_id, log_extra=None, **kwargs):
        response = {
          "corp_user": {
            "id": "corp_user",
            "fullname": u"Корп Юзер"
          },
          "corp_user_2": {
            "id": "corp_user_2",
            "fullname": u"Корп Юзер"
          }
        }
        return response[user_id]


@pytest.fixture(autouse=True)
def patch_compare_ride_reports(patch):
    @patch('taxi_stq.client.compare_ride_report_messages_call')
    @async.inline_callbacks
    def compare_ride_report_messages_call(*args, **kwargs):
        yield


@pytest.fixture()
def patch_exp3_compare_ride_reports_enabled(patch):
    @patch('taxi.external.experiments3.get_values')
    @async.inline_callbacks
    def mock_exp3_get_values(*args, **kwargs):
        yield
        result = [
            experiments3.ExperimentsValue(
                name='compare_ride_reports_enabled',
                value={'enable': True},
            )
        ]
        async.return_value(result)


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
def patch_userapi_request_user_api_get_emails(patch):
    @patch('taxi.external.userapi.request_user_api_get_emails')
    @async.inline_callbacks
    def mock_request_user_api_get_emails(
            request,
            log_extra=None,
    ):
        user_emails = {
            'user_phone_1': {
                'personal_email_id': '1234',
                'confirmed': True,
                'confirmation_code': '1234',
            },
            'user_phone_2': {
                'personal_email_id': '5678',
                'confirmed': False,
                'confirmation_code': '5678',
            },
            'user_phone_3': {
                'personal_email_id': '9012',
                'confirmed': True,
                'confirmation_code': 'deadfood',
            },
            'personal_email_id_1': {
                'personal_email_id': 'personal_email_id_1',
                'confirmed': True,
                'confirmation_code': '1234',
            },
        }
        if request.get('phone_ids') is not None:
            phone_id = request['phone_ids'][0]

            if phone_id not in user_emails:
                yield async.return_value({'items': []})

            user_email = user_emails[phone_id]
            yield async.return_value({'items':
                [
                    {
                        'id': phone_id,
                        'phone_id': phone_id,
                        'confirmed': user_email['confirmed'],
                        'confirmation_code': user_email['confirmation_code'],
                        'personal_email_id': user_email['personal_email_id'],
                    },
                ],
            })
        elif request.get('personal_email_ids') is not None:
            personal_email_id = request['personal_email_ids'][0]
            if personal_email_id not in user_emails:
                yield async.return_value({'items': []})
            user_email = user_emails[personal_email_id]
            yield async.return_value({'items':
                [
                    {
                        'id': personal_email_id,
                        'confirmed': user_email['confirmed'],
                        'confirmation_code': user_email['confirmation_code'],
                        'personal_email_id': user_email['personal_email_id'],
                    },
                ],
            })


@pytest.fixture(autouse=True)
def patch_personal_retrieve(patch):
    @patch('taxi.external.personal.retrieve')
    @async.inline_callbacks
    def mock_personal(data_type, request_id, log_extra=None, **kwargs):
        emails = {
            '1234': 'sample@ya.ru',
            '5678': 'another@ya.ru',
            '9012': 'andanotherone@ya.ru',
            'personal_email_id_1': 'example1@ya.ru',
        }
        yield async.return_value(
            {
                'id': request_id,
                'email': emails[request_id],
            },
        )


@pytest.fixture(autouse=True)
def patch_personal_store(patch):
    @patch('taxi.external.personal.store')
    @async.inline_callbacks
    def mock_store(data_type, request_value, validate=True, log_extra=None):
        emails = {
            "taxi@yandex.ru": "personal_email_id_0",
            "corp@email.ru": "personal_email_id_1",
            "corp-2@email.ru": "personal_email_id_2",
        }
        yield async.return_value(
            {
                'id': emails[request_value],
                'email': request_value,
            },
        )


@pytest.inline_callbacks
def test_create_maps_urls():
    points = [(55, 44), (55, 44.1), (55, 44.2)]
    track = [(55, 44), (55.1, 44.1), (55, 44.1), (54.3, 44.1), (55, 44.2)]
    result = yield ride_report._create_maps_url_with_track(
        'yataxi', None, points, track,
    )
    expected = ('https://tc-tst.mobile.yandex.net/get-map/1.x/?lg=0&scale=1'
                '&pt=55.00000,44.00000,comma_solid_red~55.00000,44.10000,'
                'trackpoint~55.00000,44.20000,comma_solid_blue&l=map&'
                'cr=0&'
                'pl=c:3C3C3CFF,w:5,55,44,55.1,44.1,55,44.1,54.3,44.1,55,44.2&'
                'size=1320,440&bbox=55.00000,43.98334~55.00000,44.21666')
    assert result == expected


@pytest.inline_callbacks
@pytest.mark.config(
    MAPS_STYLES_BY_BRAND={
        '__default__': {'val': 'default', 'size': 'standard'},
        'yataxi': {'val': 'taxi', 'size': 'standard'},
        'yauber': {'val': 'uber', 'size': 'standard'},
    },
    RIDE_REPORT_MAP_PARAMS={
        'size': 'small',
    }
)
@pytest.mark.parametrize(
    'brand, expected',
    [
        ('unknown', {'val': 'default', 'size': 'small'}),
        ('yataxi', {'val': 'taxi', 'size': 'small'}),
        ('yauber', {'val': 'uber', 'size': 'small'}),
    ],
)
def test_get_map_params(brand, expected):
    map_params = yield ride_report.get_map_params(brand)
    assert map_params == expected


@pytest.inline_callbacks
def test_create_sizeless_maps_urls():
    points = [(55, 44), (55, 44.1), (55, 44.2)]
    track = [(55, 44), (55.1, 44.1), (55, 44.1), (54.3, 44.1), (55, 44.2)]
    result = yield ride_report._create_sizeless_maps_url(
        'yataxi', None, points, track)
    expected = ('https://tc-tst.mobile.yandex.net/get-map/1.x/'
                '?lg=0&scale=1&'
                'pt=55.00000,44.00000,comma_solid_red~55.00000,44.10000,'
                'trackpoint~55.00000,44.20000,comma_solid_blue&'
                'l=map&cr=0&'
                'pl=c:3C3C3CFF,w:5,55,44,55.1,44.1,55,44.1,54.3,44.1,55,44.2&'
                'bbox=54.23336,43.98334~55.16664,44.21666')
    assert result == expected


SEND_REPORT_CONFIGS = {
    'TEST_RIDE_REPORT_PARAMS_EXTENDED': {
        '__default__': {
            '__default__': {
                '__default__': {
                    'point_a': '',
                    'point_b': '',
                    'shadow': '',
                    'ruble': '',
                    'ruble_big': '',
                    'print_png': '',
                    'lightning': '',
                    'visa_card': '',
                    'arrow_png': '',
                },
                'uk': {
                    'ride_report_template': 'yandex_ride_report_overridden',
                },
            },
        },
        'yauber': {
            '__default__': {
                '__default__': {
                },
            },
        },
    },
    'RIDE_REPORT_PARAMS_EXTENDED': {
        '__default__': {
            '__default__': {
                '__default__': {
                    'confirmation_logo': (
                        'https://avatars.yandex.net'
                        '/get-bunker/9e3e50cf4aacee02339e7dc042787003614d70e5/'
                        'normal/9e3e50.png'
                    ),
                    'headers': {
                        'X-Yandex-Hint': 'label=SystMetkaSO:taxi'
                    },
                    'logo_url': (
                        'https://avatars.mds.yandex.net/'
                        'get-bunker/56833/'
                        '15417569036e4245365ff16829d5019ca7fd6304/orig'
                    ),
                    'logo_width': 154,
                    'scheme_url': (
                        'https://avatars.yandex.net/get-bunker/'
                        '4ab84a91647dceb293f96b81f67112bb959c86b8/'
                        'normal/4ab84a.png'
                    ),
                    'sender': 'Yandex.Taxi <no-reply@taxi.yandex.com>',
                    'from_name': 'Yandex.Taxi',
                    'from_email': 'no-reply@taxi.yandex.com',
                    'support_url': (
                        'https://yandex.ru/support/taxi/contact-us.html'
                    ),
                    'taxi_host': 'taxi.yandex.com',
                },
                'uk': {
                    'send_pdf': True,
                    'pdf_report_template': 'yandex_ride_report_pdf',
                    'pdf_attachment_name': 'payment_confirmation.pdf',
                    'receipt_mode': 'bill',
                },
                'ru': {
                    'logo_url': (
                        'https://avatars.mds.yandex.net/get-bunker/'
                        '56833/b75e7dd2f0cccd0b099e71839e5fd0ce755abac5/orig'
                    ),
                    'logo_width': 178,
                    'scheme_url': (
                        'https://avatars.yandex.net/get-bunker/'
                        '31664ffe4afcef6bc9996bbe1dea633bd73fc656/'
                        'normal/31664f.png'
                    ),
                    'sender': 'Яндекс.Такси <no-reply@taxi.yandex.ru>',
                    'from_name': 'Яндекс.Такси',
                    'from_email': 'no-reply@taxi.yandex.ru',
                    'taxi_host': 'taxi.yandex.ru',
                    'show_user_fullname': True,
                    'show_fare_with_vat_only': True,
                    'extended_uber_report': True,
                },
                'en': {
                },
            },
        },
        'yauber': {
            '__default__': {
                '__default__': {
                    'arrow_png': (
                        'https://avatars.mds.yandex.net/get-bunker/128809/'
                        'a023cc1566435200a0532a4bac6a63b8c25cb9bc/orig'
                    ),
                    'confirmation_logo': (
                        'https://avatars.mds.yandex.net/'
                        'get-bunker/998550/41023f8711cc42f7e350e5ca8fb1b2c6/'
                        'orig'
                    ),
                    'headers': {
                      'X-Yandex-Hint': 'label=SystMetkaSO:taxi'
                    },
                    'lightning': (
                        'https://avatars.mds.yandex.net/get-bunker/'
                        '135516/8f10592b24260f3b3b4fa7ddd66061b711190e32/orig'
                    ),
                    'logo_url': (
                        'https://avatars.mds.yandex.net/get-bunker/'
                        '998550/c2102c61126c64fb1ca1453335e0776ecfee32fb/orig'
                    ),
                    'logo_width': 100,
                    'point_a': (
                        'https://avatars.mds.yandex.net/get-bunker/'
                        '994123/da9297f4801951a4e5cb7afd2f2c31cabf92122a/orig'
                    ),
                    'point_b': (
                        'https://avatars.mds.yandex.net/get-bunker/'
                        '994123/e6b877a34096bb0a882c741f210c772ae03bda32/orig'
                    ),
                    'print_png': (
                        'https://avatars.mds.yandex.net/get-bunker/'
                        '118781/af63937c4f091feb00d07adc0d539a5df2659023/orig'
                    ),
                    'ruble': (
                        'https://avatars.mds.yandex.net/get-bunker/'
                        '50064/5bfe8f003dcd99938a7149327cff74c49b58957f/orig'
                    ),
                    'ruble_big': (
                        'https://avatars.mds.yandex.net/get-bunker/'
                        '60661/dfc51446c2e6bc0da87cac1f7c037237215f8381/orig'
                    ),
                    'scheme_url': (
                        'https://avatars.yandex.net/get-bunker/'
                        '4ab84a91647dceb293f96b81f67112bb959c86b8/'
                        'normal/4ab84a.png'
                    ),
                    'sender': 'Uber <no-reply@support-uber.com>',
                    'from_name': 'Uber',
                    'from_email': 'no-reply@support-uber.com',
                    'shadow': (
                        'https://avatars.mds.yandex.net/get-bunker/'
                        '56833/70b8558e46b44d61151d068c01aba81e8b3143c4/orig'
                    ),
                    'support_url': 'https://support-uber.com/support',
                    'taxi_host': 'support-uber.com',
                    'visa_card': (
                        'https://avatars.mds.yandex.net/get-bunker/'
                        '49769/fae67159297c3d12777e74e47237967aab10a1b4/orig'
                    ),
                    'show_fare_with_vat_only': True,
                },
                'ru': {
                    'show_fare_with_vat_only': True,
                },
            },
        },
    },
}
SEND_REPORT_TRANSLATIONS = [
    ('color', 'red', 'de', u'красный'),
    ('color', 'red', 'en', u'red'),
    ('color', 'red', 'ru', u'красный'),
    ('color', 'red', 'uk', u'красный'),
    ('color', u'C49648', 'ru', u'желтый'),
    ('color', u'C49648', 'uk', u'желтый'),
    (
        'notify', 'helpers.humanized_date_fmt', 'de',
        u'%(day)d %(month)s %(year)04d г.',
    ),
    (
        'notify', 'helpers.humanized_date_fmt', 'en',
        u'%(day)d %(month)s, %(year)04d',
    ),
    (
        'notify', 'helpers.humanized_date_fmt', 'ru',
        u'%(day)d %(month)s %(year)04d г.',
    ),
    (
        'notify', 'helpers.humanized_date_fmt', 'uk',
        u'%(day)d %(month)s %(year)04d г.',
    ),
    ('notify', 'helpers.month_1_part', 'ru', u'января'),
    ('notify', 'helpers.month_6_part', 'de', u'июня'),
    ('notify', 'helpers.month_6_part', 'en', u'June'),
    ('notify', 'helpers.month_6_part', 'ru', u'июня'),
    ('notify', 'helpers.month_6_part', 'uk', u'июня'),
    ('notify', 'helpers.month_8_part', 'ru', u'августа'),
    ('notify', 'helpers.month_8_part', 'uk', u'августа'),
    (
        'notify', 'report.unknown_destination', 'ru',
        u'Остановка по требованию пользователя',
    ),
    ('notify', 'ride_report.body.footer', 'en', ''),
    ('notify', 'ride_report.body.footer', 'ru', ''),
    ('notify', 'ride_report.body.footer', 'uk', ''),
    ('notify', 'ride_report.body.hello', 'en', u'Hello'),
    ('notify', 'ride_report.body.hello', 'ru', u'Привет'),
    ('notify', 'ride_report.body.hello', 'uk', u'Привет'),
    ('notify', 'ride_report.body.trip_info', 'en', ''),
    ('notify', 'ride_report.body.trip_info', 'ru', ''),
    ('notify', 'ride_report.body.trip_info', 'uk', ''),
    ('notify', 'ride_report.html_body.about_support', 'en', ''),
    ('notify', 'ride_report.html_body.about_support', 'ru', ''),
    ('notify', 'ride_report.html_body.about_support', 'uk', ''),
    ('notify', 'ride_report.html_body.bill_title', 'en', u'Квитанция'),
    ('notify', 'ride_report.html_body.bill_title', 'ru', u'Квитанция'),
    ('notify', 'ride_report.html_body.bill_title', 'uk', u'Квитанция'),
    ('notify', 'ride_report.html_body.carrier_title', 'en', u'Перевозчик'),
    ('notify', 'ride_report.html_body.carrier_title', 'ru', u'Перевозчик'),
    ('notify', 'ride_report.html_body.carrier_title', 'uk', u'Перевозчик'),
    ('notify', 'ride_report.html_body.card_payment_phrase', 'en', u'Карта'),
    ('notify', 'ride_report.html_body.card_payment_phrase', 'ru', u'Карта'),
    ('notify', 'ride_report.html_body.card_payment_phrase', 'uk', u'Карта'),
    ('notify', 'ride_report.html_body.cash_payment_phrase', 'en', u'Наличные'),
    ('notify', 'ride_report.html_body.cash_payment_phrase', 'ru', u'Наличные'),
    ('notify', 'ride_report.html_body.cash_payment_phrase', 'uk', u'Наличные'),
    (
        'notify', 'ride_report.html_body.corp_payment_phrase', 'en',
        u'Корпоративный счет',
    ),
    (
        'notify', 'ride_report.html_body.corp_payment_phrase', 'ru',
        u'Корпоративный счет',
    ),
    (
        'notify', 'ride_report.html_body.corp_payment_phrase', 'uk',
        u'Корпоративный счет',
    ),
    ('notify', 'ride_report.html_body.date_title', 'en', u'Дата'),
    ('notify', 'ride_report.html_body.date_title', 'ru', u'Дата'),
    ('notify', 'ride_report.html_body.date_title', 'uk', u'Дата'),
    ('notify', 'ride_report.html_body.details_title', 'en', u'Детали'),
    ('notify', 'ride_report.html_body.details_title', 'ru', u'Детали'),
    ('notify', 'ride_report.html_body.details_title', 'uk', u'Детали'),
    (
        'notify', 'ride_report.html_body.dst_changed', 'en',
        u'Точка назначения изменена',
    ),
    (
        'notify', 'ride_report.html_body.dst_changed', 'ru',
        u'Точка назначения изменена',
    ),
    (
        'notify', 'ride_report.html_body.dst_changed', 'uk',
        u'Точка назначения изменена',
    ),
    ('notify', 'ride_report.html_body.duration', 'en', ''),
    ('notify', 'ride_report.html_body.duration', 'ru', ''),
    ('notify', 'ride_report.html_body.duration', 'uk', ''),
    ('notify', 'ride_report.html_body.fare', 'en', ''),
    ('notify', 'ride_report.html_body.fare', 'ru', ''),
    ('notify', 'ride_report.html_body.fare', 'uk', ''),
    ('notify', 'ride_report.html_body.fare_title', 'en', u'Общая стоимость'),
    ('notify', 'ride_report.html_body.fare_title', 'ru', u'Общая стоимость'),
    ('notify', 'ride_report.html_body.fare_title', 'uk', u'Общая стоимость'),
    ('notify', 'ride_report.html_body.fare_type', 'en', ''),
    ('notify', 'ride_report.html_body.fare_type', 'ru', ''),
    ('notify', 'ride_report.html_body.fare_type', 'uk', ''),
    ('notify', 'ride_report.html_body.legal_address_title', 'en', u'Юр. адрес'),
    ('notify', 'ride_report.html_body.legal_address_title', 'ru', u'Юр. адрес'),
    ('notify', 'ride_report.html_body.legal_address_title', 'uk', u'Юр. адрес'),
    ('notify', 'ride_report.html_body.logo_title', 'en', ''),
    ('notify', 'ride_report.html_body.logo_title', 'ru', ''),
    ('notify', 'ride_report.html_body.logo_title', 'uk', ''),
    ('notify', 'ride_report.html_body.name_title', 'en', u'Имя'),
    ('notify', 'ride_report.html_body.name_title', 'ru', u'Имя'),
    ('notify', 'ride_report.html_body.name_title', 'uk', u'Имя'),
    (
        'notify', 'ride_report.html_body.ogrn_title', 'en',
        u'Свидетельство регистрации парка',
    ),
    (
        'notify', 'ride_report.html_body.ogrn_title', 'ru',
        u'Свидетельство регистрации парка',
    ),
    (
        'notify', 'ride_report.html_body.ogrn_title', 'uk',
        u'Свидетельство регистрации парка',
    ),
    (
        'notify', 'ride_report.html_body.order_number_title', 'en',
        u'Номер заказа',
    ),
    (
        'notify', 'ride_report.html_body.order_number_title', 'ru',
        u'Номер заказа',
    ),
    (
        'notify', 'ride_report.html_body.order_number_title', 'uk',
        u'Номер заказа',
    ),
    ('notify', 'ride_report.html_body.passenger', 'en', ''),
    ('notify', 'ride_report.html_body.passenger', 'ru', ''),
    ('notify', 'ride_report.html_body.passenger', 'uk', ''),
    (
        'notify', 'ride_report.html_body.payment_method_title', 'en',
        u'Способ оплаты',
    ),
    (
        'notify', 'ride_report.html_body.payment_method_title', 'ru',
        u'Способ оплаты',
    ),
    (
        'notify', 'ride_report.html_body.payment_method_title', 'uk',
        u'Способ оплаты',
    ),
    ('notify', 'ride_report.html_body.payment_phrase', 'en', ''),
    ('notify', 'ride_report.html_body.payment_phrase', 'ru', ''),
    ('notify', 'ride_report.html_body.payment_phrase', 'uk', ''),
    ('notify', 'ride_report.html_body.payment_title', 'en', u'Оплата'),
    ('notify', 'ride_report.html_body.payment_title', 'ru', u'Оплата'),
    ('notify', 'ride_report.html_body.payment_title', 'uk', u'Оплата'),
    ('notify', 'ride_report.html_body.phone_title', 'en', u'Телефон'),
    ('notify', 'ride_report.html_body.phone_title', 'ru', u'Телефон'),
    ('notify', 'ride_report.html_body.phone_title', 'uk', u'Телефон'),
    ('notify', 'ride_report.html_body.receipt_title', 'en', u'Чек поездки'),
    ('notify', 'ride_report.html_body.receipt_title', 'ru', u'Чек поездки'),
    ('notify', 'ride_report.html_body.receipt_title', 'uk', u'Чек поездки'),
    ('notify', 'ride_report.html_body.ride_receipt', 'en', ''),
    ('notify', 'ride_report.html_body.ride_receipt', 'uk', ''),
    ('notify', 'ride_report.html_body.ride_receipt', 'ru', ''),
    ('notify', 'ride_report.html_body.ride_title', 'en', u'Поездка'),
    ('notify', 'ride_report.html_body.ride_title', 'ru', u'Поездка'),
    ('notify', 'ride_report.html_body.ride_title', 'uk', u'Поездка'),
    ('notify', 'ride_report.html_body.route_title', 'en', u'Маршрут'),
    ('notify', 'ride_report.html_body.route_title', 'ru', u'Маршрут'),
    ('notify', 'ride_report.html_body.route_title', 'uk', u'Маршрут'),
    ('notify', 'ride_report.html_body.scheme_title', 'en', ''),
    ('notify', 'ride_report.html_body.scheme_title', 'ru', ''),
    ('notify', 'ride_report.html_body.scheme_title', 'uk', ''),
    ('notify', 'ride_report.html_body.support_phrase', 'en', ''),
    ('notify', 'ride_report.html_body.support_phrase', 'ru', ''),
    ('notify', 'ride_report.html_body.support_phrase', 'uk', ''),
    ('notify', 'ride_report.html_body.support_title', 'en', u'Техподдержка'),
    ('notify', 'ride_report.html_body.support_title', 'ru', u'Техподдержка'),
    ('notify', 'ride_report.html_body.support_title', 'uk', u'Техподдержка'),
    ('notify', 'ride_report.html_body.taxi_ordered_corp', 'en', ''),
    ('notify', 'ride_report.html_body.taxi_ordered_corp', 'ru', ''),
    ('notify', 'ride_report.html_body.taxi_ordered_corp', 'uk', ''),
    ('notify', 'ride_report.html_body.taxi_ordered_personal', 'en', ''),
    ('notify', 'ride_report.html_body.taxi_ordered_personal', 'ru', ''),
    ('notify', 'ride_report.html_body.taxi_ordered_personal', 'uk', ''),
    ('notify', 'ride_report.html_body.text_before_scheme_corp', 'en', ''),
    ('notify', 'ride_report.html_body.text_before_scheme_corp', 'uk', ''),
    ('notify', 'ride_report.html_body.text_before_scheme_corp', 'ru', ''),
    ('notify', 'ride_report.html_body.text_before_scheme_personal', 'en', ''),
    ('notify', 'ride_report.html_body.text_before_scheme_personal', 'ru', ''),
    ('notify', 'ride_report.html_body.text_before_scheme_personal', 'uk', ''),
    ('notify', 'ride_report.html_body.th_car', 'en', ''),
    ('notify', 'ride_report.html_body.th_car', 'ru', ''),
    ('notify', 'ride_report.html_body.th_car', 'uk', ''),
    ('notify', 'ride_report.html_body.th_driver', 'en', ''),
    ('notify', 'ride_report.html_body.th_driver', 'ru', ''),
    ('notify', 'ride_report.html_body.th_driver', 'uk', ''),
    ('notify', 'ride_report.html_body.th_park', 'en', ''),
    ('notify', 'ride_report.html_body.th_park', 'ru', ''),
    ('notify', 'ride_report.html_body.th_park', 'uk', ''),
    ('notify', 'ride_report.html_body.tips_title', 'en', u'Чаевые'),
    ('notify', 'ride_report.html_body.tips_title', 'ru', u'Чаевые'),
    ('notify', 'ride_report.html_body.tips_title', 'uk', u'Чаевые'),
    ('notify', 'ride_report.html_body.title', 'en', ''),
    ('notify', 'ride_report.html_body.title', 'ru', ''),
    ('notify', 'ride_report.html_body.title', 'uk', ''),
    ('notify', 'ride_report.html_body.total_fare_cost', 'en', ''),
    ('notify', 'ride_report.html_body.total_fare_cost', 'ru', ''),
    ('notify', 'ride_report.html_body.total_fare_cost', 'uk', ''),
    ('notify', 'ride_report.html_body.unp_title', 'en', u'УНП'),
    ('notify', 'ride_report.html_body.unp_title', 'ru', u'УНП'),
    ('notify', 'ride_report.html_body.unp_title', 'uk', u'УНП'),
    ('notify', 'ride_report.html_body.unsubscribe_text', 'en', ''),
    ('notify', 'ride_report.html_body.unsubscribe_text', 'ru', ''),
    ('notify', 'ride_report.html_body.unsubscribe_text', 'uk', ''),
    ('notify', 'ride_report.html_body.vat_title', 'en', ''),
    ('notify', 'ride_report.html_body.vat_title', 'ru', ''),
    ('notify', 'ride_report.html_body.vat_title', 'uk', ''),
    ('notify', 'ride_report.html_body.yandex_taxi_team', 'en', ''),
    ('notify', 'ride_report.html_body.yandex_taxi_team', 'ru', ''),
    ('notify', 'ride_report.html_body.yandex_taxi_team', 'uk', ''),
    ('notify', 'ride_report.html_body.invoice', 'en', ''),
    ('notify', 'ride_report.html_body.invoice', 'ru', ''),
    ('notify', 'ride_report.html_body.invoice', 'uk', ''),
    ('notify', 'ride_report.html_body.invoice_isr', 'en', ''),
    ('notify', 'ride_report.html_body.invoice_isr', 'ru', ''),
    ('notify', 'ride_report.html_body.invoice_isr', 'uk', ''),
    ('notify', 'ride_report.html_body.payment_method_title', 'en', ''),
    ('notify', 'ride_report.html_body.payment_method_title', 'ru', ''),
    ('notify', 'ride_report.html_body.payment_method_title', 'uk', ''),
    ('notify', 'ride_report.html_body.order_num', 'en', ''),
    ('notify', 'ride_report.html_body.order_num', 'ru', ''),
    ('notify', 'ride_report.html_body.order_num', 'uk', ''),
    ('notify', 'ride_report.html_body.price_title', 'en', ''),
    ('notify', 'ride_report.html_body.price_title', 'ru', ''),
    ('notify', 'ride_report.html_body.price_title', 'uk', ''),
    ('notify', 'ride_report.html_body.legal_isr', 'en', ''),
    ('notify', 'ride_report.html_body.legal_isr', 'ru', ''),
    ('notify', 'ride_report.html_body.legal_isr', 'uk', ''),
    ('notify', 'ride_report.html_body.company_name', 'en', ''),
    ('notify', 'ride_report.html_body.company_name', 'ru', ''),
    ('notify', 'ride_report.html_body.company_name', 'uk', ''),
    ('notify', 'ride_report.html_body.company_name_isr', 'en', ''),
    ('notify', 'ride_report.html_body.company_name_isr', 'ru', ''),
    ('notify', 'ride_report.html_body.company_name_isr', 'uk', ''),
    ('notify', 'ride_report.html_body.company_name_fin', 'en', ''),
    ('notify', 'ride_report.html_body.company_name_fin', 'ru', ''),
    ('notify', 'ride_report.html_body.company_name_fin', 'uk', ''),
    ('notify', 'ride_report.html_body.recipient_title', 'en', ''),
    ('notify', 'ride_report.html_body.recipient_title', 'ru', ''),
    ('notify', 'ride_report.html_body.recipient_title', 'uk', ''),
    ('notify', 'ride_report.html_body.user_fullname_title', 'en', u'ФИО пассажира'),
    ('notify', 'ride_report.html_body.user_fullname_title', 'ru', u'ФИО пассажира'),
    ('notify', 'ride_report.html_body.user_fullname_title', 'uk', u'ФИО пассажира'),
    ('notify', 'ride_report.html_body.user_fullname_stub', 'en', u'Пользователь не предоставил данные'),
    ('notify', 'ride_report.html_body.user_fullname_stub', 'ru', u'Пользователь не предоставил данные'),
    ('notify', 'ride_report.html_body.user_fullname_stub', 'uk', u'Пользователь не предоставил данные'),
    ('notify', 'ride_report.html_body.ride_cost_title', 'en', u'Стоимость поездки'),
    ('notify', 'ride_report.html_body.ride_cost_title', 'ru', u'Стоимость поездки'),
    ('notify', 'ride_report.html_body.ride_cost_title', 'uk', u'Стоимость поездки'),
    ('notify', 'ride_report.html_body.tax_hint_title', 'en', u'(вкл.прим.налоги)'),
    ('notify', 'ride_report.html_body.tax_hint_title', 'ru', u'(вкл.прим.налоги)'),
    ('notify', 'ride_report.html_body.tax_hint_title', 'uk', u'(вкл.прим.налоги)'),
    ('notify', 'ride_report.html_body.extra_invoice_title', 'en',
     u'electronic report on transportation of the passenger'),
    ('notify', 'ride_report.html_body.extra_invoice_title', 'ru',
     u'electronic report on transportation of the passenger'),
    ('notify', 'ride_report.html_body.extra_invoice_title', 'uk',
     u'electronic report on transportation of the passenger'),
    ('notify', 'ride_report.html_body.extra_invoice_doc_number', 'en', u'reg #'),
    ('notify', 'ride_report.html_body.extra_invoice_doc_number', 'ru', u'reg #'),
    ('notify', 'ride_report.html_body.extra_invoice_doc_number', 'uk', u'reg #'),
    ('notify', 'ride_report.html_body.extra_invoice_recipient', 'en', u'адресат:'),
    ('notify', 'ride_report.html_body.extra_invoice_recipient', 'ru', u'адресат:'),
    ('notify', 'ride_report.html_body.extra_invoice_recipient', 'uk', u'адресат:'),
    ('notify', 'ride_report.html_body.extra_invoice_partner_company', 'en', u'partner company'),
    ('notify', 'ride_report.html_body.extra_invoice_partner_company', 'ru', u'partner company'),
    ('notify', 'ride_report.html_body.extra_invoice_partner_company', 'uk', u'partner company'),
    ('notify', 'ride_report.html_body.extra_invoice_transporter_company', 'en', u'transporter company'),
    ('notify', 'ride_report.html_body.extra_invoice_transporter_company', 'ru', u'transporter company'),
    ('notify', 'ride_report.html_body.extra_invoice_transporter_company', 'uk', u'transporter company'),
    ('notify', 'ride_report.html_body.extra_invoice_driver_info_title', 'en', u'Информация о водителе'),
    ('notify', 'ride_report.html_body.extra_invoice_driver_info_title', 'ru', u'Информация о водителе'),
    ('notify', 'ride_report.html_body.extra_invoice_driver_info_title', 'uk', u'Информация о водителе'),
    ('notify', 'ride_report.html_body.extra_invoice_driver_name', 'en', u'Водитель'),
    ('notify', 'ride_report.html_body.extra_invoice_driver_name', 'ru', u'Водитель'),
    ('notify', 'ride_report.html_body.extra_invoice_driver_name', 'uk', u'Водитель'),
    ('notify', 'ride_report.html_body.extra_invoice_driver_license', 'en', u'Номер лицензии водителя'),
    ('notify', 'ride_report.html_body.extra_invoice_driver_license', 'ru', u'Номер лицензии водителя'),
    ('notify', 'ride_report.html_body.extra_invoice_driver_license', 'uk', u'Номер лицензии водителя'),
    ('notify', 'ride_report.html_body.extra_invoice_car_number', 'en', u'Номер автомобиля'),
    ('notify', 'ride_report.html_body.extra_invoice_car_number', 'ru', u'Номер автомобиля'),
    ('notify', 'ride_report.html_body.extra_invoice_car_number', 'uk', u'Номер автомобиля'),
    ('notify', 'ride_report.html_body.car_permit_number_title', 'en', u'Лицензия перевозчика'),
    ('notify', 'ride_report.html_body.car_permit_number_title', 'ru', u'Лицензия перевозчика'),
    ('notify', 'ride_report.html_body.car_permit_number_title', 'uk', u'Лицензия перевозчика'),
    ('notify', 'ride_report.html_body.extra_invoice_ride_info_title', 'en', u'Информация о поездке'),
    ('notify', 'ride_report.html_body.extra_invoice_ride_info_title', 'ru', u'Информация о поездке'),
    ('notify', 'ride_report.html_body.extra_invoice_ride_info_title', 'uk', u'Информация о поездке'),
    ('notify', 'ride_report.html_body.extra_invoice_departure_address', 'en', u'Точка А'),
    ('notify', 'ride_report.html_body.extra_invoice_departure_address', 'ru', u'Точка А'),
    ('notify', 'ride_report.html_body.extra_invoice_departure_address', 'uk', u'Точка А'),
    ('notify', 'ride_report.html_body.extra_invoice_destination_address', 'en', u'Точка Б'),
    ('notify', 'ride_report.html_body.extra_invoice_destination_address', 'ru', u'Точка Б'),
    ('notify', 'ride_report.html_body.extra_invoice_destination_address', 'uk', u'Точка Б'),
    ('notify', 'ride_report.html_body.extra_invoice_distance', 'en', u'Дистанция'),
    ('notify', 'ride_report.html_body.extra_invoice_distance', 'ru', u'Дистанция'),
    ('notify', 'ride_report.html_body.extra_invoice_distance', 'uk', u'Дистанция'),
    ('notify', 'ride_report.html_body.extra_invoice_ride_start_dt', 'en', u'Дата начала поезки'),
    ('notify', 'ride_report.html_body.extra_invoice_ride_start_dt', 'ru', u'Дата начала поезки'),
    ('notify', 'ride_report.html_body.extra_invoice_ride_start_dt', 'uk', u'Дата начала поезки'),
    ('notify', 'ride_report.html_body.extra_invoice_ride_time', 'en', u'Время в поездке'),
    ('notify', 'ride_report.html_body.extra_invoice_ride_time', 'ru', u'Время в поездке'),
    ('notify', 'ride_report.html_body.extra_invoice_ride_time', 'uk', u'Время в поездке'),
    ('notify', 'ride_report.html_body.extra_invoice_vat', 'en', u'НДС'),
    ('notify', 'ride_report.html_body.extra_invoice_vat', 'ru', u'НДС'),
    ('notify', 'ride_report.html_body.extra_invoice_vat', 'uk', u'НДС'),
    ('notify', 'ride_report.html_body.extra_invoice_final_price', 'en', u'Итоговая сумма'),
    ('notify', 'ride_report.html_body.extra_invoice_final_price', 'ru', u'Итоговая сумма'),
    ('notify', 'ride_report.html_body.extra_invoice_final_price', 'uk', u'Итоговая сумма'),
    ('notify', 'ride_report.html_body.yandex_card_payment_phrase', 'en',
     u'Yandex Card'),
    ('notify', 'ride_report.html_body.yandex_card_payment_phrase', 'ru',
     u'Яндекс Карта'),
    ('notify', 'ride_report.html_body.yandex_card_payment_phrase', 'uk',
     u'Яндекс Карта'),
    ('notify', 'ride_report.html_body.extended_subscribe_title', 'en',
     u'Стоимость расширенной подписки Яндекс.Плюс'),
    ('notify', 'ride_report.html_body.extended_subscribe_title', 'ru',
     u'Стоимость расширенной подписки Яндекс.Плюс'),
    ('notify', 'ride_report.html_body.extended_subscribe_title', 'uk',
     u'Стоимость расширенной подписки Яндекс.Плюс'),
    ('notify', 'ride_report.html_body.extended_subscribe_section_title', 'en',
     u'Оператор Программы лояльности Яндекс.Плюс'),
    ('notify', 'ride_report.html_body.extended_subscribe_section_title', 'ru',
     u'Оператор Программы лояльности Яндекс.Плюс'),
    ('notify', 'ride_report.html_body.extended_subscribe_section_title', 'uk',
     u'Оператор Программы лояльности Яндекс.Плюс'),
    ('notify', 'ride_report.html_body.extended_subscribe_section_info', 'en',
     u'Доступ к Расширенному уровню подписки Яндекс Плюс - ООО "Яндекс", УНП (ИНН)'),
    ('notify', 'ride_report.html_body.extended_subscribe_section_info', 'ru',
     u'Доступ к Расширенному уровню подписки Яндекс Плюс - ООО "Яндекс", УНП (ИНН)'),
    ('notify', 'ride_report.html_body.extended_subscribe_section_info', 'uk',
     u'Доступ к Расширенному уровню подписки Яндекс Плюс - ООО "Яндекс", УНП (ИНН)'),
    ('notify', 'ride_report.html_body.composite_title', 'en', u'Оплачено баллами'),
    ('notify', 'ride_report.html_body.composite_title', 'ru', u'Оплачено баллами'),
    ('notify', 'ride_report.html_body.composite_title', 'uk', u'Оплачено баллами'),
    ('notify', 'ride_report.html_body.cashback_spent_name_title', 'en', u'Способ оплаты'),
    ('notify', 'ride_report.html_body.cashback_spent_name_title', 'ru', u'Способ оплаты'),
    ('notify', 'ride_report.html_body.cashback_spent_name_title', 'uk', u'Способ оплаты'),
    ('notify', 'ride_report.html_body.cashback_spent_name_title', 'lv', u'Способ оплаты'),
    ('notify', 'ride_report.html_body.cashback_spent_value_title', 'en', u'Сумма'),
    ('notify', 'ride_report.html_body.cashback_spent_value_title', 'ru', u'Сумма'),
    ('notify', 'ride_report.html_body.cashback_spent_value_title', 'uk', u'Сумма'),
    ('notify', 'ride_report.html_body.cashback_spent_value_title', 'lv', u'Сумма'),
    ('notify', 'ride_report.html_body.legal_isr_composite', 'en', u'Соглашение'),
    ('notify', 'ride_report.html_body.legal_isr_composite', 'ru', u'Соглашение'),
    ('notify', 'ride_report.html_body.legal_isr_composite', 'uk', u'Соглашение'),
    ('notify', 'ride_report.html_body.legal_isr_composite', 'lv', u'Соглашение'),
    ('notify', 'ride_report.subject', 'en', 'subject'),
    ('notify', 'ride_report.subject', 'ru', 'subject'),
    ('notify', 'ride_report.subject', 'uk', 'subject'),
    ('notify', 'time', 'de', u'%H:%M'),
    ('notify', 'time', 'en', u'%H:%M'),
    ('notify', 'time', 'ru', u'%H:%M'),
    ('notify', 'time', 'uk', u'%H:%M'),
    ('notify', 'uber_ride_report.body.footer', 'ru', ''),
    ('notify', 'uber_ride_report.body.hello', 'ru', u'Привет'),
    ('notify', 'uber_ride_report.body.trip_info', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.about_support', 'ru', ''),
    (
        'notify', 'uber_ride_report.html_body.cash_payment_phrase', 'ru',
        u'Наличные',
    ),
    (
        'notify', 'uber_ride_report.html_body.card_payment_phrase', 'ru',
        u'Карта',
    ),
    (
        'notify', 'uber_ride_report.html_body.corp_payment_phrase', 'ru',
        u'Корпоративный счет',
    ),
    ('notify', 'uber_ride_report.html_body.driver_name_row', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.duration', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.fare', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.ride_cost_title', 'ru', u'Стоимость поездки'),
    ('notify', 'uber_ride_report.html_body.tax_hint_title', 'ru', u'(вкл.прим.налоги)'),
    ('notify', 'uber_ride_report.html_body.fare_type', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.logo_title', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.park_data_row', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.passenger', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.payment_phrase', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.ride_receipt', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.scheme_title', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.support_phrase', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.taxi_ordered_corp', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.taxi_ordered_personal', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.taxi_team', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.text_before_scheme_corp', 'ru', ''),
    (
        'notify', 'uber_ride_report.html_body.text_before_scheme_personal',
        'ru', '',
    ),
    ('notify', 'uber_ride_report.html_body.th_car', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.th_driver', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.th_park', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.title', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.total_fare_cost', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.unsubscribe_text', 'ru', ''),
    ('notify', 'uber_ride_report.html_body.date_title', 'ru', u'Дата'),
    ('notify', 'uber_ride_report.html_body.unp_title', 'ru', u'УНП'),
    ('notify', 'uber_ride_report.html_body.legal_address_title', 'ru', u'Юр. адрес'),
    ('notify', 'uber_ride_report.html_body.user_fullname_title', 'ru', u'ФИО пассажира'),
    ('notify', 'uber_ride_report.html_body.user_fullname_stub', 'ru', u'Пользователь не предоставил данные'),
    ('notify', 'uber_ride_report.subject', 'ru', 'subject'),
    ('notify', 'uber_ride_report.html_body.order_number_title', 'ru', u'Номер заказа'),
    ('tariff', 'currency.rub', 'de', u' руб'),
    ('tariff', 'currency.rub', 'en', ' rub'),
    ('tariff', 'currency.rub', 'ru', u' руб'),
    ('tariff', 'currency.rub', 'uk', u' руб'),
    ('tariff', 'currency_sign.rub', 'ru', u'₽'),
    ('tariff', 'currency_value.default', 'de', '%(value).0f'),
    ('tariff', 'currency_value.default', 'en', '%(value).0f'),
    ('tariff', 'currency_value.default', 'ru', '%(value).0f'),
    ('tariff', 'currency_value.default', 'uk', '%(value).0f'),
    ('tariff', 'currency_with_sign.default', 'de', '$VALUE$$SIGN$$CURRENCY$'),
    ('tariff', 'currency_with_sign.default', 'en', '$VALUE$$SIGN$$CURRENCY$'),
    ('tariff', 'currency_with_sign.default', 'ru', '$VALUE$$SIGN$$CURRENCY$'),
    ('tariff', 'currency_with_sign.default', 'uk', '$VALUE$$SIGN$$CURRENCY$'),
    ('tariff', 'detailed.kilometer', 'de', u'км'),
    ('tariff', 'detailed.kilometer', 'en', u'km'),
    ('tariff', 'detailed.kilometer', 'ru', u'км'),
    ('tariff', 'detailed.kilometer', 'uk', u'км'),
    ('tariff', 'detailed.kilometers', 'de', u'%(value).0f км'),
    ('tariff', 'detailed.kilometers', 'en', u'%(value).0f km'),
    ('tariff', 'detailed.kilometers', 'ru', u'%(value).0f км'),
    ('tariff', 'detailed.kilometers', 'uk', u'%(value).0f км'),
    ('tariff', 'round.kilometers', 'de', u'%(value).0f км'),
    ('tariff', 'round.kilometers', 'en', u'%(value).0f km'),
    ('tariff', 'round.kilometers', 'ru', u'%(value).0f км'),
    ('tariff', 'round.kilometers', 'uk', u'%(value).0f км'),
    ('tariff', 'detailed.kilometers_meters', 'de', u'%(value).3f км'),
    ('tariff', 'detailed.kilometers_meters', 'en', u'%(value).3f km'),
    ('tariff', 'detailed.kilometers_meters', 'ru', u'%(value).3f км'),
    ('tariff', 'detailed.kilometers_meters', 'uk', u'%(value).3f км'),
    ('tariff', 'detailed.minutes', 'de', u'%(value).0f мин'),
    ('tariff', 'detailed.minutes', 'en', u'%(value).0f min'),
    ('tariff', 'detailed.minutes', 'ru', u'%(value).0f мин'),
    ('tariff', 'detailed.minutes', 'uk', u'%(value).0f мин'),
    ('tariff', 'detailed.seconds', 'de', u'%(value).0f сек'),
    ('tariff', 'detailed.seconds', 'en', u'%(value).0f sec'),
    ('tariff', 'detailed.seconds', 'ru', u'%(value).0f сек'),
    ('tariff', 'detailed.seconds', 'uk', u'%(value).0f сек'),
    ('tariff', 'name.econom', 'de', u'эконом'),
    ('tariff', 'name.econom', 'en', u'Economy'),
    ('tariff', 'name.econom', 'ru', u'эконом'),
    ('tariff', 'name.econom', 'uk', u'эконом'),
    ('tariff', 'name.uberx', 'ru', u'UberX'),
]

for (keyset, key, locale, value) in SEND_REPORT_TRANSLATIONS:
    if locale == 'en':
        SEND_REPORT_TRANSLATIONS.append((keyset, key, 'lv', value))

SEND_REPORT_PARAMS = [
    # order_id, locale, expected email content, expected pdf
    # Case 1: email is unconfirmed
    ('completed_unconfirmed', 'ru', None, None, False),
    # Case 2: email is confirmed, but ride is incomplete
    ('incomplete_confirmed', 'ru', None, None, False),
    # Case 3: incomplete ride for unconfirmed email
    ('incomplete_unconfirmed', 'ru', None, None, False),
    # Case 4: the same, but in forced English locale
    ('completed_confirmed', 'en', None, 'report_en.html', False),
    # Case 5: empty destinations (no short_text, no geopoint)
    (
        'completed_confirmed_no_dest', None, None, 'report_ru_no_dest.html',
        False,
    ),
    # Case 6: destinations are present, but contain geopoint only
    (
        'completed_confirmed_no_dest_text', None, None,
        'report_ru_no_dest_text.html', False,
    ),
    # Case 7: no destinations, no geopoint in complete status
    (
        'completed_confirmed_wrong_dest', None, None,
        'report_ru_wrong_dest.html', False,
    ),
    # Case 8: order with promocode
    (
        'completed_confirmed_coupon', None, None,
        'report_ru_coupon.html', False,
    ),
    # Case 9: short ride (no time)
    (
        'completed_confirmed_short_ride', None, None,
        'report_ru_short_ride.html', False,
    ),
    # Case 10: missing driver and car data
    (
        'completed_confirmed_missing', None, None,
        'report_ru_missing.html', False,
    ),
    # Case 11: test old order with some fields missing from order_proc
    ('old_order', 'ru', None, 'report_old_order.html', False),
    # Case 12: test new ride report template
    (
        'completed_test_new_report', 'ru', None,
        'test_new_report_ru.html', False,
    ),
    # Case 13: same, order determines locale
    (
        'completed_test_new_report', None, None,
        'test_new_report_ru.html', False,
    ),
    # Case 14: test new ride report template with corp payment
    (
        'completed_test_new_report_corp', 'ru', None,
        'test_new_report_ru_corp.html', False,
    ),
    # Case 15: test new ride report template with cash payment
    (
        'completed_test_new_report_cash', 'ru', None,
        'test_new_report_ru_cash.html', False,
    ),
    # Case 16: test new ride report template with apple pay payment
    (
        'completed_test_new_report_apple_pay', 'ru', None,
        'test_new_report_ru_apple_pay.html', False,
    ),
    # Case 17: test new ride report template with google pay payment
    (
        'completed_test_new_report_google_pay', 'ru', None,
        'test_new_report_ru_google_pay.html', False,
    ),
    # Case 18: test new ride report template with default ru locale
    (
        'completed_test_new_report', 'de', None,
        'test_new_report_de_ru.html', False,
    ),
    # Case 19: test uber template for old uber (no application in order_proc)
    (
        'completed_test_uber_report', 'ru', None,
        'test_uber_report_ru.html', False,
    ),
    # Case 20: test overridden ride report template with uk locale
    (
        'completed_test_new_report', 'uk', None,
        'test_new_report_uk_overridden.html', True,
    ),
    # Case 21: test overridden ride report template
    # with uk locale and google pay
    (
        'completed_experimental_report_google_pay', 'uk', None,
        'test_new_report_uk_overridden_google_pay.html', True,
    ),
    # Case 22: test overridden ride report template
    # with uk locale and broken_park
    (
        'completed_experimental_report_corp', 'uk', None,
        'test_new_report_uk_overridden_corp.html', False,
    ),
    # Case 23: test overridden ride report template
    # with uk locale and broken_park and need_accept
    (
        'completed_experimental_report_corp_need_accept', 'uk', None, (
            'test_new_report_uk_overridden_corp_need_accept_passenger.html',
            'test_new_report_uk_overridden_corp_need_accept.html'
        ),
        True,
    ),
    # Case 24: test overriden ride report template
    # with `vat`less country (cash)
    (
        'completed_test_new_report_cash_no_vat', 'uk', None,
        'test_new_report_uk_overridden_cash_no_vat.html', True,
    ),
    # Case 25: self-driving order has no cost
    (
        'completed_test_new_report_cash_no_cost', 'uk', None,
        'test_new_report_uk_overridden_cash_no_cost.html', True,
    ),
    # Case 26: test old order with pdf _
    ('old_order', 'uk', None, 'report_old_order_uk.html', True),
    # Case 27: test completed corp ride, then user has no attached email
    (
        'completed_experimental_report_corp_no_user_mail', 'rus', None,
        'test_new_report_ru_corp_no_user_mail.html', False,
    ),
    # Case 28: test ride with cashback (cashback should be added to ride cost)
    ('completed_cashback', 'ru', None, 'report_cashback.html', False),
    # Case 29: order cost with included coupon. Coupon value takes from new pricing metas
    (
        'with_order_cost_included_coupon', None, None,
        'report_ru_order_cost_includes_coupon.html', False,
    ),
    # Case 30: send email when user email is not confirmed
    ('completed_unconfirmed', 'ru', 'personal_email_id_1', 'send_by_email_id.html', False),
]


class FakeCard(object):
    pass


def mock_common_ride_report_deps(patch):
    mock_cardstorage(patch)

    @patch('taxi.internal.city_kit.country_manager.clean_international_phone')
    @async.inline_callbacks
    def clean_international_phone(phone, country):
        yield
        async.return_value(phone)

    @patch('taxi.external.territories.get_all_countries')
    @async.inline_callbacks
    def get_all_countries(retries, retry_interval, log_extra=None):
        yield
        async.return_value([
            {'_id': 'rus', 'vat': 12000},
            {'_id': 'wtf'}
        ])

    @patch('taxi.internal.order_kit.ride_report._prepare_meta_json')
    def _prepare_meta_json(*args, **kwargs):
        return {}

    @patch('taxi.internal.geoarea_manager.get_geo_id_by_name')
    @async.inline_callbacks
    def get_geo_id_by_name(zone_name):
        yield
        async.return_value(1)

    @patch('taxi.internal.order_kit.ride_report._sleep')
    def _sleep(seconds):
        return

    @patch('taxi.external.geotracks.get_driver_track')
    @async.inline_callbacks
    def get_driver_track(*args, **kwargs):
        yield
        async.return_value({'track': []})

    @patch('taxi.external.taxi_protocol.localize_geo_objects')
    @async.inline_callbacks
    def localize_geo_objects(orderid, locale, route_objects, log_extra=None):
        assert len(route_objects) == 1
        route_object = route_objects[0]
        yield
        ans = []
        if 'text' not in route_object:
            # reverse geocoding
            # Empty answer for zero point
            if route_object['point'] != [0, 0]:
                short_text = {
                    'ru': u'Якорная улица, 10к1',
                    'uk': u'Якорная улица, 10к1',
                    'en': u'Yakornaya ulitsa, 10k1'
                }
                ans.append({
                    'fullname': short_text[locale],
                    'short_text': short_text[locale],
                    'geopoint': route_object['point'],
                })

        elif locale in ('ru', 'uk'):
            # cause we have either Lva Tolstogo, 16 or Yakornaya, 10
            if '16' in route_object['text']:
                ans.append({
                    'fullname': u'Москва, улица Льва Толстого, 16',
                    'short_text': u'улица Льва Толстого, 16'
                })
            else:
                ans.append({
                    'fullname': u'Москва, Якорная улица, 10к1',
                    'short_text': u'Якорная улица, 10к1'
                })
        else:
            # cause we have either Lva Tolstogo, 16 or Yakornaya, 10
            if '16' in route_object['text']:
                ans.append({
                    'fullname': u'Moscow, ulitsa Lva Tolstogo, 16',
                    'short_text': u'ulitsa Lva Tolstogo, 16'
                })
            else:
                ans.append({
                    'fullname': u'Moscow, Yakornaya ulitsa, 10k1',
                    'short_text': u'Yakornaya ulitsa, 10k1'
                })
        async.return_value({'addresses': ans})

    @patch('taxi.internal.card_operations.get_card_from_db')
    @async.inline_callbacks
    def get_card_from_db(*args):
        yield
        card = FakeCard()
        card.number = '400000****9067'
        card.system = 'VISA'
        async.return_value(card)


@pytest.mark.filldb()
@pytest.mark.config(
    SEND_RIDE_REPORT_BY_PERSONAL_ID=False,
    **SEND_REPORT_CONFIGS
)
@pytest.mark.parametrize(
    'order_id,locale,personal_email_id,expected,pdf_expected',
    [x[:5] for x in SEND_REPORT_PARAMS],
)
@pytest.mark.translations(SEND_REPORT_TRANSLATIONS)
@pytest.inline_callbacks
def test_send_report_with_smailik(
        patch,
        patch_exp3_compare_ride_reports_enabled,
        load,
        order_id,
        locale,
        personal_email_id,
        expected,
        pdf_expected,
        areq_request,
        corp_clients_get_client_by_client_id_mock,
):
    mock_common_ride_report_deps(patch)

    @patch('taxi.internal.email_sender.send')
    def _send(email_message, log_extra=None):
        email_message.validate()

    @patch('taxi.external.render_template.convert_html_to_pdf')
    @async.inline_callbacks
    def _convert_html_to_pdf(html, **kwargs):
        async.return_value('')
        yield

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    yield ride_report.send_report(order_id, personal_email_id=personal_email_id, locale=locale)

    if expected:
        calls = _send.calls
        if isinstance(expected, (str, unicode)):
            expected = [expected]
        assert len(calls) == len(expected)
        for call, filename in zip(calls, expected):
            email_message = call['email_message']
            expected_body = load(filename).decode('utf-8').rstrip()
            assert email_message.html_body == expected_body

        calls = _convert_html_to_pdf.calls
        if pdf_expected:
            assert calls
        else:
            assert not calls
    else:
        assert _send.calls == []


@pytest.mark.filldb()
@pytest.mark.config(
    # SEND_RIDE_REPORT_BY_PERSONAL_ID=False,
    RIDE_REPORT_ADD_EXTRA_LATVIA_INVOICE=True,
    **SEND_REPORT_CONFIGS
)
@pytest.mark.parametrize(
    ['experiment_value', 'expected_report', 'expected_pdf'],
    [
        # unconfirmed email, no exp
        (None, None, None),
        # unconfirmed email, exp, plates dont match
        (['FOO'], 'report_en_2.html', 'extra_latvia_report.html'),
        # unconfirmed email, exp, plates match
        (['FOO', u'С240'], None, None),
    ]
)
@pytest.mark.translations(SEND_REPORT_TRANSLATIONS)
@pytest.inline_callbacks
def test_latvia_extra_invoice(
        patch,
        load,
        areq_request,
        experiment_value,
        expected_report,
        expected_pdf
):

    order_id = 'completed_unconfirmed_latvia'
    locale = 'en'
    mock_common_ride_report_deps(patch)

    @areq_request
    def exp_request(method, url, **kwargs):
        if url == 'http://experiments3.taxi.yandex.net/v1/experiments':
            consumer = kwargs['json']['consumer']
            assert consumer in (
                'ride_report_sender', 'order-notify/stq/call_old_ride_report'
            )

            if consumer == 'order-notify/stq/call_old_ride_report':
                exp_items = [{
                    'name': 'compare_ride_reports_enabled',
                    'value': {'enable': True},
                }]
                return areq_request.response(
                    200,
                    body=json.dumps({
                        'items': exp_items,
                    }),
                )

            if experiment_value is not None:
                exp_items = [{
                    'name': 'latvia_extra_invoice_attachment',
                    'value': {'excluded_plates': experiment_value},
                }]
            else:
                exp_items = []
            return areq_request.response(
                200, body=json.dumps({'items': exp_items}),
            )
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))
        assert 0, 'Unknown url'

    @patch('taxi.internal.email_sender.send')
    def _send(email_message, log_extra=None):
        email_message.validate()

    @patch('taxi.external.render_template.convert_html_to_pdf')
    @async.inline_callbacks
    def _convert_html_to_pdf(html, **kwargs):
        expected_html = load(expected_pdf).decode('utf-8')
        assert html.strip() == expected_html.strip()
        async.return_value('')
        yield

    yield ride_report.send_report(order_id, locale=locale)

    if expected_report:
        calls = _send.calls
        assert len(calls) == 1
        email_message = calls[0]['email_message']
        expected_body = load(expected_report).decode('utf-8').rstrip()
        assert email_message.html_body == expected_body
    else:
        assert len(_send.calls) == 0

    if expected_pdf:
        assert len(_convert_html_to_pdf.calls) == 1
    else:
        assert len(_convert_html_to_pdf.calls) == 0


@pytest.mark.filldb()
@pytest.mark.config(RIDE_REPORT_RESOLVE_USER_FIRST_NAME=True)
@pytest.mark.translations(SEND_REPORT_TRANSLATIONS)
@pytest.inline_callbacks
def test_user_first_name_param(patch, areq_request):
    mock_common_ride_report_deps(patch)

    @areq_request
    def _requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [
                    {'value': x['id'][3:], 'id': x['id']}
                    for x in kwargs['json']['items']
                ]
            }
            return areq_request.response(200, body=json.dumps(response))

    @patch('taxi.external.passenger_profile.get_first_name')
    @async.inline_callbacks
    def _get_first_name(*args, **kwargs):
        yield
        async.return_value('Michael')

    @patch('taxi.internal.order_kit.ride_report._make_report')
    @async.inline_callbacks
    def _patched_make_report(report_kwargs, *args, **kwargs):
        yield
        assert 'user_first_name' in report_kwargs
        assert report_kwargs['user_first_name'] == 'Michael'

    @patch('taxi.internal.email_manager.send_message')
    @async.inline_callbacks
    def _patched_send_message(*args, **kwargs):
        yield
        pass

    yield ride_report.send_report('completed_confirmed', locale='en')
    assert len(_patched_make_report.calls) == 1


@pytest.mark.filldb()
@pytest.mark.config(
    SEND_RIDE_REPORT_BY_PERSONAL_ID=True,
    **SEND_REPORT_CONFIGS
)
@pytest.mark.parametrize(
    'order_id,locale,personal_email_id,expected,pdf_expected',
    SEND_REPORT_PARAMS,
)
@pytest.mark.config(
    RIDE_REPORT_SENDER_SLUGS=[
        {
            'from_email': 'no-reply@taxi.yandex.ru',
            'account': 'taxi',
            'slug': 'test_slug_yandex',
        },
        {
            'from_email': 'no-reply@taxi.yandex.com',
            'account': 'taxi',
            'slug': 'test_slug_yandex',
        },
        {
            'from_email': 'no-reply@support-uber.com',
            'account': 'uber',
            'slug': 'test_slug_uber',
        },
    ],
)
@pytest.mark.parametrize('experiment_accepted', [True, False])
@pytest.mark.parametrize('use_sender_experiment_accepted', [True, False])
@pytest.mark.translations(SEND_REPORT_TRANSLATIONS)
@pytest.inline_callbacks
def test_send_report_with_sticker(
        patch,
        load,
        areq_request,
        order_id,
        locale,
        personal_email_id,
        expected,
        pdf_expected,
        experiment_accepted,
        use_sender_experiment_accepted,
        corp_clients_get_client_by_client_id_mock,
):
    mock_common_ride_report_deps(patch)

    @areq_request
    def exp_request(method, url, **kwargs):
        if url == 'http://experiments3.taxi.yandex.net/v1/experiments':
            consumer = kwargs['json']['consumer']
            assert consumer in (
                'ride_report_sender', 'order-notify/stq/call_old_ride_report'
            )

            if consumer == 'order-notify/stq/call_old_ride_report':
                exp_items = [{
                    'name': 'compare_ride_reports_enabled',
                    'value': {'enable': True},
                }]
                return areq_request.response(
                    200,
                    body=json.dumps({
                        'items': exp_items,
                    }),
                )

            if experiment_accepted:
                exp_items = [{
                    'name': 'user_sticker_to_send_mail_report',
                    'value': 1,
                }]
            else:
                exp_items = []
            if use_sender_experiment_accepted:
                exp_items.append({
                    'name': 'send_mail_report_via_sticker_and_sender',
                    'value': 1,
                })
            return areq_request.response(
                200,
                body=json.dumps({
                    'items': exp_items,
                }),
            )
        if url == 'http://sticker.taxi.dev.yandex.net/status/':
            return areq_request.response(200, body=json.dumps({
                'status': 'SCHEDULED',
            }))
        if url == 'http://sticker.taxi.dev.yandex.net/send/':
            assert not use_sender_experiment_accepted
            return areq_request.response(200)
        if url == 'http://sticker.taxi.dev.yandex.net/v2/send/':
            assert use_sender_experiment_accepted
            return areq_request.response(200)
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))
        assert 0, 'Unknown url'

    @patch('taxi.internal.email_sender.send')
    @async.inline_callbacks
    def _smailik_send(email_message, log_extra=None):
        yield
        email_message.validate()
        stq_task.check_email(
            message_id=email_message.message_id,
            counter=0,
            log_extra=log_extra,
        )

    original_method = sticker.send

    @patch('taxi.internal.email_sender.sticker.send')
    @async.inline_callbacks
    def _sticker_send(email_message, email_personal_id, send_via_sender=False, log_extra=None):
        email_message.validate(recipient_required=False)
        stq_task.check_email(
            message_id='{}={}'.format(email_personal_id, 'some'),
            counter=0,
            log_extra=log_extra,
        )
        assert send_via_sender is use_sender_experiment_accepted
        yield original_method(email_message, email_personal_id, send_via_sender, log_extra)

    @patch('taxi.util.smailik.render_for_smailik')
    def _render_for_smailik(email_message, email_dst_object, recipient_required=True):
        return

    @patch('taxi.external.render_template.convert_html_to_pdf')
    @async.inline_callbacks
    def _convert_html_to_pdf(html, **kwargs):
        yield
        async.return_value('')

    @patch('taxi.internal.email_sender.common.EmailMessage.attach_file')
    def _attach_file(*args, **kwargs):
        pass

    yield ride_report.send_report(order_id, personal_email_id=personal_email_id, locale=locale)

    _calls = {}
    for mock in (
        _attach_file, _convert_html_to_pdf, _smailik_send, _sticker_send,
    ):
        _calls[mock] = mock.calls

    for mock in (_attach_file, _convert_html_to_pdf):
        assert bool(_calls[mock]) == pdf_expected, mock.func_name

    if not experiment_accepted and not use_sender_experiment_accepted:
        assert not _calls[_sticker_send]

    if not expected:
        assert _calls[_sticker_send] == []
        return

    calls = _calls[_sticker_send] + _calls[_smailik_send]
    if isinstance(expected, (str, unicode)):
        expected = [expected]
    assert len(calls) == len(expected), mock.func_name
    for call, filename in zip(calls, expected):
        email_message = call['args'][0]
        expected_body = load(filename).decode('utf-8').rstrip()
        assert email_message.html_body == expected_body, mock.func_name


@pytest.mark.parametrize(
    'order_proc, city_doc, geo_id, locale, expected',
    [
        (
            {
                'order': {
                    'created': datetime.datetime(2016, 2, 8, 19, 15, 30),
                    'city': u'Москва',
                    'cost': 230,
                    'request': {
                        'source': {
                            'fullname': u'Москва, Льва Толстого 16',
                            'geopoint': [
                                37, 55
                            ],
                            'uris': ['uri1']
                        },
                        'requirements': {},
                    },
                    'calc': {
                        'distance': 2145,
                        'time': 183,
                    },
                    'performer': {
                        'tariff': {
                            'class': 'econom',
                        }
                    },
                },
                'order_info': {
                    'statistics': {
                        'status_updates': [
                            {
                                't': 'transporting',
                                'c': datetime.datetime(2016, 2, 8, 19, 25, 30),
                            },
                            {
                                't': 'complete',
                                'c': datetime.datetime(2016, 2, 8, 19, 35, 30),
                            },
                        ]
                    }
                }
            },
            {},
            213,
            'ru',
            {
                'arr': u'Москва, Остоженка 25',
                'dep': u'Москва, Льва Толстого 16',
                'cost': 230,
                'car': 'Mitsubishi Galant',
                'time_dep': '0.0.0 22:25:30',
                'city_dep': u'Москва',
                'duration': '0:10:0',
                'order_date': '8.2.2016 22:15:30',
                'time_arr': '0.0.0 22:35:30',
                'city_dep_geoid': 213,
                'dist': 2.145,
                'trip_class': 'econom',
            }
        ),
        (
            {
                'order': {
                    'created': datetime.datetime(2016, 2, 8, 19, 15, 30),
                    'city': u'Москва',
                    'cost': 230,
                    'request': {
                        'source': {
                            'fullname': u'Москва, Льва Толстого 16',
                            'geopoint': [
                                37, 55
                            ],
                            'uris': ['uri2']
                        },
                        'requirements': {},
                    },
                    'performer': {
                        'tariff': {
                            'class': 'econom',
                        }
                    },
                },
            },
            {},
            None,
            'en',
            {
                'arr': u'Moskva, Ostozhenka 25',
                'dep': u'Moskva, Lva Tolstogo 16',
                'cost': 230,
                'car': 'Mitsubishi Galant',
                'city_dep': u'Moskva',
                'order_date': '8.2.2016 22:15:30',
                'trip_class': 'econom',
            }
        ),
        (
            {
                'order': {
                    'created': datetime.datetime(2016, 2, 8, 19, 15, 30),
                    'city': u'Москва',
                    'cost': 230,
                    'cashback_cost': 26,
                    'request': {
                        'source': {
                            'fullname': u'Москва, Льва Толстого 16',
                            'geopoint': [
                                37, 55
                            ],
                            'uris': ['uri2']
                        },
                        'requirements': {},
                    },
                    'performer': {
                        'tariff': {
                            'class': 'business',
                        }
                    },
                },
            },
            {},
            None,
            'en',
            {
                'arr': u'Moskva, Ostozhenka 25',
                'dep': u'Moskva, Lva Tolstogo 16',
                'cost': 256,
                'car': 'Mitsubishi Galant',
                'city_dep': u'Moskva',
                'order_date': '8.2.2016 22:15:30',
                'trip_class': 'business',
            },
        )
    ]
)
@pytest.inline_callbacks
def test_prepare_meta_json(
        order_proc, city_doc, geo_id, locale, expected, patch):
    @patch('taxi.external.taxi_protocol.localize_geo_objects')
    @async.inline_callbacks
    def localize_geo_objects(orderid, locale, route_objects, log_extra=None):
        yield
        if locale == 'ru':
            async.return_value({
                'addresses': [{
                    'fullname': u'Москва, Льва Толстого 16',
                    'short_text': u'Льва Толстого 16'
                }
                for _ in range(len(route_objects))]
            })
        else:
            async.return_value({
                'addresses': [{
                    'fullname': 'Moskva, Lva Tolstogo 16',
                    'short_text': 'Lva Tolstogo 16'
                }
                for _ in range(len(route_objects))]
            })

    city = {
        'tz': 'Europe/Moscow',
    }
    city.update(city_doc)
    car_doc = {
        'model': 'Mitsubishi Galant',
    }
    arrival_desc = u'Москва, Остоженка 25'

    order_proc = dbh.order_proc.Doc(order_proc)

    result = yield ride_report._prepare_meta_json(
        order_proc=order_proc,
        city_doc=city,
        car_doc=car_doc,
        arrival_desc=arrival_desc,
        locale=locale,
        geo_id=geo_id,
        request=order_proc.order.request,
        calc_info=order_proc.order.calc,
    )
    assert result == expected


@pytest.mark.parametrize('pk, expected', [
    ('', ''),
    ('123', '123'),
    ('1234', '1234'),
    ('12345', '1234 5'),
    ('12345678', '1234 5678'),
    ('1234567890abcdef', '1234 5678 90ab cdef')
])
def test_separate_id(pk, expected):
    result = ride_report._format_pk(pk)
    assert result == expected


PAYMENT_TYPE_MAP_BILLING_SERVICE_ID = {
    const.CORP: 135,
    const.PERSONAL_WALLET: 124,
    const.COOP_ACCOUNT: 124,
}

TRUST_RECEIPT_PAYMENT_METHODS = [
    const.APPLE,
    const.CARD,
    const.COOP_ACCOUNT,
    const.GOOGLE,
]


@pytest.mark.config(
    ORDERS_HISTORY_SHOW_FETCHED_RECEIPT_IN_COUNTRIES=['bel'],
    ORDERS_HISTORY_SHOW_TRUST_RECEIPT_IN_COUNTRIES=['rus'],
)
@pytest.mark.parametrize('order_proc, billing_service_id', [
    (
        {'order': {'performer': {'taxi_alias': {'id': None}}}},
        None,
    ),
    (
        {'order': {'performer': {'taxi_alias': {'id': '1'}}}},
        124,
    ),
    (
        {
            'order': {
                'performer': {'taxi_alias': {'id': '1'}},
                'source': 'yandex',
                'application': 'android',
            },
        },
        124,
    ),
    (
        {
            'order': {
                'performer': {'taxi_alias': {'id': '1'}},
                'source': 'yauber',
                'application': 'uber_iphone',
            },
        },
        125,
    ),
])
@pytest.mark.parametrize('payment_type', [
    const.CASH,
    const.CORP,
    const.PERSONAL_WALLET,
    const.COOP_ACCOUNT,
    const.CARD,
    const.APPLE,
    const.GOOGLE,
])
@pytest.mark.parametrize('billing_by_brand_enabled', [False, True])
@pytest.inline_callbacks
def test_ride_receipt_url_from_trust(
        order_proc, billing_service_id, payment_type, billing_by_brand_enabled,
):
    yield config.BILLING_SERVICE_NAME_MAP_BY_BRAND_ENABLED.save(
        billing_by_brand_enabled,
    )
    order_proc = dbh.order_proc.Doc(order_proc)

    has_performer_id = order_proc.order.performer.taxi_alias.id is not None

    if payment_type in PAYMENT_TYPE_MAP_BILLING_SERVICE_ID:
        billing_service_id = PAYMENT_TYPE_MAP_BILLING_SERVICE_ID[payment_type]

    if (not has_performer_id or
        billing_service_id is None or
        payment_type not in TRUST_RECEIPT_PAYMENT_METHODS
    ):
        expected_url = None
    else:
        expected_url = 'https://trust.yandex.ru/receipts/{}-1/'.format(
            billing_service_id
        )
    actual_url = yield ride_report._get_receipt_url(order_proc, 'rus', payment_type)

    assert actual_url == expected_url


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    ORDERS_HISTORY_SHOW_FETCHED_RECEIPT_IN_COUNTRIES=['kaz'],
    ORDERS_HISTORY_SHOW_TRUST_RECEIPT_IN_COUNTRIES=[],
)
@pytest.mark.parametrize('payment_type', [
    const.CASH,
    const.CORP,
    const.PERSONAL_WALLET,
    const.COOP_ACCOUNT,
    const.CARD,
    const.APPLE,
    const.GOOGLE,
])
@pytest.mark.parametrize('country_code', ['rus', 'kaz', ])
@pytest.mark.parametrize('receipt_fetching_code', [
    200,
    400,
    401,
    404,
    500,
    504,
])
@pytest.inline_callbacks
def test_ride_receipt_url_from_receit_fetching(
      areq_request, payment_type, country_code, receipt_fetching_code
):
    _order_id = '801fb61ae4ca2b08be680e5c64eb7fc8'
    order_proc = {
        '_id': _order_id,
        'order': {
            'performer': {'taxi_alias': {'id': '1'}},
            'source': 'yandex',
            'application': 'android',
        },
    }
    order_proc = dbh.order_proc.Doc(order_proc)

    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'POST'
        assert url == 'http://receipt-fetching.taxi.dev.yandex.net/receipts'

        if receipt_fetching_code != 200:
            return areq_request.response(receipt_fetching_code)

        order_id = kwargs['json']['order_ids'][0]
        assert order_id == _order_id

        response = {
            'receipts': [
                  {
                      'order_id': order_id,
                      'receipt_url': 'https://buhta.kz/yt/{}'.format(order_id),
                  }
            ]
        }
        return areq_request.response(200, body=json.dumps(response))

    actual_url = yield ride_report._get_receipt_url(order_proc, country_code, payment_type)

    if country_code == 'kaz' and receipt_fetching_code == 200:
        assert actual_url == 'https://buhta.kz/yt/{}'.format(_order_id)
    else:
        assert actual_url is None


@pytest.mark.filldb()
@pytest.mark.config(
    APPLICATION_MAP_TRANSLATIONS={
        'android:3': {
            'notify': 'notify',
        },
    },
    **SEND_REPORT_CONFIGS
)
@pytest.mark.translations(
    SEND_REPORT_TRANSLATIONS +
    [
        ('notify', 'ride_report.body.footer', 'ru', u'Yandex.Go footer'),
        ('notify', 'ride_report.subject', 'ru', u'Yandex.Go subject'),
    ],
)
@pytest.inline_callbacks
def test_send_report_app_override(
        patch, patch_exp3_compare_ride_reports_enabled, load, areq_request,
):
    mock_common_ride_report_deps(patch)

    @patch('taxi.internal.email_sender.send')
    def _send(email_message, log_extra=None):
        email_message.validate()

    @patch('taxi.external.render_template.convert_html_to_pdf')
    @async.inline_callbacks
    def _convert_html_to_pdf(html, **kwargs):
        async.return_value('')
        yield

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    yield ride_report.send_report('completed_test_new_report', locale=None)

    calls = _send.calls
    assert len(calls) == 1
    message = calls[0]['email_message']
    assert message.subject == 'Yandex.Go subject'
    assert message.body == 'txt report Yandex.Go footer'


@pytest.mark.config(
    RIDE_REPORT_EXCLUDED_APPLICATIONS=['excluded_app_name'],
    **SEND_REPORT_CONFIGS
)
@pytest.mark.translations(SEND_REPORT_TRANSLATIONS)
@pytest.inline_callbacks
def test_excluded_applications(
        patch,
        areq_request,
):

    @patch('taxi.internal.email_sender.send')
    def _send(email_message, log_extra=None):
        email_message.validate()

    @areq_request
    def requests_request(method, url, **kwargs):
        if url == "http://personal.taxi.yandex.net/v1/phones/bulk_retrieve":
            response = {
                "items": [{'value': x['id'][3:], 'id': x['id']} for x in kwargs['json']['items']]
            }
            return areq_request.response(200, body=json.dumps(response))

    mock_common_ride_report_deps(patch)

    yield ride_report.send_report('excluded_app_order',
     personal_email_id='just_any_email')

    calls = _send.calls
    assert len(calls) == 0
