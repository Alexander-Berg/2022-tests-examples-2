# pylint: disable=too-many-lines
import pytest

RU_HEADERS = {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-RU'}
RU_HEADERS_2 = {'X-Yandex-Login': 'mikh-vasily', 'Accept-Language': 'ru-RU'}
EN_HEADERS = {'X-Yandex-Login': 'webalex', 'Accept-Language': 'en-EN'}
RU_HEADERS_3 = {'X-Yandex-Login': 'volozh', 'Accept-Language': 'ru-RU'}
RU_HEADERS_4 = {'X-Yandex-Login': 'unholy', 'Accept-Language': 'ru-RU'}
RU_HEADERS_5 = {'X-Yandex-Login': 'valentin', 'Accept-Language': 'ru-RU'}
RU_HEADERS_6 = {'X-Yandex-Login': 'justmark0', 'Accept-Language': 'ru-RU'}

AVATAR_TEMPLATE = 'https://center.yandex-team.ru/api/v1/user/%s/photo/300.jpg'


PROJECT_SETTINGS = {
    'default': {'enable_chatterbox': False, 'profile_information': []},
    'calltaxi': {
        'enable_chatterbox': False,
        'main_permission': 'user_calltaxi',
        'profile_information': ['phones', 'telegrams'],
    },
    'taxisupport': {
        'enable_chatterbox': False,
        'piecework_tariff': 'support-taxi',
    },
    'lavkasupport': {
        'enable_chatterbox': False,
        'piecework_tariff': 'grocery',
    },
}

CONFIG = {
    'widget_calltaxi_callsall': {
        'type': 'progress',
        'position': 1,
        'indicator_type': 'absolute',
        'direction': 'asc',
        'tanker_title_key': 'title_widget_calltaxi_callsall',
        'tanker_subtitle_key': 'subtitle_widget_calltaxi_callsall',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_calltaxi_callstrip': {
        'type': 'progress',
        'position': 2,
        'indicator_type': 'absolute',
        'direction': 'asc',
        'tanker_title_key': 'title_widget_calltaxi_callstrip',
        'tanker_subtitle_key': 'subtitle_widget_calltaxi_callstrip',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_calltaxi_convert': {
        'type': 'progress',
        'position': 3,
        'indicator_type': 'progress',
        'scale': [90],
        'scales_teams': {'default': [90]},
        'direction': 'asc',
        'tanker_title_key': 'title_widget_calltaxi_convert',
        'tanker_subtitle_key': 'subtitle_widget_calltaxi_convert',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_calltaxi_qa': {
        'size': 'small',
        'type': 'progress',
        'position': 4,
        'indicator_type': 'progress',
        'scale': [90],
        'scales_teams': {'default': [90]},
        'direction': 'asc',
        'tanker_title_key': 'title_widget_calltaxi_qa',
        'tanker_subtitle_key': 'subtitle_widget_calltaxi_qa',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_calltaxi_discipline': {
        'type': 'progress',
        'position': 5,
        'indicator_type': 'progress',
        'scale': [90],
        'scales_teams': {'default': [90]},
        'direction': 'asc',
        'tanker_title_key': 'title_widget_calltaxi_discipline',
        'tanker_subtitle_key': 'subtitle_widget_calltaxi_discipline',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_calltaxi_basic_score': {
        'type': 'progress',
        'position': 6,
        'indicator_type': 'absolute',
        'direction': 'asc',
        'tanker_title_key': 'title_widget_calltaxi_basic_score',
        'tanker_subtitle_key': 'subtitle_widget_calltaxi_basic_score',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_comdelivery_algorithm': {
        'show_in_cabinet': True,
        'show_in_profile': True,
        'indicator_type': 'absolute',
        'tanker_about_key': 'about_widget_waiting',
        'tanker_subtitle_key': 'subtitle_widget_by_period',
        'tanker_title_key': 'title_widget_comdelivery_algorithm',
        'type': 'progress',
    },
    'widget_comdelivery_callssccs': {
        'show_in_cabinet': True,
        'show_in_profile': True,
        'indicator_type': 'absolute',
        'tanker_about_key': 'about_widget_waiting',
        'tanker_subtitle_key': 'subtitle_widget_by_period',
        'tanker_title_key': 'title_widget_comdelivery_callssccs',
        'type': 'progress',
    },
    'widget_comdelivery_contracts': {
        'show_in_cabinet': True,
        'show_in_profile': True,
        'indicator_type': 'absolute',
        'tanker_about_key': 'about_widget_waiting',
        'tanker_subtitle_key': 'subtitle_widget_by_period',
        'tanker_title_key': 'title_widget_comdelivery_contracts',
        'type': 'progress',
    },
    'widget_comdelivery_deliverysccs': {
        'show_in_cabinet': True,
        'show_in_profile': True,
        'indicator_type': 'absolute',
        'tanker_about_key': 'about_widget_waiting',
        'tanker_subtitle_key': 'subtitle_widget_by_period',
        'tanker_title_key': 'title_widget_comdelivery_deliverysccs',
        'type': 'progress',
    },
    'widget_comdelivery_donetasks': {
        'show_in_cabinet': True,
        'show_in_profile': True,
        'indicator_type': 'absolute',
        'tanker_about_key': 'about_widget_waiting',
        'tanker_subtitle_key': 'subtitle_widget_by_period',
        'tanker_title_key': 'title_widget_comdelivery_donetasks',
        'type': 'progress',
    },
    'widget_comdelivery_health': {
        'show_in_cabinet': True,
        'show_in_profile': True,
        'indicator_type': 'absolute',
        'tanker_about_key': 'about_widget_waiting',
        'tanker_subtitle_key': 'subtitle_widget_by_period',
        'tanker_title_key': 'title_widget_comdelivery_health',
        'type': 'progress',
    },
    'widget_comdelivery_hygiene': {
        'show_in_cabinet': True,
        'show_in_profile': True,
        'indicator_type': 'absolute',
        'tanker_about_key': 'about_widget_waiting',
        'tanker_subtitle_key': 'subtitle_widget_by_period',
        'tanker_title_key': 'title_widget_comdelivery_hygiene',
        'type': 'progress',
    },
    'widget_comdelivery_listedclients': {
        'show_in_cabinet': True,
        'show_in_profile': True,
        'indicator_type': 'absolute',
        'tanker_about_key': 'about_widget_waiting',
        'tanker_subtitle_key': 'subtitle_widget_by_period',
        'tanker_title_key': 'title_widget_comdelivery_listedclients',
        'type': 'progress',
    },
    'widget_comdelivery_quality': {
        'show_in_cabinet': True,
        'show_in_profile': True,
        'indicator_type': 'absolute',
        'tanker_about_key': 'about_widget_waiting',
        'tanker_subtitle_key': 'subtitle_widget_by_period',
        'tanker_title_key': 'title_widget_comdelivery_quality',
        'type': 'progress',
    },
    'widget_comdelivery_tov': {
        'show_in_cabinet': True,
        'show_in_profile': True,
        'indicator_type': 'absolute',
        'tanker_about_key': 'about_widget_waiting',
        'tanker_subtitle_key': 'subtitle_widget_by_period',
        'tanker_title_key': 'title_widget_comdelivery_tov',
        'type': 'progress',
    },
    'widget_directsupport_csat': {
        'type': 'progress',
        'position': 1,
        'indicator_type': 'progress',
        'scale': [90],
        'scales_teams': {'default': [90]},
        'direction': 'asc',
        'tanker_title_key': 'title_widget_directsupport_csat',
        'tanker_subtitle_key': 'subtitle_widget_directsupport_csat',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_directsupport_skip': {
        'type': 'progress',
        'position': 2,
        'indicator_type': 'progress',
        'scale': [90],
        'scales_teams': {'default': [90]},
        'direction': 'asc',
        'tanker_title_key': 'title_widget_directsupport_skip',
        'tanker_subtitle_key': 'subtitle_widget_directsupport_skip',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_directsupport_wfm': {
        'type': 'progress',
        'position': 3,
        'indicator_type': 'progress',
        'scale': [90],
        'scales_teams': {'default': [90]},
        'direction': 'asc',
        'tanker_title_key': 'title_widget_directsupport_wfm',
        'tanker_subtitle_key': 'subtitle_widget_directsupport_wfm',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_calltaxi_speed': {
        'type': 'progress',
        'position': 7,
        'indicator_type': 'absolute',
        'direction': 'asc',
        'tanker_title_key': 'title_widget_calltaxi_speed',
        'tanker_subtitle_key': 'subtitle_widget_calltaxi_speed',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_calltaxi_production': {
        'type': 'progress',
        'position': 8,
        'indicator_type': 'progress',
        'scale': [90],
        'scales_teams': {'default': [90]},
        'direction': 'asc',
        'tanker_title_key': 'title_widget_calltaxi_production',
        'tanker_subtitle_key': 'subtitle_widget_calltaxi_production',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_taxisupport_csat': {
        'type': 'progress',
        'position': 1,
        'indicator_type': 'progress',
        'scale': [90],
        'scales_teams': {'default': [90]},
        'direction': 'asc',
        'tanker_title_key': 'title_widget_taxisupport_csat',
        'tanker_subtitle_key': 'subtitle_widget_taxisupport_csat',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_taxisupport_qa': {
        'type': 'progress',
        'position': 2,
        'indicator_type': 'progress',
        'scale': [90],
        'scales_teams': {'default': [90]},
        'direction': 'asc',
        'tanker_title_key': 'title_widget_taxisupport_qa',
        'tanker_subtitle_key': 'subtitle_widget_taxisupport_qa',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_taxisupport_norm': {
        'type': 'progress',
        'position': 3,
        'indicator_type': 'progress',
        'scale': [90],
        'scales_teams': {'default': [90]},
        'direction': 'asc',
        'tanker_title_key': 'title_widget_taxisupport_norm',
        'tanker_subtitle_key': 'subtitle_widget_taxisupport_norm',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_edasupport_csat': {
        'type': 'progress',
        'position': 1,
        'indicator_type': 'progress',
        'scale': [],
        'direction': 'asc',
        'tanker_title_key': 'title_widget_edasupport_csat',
        'tanker_subtitle_key': 'subtitle_widget_edasupport_csat',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_edasupport_qa': {
        'type': 'progress',
        'position': 2,
        'indicator_type': 'progress',
        'scale': [],
        'direction': 'asc',
        'tanker_title_key': 'title_widget_edasupport_qa',
        'tanker_subtitle_key': 'subtitle_widget_edasupport_qa',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_lavkasupport_norm': {
        'type': 'progress',
        'position': 3,
        'indicator_type': 'progress',
        'scale': [90],
        'scales_teams': {'default': [90]},
        'direction': 'asc',
        'tanker_title_key': 'title_widget_lavkasupport_norm',
        'tanker_subtitle_key': 'subtitle_widget_lavkasupport_norm',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_lavkasupport_csat': {
        'type': 'progress',
        'position': 1,
        'indicator_type': 'progress',
        'scale': [90],
        'scales_teams': {'default': [90]},
        'direction': 'asc',
        'tanker_title_key': 'title_widget_lavkasupport_csat',
        'tanker_subtitle_key': 'subtitle_widget_lavkasupport_csat',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_deliverysupport_norm': {
        'type': 'progress',
        'position': 3,
        'indicator_type': 'progress',
        'scale': [90],
        'scales_teams': {'default': [90]},
        'direction': 'asc',
        'tanker_title_key': 'title_widget_deliverysupport_norm',
        'tanker_subtitle_key': 'subtitle_widget_deliverysupport_norm',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_driverhiring_speed': {
        'type': 'progress',
        'position': 1,
        'indicator_type': 'progress',
        'scale': [90],
        'scales_teams': {'default': [90]},
        'direction': 'asc',
        'tanker_title_key': 'title_widget_driverhiring_speed',
        'tanker_subtitle_key': 'subtitle_widget_driverhiring_speed',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_driverhiring_conversion': {
        'type': 'progress',
        'position': 1,
        'indicator_type': 'progress',
        'scale': [90],
        'scales_teams': {'default': [90]},
        'direction': 'asc',
        'tanker_title_key': 'title_widget_driverhiring_conversion',
        'tanker_subtitle_key': 'subtitle_widget_driverhiring_conversion',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_driverhiring_calls': {
        'type': 'progress',
        'position': 1,
        'indicator_type': 'absolute',
        'scale': [90],
        'scales_teams': {'default': [90]},
        'direction': 'asc',
        'tanker_title_key': 'title_widget_driverhiring_calls',
        'tanker_subtitle_key': 'subtitle_widget_driverhiring_calls',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_driverhiring_actives': {
        'type': 'progress',
        'position': 1,
        'indicator_type': 'absolute',
        'scale': [90],
        'scales_teams': {'default': [90]},
        'direction': 'asc',
        'tanker_title_key': 'title_widget_driverhiring_actives',
        'tanker_subtitle_key': 'subtitle_widget_driverhiring_actives',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_driverhiring_qa': {
        'type': 'progress',
        'position': 1,
        'indicator_type': 'progress',
        'scale': [90],
        'scales_teams': {'default': [90]},
        'direction': 'asc',
        'tanker_title_key': 'title_widget_driverhiring_qa',
        'tanker_subtitle_key': 'subtitle_widget_driverhiring_qa',
        'tanker_about_key': 'about_widget',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
}

TRANSLATE = {
    'title_widget_calltaxi_callsall': {'ru': 'Звонки', 'en': 'Call'},
    'subtitle_widget_calltaxi_callsall': {
        'ru': 'за период',
        'en': 'on period',
    },
    'title_widget_calltaxi_callstrip': {'ru': 'Успешные звонки', 'en': 'Call'},
    'subtitle_widget_calltaxi_callstrip': {
        'ru': 'за период',
        'en': 'on period',
    },
    'title_widget_calltaxi_convert': {'ru': 'Конверсия', 'en': 'Convert'},
    'subtitle_widget_calltaxi_convert': {'ru': 'за период', 'en': 'on period'},
    'title_widget_calltaxi_qa': {'ru': 'Качество', 'en': 'QA'},
    'subtitle_widget_calltaxi_qa': {'ru': 'за период', 'en': 'on period'},
    'value_widget_calltaxi_qa': {'ru': '{value}%', 'en': '{value}%'},
    'title_widget_calltaxi_discipline': {
        'ru': 'Дисциплина',
        'en': 'Discipline',
    },
    'subtitle_widget_calltaxi_discipline': {
        'ru': 'за период',
        'en': 'on period',
    },
    'title_widget_calltaxi_basic_score': {'ru': 'БО', 'en': 'BO'},
    'subtitle_widget_calltaxi_basic_score': {
        'ru': 'за период',
        'en': 'on period',
    },
    'title_widget_calltaxi_speed': {'ru': 'БО/ч', 'en': 'BOPH'},
    'subtitle_widget_calltaxi_speed': {'ru': 'за период', 'en': 'on period'},
    'value_widget_calltaxi_speed': {'ru': '{value}', 'en': '{value}'},
    'title_widget_calltaxi_production': {
        'ru': 'Выработка',
        'en': 'Production',
    },
    'subtitle_widget_calltaxi_production': {
        'ru': 'за период',
        'en': 'on period',
    },
    'value_widget_calltaxi_production': {'ru': '{value}', 'en': '{value}'},
    'title_widget_taxisupport_csat': {'ru': 'КСАТ', 'en': 'CSAT'},
    'subtitle_widget_taxisupport_csat': {'ru': 'за период', 'en': 'on period'},
    'title_widget_taxisupport_qa': {'ru': 'Качество', 'en': 'Quality'},
    'subtitle_widget_taxisupport_qa': {'ru': 'за период', 'en': 'on period'},
    'title_widget_edasupport_csat': {'ru': 'КСАТ', 'en': 'CSAT'},
    'subtitle_widget_edasupport_csat': {'ru': 'за период', 'en': 'on period'},
    'title_widget_edasupport_qa': {'ru': 'Качество', 'en': 'Quality'},
    'subtitle_widget_edasupport_qa': {'ru': 'за период', 'en': 'on period'},
    'about_widget': {
        'ru': 'Информация о виджете',
        'en': 'Информация о виджете',
    },
    'title_widget_taxisupport_norm': {'ru': 'Норма', 'en': 'Norm'},
    'subtitle_widget_taxisupport_norm': {'ru': 'за период', 'en': 'on period'},
    'title_widget_lavkasupport_norm': {'ru': 'Норма', 'en': 'Norm'},
    'subtitle_widget_lavkasupport_norm': {
        'ru': 'за период',
        'en': 'on period',
    },
    'title_widget_deliverysupport_norm': {'ru': 'Норма', 'en': 'Norm'},
    'subtitle_widget_deliverysupport_norm': {
        'ru': 'за период',
        'en': 'on period',
    },
    'title_widget_lavkasupport_csat': {'ru': 'КСАТ', 'en': 'CSAT'},
    'subtitle_widget_lavkasupport_csat': {
        'ru': 'за период',
        'en': 'on period',
    },
}


EXPECTED_1 = {
    'login': 'webalex',
    'email': 'webalex@yandex-team.ru',
    'avatar': (
        'https://center.yandex-team.ru/api/v1/user/webalex/photo/300.jpg'
    ),
    'first_name': 'Александр',
    'last_name': 'Иванов',
    'phones': [],
    'telegrams': [],
    'features': ['view_profile', 'view_payday'],
    'team': {'key': 'team_1', 'name': 'Команда 1'},
    'balance_of_coins': 0,
    'main_indicators': [],
}

EXPECTED_1_EN = {
    'login': 'webalex',
    'email': 'webalex@yandex-team.ru',
    'avatar': (
        'https://center.yandex-team.ru/api/v1/user/webalex/photo/300.jpg'
    ),
    'first_name': 'Alexandr',
    'last_name': 'Ivanov',
    'phones': [],
    'telegrams': [],
    'main_indicators': [],
    'features': ['view_profile', 'view_payday'],
    'team': {'key': 'team_1', 'name': 'team_1'},
    'balance_of_coins': 0,
}

EXPECTED_2 = {
    'login': 'webalex',
    'email': 'webalex@yandex-team.ru',
    'avatar': AVATAR_TEMPLATE % 'webalex',
    'first_name': 'Александр',
    'last_name': 'Иванов',
    'phones': ['+74950000000'],
    'telegrams': ['@telegram_account'],
    'main_indicators': [
        {
            'id': 'widget_calltaxi_callsall',
            'position': 1,
            'title': 'Звонки',
            'subtitle': 'за период',
            'type': 'absolute',
            'about': 'Информация о виджете',
            'detailing': False,
            'value': {'value': 200, 'style': 'decimal'},
        },
        {
            'id': 'widget_calltaxi_callstrip',
            'position': 2,
            'title': 'Успешные звонки',
            'subtitle': 'за период',
            'type': 'absolute',
            'about': 'Информация о виджете',
            'detailing': False,
            'value': {'value': 100, 'style': 'decimal'},
        },
        {
            'id': 'widget_calltaxi_convert',
            'position': 3,
            'title': 'Конверсия',
            'subtitle': 'за период',
            'type': 'progress',
            'about': 'Информация о виджете',
            'detailing': False,
            'value': {'value': 0.5, 'style': 'percent'},
            'progress': {'scale': [0.9], 'direction': 'asc'},
        },
        {
            'id': 'widget_calltaxi_qa',
            'position': 4,
            'title': 'Качество',
            'subtitle': 'за период',
            'type': 'computing',
            'about': 'Информация о виджете',
        },
        {
            'id': 'widget_calltaxi_discipline',
            'position': 5,
            'title': 'Дисциплина',
            'subtitle': 'за период',
            'type': 'progress',
            'about': 'Информация о виджете',
            'detailing': False,
            'value': {'value': 0.85, 'style': 'percent'},
            'progress': {'scale': [0.9], 'direction': 'asc'},
        },
        {
            'id': 'widget_calltaxi_basic_score',
            'position': 6,
            'title': 'БО',
            'subtitle': 'за период',
            'type': 'absolute',
            'about': 'Информация о виджете',
            'detailing': False,
            'value': {'value': 4138, 'style': 'decimal'},
        },
        {
            'id': 'widget_calltaxi_speed',
            'position': 7,
            'title': 'БО/ч',
            'subtitle': 'за период',
            'type': 'absolute',
            'about': 'Информация о виджете',
            'detailing': False,
            'value': {'value': 99, 'style': 'decimal'},
        },
        {
            'id': 'widget_calltaxi_production',
            'position': 8,
            'title': 'Выработка',
            'subtitle': 'за период',
            'type': 'progress',
            'about': 'Информация о виджете',
            'detailing': False,
            'value': {'value': 0.5, 'style': 'percent'},
            'progress': {'scale': [0.9], 'direction': 'asc'},
        },
    ],
    'features': [],
    'team': {'key': 'team_1', 'name': 'Команда 1'},
    'balance_of_coins': 0,
}

EXPECTED_3 = {
    'avatar': (
        'https://center.yandex-team.ru/api/v1/user/webalex/photo/300.jpg'
    ),
    'login': 'webalex',
    'first_name': 'Alexandr',
    'last_name': 'Ivanov',
    'features': ['view_profile', 'view_payday'],
    'team': {'key': 'team_1', 'name': 'team_1'},
    'balance_of_coins': 0,
    'phones': ['+74950000000'],
    'telegrams': ['@telegram_account'],
    'email': 'webalex@yandex-team.ru',
    'main_indicators': [
        {
            'id': 'widget_calltaxi_callsall',
            'position': 1,
            'detailing': False,
            'type': 'absolute',
            'title': 'Call',
            'subtitle': 'on period',
            'about': 'Информация о виджете',
            'value': {'value': 200, 'style': 'decimal'},
        },
        {
            'id': 'widget_calltaxi_callstrip',
            'position': 2,
            'detailing': False,
            'type': 'absolute',
            'title': 'Call',
            'subtitle': 'on period',
            'about': 'Информация о виджете',
            'value': {'value': 100, 'style': 'decimal'},
        },
        {
            'id': 'widget_calltaxi_convert',
            'position': 3,
            'detailing': False,
            'type': 'progress',
            'title': 'Convert',
            'subtitle': 'on period',
            'about': 'Информация о виджете',
            'value': {'value': 0.5, 'style': 'percent'},
            'progress': {'scale': [0.9], 'direction': 'asc'},
        },
        {
            'id': 'widget_calltaxi_qa',
            'position': 4,
            'type': 'computing',
            'title': 'QA',
            'subtitle': 'on period',
            'about': 'Информация о виджете',
        },
        {
            'id': 'widget_calltaxi_discipline',
            'position': 5,
            'detailing': False,
            'type': 'progress',
            'title': 'Discipline',
            'subtitle': 'on period',
            'about': 'Информация о виджете',
            'value': {'value': 0.85, 'style': 'percent'},
            'progress': {'scale': [0.9], 'direction': 'asc'},
        },
        {
            'id': 'widget_calltaxi_speed',
            'position': 7,
            'detailing': False,
            'type': 'absolute',
            'title': 'BOPH',
            'subtitle': 'on period',
            'about': 'Информация о виджете',
            'value': {'value': 99, 'style': 'decimal'},
        },
        {
            'id': 'widget_calltaxi_production',
            'position': 8,
            'detailing': False,
            'type': 'progress',
            'title': 'Production',
            'subtitle': 'on period',
            'about': 'Информация о виджете',
            'value': {'value': 0.5, 'style': 'percent'},
            'progress': {'scale': [0.9], 'direction': 'asc'},
        },
        {
            'id': 'widget_calltaxi_basic_score',
            'position': 6,
            'detailing': False,
            'type': 'absolute',
            'title': 'BO',
            'subtitle': 'on period',
            'about': 'Информация о виджете',
            'value': {'value': 4138, 'style': 'decimal'},
        },
    ],
}

EXPECTED_4 = {
    'login': 'akozhevina',
    'email': 'akozhevina@yandex-team.ru',
    'avatar': (
        'https://center.yandex-team.ru/api/v1/user/akozhevina/photo/300.jpg'
    ),
    'first_name': 'Анна',
    'last_name': 'Кожевина',
    'phones': [],
    'telegrams': [],
    'main_indicators': [],
    'features': ['view_settings', 'view_profile'],
    'team': {'key': None, 'name': None},
    'balance_of_coins': 0,
}

EXPECTED_5 = {
    'login': 'mikh-vasily',
    'email': 'mikh-vasily@yandex-team.ru',
    'avatar': (
        'https://center.yandex-team.ru/api/v1/user/mikh-vasily/photo/300.jpg'
    ),
    'first_name': 'Василий',
    'last_name': 'Михайлов',
    'phones': [],
    'telegrams': [],
    'main_indicators': [
        {
            'id': 'widget_calltaxi_callsall',
            'position': 1,
            'title': 'Звонки',
            'subtitle': 'за период',
            'type': 'absolute',
            'about': 'Информация о виджете',
            'detailing': False,
            'value': {'value': 200, 'style': 'decimal'},
        },
        {
            'id': 'widget_calltaxi_callstrip',
            'position': 2,
            'title': 'Успешные звонки',
            'subtitle': 'за период',
            'type': 'absolute',
            'about': 'Информация о виджете',
            'detailing': False,
            'value': {'value': 100, 'style': 'decimal'},
        },
        {
            'id': 'widget_calltaxi_convert',
            'position': 3,
            'title': 'Конверсия',
            'subtitle': 'за период',
            'type': 'progress',
            'about': 'Информация о виджете',
            'detailing': False,
            'value': {'value': 0.5, 'style': 'percent'},
            'progress': {'scale': [0.9], 'direction': 'asc'},
        },
        {
            'id': 'widget_calltaxi_qa',
            'position': 4,
            'title': 'Качество',
            'subtitle': 'за период',
            'type': 'progress',
            'about': 'Информация о виджете',
            'detailing': False,
            'value': {'value': 1, 'style': 'percent'},
            'progress': {'scale': [0.9], 'direction': 'asc'},
        },
        {
            'id': 'widget_calltaxi_discipline',
            'position': 5,
            'title': 'Дисциплина',
            'subtitle': 'за период',
            'type': 'progress',
            'about': 'Информация о виджете',
            'detailing': False,
            'value': {'value': 1, 'style': 'percent'},
            'progress': {'scale': [0.9], 'direction': 'asc'},
        },
        {
            'id': 'widget_calltaxi_basic_score',
            'position': 6,
            'title': 'БО',
            'subtitle': 'за период',
            'type': 'absolute',
            'about': 'Информация о виджете',
            'detailing': False,
            'value': {'value': 30, 'style': 'decimal'},
        },
        {
            'id': 'widget_calltaxi_speed',
            'position': 7,
            'title': 'БО/ч',
            'subtitle': 'за период',
            'type': 'absolute',
            'about': 'Информация о виджете',
            'detailing': False,
            'value': {'value': 0, 'style': 'decimal'},
        },
        {
            'id': 'widget_calltaxi_production',
            'position': 8,
            'title': 'Выработка',
            'subtitle': 'за период',
            'type': 'progress',
            'about': 'Информация о виджете',
            'detailing': False,
            'value': {'value': 0, 'style': 'percent'},
            'progress': {'scale': [0.9], 'direction': 'asc'},
        },
    ],
    'features': [],
    'team': {'key': 'team_1', 'name': 'Команда 1'},
    'balance_of_coins': 0,
}

EXPECTED_6 = {
    'login': 'strashnov',
    'email': 'strashnov@yandex-team.ru',
    'avatar': (
        'https://center.yandex-team.ru/api/v1/user/strashnov/photo/300.jpg'
    ),
    'first_name': 'Александр',
    'last_name': 'Страшнов',
    'phones': [],
    'telegrams': [],
    'main_indicators': [],
    'features': ['view_settings', 'view_profile'],
    'team': {'key': None, 'name': None},
    'balance_of_coins': 0,
}

EXPECTED_7 = {
    'avatar': 'https://center.yandex-team.ru/api/v1/user/unholy/photo/300.jpg',
    'login': 'unholy',
    'first_name': 'Нияз',
    'last_name': 'Наибулин',
    'features': ['view_profile'],
    'team': {'key': None, 'name': None},
    'balance_of_coins': 0,
    'phones': [],
    'telegrams': [],
    'email': 'unholy@yandex-team.ru',
    'main_indicators': [
        {
            'id': 'widget_calltaxi_basic_score',
            'position': 6,
            'type': 'computing',
            'title': 'БО',
            'subtitle': 'за период',
            'about': 'Информация о виджете',
        },
        {
            'id': 'widget_directsupport_csat',
            'position': 1,
            'type': 'computing',
            'title': 'widget_directsupport_csat',
            'subtitle': 'widget_directsupport_csat',
            'about': 'Информация о виджете',
        },
        {
            'id': 'widget_directsupport_skip',
            'position': 2,
            'type': 'computing',
            'title': 'widget_directsupport_skip',
            'subtitle': 'widget_directsupport_skip',
            'about': 'Информация о виджете',
        },
        {
            'id': 'widget_directsupport_wfm',
            'position': 3,
            'type': 'computing',
            'title': 'widget_directsupport_wfm',
            'subtitle': 'widget_directsupport_wfm',
            'about': 'Информация о виджете',
        },
    ],
}

EXPECTED_8 = {
    'avatar': (
        'https://center.yandex-team.ru/api/v1/user/valentin/photo/300.jpg'
    ),
    'login': 'valentin',
    'first_name': 'Валентин',
    'last_name': 'Петухов',
    'features': ['view_profile'],
    'team': {'key': 'team_1', 'name': 'Команда 1'},
    'balance_of_coins': 0,
    'phones': [],
    'telegrams': [],
    'email': 'valentin@yandex-team.ru',
    'main_indicators': [
        {
            'id': 'widget_calltaxi_basic_score',
            'position': 6,
            'type': 'computing',
            'title': 'БО',
            'subtitle': 'за период',
            'about': 'Информация о виджете',
        },
        {
            'id': 'widget_calltaxi_callsall',
            'position': 1,
            'type': 'computing',
            'title': 'Звонки',
            'subtitle': 'за период',
            'about': 'Информация о виджете',
        },
        {
            'id': 'widget_calltaxi_callstrip',
            'position': 2,
            'type': 'computing',
            'title': 'Успешные звонки',
            'subtitle': 'за период',
            'about': 'Информация о виджете',
        },
        {
            'id': 'widget_calltaxi_convert',
            'position': 3,
            'type': 'computing',
            'title': 'Конверсия',
            'subtitle': 'за период',
            'about': 'Информация о виджете',
        },
        {
            'id': 'widget_calltaxi_discipline',
            'position': 5,
            'type': 'computing',
            'title': 'Дисциплина',
            'subtitle': 'за период',
            'about': 'Информация о виджете',
        },
        {
            'id': 'widget_calltaxi_production',
            'position': 8,
            'type': 'computing',
            'title': 'Выработка',
            'subtitle': 'за период',
            'about': 'Информация о виджете',
        },
        {
            'id': 'widget_calltaxi_qa',
            'position': 4,
            'type': 'computing',
            'title': 'Качество',
            'subtitle': 'за период',
            'about': 'Информация о виджете',
        },
        {
            'id': 'widget_calltaxi_speed',
            'position': 7,
            'type': 'computing',
            'title': 'БО/ч',
            'subtitle': 'за период',
            'about': 'Информация о виджете',
        },
    ],
}

EXPECTED_9 = {
    'avatar': (
        'https://center.yandex-team.ru/api/v1/user/justmark0/photo/300.jpg'
    ),
    'login': 'justmark0',
    'first_name': 'Марк',
    'last_name': 'Николсон',
    'features': ['view_profile'],
    'team': {'key': None, 'name': None},
    'balance_of_coins': 0,
    'phones': [],
    'telegrams': [],
    'email': 'justmark0@yandex-team.ru',
    'main_indicators': [
        {
            'id': 'widget_comdelivery_algorithm',
            'position': 1,
            'detailing': False,
            'type': 'absolute',
            'title': 'widget_comdelivery_algorithm',
            'subtitle': 'widget_comdelivery_algorithm',
            'about': 'widget_comdelivery_algorithm',
            'value': {'value': 30, 'style': 'decimal'},
        },
        {
            'id': 'widget_comdelivery_callssccs',
            'position': 1,
            'detailing': False,
            'type': 'absolute',
            'title': 'widget_comdelivery_callssccs',
            'subtitle': 'widget_comdelivery_callssccs',
            'about': 'widget_comdelivery_callssccs',
            'value': {'value': 61, 'style': 'decimal'},
        },
        {
            'id': 'widget_comdelivery_contracts',
            'position': 1,
            'detailing': False,
            'type': 'absolute',
            'title': 'widget_comdelivery_contracts',
            'subtitle': 'widget_comdelivery_contracts',
            'about': 'widget_comdelivery_contracts',
            'value': {'value': 123, 'style': 'decimal'},
        },
        {
            'id': 'widget_comdelivery_deliverysccs',
            'position': 1,
            'detailing': False,
            'type': 'absolute',
            'title': 'widget_comdelivery_deliverysccs',
            'subtitle': 'widget_comdelivery_deliverysccs',
            'about': 'widget_comdelivery_deliverysccs',
            'value': {'value': 15, 'style': 'decimal'},
        },
        {
            'id': 'widget_comdelivery_donetasks',
            'position': 1,
            'detailing': False,
            'type': 'absolute',
            'title': 'widget_comdelivery_donetasks',
            'subtitle': 'widget_comdelivery_donetasks',
            'about': 'widget_comdelivery_donetasks',
            'value': {'value': 20, 'style': 'decimal'},
        },
        {
            'id': 'widget_comdelivery_health',
            'position': 1,
            'detailing': False,
            'type': 'absolute',
            'title': 'widget_comdelivery_health',
            'subtitle': 'widget_comdelivery_health',
            'about': 'widget_comdelivery_health',
            'value': {'value': 95.4, 'style': 'decimal'},
        },
        {
            'id': 'widget_comdelivery_hygiene',
            'position': 1,
            'detailing': False,
            'type': 'absolute',
            'title': 'widget_comdelivery_hygiene',
            'subtitle': 'widget_comdelivery_hygiene',
            'about': 'widget_comdelivery_hygiene',
            'value': {'value': 40, 'style': 'decimal'},
        },
        {
            'id': 'widget_comdelivery_listedclients',
            'position': 1,
            'detailing': False,
            'type': 'absolute',
            'title': 'widget_comdelivery_listedclients',
            'subtitle': 'widget_comdelivery_listedclients',
            'about': 'widget_comdelivery_listedclients',
            'value': {'value': 321, 'style': 'decimal'},
        },
        {
            'id': 'widget_comdelivery_quality',
            'position': 1,
            'detailing': False,
            'type': 'absolute',
            'title': 'widget_comdelivery_quality',
            'subtitle': 'widget_comdelivery_quality',
            'about': 'widget_comdelivery_quality',
            'value': {'value': 4.5, 'style': 'decimal'},
        },
        {
            'id': 'widget_comdelivery_tov',
            'position': 1,
            'detailing': False,
            'type': 'absolute',
            'title': 'widget_comdelivery_tov',
            'subtitle': 'widget_comdelivery_tov',
            'about': 'widget_comdelivery_tov',
            'value': {'value': 5.7, 'style': 'decimal'},
        },
    ],
}


@pytest.mark.config(AGENT_PROJECT_SETTINGS=PROJECT_SETTINGS)
@pytest.mark.parametrize(
    'body,headers,status_code,expected_data',
    [
        ({'login': 'nofounduser'}, RU_HEADERS, 404, {}),
        ({}, RU_HEADERS, 400, {}),
        ({'login': 'webalex'}, {}, 400, {}),
        ({'login': 'webalex'}, RU_HEADERS, 200, EXPECTED_1),
        ({'login': 'webalex'}, EN_HEADERS, 200, EXPECTED_1_EN),
        ({'login': 'akozhevina'}, RU_HEADERS, 200, EXPECTED_4),
        ({'login': 'topalyan'}, RU_HEADERS, 403, {}),
        ({'login': 'strashnov'}, RU_HEADERS_3, 200, EXPECTED_6),
        ({'login': 'nikslim'}, RU_HEADERS_3, 403, {}),
    ],
)
@pytest.mark.config(AGENT_PROJECT_SETTINGS=PROJECT_SETTINGS)
async def test_profile_without_config(
        web_app_client,
        body,
        headers,
        status_code,
        expected_data,
        mock_retrieve_personal,
        mock_retrieve_telegrams,
):
    response = await web_app_client.post(
        '/profile', headers=headers, json=body,
    )
    if status_code == 200:
        assert response.status == status_code
        content = await response.json()
        assert content == expected_data


@pytest.mark.now('2021-01-10T12:00:00+0000')
@pytest.mark.translations(agent=TRANSLATE)
@pytest.mark.config(AGENT_WIDGETS_SETTINGS=CONFIG)
@pytest.mark.parametrize(
    'body,headers,status_code,expected_data',
    [
        ({'login': 'webalex'}, RU_HEADERS, 200, EXPECTED_2),
        ({'login': 'webalex'}, EN_HEADERS, 200, EXPECTED_3),
        ({'login': 'mikh-vasily'}, RU_HEADERS_2, 200, EXPECTED_5),
        ({'login': 'unholy'}, RU_HEADERS_4, 200, EXPECTED_7),
        ({'login': 'valentin'}, RU_HEADERS_5, 200, EXPECTED_8),
        ({'login': 'justmark0'}, RU_HEADERS_6, 200, EXPECTED_9),
    ],
)
async def test_profile_with_config(
        web_app_client,
        mock_piecework_calc_load,
        body,
        headers,
        status_code,
        expected_data,
        mock_retrieve_personal,
        mock_retrieve_telegrams,
):
    response = await web_app_client.post(
        '/profile', headers=headers, json=body,
    )
    if status_code == 200:
        assert response.status == status_code
        content = await response.json()
        assert len(content['main_indicators']) == len(
            expected_data['main_indicators'],
        )
        for content_widget in content['main_indicators']:
            key = content_widget['id']
            for expected_widget in expected_data['main_indicators']:
                if key == expected_widget['id']:
                    assert content_widget == expected_widget


@pytest.mark.config(AGENT_PROJECT_SETTINGS=PROJECT_SETTINGS)
async def test_battle_pass_features_check(
        web_context,
        web_app_client,
        mock_retrieve_personal,
        mock_retrieve_telegrams,
):
    response = await web_app_client.post(
        '/profile',
        headers={
            'X-Yandex-Login': 'test_battlepass_login',
            'Accept-Language': 'ru-RU',
        },
        json={'login': 'test_battlepass_login'},
    )
    assert response.status == 200
    content = await response.json()
    assert 'view_battle_pass' in content['features']


@pytest.mark.parametrize(
    'login, piecework_response, expected_answer',
    [
        (
            'taxisupport_support_login',
            {
                'calculation': {'commited': True},
                'logins': [
                    {
                        'login': 'taxisupport_support_login',
                        'bo': {
                            'daytime_cost': 15.003,
                            'night_cost': 15.003,
                            'holidays_daytime_cost': 15.003,
                            'holidays_night_cost': 15.003,
                        },
                        'benefit_details': {
                            'min_hour_cost': 12,
                            'workshifts_duration_sec': 12,
                        },
                        'corrections': {
                            'intermediate': {
                                'daytime_bo': 44.12,
                                'night_bo': 44.12,
                                'holidays_daytime_bo': 44.12,
                                'holidays_night_bo': 44.12,
                            },
                        },
                        'benefits': 0,
                    },
                ],
            },
            {
                'avatar': AVATAR_TEMPLATE % 'taxisupport_support_login',
                'login': 'taxisupport_support_login',
                'first_name': 'taxisupport_support_first_name',
                'last_name': 'taxisupport_support_last_name',
                'features': ['view_profile'],
                'team': {'key': None, 'name': None},
                'balance_of_coins': 0,
                'phones': [],
                'telegrams': [],
                'email': 'taxisupport_support_login@yandex-team.ru',
                'main_indicators': [
                    {
                        'id': 'widget_taxisupport_csat',
                        'position': 1,
                        'type': 'computing',
                        'title': 'КСАТ',
                        'subtitle': 'за период',
                        'about': 'Информация о виджете',
                    },
                    {
                        'id': 'widget_taxisupport_norm',
                        'position': 3,
                        'detailing': False,
                        'type': 'progress',
                        'title': 'Норма',
                        'subtitle': 'за период',
                        'about': 'Информация о виджете',
                        'value': {'value': 5912.3, 'style': 'percent'},
                        'progress': {'scale': [0.9], 'direction': 'asc'},
                    },
                    {
                        'id': 'widget_taxisupport_qa',
                        'position': 2,
                        'type': 'computing',
                        'title': 'Качество',
                        'subtitle': 'за период',
                        'about': 'Информация о виджете',
                    },
                ],
            },
        ),
        (
            'taxisupport_support_login_1',
            {
                'calculation': {'commited': True},
                'logins': [
                    {
                        'login': 'taxisupport_support_login',
                        'bo': {
                            'daytime_cost': 15.003,
                            'night_cost': 15.003,
                            'holidays_daytime_cost': 15.003,
                            'holidays_night_cost': 15.003,
                        },
                        'benefit_details': {
                            'min_hour_cost': 12,
                            'workshifts_duration_sec': 12,
                        },
                        'corrections': {
                            'intermediate': {
                                'daytime_bo': 44.12,
                                'night_bo': 44.12,
                                'holidays_daytime_bo': 44.12,
                                'holidays_night_bo': 44.12,
                            },
                        },
                        'benefits': 0,
                    },
                ],
            },
            {
                'avatar': AVATAR_TEMPLATE % 'taxisupport_support_login_1',
                'login': 'taxisupport_support_login_1',
                'first_name': 'taxisupport_support_first_name',
                'last_name': 'taxisupport_support_last_name',
                'features': ['view_profile'],
                'team': {'key': None, 'name': None},
                'balance_of_coins': 0,
                'phones': [],
                'telegrams': [],
                'email': 'taxisupport_support_login_1@yandex-team.ru',
                'main_indicators': [
                    {
                        'id': 'widget_taxisupport_csat',
                        'position': 1,
                        'type': 'computing',
                        'title': 'КСАТ',
                        'subtitle': 'за период',
                        'about': 'Информация о виджете',
                    },
                    {
                        'id': 'widget_taxisupport_norm',
                        'position': 3,
                        'type': 'computing',
                        'title': 'Норма',
                        'subtitle': 'за период',
                        'about': 'Информация о виджете',
                    },
                    {
                        'id': 'widget_taxisupport_qa',
                        'position': 2,
                        'type': 'computing',
                        'title': 'Качество',
                        'subtitle': 'за период',
                        'about': 'Информация о виджете',
                    },
                ],
            },
        ),
        (
            'taxisupport_support_login_2',
            {
                'calculation': {'commited': True},
                'logins': [
                    {
                        'login': 'taxisupport_support_login',
                        'bo': {
                            'daytime_cost': 15.003,
                            'night_cost': 15.003,
                            'holidays_daytime_cost': 15.003,
                            'holidays_night_cost': 15.003,
                        },
                        'benefit_details': {
                            'min_hour_cost': 0,
                            'workshifts_duration_sec': 12,
                        },
                        'corrections': {
                            'intermediate': {
                                'daytime_bo': 44.12,
                                'night_bo': 44.12,
                                'holidays_daytime_bo': 44.12,
                                'holidays_night_bo': 44.12,
                            },
                        },
                        'benefits': 0,
                    },
                ],
            },
            {
                'avatar': AVATAR_TEMPLATE % 'taxisupport_support_login_2',
                'login': 'taxisupport_support_login_2',
                'first_name': 'taxisupport_support_first_name',
                'last_name': 'taxisupport_support_last_name',
                'features': ['view_profile'],
                'team': {'key': None, 'name': None},
                'balance_of_coins': 0,
                'phones': [],
                'telegrams': [],
                'email': 'taxisupport_support_login_2@yandex-team.ru',
                'main_indicators': [
                    {
                        'id': 'widget_taxisupport_csat',
                        'position': 1,
                        'detailing': False,
                        'type': 'progress',
                        'title': 'КСАТ',
                        'subtitle': 'за период',
                        'about': 'Информация о виджете',
                        'value': {'value': 0.24, 'style': 'percent'},
                        'progress': {'scale': [0.9], 'direction': 'asc'},
                    },
                    {
                        'id': 'widget_taxisupport_norm',
                        'position': 3,
                        'type': 'computing',
                        'title': 'Норма',
                        'subtitle': 'за период',
                        'about': 'Информация о виджете',
                    },
                    {
                        'id': 'widget_taxisupport_qa',
                        'position': 2,
                        'detailing': False,
                        'type': 'progress',
                        'title': 'Качество',
                        'subtitle': 'за период',
                        'about': 'Информация о виджете',
                        'value': {'value': 0.26, 'style': 'percent'},
                        'progress': {'scale': [0.9], 'direction': 'asc'},
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.translations(agent=TRANSLATE)
@pytest.mark.now('2021-12-20T12:00:00+0000')
@pytest.mark.config(
    AGENT_WIDGETS_SETTINGS=CONFIG, AGENT_PROJECT_SETTINGS=PROJECT_SETTINGS,
)
async def test_taxisupport_profile(
        web_app_client,
        web_context,
        mockserver,
        login,
        piecework_response,
        expected_answer,
        mock_retrieve_personal,
        mock_retrieve_telegrams,
):
    @mockserver.json_handler(
        'piecework-calculation/v1/calculation/load', prefix=False,
    )
    def _mock(*args, **kwargs):
        return piecework_response

    response = await web_app_client.post(
        '/profile/',
        headers={'X-Yandex-Login': login, 'Accept-Language': 'ru-RU'},
        json={'login': login},
    )

    assert response.status == 200
    content = await response.json()
    assert content == expected_answer


@pytest.mark.parametrize(
    'login, piecework_response, expected_answer',
    [
        (
            'lavkasupport_user_1',
            {
                'calculation': {'commited': True},
                'logins': [
                    {
                        'login': 'lavkasupport_user_1',
                        'bo': {
                            'daytime_cost': 15.003,
                            'night_cost': 15.003,
                            'holidays_daytime_cost': 15.003,
                            'holidays_night_cost': 15.003,
                        },
                        'benefit_details': {
                            'min_hour_cost': 12,
                            'workshifts_duration_sec': 12,
                        },
                        'corrections': {
                            'intermediate': {
                                'daytime_bo': 44.12,
                                'night_bo': 44.12,
                                'holidays_daytime_bo': 44.12,
                                'holidays_night_bo': 44.12,
                            },
                        },
                        'benefits': 0,
                    },
                ],
            },
            {
                'avatar': AVATAR_TEMPLATE % 'lavkasupport_user_1',
                'login': 'lavkasupport_user_1',
                'first_name': 'lavkasupport_user_1_first_name',
                'last_name': 'lavkasupport_user_1_last_name',
                'features': ['view_profile'],
                'team': {'key': None, 'name': None},
                'balance_of_coins': 0,
                'phones': [],
                'telegrams': [],
                'email': 'lavkasupport_user_1@yandex-team.ru',
                'main_indicators': [
                    {
                        'id': 'widget_lavkasupport_csat',
                        'position': 1,
                        'detailing': False,
                        'type': 'progress',
                        'title': 'КСАТ',
                        'subtitle': 'за период',
                        'about': 'Информация о виджете',
                        'value': {'value': 0.77, 'style': 'percent'},
                        'progress': {'scale': [0.9], 'direction': 'asc'},
                    },
                    {
                        'id': 'widget_lavkasupport_norm',
                        'position': 3,
                        'detailing': False,
                        'type': 'progress',
                        'title': 'Норма',
                        'subtitle': 'за период',
                        'about': 'Информация о виджете',
                        'value': {'value': 5912.3, 'style': 'percent'},
                        'progress': {'scale': [0.9], 'direction': 'asc'},
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.translations(agent=TRANSLATE)
@pytest.mark.now('2021-12-20T12:00:00+0000')
@pytest.mark.config(
    AGENT_WIDGETS_SETTINGS=CONFIG, AGENT_PROJECT_SETTINGS=PROJECT_SETTINGS,
)
async def test_lavkasupport_profile(
        web_app_client,
        web_context,
        mockserver,
        login,
        piecework_response,
        expected_answer,
        mock_retrieve_personal,
        mock_retrieve_telegrams,
):
    @mockserver.json_handler(
        'piecework-calculation/v1/calculation/load', prefix=False,
    )
    def _mock(*args, **kwargs):
        return piecework_response

    response = await web_app_client.post(
        '/profile/',
        headers={'X-Yandex-Login': login, 'Accept-Language': 'ru-RU'},
        json={'login': login},
    )

    assert response.status == 200
    content = await response.json()
    assert content == expected_answer


@pytest.mark.parametrize(
    'login, piecework_response, expected_answer',
    [
        (
            'deliverysupport_user_1',
            {
                'calculation': {'commited': True},
                'logins': [
                    {
                        'login': 'deliverysupport_user_1',
                        'bo': {
                            'daytime_cost': 15.003,
                            'night_cost': 15.003,
                            'holidays_daytime_cost': 15.003,
                            'holidays_night_cost': 15.003,
                        },
                        'benefit_details': {
                            'min_hour_cost': 12,
                            'workshifts_duration_sec': 12,
                        },
                        'corrections': {
                            'intermediate': {
                                'daytime_bo': 44.12,
                                'night_bo': 44.12,
                                'holidays_daytime_bo': 44.12,
                                'holidays_night_bo': 44.12,
                            },
                        },
                        'benefits': 0,
                    },
                ],
            },
            {
                'avatar': AVATAR_TEMPLATE % 'deliverysupport_user_1',
                'login': 'deliverysupport_user_1',
                'first_name': 'deliverysupport_user_1_first_name',
                'last_name': 'deliverysupport_user_1_last_name',
                'features': ['view_profile'],
                'team': {'key': None, 'name': None},
                'balance_of_coins': 0,
                'phones': [],
                'telegrams': [],
                'email': 'deliverysupport_user_1@yandex-team.ru',
                'main_indicators': [
                    {
                        'id': 'widget_deliverysupport_norm',
                        'position': 3,
                        'detailing': False,
                        'type': 'progress',
                        'title': 'Норма',
                        'subtitle': 'за период',
                        'about': 'Информация о виджете',
                        'value': {'value': 5912.3, 'style': 'percent'},
                        'progress': {'scale': [0.9], 'direction': 'asc'},
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.translations(agent=TRANSLATE)
@pytest.mark.now('2021-12-20T12:00:00+0000')
@pytest.mark.config(
    AGENT_WIDGETS_SETTINGS=CONFIG, AGENT_PROJECT_SETTINGS=PROJECT_SETTINGS,
)
async def test_deliverysupport_profile(
        web_app_client,
        web_context,
        mockserver,
        login,
        piecework_response,
        expected_answer,
        mock_retrieve_personal,
        mock_retrieve_telegrams,
):
    @mockserver.json_handler(
        'piecework-calculation/v1/calculation/load', prefix=False,
    )
    def _mock(*args, **kwargs):
        return piecework_response

    response = await web_app_client.post(
        '/profile/',
        headers={'X-Yandex-Login': login, 'Accept-Language': 'ru-RU'},
        json={'login': login},
    )

    assert response.status == 200
    content = await response.json()
    assert content == expected_answer


@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'zapravki': {
            'enable_chatterbox': False,
            'wfm_effrat_domain': 'mediaservices',
            'piecework_tariff': 'zapravki_piecework_project',
            'main_permission': 'user_zapravki',
            'profile_information': ['phones'],
            'piecework_detailing_type': 'day',
            'piecework_source': 'piecework_calculation',
        },
    },
)
async def test_view_piecework_in_features(
        web_app_client, web_context, mock_retrieve_personal,
):
    response = await web_app_client.post(
        '/profile/',
        headers={'X-Yandex-Login': 'piece_user_1', 'Accept-Language': 'ru-RU'},
        json={'login': 'piece_user_1'},
    )

    assert response.status == 200
    content = await response.json()
    assert 'view_finance' in content['features']
    assert 'view_profile' in content['features']
    assert 'view_piecework_detailing_days' in content['features']


@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'zapravki': {
            'enable_chatterbox': False,
            'wfm_effrat_domain': 'mediaservices',
            'main_permission': 'user_zapravki',
            'profile_information': ['phones'],
            'piecework_detailing_type': 'day',
            'piecework_source': 'hrms',
        },
    },
)
async def test_view_piecework_in_features_hrms(
        web_app_client, web_context, mock_retrieve_personal,
):
    response = await web_app_client.post(
        '/profile/',
        headers={'X-Yandex-Login': 'piece_user_1', 'Accept-Language': 'ru-RU'},
        json={'login': 'piece_user_1'},
    )

    assert response.status == 200
    content = await response.json()
    assert 'view_finance' in content['features']
    assert 'view_profile' in content['features']
    assert 'view_piecework_detailing_days' in content['features']


@pytest.mark.parametrize(
    'login, piecework_response, expected_response',
    [
        (
            'eats_user_1',
            {'csat': 4.5, 'quality': 80.0},
            {
                'avatar': AVATAR_TEMPLATE % 'eats_user_1',
                'login': 'eats_user_1',
                'first_name': 'eats_user_1_first_name',
                'last_name': 'eats_user_1_last_name',
                'features': ['view_profile'],
                'team': {'key': None, 'name': None},
                'balance_of_coins': 0,
                'phones': [],
                'telegrams': [],
                'email': 'eats_user_1@yandex-team.ru',
                'main_indicators': [
                    {
                        'id': 'widget_edasupport_csat',
                        'position': 1,
                        'progress': {'direction': 'asc', 'scale': []},
                        'type': 'progress',
                        'title': 'КСАТ',
                        'subtitle': 'за период',
                        'detailing': False,
                        'about': 'Информация о виджете',
                        'value': {'style': 'percent', 'value': 0.04},
                    },
                    {
                        'id': 'widget_edasupport_qa',
                        'position': 2,
                        'progress': {'direction': 'asc', 'scale': []},
                        'type': 'progress',
                        'title': 'Качество',
                        'subtitle': 'за период',
                        'about': 'Информация о виджете',
                        'detailing': False,
                        'value': {'style': 'percent', 'value': 0.8},
                    },
                ],
            },
        ),
        (
            'eats_user_1',
            {'csat': 0.0, 'quality': 0.0},
            {
                'avatar': AVATAR_TEMPLATE % 'eats_user_1',
                'login': 'eats_user_1',
                'first_name': 'eats_user_1_first_name',
                'last_name': 'eats_user_1_last_name',
                'features': ['view_profile'],
                'team': {'key': None, 'name': None},
                'balance_of_coins': 0,
                'phones': [],
                'telegrams': [],
                'email': 'eats_user_1@yandex-team.ru',
                'main_indicators': [
                    {
                        'id': 'widget_edasupport_csat',
                        'position': 1,
                        'type': 'computing',
                        'title': 'КСАТ',
                        'subtitle': 'за период',
                        'about': 'Информация о виджете',
                    },
                    {
                        'id': 'widget_edasupport_qa',
                        'position': 2,
                        'type': 'computing',
                        'title': 'Качество',
                        'subtitle': 'за период',
                        'about': 'Информация о виджете',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.config(AGENT_PROJECT_SETTINGS=PROJECT_SETTINGS)
@pytest.mark.translations(agent=TRANSLATE)
@pytest.mark.now('2022-01-25T12:00:00+0000')
@pytest.mark.config(AGENT_WIDGETS_SETTINGS=CONFIG)
async def test_eats_support_green(
        web_app_client,
        web_context,
        mockserver,
        login,
        piecework_response,
        expected_response,
        mock_retrieve_personal,
        mock_retrieve_telegrams,
):
    @mockserver.json_handler(
        'piecework-calculation/v1/eats-support-metrics', prefix=False,
    )
    def _get_eats_support_metrics(*args, **kwargs):
        return piecework_response

    response = await web_app_client.post(
        '/profile/',
        headers={'X-Yandex-Login': login, 'Accept-Language': 'ru-RU'},
        json={'login': login},
    )

    assert response.status == 200
    content = await response.json()
    assert content == expected_response


@pytest.mark.parametrize(
    'login, piecework_status, expected_response',
    [
        (
            'eats_user_1',
            500,
            {
                'avatar': AVATAR_TEMPLATE % 'eats_user_1',
                'login': 'eats_user_1',
                'first_name': 'eats_user_1_first_name',
                'last_name': 'eats_user_1_last_name',
                'features': ['view_profile'],
                'team': {'key': None, 'name': None},
                'balance_of_coins': 0,
                'phones': [],
                'telegrams': [],
                'email': 'eats_user_1@yandex-team.ru',
                'main_indicators': [
                    {
                        'id': 'widget_edasupport_csat',
                        'position': 1,
                        'type': 'computing',
                        'title': 'КСАТ',
                        'subtitle': 'за период',
                        'about': 'Информация о виджете',
                    },
                    {
                        'id': 'widget_edasupport_qa',
                        'position': 2,
                        'type': 'computing',
                        'title': 'Качество',
                        'subtitle': 'за период',
                        'about': 'Информация о виджете',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.translations(agent=TRANSLATE)
@pytest.mark.now('2022-01-25T12:00:00+0000')
@pytest.mark.config(AGENT_PROJECT_SETTINGS=PROJECT_SETTINGS)
@pytest.mark.config(AGENT_WIDGETS_SETTINGS=CONFIG)
async def test_eats_support_piecework_red(
        web_app_client,
        web_context,
        mockserver,
        login,
        piecework_status,
        expected_response,
        mock_retrieve_personal,
        mock_retrieve_telegrams,
):
    @mockserver.json_handler(
        'piecework-calculation/v1/eats-support-metrics', prefix=False,
    )
    def _get_eats_support_metrics(*args, **kwargs):
        return mockserver.make_response(status=piecework_status, json={})

    response = await web_app_client.post(
        '/profile/',
        headers={'X-Yandex-Login': login, 'Accept-Language': 'ru-RU'},
        json={'login': login},
    )

    assert response.status == 200
    content = await response.json()
    assert content == expected_response


@pytest.mark.parametrize(
    'login, piecework_response, expected_answer',
    [
        (
            'driverhiring_user_1',
            {
                'calculation': {'commited': True},
                'logins': [
                    {
                        'login': 'driverhiring_user_1',
                        'bo': {
                            'daytime_cost': 15.003,
                            'night_cost': 15.003,
                            'holidays_daytime_cost': 15.003,
                            'holidays_night_cost': 15.003,
                        },
                        'benefit_details': {'hour_cost': 12},
                        'corrections': {},
                        'benefits': 0,
                    },
                ],
            },
            {
                'avatar': AVATAR_TEMPLATE % 'driverhiring_user_1',
                'login': 'driverhiring_user_1',
                'first_name': 'driverhiring_user_1',
                'last_name': 'driverhiring_user_1',
                'features': ['view_profile'],
                'team': {'key': None, 'name': None},
                'balance_of_coins': 0,
                'phones': [],
                'telegrams': [],
                'email': 'driverhiring_user_1@yandex-team.ru',
                'main_indicators': [
                    {
                        'id': 'widget_driverhiring_actives',
                        'position': 1,
                        'detailing': False,
                        'type': 'absolute',
                        'title': 'widget_driverhiring_actives',
                        'subtitle': 'widget_driverhiring_actives',
                        'about': 'Информация о виджете',
                        'value': {'value': 288, 'style': 'decimal'},
                    },
                    {
                        'id': 'widget_driverhiring_calls',
                        'position': 1,
                        'detailing': False,
                        'type': 'absolute',
                        'title': 'widget_driverhiring_calls',
                        'subtitle': 'widget_driverhiring_calls',
                        'about': 'Информация о виджете',
                        'value': {'value': 200, 'style': 'decimal'},
                    },
                    {
                        'id': 'widget_driverhiring_conversion',
                        'position': 1,
                        'detailing': False,
                        'type': 'progress',
                        'title': 'widget_driverhiring_conversion',
                        'subtitle': 'widget_driverhiring_conversion',
                        'about': 'Информация о виджете',
                        'value': {'value': 1.44, 'style': 'percent'},
                        'progress': {'scale': [0.9], 'direction': 'asc'},
                    },
                    {
                        'id': 'widget_driverhiring_qa',
                        'position': 1,
                        'detailing': False,
                        'type': 'progress',
                        'title': 'widget_driverhiring_qa',
                        'subtitle': 'widget_driverhiring_qa',
                        'about': 'Информация о виджете',
                        'value': {'value': 0.02, 'style': 'percent'},
                        'progress': {'scale': [0.9], 'direction': 'asc'},
                    },
                    {
                        'id': 'widget_driverhiring_speed',
                        'position': 1,
                        'detailing': False,
                        'type': 'progress',
                        'title': 'widget_driverhiring_speed',
                        'subtitle': 'widget_driverhiring_speed',
                        'about': 'Информация о виджете',
                        'value': {'value': 0.12, 'style': 'percent'},
                        'progress': {'scale': [0.9], 'direction': 'asc'},
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.translations(agent=TRANSLATE)
@pytest.mark.now('2022-01-20T00:00:00+0000')
@pytest.mark.config(
    AGENT_WIDGETS_SETTINGS=CONFIG,
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'driverhiring': {
            'enable_chatterbox': False,
            'piecework_tariff': 'support-taxi',
            'main_permission': 'user_driverhiring',
            'profile_information': ['phones'],
        },
    },
)
async def test_driverhiring_profile(
        web_app_client,
        web_context,
        mockserver,
        login,
        piecework_response,
        expected_answer,
        mock_retrieve_personal,
        mock_retrieve_telegrams,
):
    @mockserver.json_handler(
        'piecework-calculation/v1/calculation/load', prefix=False,
    )
    def _mock(*args, **kwargs):
        return piecework_response

    response = await web_app_client.post(
        '/profile/',
        headers={'X-Yandex-Login': login, 'Accept-Language': 'ru-RU'},
        json={'login': login},
    )

    assert response.status == 200
    content = await response.json()
    assert content == expected_answer
