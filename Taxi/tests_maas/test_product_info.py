import pytest


MAAS_DEFAULT_TARIFF = 'maas_s'
MAAS_XS_SETTINGS = {
    'sale_allowed': True,
    'coupon_series': 'coupon_series_id',
    'trips_count': 1,
    'duration_days': 31,
    'taxi_price': '999',
    'subscription_price': '999.4',
    'description_text_tanker_key': 'maas.tariffs.maas_s.description_text',
    'detailed_description_content_tanker_key': (
        'maas.tariffs.maas_s.detailed_description_content'
    ),
    'hints': ['hint_1', 'hint_2'],
    'title_tanker_key': 'maas.tariffs.maas_s.title',
    'toggle_title_tanker_key': 'maas.tariffs.maas_s.toggle_title',
    'composite_maas_tariff_id': 'maas_tariff_id',
    'active_image_tag': 'active_tag',
    'expired_image_tag': 'expired_tag',
    'outer_description_tanker_key': 'maas.tariffs.maas_s.outer_description',
}

MAAS_S_SETTINGS = {
    'sale_allowed': True,
    'coupon_series': 'coupon_series_id',
    'trips_count': 5,
    'duration_days': 31,
    'taxi_price': '1999',
    'subscription_price': '2999.4',
    'description_text_tanker_key': 'maas.tariffs.maas_s.description_text',
    'detailed_description_content_tanker_key': (
        'maas.tariffs.maas_s.detailed_description_content'
    ),
    'hints': ['hint_1', 'hint_2'],
    'title_tanker_key': 'maas.tariffs.maas_s.title',
    'toggle_title_tanker_key': 'maas.tariffs.maas_s.toggle_title',
    'composite_maas_tariff_id': 'maas_tariff_id',
    'active_image_tag': 'active_tag',
    'expired_image_tag': 'expired_tag',
    'reserved_image_tag': 'reserved_tag',
    'outer_description_tanker_key': 'maas.tariffs.maas_s.outer_description',
}

MAAS_M_SETTINGS = {
    'sale_allowed': True,
    'coupon_series': 'coupon_series_id',
    'trips_count': 10,
    'duration_days': 31,
    'taxi_price': '2999',
    'subscription_price': '3999',
    'description_text_tanker_key': 'maas.tariffs.maas_m.description_text',
    'detailed_description_content_tanker_key': (
        'maas.tariffs.maas_m.detailed_description_content'
    ),
    'hints': [],
    'title_tanker_key': 'maas.tariffs.maas_m.title',
    'toggle_title_tanker_key': 'maas.tariffs.maas_m.toggle_title',
    'composite_maas_tariff_id': 'maas_tariff_id',
    'active_image_tag': 'active_tag',
    'expired_image_tag': 'expired_tag',
    'reserved_image_tag': 'reserved_tag',
    'outer_description_tanker_key': 'maas.tariffs.maas_m.outer_description',
}

MAAS_S_SETTINGS_OBSOLETE = {
    'sale_allowed': False,
    'coupon_series': 'coupon_series_id',
    'trips_count': 5,
    'duration_days': 31,
    'taxi_price': '1999',
    'subscription_price': '2999',
    'description_text_tanker_key': 'maas.tariffs.maas_s.description_text',
    'detailed_description_content_tanker_key': (
        'maas.tariffs.maas_s.detailed_description_content'
    ),
    'hints': [],
    'title_tanker_key': 'maas.tariffs.maas_s.title',
    'toggle_title_tanker_key': 'maas.tariffs.maas_s.toggle_title',
    'composite_maas_tariff_id': 'maas_tariff_id',
    'active_image_tag': 'active_tag',
    'expired_image_tag': 'expired_tag',
    'reserved_image_tag': 'reserved_tag',
    'outer_description_tanker_key': 'maas.tariffs.maas_s.outer_description',
}

MAAS_TARIFFS = {
    'maas_s': MAAS_S_SETTINGS,
    'maas_m': MAAS_M_SETTINGS,
    'maas_s_obsolete': MAAS_S_SETTINGS_OBSOLETE,
    'maas_xs': MAAS_XS_SETTINGS,
}

MAAS_TARIFF_HINTS = {
    'hint_1': {
        'background_color': '#F1F0ED',
        'background_image_tag': 'hint_1_tag',
        'fullscreen_deeplink': 'yandextaxi://banner?id=hint_1_promotion',
        'text_color': '#000000',
        'title_tanker_key': 'maas.tariffs.hint_1_title',
    },
    'hint_2': {
        'background_color': '#F1F0ED',
        'background_image_tag': 'hint_2_tag',
        'fullscreen_deeplink': 'yandextaxi://banner?id=hint_2_promotion',
        'text_color': '#000000',
        'title_tanker_key': 'maas.tariffs.hint_2_title',
    },
}

MAAS_PAYMENT_METHODS_V2 = {
    'applepay': {
        'image_tag': 'applepay_image_tag',
        'title_tanker_key': 'payment_methods.applepay',
        'show_card_last_digits': False,
    },
    'googlepay': {
        'image_tag': 'googlepay_image_tag',
        'title_tanker_key': 'payment_methods.googlepay',
        'show_card_last_digits': False,
    },
    'card': {
        'image_tag': 'card_image_tag',
        'title_tanker_key': 'payment_methods.card',
        'show_card_last_digits': True,
    },
}


MAAS_DEFAULT_PAYMENT_METHODS = {'iphone': 'applepay', 'android': 'googlepay'}


@pytest.mark.translations(
    client_messages={
        'maas.choose_tariff_ui.details_button': {'ru': 'Узнать подробности'},
        'maas.choose_tariff_ui.start_paying_button': {'ru': 'Купить'},
        'maas.details_ui.title': {'ru': 'Как работает абонемент'},
        'maas.details_ui.ok_button': {'ru': 'Теперь понятно'},
        'maas.details_ui.start_paying_button': {'ru': 'Купить'},
        'maas.payment_method_ui.title.ios': {'ru': 'Apple Pay или карта?'},
        'maas.payment_method_ui.title.android': {
            'ru': 'Google Pay или карта?',
        },
        'maas.payment_method_ui.description.ios': {
            'ru': (
                'Нужно выбрать только один способ оплаты - '
                'Apple Pay или карта. '
                'Другой в транспорте работать не будет'
            ),
        },
        'maas.payment_method_ui.description.android': {
            'ru': (
                'Нужно выбрать только один способ оплаты - '
                'Google Pay или карта. '
                'Другой в транспорте работать не будет'
            ),
        },
        'maas.payment_method_ui.agreement_with_the_rules': {
            'ru': 'Нажимая "Продолжить", вы соглашаетесь с правилами сервиса',
        },
        'maas.payment_method_ui.warning_payment_via_vtb': {
            'ru': 'Оплата будет происходить через ВТБ',
        },
        'maas.payment_method_ui.pay_button_text': {'ru': 'Оплатить'},
        'maas.tariffs.maas_s.title': {'ru': 'МультиТранспорт'},
        'maas.tariffs.maas_m.title': {'ru': 'МультиТранспорт'},
        'maas.tariffs.maas_s.description_text': {
            'ru': (
                'Единый абонемент для поездок по городу. '
                'Входит от 5 до 10 поездок на такси'
            ),
        },
        'maas.tariffs.maas_m.description_text': {
            'ru': (
                'Единый абонемент для поездок по городу. '
                'Входит от 10 до 20 поездок на такси'
            ),
        },
        'maas.tariffs.maas_s.toggle_title': {'ru': 'S'},
        'maas.tariffs.maas_m.toggle_title': {'ru': 'M'},
        'maas.tariffs.maas_s.detailed_description_content': {
            'ru': (
                'Поездки на такси от и до метро поблизости '
                'включены в стоимость'
            ),
        },
        'maas.tariffs.maas_m.detailed_description_content': {
            'ru': (
                'Поездки на такси от и до метро поблизости '
                'включены в стоимость'
            ),
        },
        'maas.tariffs.hint_1_title': {'ru': 'До метро'},
        'maas.tariffs.hint_2_title': {'ru': 'Как пользоваться'},
        'payment_methods.applepay': {'ru': 'Apple Pay'},
        'payment_methods.googlepay': {'ru': 'Google Pay'},
        'payment_methods.card': {'ru': 'Карта'},
    },
)
@pytest.mark.experiments3(filename='config3_maas_tariffs.json')
@pytest.mark.config(MAAS_DEFAULT_TARIFF=MAAS_DEFAULT_TARIFF)
@pytest.mark.config(MAAS_TARIFF_HINTS=MAAS_TARIFF_HINTS)
@pytest.mark.config(MAAS_PAYMENT_METHODS_V2=MAAS_PAYMENT_METHODS_V2)
@pytest.mark.config(MAAS_DEFAULT_PAYMENT_METHODS=MAAS_DEFAULT_PAYMENT_METHODS)
@pytest.mark.parametrize(
    'application, has_nfc, response_json',
    [
        pytest.param(
            'iphone',
            None,
            'product_info_response_with_apay.json',
            marks=pytest.mark.experiments3(
                filename='maas_payment_methods_with_app_pay.json',
            ),
            id='apay_enabled',
        ),
        pytest.param(
            'iphone',
            None,
            'product_info_response_ios_card_only.json',
            id='apay_disabled_by_exp',
        ),
        pytest.param(
            'android',
            None,
            'product_info_response_android_card_only.json',
            marks=pytest.mark.experiments3(
                filename='maas_payment_methods_with_app_pay.json',
            ),
            id='gpay_disabled_by_nfc_1',
        ),
        pytest.param(
            'android',
            False,
            'product_info_response_android_card_only.json',
            marks=pytest.mark.experiments3(
                filename='maas_payment_methods_with_app_pay.json',
            ),
            id='gpay_disabled_by_nfc_2',
        ),
        pytest.param(
            'android',
            True,
            'product_info_response_with_gpay.json',
            marks=pytest.mark.experiments3(
                filename='maas_payment_methods_with_app_pay.json',
            ),
            id='gpay_enabled',
        ),
        pytest.param(
            'android',
            True,
            'product_info_response_android_card_only.json',
            id='gpay_disabled_by_exp',
        ),
    ],
)
async def test_product_info(
        taxi_maas, load_json, application, has_nfc, response_json,
):
    application_header = (
        'app_name=iphone,app_ver1=4,app_ver2=90'
        if application == 'iphone'
        else 'app_name=android,app_brand=yataxi'
    )
    headers = {
        'X-Yandex-Uid': '123456',
        'X-YaTaxi-UserId': 'testsuite',
        'X-Request-Application': application_header,
    }
    reqest_body = {'has_nfc': has_nfc} if has_nfc is not None else {}
    response = await taxi_maas.post(
        '/4.0/maas/v1/subscription/product-info',
        headers=headers,
        json=reqest_body,
    )
    assert response.status_code == 200
    assert response.json() == load_json(response_json)
