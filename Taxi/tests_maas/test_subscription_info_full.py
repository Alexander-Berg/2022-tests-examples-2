import pytest

import common


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
        'pay_systems': {
            'mastercard': {
                'image_tag': 'mastercard_card',
                'title_tanker_key': (
                    'maas.subscription_info_ui.'
                    'subscription_card_button.title.mastercard'
                ),
            },
        },
    },
}


MAAS_DEFAULT_PAYMENT_METHODS = {'iphone': 'applepay', 'android': 'googlepay'}


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


MAAS_TARIFF_SETTINGS = {
    'sale_allowed': True,
    'coupon_series': 'coupon_series_id',
    'trips_count': 10,
    'duration_days': 31,
    'taxi_price': '1999',
    'subscription_price': '2999',
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


MAAS_TARIFFS = {'maas_tariff_id': MAAS_TARIFF_SETTINGS}


DEFAULT_VTB_FAILED_CHANGE_ACCESS_KEY_UI = {
    'change_button_text': 'Продолжить',
    'title': 'Изменить способ оплаты?',
    'do_not_change_button_text': 'Оставить как есть',
    'description': 'За месяц его можно изменить только 3 раза.',
}


CLIENT_MESSAGES = {
    'maas.payment_method_ui.title.ios': {'ru': 'Apple Pay или карта?'},
    'maas.payment_method_ui.title.android': {'ru': 'Google Pay или карта?'},
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
    'payment_methods.applepay': {'ru': 'Apple Pay'},
    'payment_methods.googlepay': {'ru': 'Google Pay'},
    'payment_methods.card': {'ru': 'Карта'},
    'maas.tariffs.hint_1_title': {'ru': 'До метро'},
    'maas.tariffs.hint_2_title': {'ru': 'Как пользоваться'},
    'maas.subscription_info_ui.title': {'ru': 'МультиТранспорт'},
    'maas.subscription_info_ui.subscription_expiration_day': {
        'ru': 'осталось до %(expiration_day)s',
    },
    'maas.subscription_info_ui.trips_info': {'ru': '%(trips_left)s поездок'},
    'maas.subscription_info_ui.subscription_expired': {'ru': 'Закончился'},
    'maas.subscription_info_ui.extend_button_text': {'ru': 'Продлить'},
    'maas.subscription_info_ui.subscription_card_button.subtitle': {
        'ru': 'Для прохода в транспорте',
    },
    'maas.subscription_info_ui.subscription_card_button.title.ios': {
        'ru': 'Apple Pay',
    },
    'maas.subscription_info_ui.subscription_card_button.title.android': {
        'ru': 'Google Pay',
    },
    'maas.subscription_info_ui.subscription_card_button.title.mastercard': {
        'ru': 'MasterCard',
    },
    'maas.payment_method_ui.change_access_key_title.android': {
        'ru': 'Способ оплаты',
    },
    'maas.payment_method_ui.change_access_key_title.ios': {
        'ru': 'Способ оплаты',
    },
    'maas.payment_method_ui.change_access_key_button_text': {'ru': 'Изменить'},
    'maas.subscription_info_ui.subscription_reserved': {
        'ru': 'Активация подписки',
    },
    'maas.payment_method_ui.change_access_key_description.ios': {
        'ru': (
            'Нужно выбрать только один способ оплаты - '
            'Apple Pay или карта. '
            'Другой в транспорте работать не будет'
        ),
    },
    'maas.payment_method_ui.change_access_key_description.android': {
        'ru': (
            'Нужно выбрать только один способ оплаты - '
            'Google Pay или карта. '
            'Другой в транспорте работать не будет'
        ),
    },
    'maas.payment_method_ui.change_access_key_agreement_with_the_rules': {
        'ru': 'Нажимая "Продолжить", вы соглашаетесь с правилами сервиса',
    },
    'maas.payment_method_ui.change_access_key_warning_payment_via_vtb': {
        'ru': '',
    },
    'maas.subscription_info_ui.reserved_status_explanation': {
        'ru': 'Это может занять некоторое время',
    },
    'maas.change_access_key_attempts_ui.title': {
        'ru': 'Изменить способ оплаты?',
    },
    'maas.change_access_key_attempts_ui.description': {
        'ru': 'За месяц его можно изменить только %(default_attempts)s раза.',
    },
    'maas.change_access_key_attempts_ui.attempts_left': {
        'ru': 'Осталось %(attempts_left)s',
    },
    'maas.change_access_key_attempts_ui.change_access_key_button_text': {
        'ru': 'Продолжить',
    },
    'maas.change_access_key_attempts_ui.'
    'do_not_change_access_key_button_text': {'ru': 'Оставить как есть'},
    'maas.change_access_key_attempts_ui.title_no_attempts_left': {
        'ru': 'В этом месяце способ оплаты больше не изменить',
    },
    'maas.change_access_key_attempts_ui.description_no_attempts_left': {
        'ru': 'Это можно делать только %(default_attempts)s раза за месяц.',
    },
    'maas.change_access_key_attempts_ui.'
    'can_not_change_access_key_button_text': {'ru': 'Понятно'},
    'maas.subscription_info_ui.details_button_text': {'ru': 'Подробнее'},
    'maas.details_ui.title': {'ru': 'Мультитранспорт'},
    'maas.details_ui.ok_button': {'ru': 'Теперь понятно'},
    'maas.tariffs.maas_s.detailed_description_content': {
        'ru': 'Подробное описание тарифа S',
    },
    'maas.tariffs.maas_m.detailed_description_content': {
        'ru': 'Подробное описание тарифа M',
    },
    'maas.tariffs.maas_l.detailed_description_content': {
        'ru': 'Подробное описание тарифа L',
    },
}


@pytest.fixture(name='vtb_mock')
def mock_vtb_api(mockserver):
    class Context:
        def call(
                self,
                payment_method_type='CARD',
                is_fail=False,
                is_without_card=False,
                key_change_left=2,
        ):
            @mockserver.json_handler('/vtb-maas/api/0.1/user/info')
            def _user_info_mock(request):
                common.check_vtb_authorization(request)

                if is_fail:
                    return mockserver.make_response(status=500, json={})

                response = {
                    'status': 'ACTIVE',
                    'key_change_left': key_change_left,
                    'key_change_limit': 5,
                    'hash_key': 'dba1-abda',
                }

                if is_without_card:
                    return response

                response.update(
                    {
                        'pay_system': 'MC',
                        'masked_pan': '5505',
                        'type': payment_method_type,
                    },
                )

                return response

    return Context()


@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
@pytest.mark.pgsql('maas', files=['subscriptions.sql', 'users.sql'])
@pytest.mark.config(MAAS_PAYMENT_METHODS_V2=MAAS_PAYMENT_METHODS_V2)
@pytest.mark.config(MAAS_DEFAULT_PAYMENT_METHODS=MAAS_DEFAULT_PAYMENT_METHODS)
@pytest.mark.config(MAAS_TARIFF_HINTS=MAAS_TARIFF_HINTS)
@pytest.mark.config(MAAS_TARIFFS=MAAS_TARIFFS)
@pytest.mark.config(MAAS_ACCESS_KEY_CHANGE_ATTEMPTS_NUMBER=3)
@pytest.mark.experiments3(filename='maas_payment_methods.json')
@pytest.mark.experiments3(filename='config3_maas_tariffs.json')
@pytest.mark.parametrize(
    'is_vtb_fail, is_without_card',
    (
        pytest.param(False, False, id='normal'),
        pytest.param(True, False, id='vtb_fail'),
        pytest.param(False, True, id='without_card_in_vtb_response'),
    ),
)
@pytest.mark.parametrize(
    'payment_method,expected_answer',
    (
        ['CARD', 'subscription_info_full_response_ios.json'],
        ['APAY', 'subscription_info_full_response_ios_applepay.json'],
    ),
)
async def test_active_subscription_iphone(
        taxi_maas,
        load_json,
        vtb_mock,
        coupon_state_mock,
        is_vtb_fail,
        is_without_card,
        payment_method,
        expected_answer,
):
    phone_id = 'active_phone_id'
    coupon_state_mock(phone_id, trips_count=0)
    vtb_mock.call(
        payment_method_type=payment_method,
        is_fail=is_vtb_fail,
        is_without_card=is_without_card,
    )

    headers = {
        'X-YaTaxi-PhoneId': phone_id,
        'X-YaTaxi-UserId': 'user_id',
        'X-Yandex-Uid': 'yandex_uid',
        'X-Request-Application': 'app_name=iphone,app_ver1=4,app_ver2=90',
    }

    response = await taxi_maas.post(
        '/4.0/maas/v1/subscription/info/full', headers=headers, json={},
    )
    assert response.status_code == 200
    response_body = response.json()
    assert 'expiring_info' in response_body['subscription_info_ui']
    response_body['subscription_info_ui'].pop('expiring_info')
    expected_response = load_json(expected_answer)

    if is_vtb_fail or is_without_card:
        expected_response['subscription_info_ui'].pop(
            'subscription_card_button',
        )
    if is_vtb_fail:
        expected_response[
            'change_access_key_attempts_ui'
        ] = DEFAULT_VTB_FAILED_CHANGE_ACCESS_KEY_UI
    assert response_body == expected_response


@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
@pytest.mark.pgsql('maas', files=['subscriptions.sql', 'users.sql'])
@pytest.mark.config(MAAS_PAYMENT_METHODS_V2=MAAS_PAYMENT_METHODS_V2)
@pytest.mark.config(MAAS_DEFAULT_PAYMENT_METHODS=MAAS_DEFAULT_PAYMENT_METHODS)
@pytest.mark.config(MAAS_TARIFF_HINTS=MAAS_TARIFF_HINTS)
@pytest.mark.config(MAAS_TARIFFS=MAAS_TARIFFS)
@pytest.mark.config(MAAS_ACCESS_KEY_CHANGE_ATTEMPTS_NUMBER=3)
@pytest.mark.experiments3(filename='maas_payment_methods.json')
@pytest.mark.experiments3(filename='config3_maas_tariffs.json')
@pytest.mark.parametrize(
    'has_nfc, response_file, is_vtb_fail, key_change_left',
    (
        pytest.param(
            True,
            'subscription_info_full_response_android.json',
            False,
            2,
            id='has_nfc',
        ),
        pytest.param(
            False,
            'subscription_info_full_response_android_no_nfc.json',
            False,
            2,
            id='no_nfc',
        ),
        pytest.param(
            True,
            'subscription_info_full_response_vtb_fail.json',
            True,
            2,
            id='vtb_fail',
        ),
        pytest.param(
            True,
            'subscription_info_full_response'
            '_no_change_access_key_attempts_left.json',
            False,
            0,
            id='no_change_access_key_attempts_left',
        ),
    ),
)
async def test_active_subscription_android(
        taxi_maas,
        load_json,
        vtb_mock,
        coupon_state_mock,
        has_nfc,
        key_change_left,
        response_file,
        is_vtb_fail,
):
    phone_id = 'active_phone_id'
    coupon_state_mock(phone_id)

    if has_nfc:
        vtb_mock.call(
            payment_method_type='GPAY',
            is_fail=is_vtb_fail,
            key_change_left=key_change_left,
        )
    else:
        vtb_mock.call(is_fail=is_vtb_fail, key_change_left=key_change_left)

    headers = {
        'X-YaTaxi-PhoneId': 'active_phone_id',
        'X-YaTaxi-UserId': 'user_id',
        'X-Yandex-Uid': 'yandex_uid',
        'X-Request-Application': 'app_name=android,app_brand=yataxi',
    }
    body = {'has_nfc': has_nfc}
    response = await taxi_maas.post(
        '/4.0/maas/v1/subscription/info/full', headers=headers, json=body,
    )
    assert response.status_code == 200
    response_body = response.json()
    assert 'expiring_info' in response_body['subscription_info_ui']
    response_body['subscription_info_ui'].pop('expiring_info')
    expected_response = load_json(response_file)
    if is_vtb_fail:
        expected_response['subscription_info_ui'].pop(
            'subscription_card_button',
        )
    assert response_body == expected_response


@pytest.mark.pgsql('maas', files=['subscriptions.sql', 'users.sql'])
@pytest.mark.config(MAAS_PAYMENT_METHODS_V2=MAAS_PAYMENT_METHODS_V2)
@pytest.mark.config(MAAS_DEFAULT_PAYMENT_METHODS=MAAS_DEFAULT_PAYMENT_METHODS)
@pytest.mark.config(MAAS_TARIFF_HINTS=MAAS_TARIFF_HINTS)
@pytest.mark.experiments3(filename='config3_maas_tariffs.json')
async def test_not_found_subscription(taxi_maas):
    headers = {
        'X-YaTaxi-PhoneId': 'not_found_phone_id',
        'X-YaTaxi-UserId': 'user_id',
        'X-Yandex-Uid': 'yandex_uid',
    }
    response = await taxi_maas.post(
        '/4.0/maas/v1/subscription/info/full', headers=headers, json={},
    )
    assert response.status_code == 404


@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
@pytest.mark.pgsql('maas', files=['subscriptions.sql', 'users.sql'])
@pytest.mark.config(MAAS_PAYMENT_METHODS_V2=MAAS_PAYMENT_METHODS_V2)
@pytest.mark.config(MAAS_DEFAULT_PAYMENT_METHODS=MAAS_DEFAULT_PAYMENT_METHODS)
@pytest.mark.config(MAAS_TARIFF_HINTS=MAAS_TARIFF_HINTS)
@pytest.mark.config(MAAS_TARIFFS=MAAS_TARIFFS)
@pytest.mark.config(MAAS_ACCESS_KEY_CHANGE_ATTEMPTS_NUMBER=3)
@pytest.mark.experiments3(filename='maas_payment_methods.json')
@pytest.mark.experiments3(filename='config3_maas_tariffs.json')
async def test_expired_subscription(taxi_maas, load_json):
    headers = {
        'X-YaTaxi-PhoneId': 'expired_phone_id',
        'X-YaTaxi-UserId': 'user_id',
        'X-Yandex-Uid': 'yandex_uid',
    }
    response = await taxi_maas.post(
        '/4.0/maas/v1/subscription/info/full', headers=headers, json={},
    )
    assert response.status_code == 200
    assert response.json() == load_json('expired_response.json')


@pytest.mark.translations(client_messages=CLIENT_MESSAGES)
@pytest.mark.pgsql('maas', files=['subscriptions.sql', 'users.sql'])
@pytest.mark.config(MAAS_PAYMENT_METHODS_V2=MAAS_PAYMENT_METHODS_V2)
@pytest.mark.config(MAAS_DEFAULT_PAYMENT_METHODS=MAAS_DEFAULT_PAYMENT_METHODS)
@pytest.mark.config(MAAS_TARIFF_HINTS=MAAS_TARIFF_HINTS)
@pytest.mark.config(MAAS_TARIFFS=MAAS_TARIFFS)
@pytest.mark.experiments3(filename='config3_maas_tariffs.json')
async def test_reserved_subscription(taxi_maas, load_json):
    headers = {
        'X-YaTaxi-PhoneId': 'reserved_phone_id',
        'X-YaTaxi-UserId': 'user_id',
        'X-Yandex-Uid': 'yandex_uid',
    }
    response = await taxi_maas.post(
        '/4.0/maas/v1/subscription/info/full', headers=headers, json={},
    )
    assert response.status_code == 200
    assert response.json() == load_json('reserved_response.json')
