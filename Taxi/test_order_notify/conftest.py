# pylint: disable=redefined-outer-name
import datetime
import uuid

import pytest

import order_notify.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from order_notify.generated.service.swagger.models.api import TemplateData

pytest_plugins = [
    'order_notify.generated.service.pytest_plugins',
    'test_order_notify.mocks.order_core',
    'test_order_notify.mocks.ucommunications',
    'test_order_notify.mocks.tariffs',
]

DEFAULT_TITLE = 'Такси'

TRANSLATIONS_NOTIFY = {
    'order_notify.time': {'ru': '%H:%M'},
    'order_notify.driving.title': {'ru': DEFAULT_TITLE},
    'order_notify.driving.autoreorder_by_cancel.title': {'ru': DEFAULT_TITLE},
    'order_notify.driving.autoreorder_by_eta.title': {'ru': DEFAULT_TITLE},
    'order_notify.waiting.title': {'ru': DEFAULT_TITLE},
    'order_notify.transporting.title': {'ru': DEFAULT_TITLE},
    'order_notify.complete.title': {'ru': DEFAULT_TITLE},
    'order_notify.cancel_by_user.title': {'ru': DEFAULT_TITLE},
    'order_notify.cancel_by_park.title': {'ru': DEFAULT_TITLE},
    'order_notify.search_failed.title': {'ru': DEFAULT_TITLE},
    'order_notify.failed_by_park.title': {'ru': DEFAULT_TITLE},
    'order_notify.moved_to_cash.title': {'ru': DEFAULT_TITLE},
    'order_notify.driving.text': {
        'ru': 'Через {estimate} мин. приедет {car_info}',
    },
    'order_notify.driving.autoreorder_by_cancel.text': {
        'ru': (
            'Водитель отменил заказ, но мы уже нашли новую машину. '
            'Через {estimate} мин. приедет {car_info}'
        ),
    },
    'order_notify.driving.autoreorder_by_eta.text': {
        'ru': (
            'Водитель задерживается, но мы уже нашли новую машину. '
            'Через {estimate} мин. приедет {car_info}'
        ),
    },
    'order_notify.waiting.text': {
        'ru': 'Водитель по заказу на {due} ждёт вас! {car_info}',
    },
    'order_notify.transporting.text': {
        'ru': 'Водитель начал выполнение заказа от {due}',
    },
    'order_notify.passenger_feedback': {'ru': 'Оцените поездку.'},
    'order_notify.complete.cost.text': {
        'ru': 'Стоимость заказа {formatted_user_cost}',
    },
    'order_notify.complete.cost_with_complement.text': {
        'ru': (
            'Стоимость заказа {formatted_total_cost}, '
            '{formatted_complement_price} оплачено баллами Плюса.'
        ),
    },
    'order_notify.complete.cost_with_cashback.text': {
        'ru': (
            'Стоимость заказа {formatted_total_cost} Кешбэк +{cashback} балл.'
        ),
    },
    'order_notify.complete.cost_with_coupon.text': {
        'ru': (
            'Стоимость {formatted_total_cost}, к оплате {formatted_user_cost} '
            '(скидка по купону {formatted_coupon}).'
        ),
    },
    'order_notify.cancel_by_user.by_early_hold.text': {
        'ru': (
            'Поездку на {due} отменили — оплата не прошла. '
            'Попробуйте изменить способ оплаты'
        ),
    },
    'order_notify.cancel_by_user.text': {'ru': 'Заказ на {due} отменён'},
    'order_notify.cancel_by_user.paid.text': {
        'ru': 'Заказ на {due} отменён. Стоимость {formatted_user_cost}',
    },
    'order_notify.cancel_by_user.early_hold.text': {
        'ru': (
            'Поездка на {due} отменена.'
            ' Деньги вернутся на карту. Чек — в истории заказов'
        ),
    },
    'order_notify.cancel_by_user.early_hold.paid.text': {
        'ru': (
            'Поездка на {due} отменена.'
            ' Водитель уже приехал, поэтому отмена '
            'платная — {formatted_user_cost}.'
            ' Остальная сумма вернётся на карту'
        ),
    },
    'order_notify.search_failed.text': {
        'ru': 'На {due} нет свободных машин. Поискать в других тарифах?',
    },
    'order_notify.search_failed.expired_before_check_in.text': {
        'ru': (
            'Вы не нажали «Я на месте», поэтому мы не смогли назначить машину'
        ),
    },
    'order_notify.cancel_by_park.text': {
        'ru': 'Водитель отказался от заказа на {due}',
    },
    'order_notify.moved_to_cash.text': {
        'ru': (
            'Способ оплаты был изменён на наличные. Повторить попытку '
            'оплаты картой вы сможете по завершении поездки.'
        ),
    },
    'order_notify.moved_to_cash.with_coupon.text': {
        'ru': (
            'Не удалось зарезервировать деньги на карте — оплатите '
            'поездку наличными. Стоимость пересчитана без скидки, '
            'ваш купон можно применить к следующей поездке.'
        ),
    },
    # for other
    'order_notify.driving_for_other.not_cash.text': {
        'en': (
            'Someone’s requested a prepaid ride for you. '
            'The car will arrive in {estimate} min. Tap to see it on the map'
        ),
    },
    'order_notify.driving_for_other.cash.text': {
        'en': (
            'Someone’s requested a ride for you. Cash payment. '
            'The car will arrive in {estimate} min. Tap to see it on the map'
        ),
    },
    'order_notify.waiting_for_other.text': {
        'en': 'Your {car_info} is waiting. Tap to see it on the map',
    },
    'order_notify.driving.text.econom_suffix': {
        'ru': 'Через {estimate} мин. приедет {car_info} | econom_suffix',
    },
    'order_notify.driving.title.econom_suffix': {
        'ru': f'{DEFAULT_TITLE} | econom_suffix',
    },
}

TRANSLATIONS_RIDE_REPORT = {
    'ride_report.html_body.bill_title': {'ru': 'Квитанция', 'en': 'Bill'},
    'ride_report.html_body.carrier_title': {
        'ru': 'Перевозчик',
        'en': 'Carrier',
    },
    'ride_report.html_body.date_title': {'ru': 'Дата', 'en': 'Date'},
    'ride_report.html_body.details_title': {'ru': 'Детали', 'en': 'Details'},
    'ride_report.html_body.disclaimer': {
        'ru': 'Дисклэймер',
        'en': 'Disclaimer',
    },
    'ride_report.html_body.dst_changed': {'ru': 'Дистанция', 'en': 'Dst'},
    'ride_report.html_body.duration': {'ru': 'Время в пути', 'en': 'Duration'},
    'ride_report.html_body.extended_subscribe_section_title': {
        'ru': 'Расшинн',
        'en': 'Ex',
    },
    'ride_report.html_body.fare_title': {
        'ru': 'Общая стоимость',
        'en': 'Fare',
    },
    'ride_report.html_body.fare_type': {'ru': 'Тариф', 'en': 'Fare Type'},
    'ride_report.html_body.legal_address_title': {
        'ru': 'Юр. адрес',
        'en': 'Legal Address',
    },
    'ride_report.html_body.name_title': {'ru': 'Имя', 'en': 'Name'},
    'ride_report.html_body.logo_title': {'ru': 'Логотип', 'en': 'Logo'},
    'ride_report.html_body.ogrn_title': {'ru': 'Огрн', 'en': 'Ogrn'},
    'ride_report.html_body.order_number_title': {
        'ru': 'Номер заказа',
        'en': 'Order number',
    },
    'ride_report.html_body.passenger': {'ru': 'Пассажир', 'en': 'Passenger'},
    'ride_report.html_body.payment_method_title': {
        'ru': 'Метод опла',
        'en': 'Payment meth',
    },
    'ride_report.html_body.payment_title': {'ru': 'Оплата', 'en': 'Payment'},
    'ride_report.html_body.phone_title': {'ru': 'Телефон', 'en': 'Phone'},
    'ride_report.html_body.receipt_title': {
        'ru': 'Чек Поездки',
        'en': 'Receipt',
    },
    'ride_report.html_body.ride_cost_title': {
        'ru': 'Стоимость поездки',
        'en': 'Ride cost',
    },
    'ride_report.html_body.ride_title': {'ru': 'Поездка', 'en': 'Ride'},
    'ride_report.html_body.route_title': {'ru': 'Маршрут', 'en': 'Route'},
    'ride_report.html_body.support_title': {
        'ru': 'Поддержка',
        'en': 'Support',
    },
    'ride_report.html_body.tax_hint_title': {'ru': 'Такси', 'en': 'Tax_hint'},
    'ride_report.html_body.th_car': {'ru': 'Автомобиль', 'en': 'Th_car'},
    'ride_report.html_body.th_driver': {'ru': 'Водитель', 'en': 'Th_driver'},
    'ride_report.html_body.th_park': {'ru': 'Партнёр', 'en': 'Th_park'},
    'ride_report.html_body.tips_title': {'ru': 'Типы', 'en': 'Tips'},
    'ride_report.html_body.title': {'ru': 'Заголовок', 'en': 'Title'},
    'ride_report.html_body.unp_title': {'ru': 'УНП', 'en': 'Unp'},
    'ride_report.html_body.unsubscribe_text': {
        'ru': 'Отписаться от отчётов',
        'en': 'Unsub',
    },
    'ride_report.html_body.user_fullname_stub': {
        'ru': 'Стаб пользовател',
        'en': 'Stub',
    },
    'ride_report.html_body.user_fullname_title': {
        'ru': 'Имя пользовател',
        'en': 'Fullname',
    },
    'ride_report.html_body.vat_title': {'ru': 'Ват', 'en': 'Vat'},
    'ride_report.html_body.scheme_title': {'ru': 'Схема', 'en': 'Route map'},
    'ride_report.html_body.ride_receipt': {
        'ru': 'Отчет о поездке',
        'en': 'Ride report',
    },
}

TRANSLATIONS_UBER_RIDE_REPORT = {
    'uber_ride_report.html_body.title': {
        'ru': 'Uber – Отчёт о поездке',
        'en': 'Uber – Ride report',
    },
    'uber_ride_report.html_body.logo_title': {'ru': 'Uber', 'en': 'Uber'},
    'uber_ride_report.html_body.passenger': {'ru': 'Пассажир', 'en': 'Client'},
    'uber_ride_report.html_body.total_fare_cost': {
        'ru': 'Стоимость поездки — ${cost}',
        'en': 'Ride cost — ${cost}',
    },
    'uber_ride_report.html_body.fare_type': {
        'ru': 'Тариф',
        'en': 'Service class',
    },
    'uber_ride_report.html_body.duration': {
        'ru': 'Время в пути',
        'en': 'Ride duration',
    },
    'uber_ride_report.html_body.fare': {'ru': 'Стоимость', 'en': 'Ride cost'},
    'uber_ride_report.html_body.about_support': {
        'ru': (
            'Любые вопросы вы можете задать на странице '
            '<a href="${support_url}" style="color: #669; '
            'text-decoration: none;">службы поддержки</a>.'
        ),
        'en': (
            'If you have any questions, please don’t hesitate to contact the '
            '<a href="${support_url}" style="color: #669; '
            'text-decoration: none;">support service</a>.'
        ),
    },
    'uber_ride_report.html_body.unsubscribe_text': {
        'ru': 'Больше не получать отчёты о поездках',
        'en': 'Opt out of receiving ride reports',
    },
    'uber_ride_report.html_body.payment_method_title': {
        'ru': 'Оплата',
        'en': 'Payment',
    },
    'uber_ride_report.html_body.cash_payment_phrase': {
        'ru': 'Наличные',
        'en': 'Cash',
    },
    'uber_ride_report.html_body.support_phrase': {
        'ru': (
            'Забыли вещи в Uber или другой вопрос по поездке?'
            ' Обратитесь в службу поддержки.'
        ),
        'en': (
            'If you left something in the car, '
            'or have any questions regarding your ride, '
            'please contact our support staff.'
        ),
    },
    'uber_ride_report.html_body.th_park': {'ru': 'Партнёр', 'en': 'Partner'},
    'uber_ride_report.html_body.date_title': {'ru': 'Дата', 'en': 'Date'},
    'uber_ride_report.html_body.unp_title': {'ru': 'УНП', 'en': 'UNP'},
    'uber_ride_report.html_body.legal_address_title': {
        'ru': 'Юр. адрес',
        'en': 'Legal address',
    },
    'uber_ride_report.html_body.user_fullname_title': {
        'ru': 'ФИО пассажира',
        'en': 'Passenger name',
    },
    'uber_ride_report.html_body.user_fullname_stub': {
        'ru': 'Пользователь не предоставил данные',
        'en': 'The user hasn\'t provided data',
    },
    'uber_ride_report.html_body.order_number_title': {
        'ru': 'Номер заказа',
        'en': 'Order number',
    },
    'uber_ride_report.subject': {
        'ru': 'Uber – отчёт о поездке %(date)s',
        'en': 'Uber – ride report for %(date)s',
    },
    'uber_ride_report.html_body.tax_hint_title': {
        'ru': '(вкл.прим.налоги)',
        'en': '(including applied taxes)',
    },
    'uber_ride_report.html_body.ride_cost_title': {
        'ru': 'Стоимость поездки',
        'en': 'Ride cost',
    },
    'uber_ride_report.html_body.th_driver': {
        'ru': 'Водитель: ',
        'en': 'Driver: ',
    },
    'uber_ride_report.html_body.ogrn_title': {'ru': 'ОГРН: ', 'en': 'OGRN: '},
}

TRANSLATIONS_NOTIFY_EXTRA = {
    'report.unknown_destination': {'ru': 'По требованию', 'en': 'On request'},
    'helpers.month_5_part': {'ru': 'мая', 'en': 'May'},
    'helpers.humanized_date_fmt': {
        'ru': '%(day)d %(month)s %(year)04d г.',
        'en': '%(day)d %(month)s, %(year)04d',
    },
}

TRANSLATIONS_TARIFF = {
    'name.econom': {'ru': 'Эконом', 'en': 'Economy'},
    'name.uberblack': {'ru': 'Black', 'en': 'Black'},
    'name.comfort': {'ru': 'Комфорт', 'en': 'Comfort'},
    'round.kilometers': {'ru': '%(value).0f км', 'en': '%(value).0f km'},
    'detailed.minutes': {'ru': '%(value).0f мин', 'en': '%(value).0f min'},
    'detailed.seconds': {'ru': '%(value).0f сек', 'en': '%(value).0f sec'},
    'currency_with_sign.rub': {
        'ru': '$VALUE$ $SIGN$$CURRENCY$',
        'en': '$SIGN$$VALUE$ $CURRENCY$',
    },
    'currency.rub': {'ru': 'руб.', 'en': 'rub'},
    'currency_sign.rub': {'ru': '₽', 'en': '₽'},
}

TRANSLATIONS_COLOR = {'EE1D19': {'ru': 'красный', 'en': 'red'}}

BASE_PAYLOAD = {
    'nearest_zone': 'angarsk'.format(),
    'currency': 'rub',
    'application': 'yataxi',
    'payment_type': 'card',
    'tariff_class': 'econom',
    'performer_phone': '+70001112233,0000',
    'performer_first_name': 'Evgeny',
    'due': datetime.datetime(2021, 5, 7, 10, 52),
    'rsk': 'random_rsk_id',
    'car_number': 'Е001КХ777',  # ru
    'car_model': 'Kia Optima',
    'car_color_code': 'FAFBFB',
    'cost': 100.0,
    'complement_price': None,
    'cashback_price': None,
    'cashback_discount': None,
    'coupon_price': None,
    'kind': None,
}

DEFAULT_TEMPLATE_DATA = TemplateData(
    map_size='500,256',
    show_fare_with_vat_only=False,
    show_ogrn_and_unp=False,
    show_order_id=False,
    show_user_fullname=False,
    campaign_slug='camplslug',
    receipt_mode='receipt',
    from_email='sm@yandex-team.ru',
    from_name='sn',
    logo_url='https://yastatic.net',
    support_url='https://yandex.ru/support/',
    taxi_host='taxi.yandex.com',
    extended_uber_report=False,
    send_pdf=False,
    map_first_point_color='comma_solid_red',
    map_last_point_color='comma_solid_blue',
    map_line_color='3C3C3CFF',
    map_line_width=3,
    map_mid_point_color='trackpoint',
    map_url='https://{}/get-map/1.x/',
)


@pytest.fixture(autouse=True)
def patch_uuid(patch):
    @patch('uuid.uuid4')
    def _uuid4():
        return uuid.UUID(int=0, version=4)


@pytest.fixture
def mock_tariff_zones(mockserver):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    def _mock_tariffs(request):
        return {
            'zones': [
                {
                    'country': 'rus',
                    'name': 'moscow',
                    'time_zone': 'Europe/Moscow',
                },
                {
                    'country': 'rus',
                    'name': 'angarsk',
                    'time_zone': 'Asia/Irkutsk',
                },
            ],
        }

    return _mock_tariffs


@pytest.fixture
def mock_yacc(mockserver):
    class MockClck:
        @staticmethod
        @mockserver.handler('/ya-cc/--')
        def click(request):
            return mockserver.make_response(
                'https://clck_url',
                headers={'Content-Type': 'text/javascript; charset=utf-8'},
            )

    return MockClck


@pytest.fixture
def mock_yt_locale_fetch(mockserver):
    @mockserver.json_handler('/archive-api/v1/yt/select_rows')
    def _mock_yt(request):
        return {'source': 'source', 'items': [{'id': 'some_id'}]}

    return _mock_yt


@pytest.fixture
def mock_feedback(mockserver):
    @mockserver.json_handler(
        '/passenger-feedback/passenger-feedback/v1/retrieve',
    )
    def _mock_feedback(request):
        return mockserver.make_response(status=404)

    return _mock_feedback
