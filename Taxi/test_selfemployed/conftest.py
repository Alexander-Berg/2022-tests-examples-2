# pylint: disable=redefined-outer-name,W0401,W0614,C0302
# pylint: disable=invalid-string-quote
import functools
import logging

import pytest

import selfemployed.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from selfemployed.generated.web import web_context as context_module

pytest_plugins = ['selfemployed.generated.service.pytest_plugins']

# Disable a wall of useless text
logging.getLogger('zeep').setLevel(logging.INFO)

TRANSLATIONS = {
    'agreement_agreed_checkbox': {'ru': 'Я ознакомился и согласен'},
    'agreement_confidential': {'ru': 'Политика конфиденциальных данных'},
    'agreement_gas_stations': {'ru': 'Оферта Яндекс.Заправок'},
    'agreement_taxi_corporate_offer': {'ru': 'Оферта по перевозке'},
    'agreement_taxi_marketing_offer': {'ru': 'Маркетинговая оферта'},
    'agreement_taxi_offer': {'ru': 'Оферта'},
    'agreement_taxi_transfer_to_third_party': {
        'ru': 'Передача данных моей учетной записи',
    },
    'error_bad_sms_code': {'ru': 'Введен неверный код подтверждения'},
    'error_sms_code_expired': {'ru': 'Код истек'},
    'error_incorrect_account_format': {'ru': 'Номер счёта введен некорректно'},
    'error_incorrect_bik': {'ru': 'БИК введен некорректно'},
    'error_bank_not_eligible_for_nonresident': {
        'ru': 'Данный банк не работает с нерезидентами',
    },
    'error_bank_not_eligible_title': {
        'ru': 'Заголовок: Данный банк не работает с нерезидентами',
    },
    'error_bank_not_eligible_subtitle': {
        'ru': 'Данный банк не работает с нерезидентами - длинный текст',
    },
    'error_bank_not_eligible_button_text': {'ru': 'Понятно'},
    'error_no_selfemployed_found': {'ru': 'Вы не являетесь самозанятым'},
    'error_nalogru_unavailable': {'ru': 'Мой Налог временно недоступен'},
    'intro_fast_money_subtitle': {'ru': 'Подзаголовок'},
    'intro_fast_money_title': {'ru': 'Деньги на карту сразу'},
    'intro_month_priority_subtitle': {'ru': 'Подзаголовок'},
    'intro_month_priority_title': {'ru': 'Приоритет на месяц'},
    'intro_no_commision_subtitle': {'ru': 'Подзаголовок'},
    'intro_no_commision_title': {'ru': 'Нет комиссии таксопарка'},
    'requisites_screen_button_text': {'ru': 'Далее'},
    'requisites_screen_description': {
        'ru': 'Нам нужны ваши реквизиты, чтобы...',
    },
    'requisites_screen_update_button_text': {'ru': 'Отправить'},
    'requisites_screen_update_description': {
        'ru': 'Нам нужны ваши реквизиты, чтобы обновить',
    },
    'step_title_address': {'ru': 'Укажите адрес прописки'},
    'step_title_agreement': {'ru': 'Соглашение'},
    'step_title_finish': {'ru': 'Поздравляем'},
    'step_title_intro': {'ru': 'Получите статус самозанятого'},
    'step_title_nalog_app': {'ru': 'Стать самозанятым'},
    'step_title_overview': {'ru': 'Регистрация'},
    'step_title_permission': {'ru': 'Свяжите профили'},
    'step_title_phone_number': {'ru': 'Проверка номера'},
    'step_title_await_own_park': {'ru': 'Потерпите'},
    'step_title_requisites': {'ru': 'Укажите реквизиты'},
    'step_title_sms': {'ru': 'Код из СМС'},
    'step_title_counter': {'ru': '{number} из {count}'},
    'intro_subtitle': {'ru': 'Быть партнером хорошо'},
    'agreement_subtitle': {'ru': 'Соглашение'},
    'selfemployed_banner_1_title': {'ru': 'Зарабатывайте больше (1)'},
    'selfemployed_banner_1_subtitle': {
        'ru': 'У самозанятых нет лишних комиссий',
    },
    'selfemployed_banner_3_title': {'ru': 'Зарабатывайте больше (2)'},
    'selfemployed_banner_3_subtitle': {
        'ru': 'У самозанятых нет лишних комиссий',
    },
    'selfemployed_banner_4_title': {'ru': 'Зарабатывайте больше (3)'},
    'selfemployed_banner_4_subtitle': {
        'ru': 'У самозанятых нет лишних комиссий',
    },
    'selfemployed_banner_5_title': {'ru': 'Зарабатывайте больше (4)'},
    'selfemployed_banner_5_subtitle': {
        'ru': 'У самозанятых нет лишних комиссий',
    },
    'selfemployed_banner_6_title': {'ru': 'Зарабатывайте больше (5)'},
    'selfemployed_banner_6_subtitle': {
        'ru': 'У самозанятых нет лишних комиссий',
    },
    'selfemployed_banner_7_title': {'ru': 'Зарабатывайте больше (6)'},
    'selfemployed_banner_7_subtitle': {
        'ru': 'У самозанятых нет лишних комиссий',
    },
    'receipt_item': {'ru': 'заказ'},
    'receipt_subvention_item': {'ru': 'субсидия'},
    'agreement_give_permission': {'ru': 'Я даю свое согласие'},
    'push_permission_error': {
        'ru': (
            '**Разрешение не получено** '
            'Откройте «Мой налог» и поставьте '
            'галочку у каждого пункта'
        ),
    },
    'push_new_profile': {
        'ru': ('**Создание нового профиля** ' 'Подождите 30 секунд'),
    },
    'sms_sent_again': {'ru': 'СМС отправлено повторно'},
    'error_inn_already_registered': {'ru': 'Ваш ИНН уже есть в базе...'},
    'push_requisites_saved': {'ru': 'Реквизиты сохранены'},
    'push_park_created': {'ru': 'Парк создан'},
    'referral_main_subtitle': {'ru': 'Ваш промокод'},
    'referral_main_text': {'ru': 'Текст описания, зачем нужно делиться'},
    'referral_bad_promocode': {'ru': 'Плохой промокод'},
    'referral_promocode_accepted': {'ru': 'Промокод ок'},
    'referral_help_title': {'ru': 'Пригласи друзей...'},
    'referral_help_main_text': {'ru': '...и получи леща!'},
    'referral_help_requirement_title': {'ru': 'Условия для друзей'},
    'referral_help_requirement_elem_1': {'ru': 'Пункт 1'},
    'referral_help_requirement_elem_2': {'ru': 'Пункт 2'},
    'referral_help_requirement_elem_3': {'ru': 'Пункт 3'},
    'referral_copy_text': {'ru': 'Хочешь денег? Введи код: {promocode}'},
    'referral_error_promocode': {
        'ru': (
            'Приглашать друзей и получать за них смены '
            'могут только самозанятые водители'
        ),
    },
    'referral_how_it_works': {'ru': 'Это раздел только для смз'},
    'error_sms_limit_exceeded': {'ru': 'Достигнут предел отправки СМС'},
    'fns_unbound_notification': {
        'ru': 'Ваш профиль был заблокирован Восстановите статус самозанятого',
    },
    'cancel_receipt_reason_for_fns': {'ru': 'Чек сформирован ошибочно'},
    'self_employment_help_title1': {'ru': 'Вопрос 1'},
    'self_employment_help_subtitle1': {'ru': 'Ответ 1'},
    'self_employment_help_title2': {'ru': 'Вопрос 2'},
    'self_employment_help_subtitle2': {'ru': 'Ответ 2'},
    'self_employment_help_title3': {'ru': 'Вопрос 3'},
    'self_employment_help_subtitle3': {'ru': 'Ответ 3'},
    'self_employment_help_moscow_title': {'ru': 'Москва'},
    'self_employment_help_kaluga_title': {'ru': 'Калуга'},
    'self_employment_help_all_russia_title': {'ru': 'Россия'},
    'se_await_park_created_title': {'ru': 'Заголовок'},
    'se_await_park_created_subtitle': {'ru': 'Подзаголовок'},
    'se_await_park_created_text': {'ru': 'Текст'},
    'error_park_creation_not_started': {'ru': 'Создание парка не начиналось'},
    'error_park_creation_not_finished': {
        'ru': 'Создание парка ещё не закончено. Пожалуйста, подождите',
    },
    'self_employment_contact_support_button': {'ru': 'Связаться с поддержкой'},
    'fns_rebind_failure_bad_driver': {'ru': 'Вы не СМЗ'},
    'fns_rebind_failure_unregistered': {
        'ru': 'Встаньте на учет в Моем налоге',
    },
    'fns_rebind_success': {'ru': 'Запрос отправлен'},
    'error_of_binding': {'ru': 'Для продолжения необходима привязка к ФНС'},
    'error_taxpayer_unregistered': {
        'ru': 'Налогоплательщик не найден в ФНС по номеру телефона',
    },
    'error_document_country_forbidden': {
        'ru': 'Регистрация запрещена для страны проживания налогоплательщика',
    },
    'error_required_agreements': {'ru': 'Требуемые соглашения не принимаются'},
    'agreement_document_not_found': {'ru': 'Документ соглашения не найден'},
    'agreement_document_not_found_by_id': {
        'ru': 'Документ соглашения по id не найден',
    },
    'sms_code_required': {'ru': 'sms код не предоставлен'},
    'sms_track_expired': {
        'ru': 'Срок действия sms кода подтверждения номера телефона истек',
    },
    'bad_sms_code': {'ru': 'неверный смс кода'},
    'nalogru_binding_incomplete': {
        'ru': 'Процесс привязки к Nalogru является неполным',
    },
    'bad_request': {
        'ru': 'Некоторые параметры запроса отсутствуют или невалидны',
    },
    'sms_limit_exceeded': {
        'ru': 'Превышено предельное количество sms сообщений. Пожалуйста подождите',  # noqa: E501
    },
    'taxpayer_not_found': {
        'ru': 'В ФНС нет налогоплательщика, зарегистрированного по этому телефону',  # noqa: E501
    },
    'park_callback_error': {
        'ru': 'нет записи с идентификатором selfemployed_id',
    },
    'profile_not_found': {'ru': 'профиль не найден'},
    'taxpayer_unregistered': {'ru': 'налогоплательщика не зарегистрирован'},
    'not_selfemployed': {'ru': 'водитель не является самозанятым'},
    'taxpayer_already_bound': {'ru': 'налогоплательщик, уже привязан'},
    'park_not_found': {'ru': 'Парк не найден'},
    'passport_invalid': {'ru': 'Паспорт недействителен'},
    'passport_is_valid': {'ru': 'Паспорт действителен'},
    'sbp_bank_name.test_bank': {'ru': 'Test Bank'},
    'admin_driver_profile_v1': {'ru': 'Профиль СМЗ v1'},
    'admin_driver_profile_v2': {'ru': 'Профиль СМЗ v2'},
    'admin_not_selfemployed': {'ru': 'Не самозанятый'},
    'admin_driver_updated_at': {'ru': 'Обновлялся {updated_at}'},
    'admin_driver_status': {'ru': 'Статус привязки {status}'},
    'admin_driver_registered_at': {
        'ru': 'Зарегистрирован {reg_time}, отвязан {unreg_time}',
    },
    'admin_driver_permissions': {'ru': 'Выданные права: {permissions}'},
    'admin_not_partner': {'ru': 'СМЗ отвязан'},
    'admin_unregistered': {'ru': 'Больше не самозанятый'},
    'admin_driver_profile_info': {
        'ru': (
            'inn_pd_id: {inn_pd_id}\n'
            'Отправлять чеки: {do_send_receipts}\n'
            'Последний год превышения дохода: {exceeded_income_year}'
        ),
    },
    'admin_driver_se_direct': {
        'ru': 'Прямой партнер\nИзначальный профиль: {initial_profile_id}',
    },
    'admin_driver_se_quasi': {'ru': 'Парковый СМЗ'},
    'intro_screen_update_app': {'ru': 'Обновите приложение'},
    'error_fns_temporary_registration': {'ru': 'У вас временная регистрация'},
    'success_fns_temporary_registration': {'ru': 'Успешно зарегистрирован'},
    'failure_fns_temporary_registration': {'ru': 'Регистрация неуспешна'},
}

GAS_STATIONS_OFFER_URL = 'https://yandex.ru/legal/zapravki_postpaidtaxi_offer/'
SELFEMPLOYED_DISABLE_CANCEL_SUBVENTION = False
SELFEMPLOYED_DISABLE_CANCEL_SUBVENTION_JOB = False

PRO_FNS_SELFEMPLOYMENT_AWAIT_PARK_CREATED_SETTINGS_RESIDENT_SRC = {
    'items': [
        {
            'subtitle': 'se_await_park_created_subtitle',
            'horizontal_divider_type': 'none',
            'id': '11',
            'type': 'header',
            'gravity': 'left',
        },
        {
            'text': 'se_await_park_created_text',
            'horizontal_divider_type': 'none',
            'id': '12',
            'type': 'text',
        },
    ],
    'bottom_items': [
        {
            'accent': True,
            'title': 'se_await_park_created_title',
            'horizontal_divider_type': 'none',
            'id': '13',
            'type': 'button',
            'payload': {'type': 'navigate_await_park_created'},
            'cool_down_info': {'end_time': 10},
        },
    ],
}
PRO_FNS_SELFEMPLOYMENT_AWAIT_PARK_CREATED_SETTINGS_NOT_RESIDENT_SRC = {
    'items': [
        {
            'subtitle': 'se_await_park_created_subtitle',
            'horizontal_divider_type': 'none',
            'id': '11',
            'type': 'header',
            'gravity': 'left',
        },
        {
            'text': 'se_await_park_created_text',
            'horizontal_divider_type': 'none',
            'id': '12',
            'type': 'text',
        },
    ],
    'bottom_items': [
        {
            'accent': True,
            'title': 'se_await_park_created_title',
            'horizontal_divider_type': 'none',
            'id': '13',
            'type': 'button',
            'payload': {'type': 'navigate_await_park_created'},
            'cool_down_info': {'end_time': 10},
        },
    ],
}
PRO_FNS_SELFEMPLOYMENT_AWAIT_PARK_CREATED_SETTINGS_RESIDENT_DST = {
    'items': [
        {
            'subtitle': 'Подзаголовок',
            'horizontal_divider_type': 'none',
            'id': '11',
            'type': 'header',
            'gravity': 'left',
        },
        {
            'text': 'Текст',
            'horizontal_divider_type': 'none',
            'id': '12',
            'type': 'text',
        },
    ],
    'bottom_items': [
        {
            'accent': True,
            'title': 'Заголовок',
            'horizontal_divider_type': 'none',
            'id': '13',
            'type': 'button',
            'payload': {'type': 'navigate_await_park_created'},
            'cool_down_info': {'end_time': 10},
        },
    ],
}
PRO_FNS_SELFEMPLOYMENT_AWAIT_PARK_CREATED_SETTINGS_NOT_RESIDENT_DST = {
    'items': [
        {
            'subtitle': 'Подзаголовок',
            'horizontal_divider_type': 'none',
            'id': '11',
            'type': 'header',
            'gravity': 'left',
        },
        {
            'text': 'Текст',
            'horizontal_divider_type': 'none',
            'id': '12',
            'type': 'text',
        },
    ],
    'bottom_items': [
        {
            'accent': True,
            'title': 'Заголовок',
            'horizontal_divider_type': 'none',
            'id': '13',
            'type': 'button',
            'payload': {'type': 'navigate_await_park_created'},
            'cool_down_info': {'end_time': 10},
        },
    ],
}

PRO_FNS_SELFEMPLOYMENT_HELP_INFO_SETTINGS_NOT_SELFREG_SRC = {
    'items': [
        {
            'subtitle': 'se_await_park_created_subtitle',
            'horizontal_divider_type': 'none',
            'id': '11',
            'type': 'header',
            'gravity': 'left',
        },
        {
            'text': 'se_await_park_created_text',
            'horizontal_divider_type': 'none',
            'id': '12',
            'type': 'text',
        },
    ],
    'bottom_items': [
        {
            'accent': True,
            'title': 'se_await_park_created_title',
            'horizontal_divider_type': 'none',
            'id': '13',
            'type': 'button',
            'payload': {'type': 'navigate_await_park_created'},
            'cool_down_info': {'end_time': 10},
        },
    ],
}
PRO_FNS_SELFEMPLOYMENT_HELP_INFO_SETTINGS_SELFREG_SRC = {
    'items': [
        {
            'subtitle': 'se_await_park_created_subtitle',
            'horizontal_divider_type': 'none',
            'id': '11',
            'type': 'header',
            'gravity': 'left',
        },
        {
            'text': 'se_await_park_created_text',
            'horizontal_divider_type': 'none',
            'id': '12',
            'type': 'text',
        },
    ],
    'bottom_items': [
        {
            'accent': True,
            'title': 'se_await_park_created_title',
            'horizontal_divider_type': 'none',
            'id': '13',
            'type': 'button',
            'payload': {'type': 'navigate_await_park_created'},
            'cool_down_info': {'end_time': 10},
        },
    ],
}
PRO_FNS_SELFEMPLOYMENT_HELP_INFO_SETTINGS_NOT_SELFREG_DST = {
    'items': [
        {
            'subtitle': 'Подзаголовок',
            'horizontal_divider_type': 'none',
            'id': '11',
            'type': 'header',
            'gravity': 'left',
        },
        {
            'text': 'Текст',
            'horizontal_divider_type': 'none',
            'id': '12',
            'type': 'text',
        },
    ],
    'bottom_items': [
        {
            'accent': True,
            'title': 'Заголовок',
            'horizontal_divider_type': 'none',
            'id': '13',
            'type': 'button',
            'payload': {'type': 'navigate_await_park_created'},
            'cool_down_info': {'end_time': 10},
        },
    ],
}
PRO_FNS_SELFEMPLOYMENT_HELP_INFO_SETTINGS_SELFREG_DST = {
    'items': [
        {
            'subtitle': 'Подзаголовок',
            'horizontal_divider_type': 'none',
            'id': '11',
            'type': 'header',
            'gravity': 'left',
        },
        {
            'text': 'Текст',
            'horizontal_divider_type': 'none',
            'id': '12',
            'type': 'text',
        },
    ],
    'bottom_items': [
        {
            'accent': True,
            'title': 'Заголовок',
            'horizontal_divider_type': 'none',
            'id': '13',
            'type': 'button',
            'payload': {'type': 'navigate_await_park_created'},
            'cool_down_info': {'end_time': 10},
        },
    ],
}

TAXIMETER_FNS_SELF_EMPLOYMENT_HELP_SETTINGS = {
    'details': [
        {
            'preview_title': 'self_employment_help_title1',
            'title': 'self_employment_help_title1',
            'subtitle': 'self_employment_help_subtitle1',
        },
        {
            'preview_title': 'self_employment_help_title2',
            'title': 'self_employment_help_title2',
            'subtitle': 'self_employment_help_subtitle2',
        },
        {
            'preview_title': 'self_employment_help_title3',
            'title': 'self_employment_help_title3',
            'subtitle': 'self_employment_help_subtitle3',
        },
    ],
    'contact_support_button_text': 'self_employment_contact_support_button',
    'phones': [
        {
            'title': 'self_employment_help_moscow_title',
            'number': '+74951222122',
        },
        {
            'title': 'self_employment_help_kaluga_title',
            'number': '+74842218111',
        },
        {
            'title': 'self_employment_help_all_russia_title',
            'number': '88006008747',
        },
    ],
}

PRO_FNS_SELFEMPLOYMENT_AGREEMENT_SETTINGS_DEFAULT_VALUE = {
    'ui': [
        {
            'horizontal_divider_type': 'body_tail',
            'subtitle': 'agreement_subtitle',
            'type': 'header',
        },
        {
            'accent': True,
            'horizontal_divider_type': '',
            'payload': {
                'title': '',
                'type': 'navigate_url',
                'url': 'https://legal.yandex.ru/confidential/',
            },
            'right_icon': 'undefined',
            'title': 'agreement_confidential',
            'type': 'detail',
        },
        {
            'accent': True,
            'check_style': 'square',
            'checked': True,
            'enabled': True,
            'payload': {
                'id': 'agreement_confidential_checkbox',
                'type': 'self_employment_agreement',
                'required': True,
            },
            'horizontal_divider_type': '',
            'title': 'agreement_give_permission',
            'type': 'default_check',
        },
        {'type': 'title'},
        {
            'accent': True,
            'horizontal_divider_type': '',
            'payload': {
                'title': '',
                'type': 'navigate_url',
                'url': 'https://yandex.ru/legal/taxi_offer/',
            },
            'right_icon': 'undefined',
            'title': 'agreement_taxi_offer',
            'type': 'detail',
        },
        {
            'accent': True,
            'check_style': 'square',
            'checked': True,
            'enabled': True,
            'payload': {
                'id': 'agreement_taxi_offer_checkbox',
                'type': 'self_employment_agreement',
                'required': True,
            },
            'horizontal_divider_type': '',
            'title': 'agreement_agreed_checkbox',
            'type': 'default_check',
        },
        {'type': 'title'},
        {
            'accent': True,
            'horizontal_divider_type': '',
            'payload': {
                'title': '',
                'type': 'navigate_url',
                'url': 'https://yandex.ru/legal/taxi_marketing_offer/',
            },
            'right_icon': 'undefined',
            'title': 'agreement_taxi_marketing_offer',
            'type': 'detail',
        },
        {
            'accent': True,
            'check_style': 'square',
            'checked': True,
            'enabled': True,
            'payload': {
                'id': 'agreement_taxi_marketing_offer_checkbox',
                'type': 'self_employment_agreement',
                'required': True,
            },
            'horizontal_divider_type': '',
            'title': 'agreement_agreed_checkbox',
            'type': 'default_check',
        },
        {'type': 'title'},
        {
            'accent': True,
            'horizontal_divider_type': '',
            'payload': {
                'title': '',
                'type': 'navigate_url',
                'url': 'https://yandex.ru/legal/taxi_corporate_offer',
            },
            'right_icon': 'undefined',
            'title': 'agreement_taxi_corporate_offer',
            'type': 'detail',
        },
        {
            'accent': True,
            'check_style': 'square',
            'checked': True,
            'enabled': True,
            # no payload for test
            'horizontal_divider_type': '',
            'title': 'agreement_agreed_checkbox',
            'type': 'default_check',
        },
    ],
}


PRO_FNS_SELFEMPLOYMENT_AGREEMENT_SETTINGS_WITH_GAS_VALUE = {
    'ui': PRO_FNS_SELFEMPLOYMENT_AGREEMENT_SETTINGS_DEFAULT_VALUE['ui'] + [
        {'title': 'agreement_taxi_transfer_to_third_party'},
        {
            'type': 'default_check',
            'title': 'agreement_agreed_checkbox',
            'payload': {
                'id': 'agreement_taxi_transfer_to_third_party_checkbox',
                'type': 'self_employment_agreement',
                'required': False,
                'sync_group_id': 'gas_stations',
            },
        },
        {
            'title': 'agreement_gas_stations',
            'payload': {'url': '{GAS_STATIONS_OFFER_URL}'},
        },
        {
            'type': 'default_check',
            'title': 'agreement_agreed_checkbox',
            'payload': {
                'id': 'agreement_taxi_gas_stations_checkbox',
                'type': 'self_employment_agreement',
                'required': False,
                'sync_group_id': 'gas_stations',
            },
        },
    ],
}
AGREEMENT_DEFAULT_RESPONSE = {
    'items': [
        {
            'horizontal_divider_type': 'body_tail',
            'subtitle': 'Соглашение',
            'type': 'header',
        },
        {
            'accent': True,
            'horizontal_divider_type': '',
            'payload': {
                'title': '',
                'type': 'navigate_url',
                'url': 'https://legal.yandex.ru/confidential/',
            },
            'right_icon': 'undefined',
            'title': 'Политика конфиденциальных данных',
            'type': 'detail',
        },
        {
            'accent': True,
            'check_style': 'square',
            'checked': True,
            'enabled': True,
            'payload': {
                'id': 'agreement_confidential_checkbox',
                'type': 'self_employment_agreement',
                'required': True,
            },
            'horizontal_divider_type': '',
            'title': 'Я даю свое согласие',
            'type': 'default_check',
        },
        {'type': 'title'},
        {
            'accent': True,
            'horizontal_divider_type': '',
            'payload': {
                'title': '',
                'type': 'navigate_url',
                'url': 'https://yandex.ru/legal/taxi_offer/',
            },
            'right_icon': 'undefined',
            'title': 'Оферта',
            'type': 'detail',
        },
        {
            'accent': True,
            'check_style': 'square',
            'checked': True,
            'enabled': True,
            'payload': {
                'id': 'agreement_taxi_offer_checkbox',
                'type': 'self_employment_agreement',
                'required': True,
            },
            'horizontal_divider_type': '',
            'title': 'Я ознакомился и согласен',
            'type': 'default_check',
        },
        {'type': 'title'},
        {
            'accent': True,
            'horizontal_divider_type': '',
            'payload': {
                'title': '',
                'type': 'navigate_url',
                'url': 'https://yandex.ru/legal/taxi_marketing_offer/',
            },
            'right_icon': 'undefined',
            'title': 'Маркетинговая оферта',
            'type': 'detail',
        },
        {
            'accent': True,
            'check_style': 'square',
            'checked': True,
            'enabled': True,
            'payload': {
                'id': 'agreement_taxi_marketing_offer_checkbox',
                'type': 'self_employment_agreement',
                'required': True,
            },
            'horizontal_divider_type': '',
            'title': 'Я ознакомился и согласен',
            'type': 'default_check',
        },
        {'type': 'title'},
        {
            'accent': True,
            'horizontal_divider_type': '',
            'payload': {
                'title': '',
                'type': 'navigate_url',
                'url': 'https://yandex.ru/legal/taxi_corporate_offer',
            },
            'right_icon': 'undefined',
            'title': 'Оферта по перевозке',
            'type': 'detail',
        },
        {
            'accent': True,
            'check_style': 'square',
            'checked': True,
            'enabled': True,
            'horizontal_divider_type': '',
            'title': 'Я ознакомился и согласен',
            'type': 'default_check',
        },
    ],
}

AGREEMENT_WITH_DRIVER_LICENSE_RESPONSE = {
    'items': AGREEMENT_DEFAULT_RESPONSE['items'] + [
        {'title': 'Передача данных моей учетной записи'},
        {
            'type': 'default_check',
            'title': 'Я ознакомился и согласен',
            'payload': {
                'id': 'agreement_taxi_transfer_to_third_party_checkbox',
                'type': 'self_employment_agreement',
                'required': False,
                'sync_group_id': 'gas_stations',
            },
        },
        {
            'title': 'Оферта Яндекс.Заправок',
            'payload': {
                'url': 'https://yandex.ru/legal/zapravki_postpaidtaxi_offer/',
            },
        },
        {
            'type': 'default_check',
            'title': 'Я ознакомился и согласен',
            'payload': {
                'id': 'agreement_taxi_gas_stations_checkbox',
                'type': 'self_employment_agreement',
                'required': False,
                'sync_group_id': 'gas_stations',
            },
        },
    ],
}

TAXIMETER_FNS_SELF_EMPLOYMENT_BANKS_SETTINGS = [
    {
        'info': '',
        'title': 'Сбербанк',
        'url': (
            'https://taxi.yandex.ru/driver-partner/info/'
            '?articleId=360000702937&lang=ru'
            '&sectionId=360000189789'
        ),
    },
    {
        'info': '',
        'title': 'Альфа-банк',
        'url': (
            'https://taxi.yandex.ru/driver-partner/info/'
            '?articleId=360000702737&lang=ru'
            '&sectionId=360000189789'
        ),
    },
    {
        'info': '',
        'title': 'Тинькофф',
        'url': (
            'https://taxi.yandex.ru/driver-partner/info/'
            '?articleId=360000702897&lang=ru'
            '&sectionId=360000189789'
        ),
    },
    {
        'info': '',
        'title': 'ВТБ',
        'url': (
            'https://taxi.yandex.ru/driver-partner/info/'
            '?articleId=360000695638&lang=ru'
            '&sectionId=360000189789'
        ),
    },
]

PRO_FNS_SELFEMPLOYMENT_INTRO_INFO_DEFAULT = {
    'items': [
        {
            'horizontal_divider_type': 'bottom_icon',
            'right_icon': 'undefined',
            'subtitle': 'intro_subtitle',
            'type': 'header',
        },
        {
            'accent': True,
            'horizontal_divider_type': 'bottom_icon',
            'left_icon': {
                'icon_size': 'default',
                'icon_type': 'self_employment_plus',
            },
            'right_icon': 'undefined',
            'title': 'intro_no_commision_title',
            'subtitle': 'intro_no_commision_subtitle',
            'type': 'icon_detail',
        },
        {
            'accent': True,
            'horizontal_divider_type': 'bottom_icon',
            'left_icon': {
                'icon_size': 'default',
                'icon_type': 'self_employment_plus',
            },
            'right_icon': 'undefined',
            'title': 'intro_fast_money_title',
            'subtitle': 'intro_fast_money_subtitle',
            'type': 'icon_detail',
        },
        {
            'accent': True,
            'horizontal_divider_type': 'bottom_icon',
            'left_icon': {
                'icon_size': 'default',
                'icon_type': 'self_employment_plus',
                'tint_color': '',
            },
            'right_icon': 'undefined',
            'title': 'intro_month_priority_title',
            'subtitle': 'intro_month_priority_subtitle',
            'type': 'icon_detail',
        },
    ],
    'bottom_items': [],
}

DEFAULT_HEADERS = {'User-Agent': 'Taximeter 9.30'}


def make_pro_app_exp_kwargs(application_version='9.30.0'):
    return [
        {'name': 'application', 'type': 'application', 'value': 'taximeter'},
        {
            'name': 'version',
            'type': 'application_version',
            'value': application_version,
        },
        {'name': 'application.brand', 'type': 'string', 'value': 'yandex'},
        {'name': 'application.platform', 'type': 'string', 'value': 'android'},
        {'name': 'build_type', 'type': 'string', 'value': ''},
    ]


def agreement_configs3(func):
    @pytest.mark.client_experiments3(
        consumer='selfemployed/fns-se/agreement',
        config_name='pro_fns_selfemployment_agreement_settings',
        args=[
            {'name': 'has_driver_license', 'type': 'bool', 'value': False},
            {'name': 'endpoint_version', 'type': 'int', 'value': 1},
        ],
        value=PRO_FNS_SELFEMPLOYMENT_AGREEMENT_SETTINGS_DEFAULT_VALUE,
    )
    @pytest.mark.client_experiments3(
        consumer='selfemployed/fns-se/agreement',
        config_name='pro_fns_selfemployment_agreement_settings',
        args=[
            {'name': 'has_driver_license', 'type': 'bool', 'value': False},
            {'name': 'endpoint_version', 'type': 'int', 'value': 2},
        ],
        value=PRO_FNS_SELFEMPLOYMENT_AGREEMENT_SETTINGS_DEFAULT_VALUE,
    )
    @pytest.mark.client_experiments3(
        consumer='selfemployed/fns-se/agreement',
        config_name='pro_fns_selfemployment_agreement_settings',
        args=[
            {'name': 'has_driver_license', 'type': 'bool', 'value': True},
            {'name': 'endpoint_version', 'type': 'int', 'value': 2},
        ],
        value=PRO_FNS_SELFEMPLOYMENT_AGREEMENT_SETTINGS_WITH_GAS_VALUE,
    )
    @functools.wraps(func)
    async def patched(*args, **kwargs):
        await func(*args, **kwargs)

    return patched


def await_park_created_configs3(func):  # noqa: F405
    @pytest.mark.client_experiments3(
        consumer='selfemployed/fns-se/await-park-created',
        config_name='pro_fns_selfemployment_await_park_created_settings',
        args=[
            {'name': 'is_resident', 'type': 'bool', 'value': True},
            {'name': 'city', 'type': 'string', 'value': 'Москва'},
        ],
        value=PRO_FNS_SELFEMPLOYMENT_AWAIT_PARK_CREATED_SETTINGS_RESIDENT_SRC,
    )
    @pytest.mark.client_experiments3(
        consumer='selfemployed/fns-se/await-park-created',
        config_name='pro_fns_selfemployment_await_park_created_settings',
        args=[
            {'name': 'is_resident', 'type': 'bool', 'value': False},
            {'name': 'city', 'type': 'string', 'value': 'Москва'},
        ],
        value=PRO_FNS_SELFEMPLOYMENT_AWAIT_PARK_CREATED_SETTINGS_NOT_RESIDENT_SRC,  # noqa: E501
    )
    @functools.wraps(func)
    async def patched(*args, **kwargs):
        await func(*args, **kwargs)

    return patched


def help_info_configs3(func):  # noqa: F405
    @pytest.mark.client_experiments3(
        consumer='selfemployed/fns-se/help-info',
        config_name='pro_fns_selfemployment_help_info_settings',
        args=[
            {'name': 'is_selfreg', 'type': 'bool', 'value': True},
            {'name': 'city', 'type': 'string', 'value': 'Москва'},
        ],
        value=PRO_FNS_SELFEMPLOYMENT_HELP_INFO_SETTINGS_SELFREG_SRC,
    )
    @pytest.mark.client_experiments3(
        consumer='selfemployed/fns-se/help-info',
        config_name='pro_fns_selfemployment_help_info_settings',
        args=[
            {'name': 'is_selfreg', 'type': 'bool', 'value': False},
            {'name': 'city', 'type': 'string', 'value': 'Москва'},
        ],
        value=PRO_FNS_SELFEMPLOYMENT_HELP_INFO_SETTINGS_NOT_SELFREG_SRC,
    )
    @functools.wraps(func)
    async def patched(*args, **kwargs):
        await func(*args, **kwargs)

    return patched


def intro_info_configs3(func):  # noqa: F405
    @pytest.mark.client_experiments3(
        consumer='selfemployed/fns-se/intro-info',
        config_name='pro_fns_selfemployment_intro_constructor_info',
        args=[
            {'name': 'is_selfreg', 'type': 'bool', 'value': False},
            {'name': 'city', 'type': 'string', 'value': 'Москва'},
            *make_pro_app_exp_kwargs('8.84.0'),
        ],
        value={
            'items': [
                {'type': 'future', 'title': 'intro_fast_money_subtitle'},
            ],
            'bottom_items': [],
        },
    )
    @pytest.mark.client_experiments3(
        consumer='selfemployed/fns-se/intro-info',
        config_name='pro_fns_selfemployment_intro_constructor_info',
        args=[
            {'name': 'is_selfreg', 'type': 'bool', 'value': False},
            {'name': 'city', 'type': 'string', 'value': 'Москва'},
            *make_pro_app_exp_kwargs('8.80.0'),
        ],
        value={
            'items': [
                {'type': 'type_detail', 'title': 'intro_fast_money_subtitle'},
            ],
            'bottom_items': [],
        },
    )
    @pytest.mark.client_experiments3(
        consumer='selfemployed/fns-se/intro-info',
        config_name='pro_fns_selfemployment_intro_constructor_info',
        args=[
            {'name': 'is_selfreg', 'type': 'bool', 'value': False},
            {'name': 'city', 'type': 'string', 'value': 'Москва'},
            *make_pro_app_exp_kwargs('8.79.0'),
        ],
        value={
            'items': [
                {'type': 'icon_detail', 'title': 'intro_fast_money_subtitle'},
            ],
            'bottom_items': [],
        },
    )
    @pytest.mark.client_experiments3(
        consumer='selfemployed/fns-se/intro-info',
        config_name='pro_fns_selfemployment_intro_constructor_info',
        args=[
            {'name': 'is_selfreg', 'type': 'bool', 'value': False},
            {'name': 'city', 'type': 'string', 'value': 'Москва'},
            *make_pro_app_exp_kwargs('1.0.0'),
        ],
        value={
            'items': [
                {'type': 'default', 'title': 'intro_fast_money_subtitle'},
            ],
            'bottom_items': [],
        },
    )
    @pytest.mark.client_experiments3(
        consumer='selfemployed/fns-se/intro-info',
        config_name='pro_fns_selfemployment_intro_constructor_info',
        args=[
            {'name': 'is_selfreg', 'type': 'bool', 'value': False},
            {'name': 'city', 'type': 'string', 'value': 'Москва'},
            *make_pro_app_exp_kwargs('9.30.0'),
        ],
        value=PRO_FNS_SELFEMPLOYMENT_INTRO_INFO_DEFAULT,
    )
    @functools.wraps(func)
    async def patched(*args, **kwargs):
        await func(*args, **kwargs)

    return patched


@pytest.fixture(autouse=True)  # noqa: F405
def simple_secdist(simple_secdist):
    simple_secdist.setdefault(
        'selfemployed_fns',
        {'FNS_MASTER_TOKEN': 'SECRET', 'FNS_EDA_MASTER_TOKEN': 'EDA_SECRET'},
    )
    simple_secdist['settings_override'].setdefault(
        'SALESFORCE',
        {
            'client_id': 'client_id',
            'client_secret': 'client_secret',
            'grant_type': 'password',
            'password': 'pwd',
            'username': 'username',
        },
    )
    return simple_secdist


@pytest.fixture(autouse=True)
@pytest.mark.config(SALESFORCE_TOKEN_LIFETIME=1)
def mock_salesforce_auth(mock_salesforce):
    @mock_salesforce('/services/oauth2/token')
    def _auth_sf(request):
        return {
            'access_token': 'access_token',
            'id': 'id',
            'instance_url': 'instance_url',
            'issued_at': '2050-01-01T12:00:00+00:00',
            'signature': 'signature',
            'token_type': 'bearer',
        }


@pytest.fixture  # noqa: F405
def mock_token_update(patch):
    """This fixture has to be put first in every test that uses web `context`
      to disable token update calls"""

    @patch('selfemployed.fns.token_cache.FNSTokenCache.on_startup')
    async def _web_on_startup():
        pass

    @patch('selfemployed.fns.token_cache.FNSTokenCache.get_token')
    async def _get_token():
        return 'AUTH_TOKEN'


@pytest.fixture  # noqa: F405
def se_client(simple_secdist, mock_token_update, web_app_client):
    return web_app_client


@pytest.fixture  # noqa: F405
async def se_web_context(
        simple_secdist, mock_token_update, web_context: context_module.Context,
):
    yield web_context


@pytest.fixture  # noqa: F405
async def se_cron_context(simple_secdist, mock_token_update, cron_context):
    yield cron_context


@pytest.fixture(name='fleet_sync', autouse=True)  # noqa: F405
def _fleet_sync(mockserver):
    @mockserver.json_handler('/fleet-synchronizer/v1/mapping/driver')
    def _mapping_driver(request):
        return {
            'mapping': [
                {
                    'driver_id': 'd1',
                    'park_id': 'p1',
                    'app_family': 'taximeter',
                },
                {
                    'driver_id': 'uber_d1',
                    'park_id': 'uber_p1',
                    'app_family': 'uberdriver',
                },
            ],
        }
