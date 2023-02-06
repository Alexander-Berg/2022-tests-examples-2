# pylint: disable=C0302
import pytest

WEBALEX_HEADERS: dict = {
    'X-Yandex-Login': 'webalex',
    'Accept-Language': 'ru-ru',
}

ORANGEVL_HEADERS: dict = {
    'X-Yandex-Login': 'orangevl',
    'Accept-Language': 'ru-ru',
}

ORANGEVL_EN_HEADERS: dict = {
    'X-Yandex-Login': 'orangevl',
    'Accept-Language': 'en-en',
}

JUSTMARK0_HEADERS: dict = {
    'X-Yandex-Login': 'justmark0',
    'Accept-Language': 'ru-ru',
}

CALLTAXI_CHIEF_HEADERS: dict = {
    'X-Yandex-Login': 'calltaxi_chief',
    'Accept-Language': 'ru-ru',
}

DIRECTSUPPORT_CHIEF_HEADERS: dict = {
    'X-Yandex-Login': 'directsupport_chief',
    'Accept-Language': 'ru-ru',
}

COMDELIVERY_CHIEF_HEADERS: dict = {
    'X-Yandex-Login': 'comdelivery_chief',
    'Accept-Language': 'ru-ru',
}

LAVKASUPPORT_CHIEF_HEADERS: dict = {
    'X-Yandex-Login': 'lavkasupport_chief',
    'Accept-Language': 'ru-ru',
}
TAXISUPPORT_CC_CHIEF_HEADERS: dict = {
    'X-Yandex-Login': 'taxisupport_cc_chief',
    'Accept-Language': 'ru-ru',
}

INTERNATIONALTAXI_CHIEF_HEADERS: dict = {
    'X-Yandex-Login': 'internationaltaxi_chief',
    'Accept-Language': 'ru-ru',
}

SLON_HEADERS: dict = {'X-Yandex-Login': 'slon', 'Accept-Language': 'ru-ru'}

VASIN_HEADERS: dict = {'X-Yandex-Login': 'vasin', 'Accept-Language': 'ru-ru'}
VASIN_EN_HEADERS: dict = {
    'X-Yandex-Login': 'vasin',
    'Accept-Language': 'en-en',
}


AVATAR_TEMPLATE = 'https://center.yandex-team.ru/api/v1/user/%s/photo/300.jpg'


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
        'tanker_subtitle_key': 'widget_calltaxi_discipline',
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
    'widget_directsupport_fcalls': {
        'indicator_type': 'absolute',
        'position': 2,
        'scale': [50, 90],
        'show_in_cabinet': True,
        'show_in_profile': True,
        'tanker_about_key': 'about_widget_waiting',
        'tanker_subtitle_key': 'subtitle_widget_directsupport_fcalls',
        'tanker_title_key': 'title_widget_directsupport_fcalls',
        'type': 'progress',
    },
    'widget_directsupport_goal1': {
        'indicator_type': 'absolute',
        'position': 3,
        'scale': [50, 90],
        'show_in_cabinet': True,
        'show_in_profile': True,
        'tanker_about_key': 'about_widget_waiting',
        'tanker_subtitle_key': 'subtitle_widget_widget_directsupport_goal1',
        'tanker_title_key': 'title_widget_directsupport_goal1',
        'type': 'progress',
    },
    'widget_directsupport_goal2': {
        'indicator_type': 'absolute',
        'position': 4,
        'scale': [50, 90],
        'show_in_cabinet': True,
        'show_in_profile': True,
        'tanker_about_key': 'about_widget_waiting',
        'tanker_subtitle_key': 'subtitle_widget_widget_directsupport_goal2',
        'tanker_title_key': 'title_widget_directsupport_goal2',
        'type': 'progress',
    },
    'widget_directsupport_nofcalls': {
        'indicator_type': 'absolute',
        'position': 5,
        'scale': [50, 90],
        'show_in_cabinet': True,
        'show_in_profile': True,
        'tanker_about_key': 'about_widget_waiting',
        'tanker_subtitle_key': 'subtitle_widget_widget_directsupport_nofcalls',
        'tanker_title_key': 'title_widget_directsupport_nofcalls',
        'type': 'progress',
    },
    'widget_directsupport_qa': {
        'indicator_type': 'progress',
        'position': 6,
        'scale': [50, 90],
        'show_in_cabinet': False,
        'show_in_profile': True,
        'tanker_about_key': 'about_widget_waiting',
        'tanker_subtitle_key': 'subtitle_widget_widget_directsupport_qa',
        'tanker_title_key': 'title_widget_directsupport_qa',
        'type': 'progress',
    },
    'widget_directsupport_skip': {
        'indicator_type': 'progress',
        'position': 7,
        'scale': [50, 90],
        'show_in_cabinet': True,
        'show_in_profile': True,
        'tanker_about_key': 'about_widget_waiting',
        'tanker_subtitle_key': 'subtitle_widget_directsupport_skip',
        'tanker_title_key': 'title_widget_directsupport_skip',
        'type': 'progress',
    },
    'widget_directsupport_upsale': {
        'indicator_type': 'progress',
        'position': 8,
        'scale': [50, 90],
        'show_in_cabinet': True,
        'show_in_profile': True,
        'tanker_about_key': 'about_widget_waiting',
        'tanker_subtitle_key': 'subtitle_widget_directsupport_upsale',
        'tanker_title_key': 'title_widget_directsupport_upsale',
        'type': 'progress',
    },
    'widget_directsupport_wfm': {
        'indicator_type': 'absolute',
        'position': 1,
        'scale': [50, 90],
        'show_in_cabinet': True,
        'show_in_profile': True,
        'tanker_about_key': 'about_widget_waiting',
        'tanker_subtitle_key': 'subtitle_widget_directsupport_wfm',
        'tanker_title_key': 'title_widget_widget_directsupport_wfm',
        'type': 'progress',
    },
    'widget_directsupport_iscore': {
        'show_in_cabinet': True,
        'show_in_profile': True,
        'indicator_type': 'absolute',
        'type': 'progress',
    },
    'widget_directsupport_pos_oscore': {
        'show_in_cabinet': True,
        'show_in_profile': True,
        'indicator_type': 'absolute',
        'type': 'progress',
    },
    'widget_lavkasupport_norm': {
        'type': 'progress',
        'indicator_type': 'progress',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_taxisupport_cc_norm': {
        'type': 'progress',
        'indicator_type': 'absolute',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_internationaltaxi_tph': {
        'type': 'progress',
        'indicator_type': 'absolute',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_internationaltaxi_sumactions': {
        'type': 'progress',
        'indicator_type': 'absolute',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_internationaltaxi_workhours': {
        'type': 'progress',
        'indicator_type': 'absolute',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
    'widget_internationaltaxi_avgtph': {
        'type': 'progress',
        'indicator_type': 'absolute',
        'show_in_profile': True,
        'show_in_cabinet': True,
    },
}


@pytest.mark.now('2022-06-01T00:00:00+0000')
@pytest.mark.config(AGENT_WIDGETS_SETTINGS=CONFIG)
@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'calltaxi': {
            'enable_chatterbox': False,
            'main_permission': 'user_calltaxi',
        },
        'support_taxi': {
            'enable_chatterbox': False,
            'main_permission': 'user_support_taxi',
            'piecework_tariff': 'support-taxi',
        },
        'cargo_callcenter': {
            'enable_chatterbox': False,
            'main_permission': 'user_cargo_callcenter',
            'piecework_tariff': 'cargo-callcenter',
        },
        'taxisupport_cc': {
            'enable_chatterbox': False,
            'piecework_tariff': 'asterisk-support-taxi',
            'main_permission': 'user_taxisupport_cc',
        },
    },
)
@pytest.mark.parametrize(
    'url,headers,expected_data',
    [
        (
            '/cabinet?limit=100',
            SLON_HEADERS,
            {
                'columns': [],
                'page': 1,
                'total': 3,
                'limit': 100,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'calltaxi_chief',
                        'department': 'calltaxi',
                        'first_name': 'first_name_1',
                        'last_name': 'last_name_1',
                        'login': 'calltaxi_chief',
                        'piece': False,
                        'team': '—',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'valera',
                        'login': 'valera',
                        'first_name': 'Валера',
                        'last_name': 'Левин',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'D-команда',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'vavan',
                        'login': 'vavan',
                        'first_name': 'Владимир',
                        'last_name': 'Николаев',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'C-команда',
                    },
                ],
            },
        ),
        (
            '/cabinet',
            WEBALEX_HEADERS,
            {'columns': [], 'page': 1, 'total': 0, 'limit': 30, 'results': []},
        ),
        (
            '/cabinet?limit=1',
            ORANGEVL_HEADERS,
            {
                'columns': [],
                'page': 1,
                'total': 4,
                'limit': 1,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'akozhevina',
                        'login': 'akozhevina',
                        'first_name': 'Анна',
                        'last_name': 'Кожевина',
                        'department': 'Яндекс',
                        'piece': False,
                        'team': '—',
                    },
                ],
            },
        ),
        (
            '/cabinet?page=2&limit=1',
            ORANGEVL_HEADERS,
            {
                'columns': [],
                'page': 2,
                'total': 4,
                'limit': 1,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'mikh-vasily',
                        'login': 'mikh-vasily',
                        'first_name': 'Василий',
                        'last_name': 'Михайлов',
                        'department': 'Яндекс.Такси',
                        'piece': False,
                        'team': '—',
                    },
                ],
            },
        ),
        (
            '/cabinet?limit=1&page=1&sort=login&sort_direction=desc',
            ORANGEVL_HEADERS,
            {
                'columns': [],
                'page': 1,
                'total': 4,
                'limit': 1,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'webalex',
                        'login': 'webalex',
                        'first_name': 'Александр',
                        'last_name': 'Иванов',
                        'department': 'Яндекс.Такси',
                        'piece': False,
                        'team': '—',
                    },
                ],
            },
        ),
        (
            '/cabinet?&department=yandex',
            ORANGEVL_HEADERS,
            {
                'columns': [],
                'page': 1,
                'total': 2,
                'limit': 30,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'akozhevina',
                        'login': 'akozhevina',
                        'first_name': 'Анна',
                        'last_name': 'Кожевина',
                        'department': 'Яндекс',
                        'piece': False,
                        'team': '—',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'orangevl',
                        'login': 'orangevl',
                        'first_name': 'Семён',
                        'last_name': 'Решетняк',
                        'department': 'Яндекс',
                        'piece': False,
                        'team': '—',
                    },
                ],
            },
        ),
        (
            '/cabinet?&department=outstaff&sort=team&sort_direction=asc',
            VASIN_HEADERS,
            {
                'columns': [],
                'page': 1,
                'total': 6,
                'limit': 30,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'vasin',
                        'login': 'vasin',
                        'first_name': 'Илья',
                        'last_name': 'Васин',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'A-команда',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'pirozhochek',
                        'login': 'pirozhochek',
                        'first_name': 'Дмитрий',
                        'last_name': 'Бобров',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'B-команда',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'vavan',
                        'login': 'vavan',
                        'first_name': 'Владимир',
                        'last_name': 'Николаев',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'C-команда',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'valera',
                        'login': 'valera',
                        'first_name': 'Валера',
                        'last_name': 'Левин',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'D-команда',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'katya',
                        'login': 'katya',
                        'first_name': 'Катя',
                        'last_name': 'Белкина',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'E-команда',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'nlo',
                        'login': 'nlo',
                        'first_name': 'Владимир',
                        'last_name': 'Владимиров',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'F-команда',
                    },
                ],
            },
        ),
        (
            '/cabinet?&department=outstaff&sort=team&sort_direction=desc',
            VASIN_HEADERS,
            {
                'columns': [],
                'page': 1,
                'total': 6,
                'limit': 30,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'nlo',
                        'login': 'nlo',
                        'first_name': 'Владимир',
                        'last_name': 'Владимиров',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'F-команда',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'katya',
                        'login': 'katya',
                        'first_name': 'Катя',
                        'last_name': 'Белкина',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'E-команда',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'valera',
                        'login': 'valera',
                        'first_name': 'Валера',
                        'last_name': 'Левин',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'D-команда',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'vavan',
                        'login': 'vavan',
                        'first_name': 'Владимир',
                        'last_name': 'Николаев',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'C-команда',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'pirozhochek',
                        'login': 'pirozhochek',
                        'first_name': 'Дмитрий',
                        'last_name': 'Бобров',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'B-команда',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'vasin',
                        'login': 'vasin',
                        'first_name': 'Илья',
                        'last_name': 'Васин',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'A-команда',
                    },
                ],
            },
        ),
        (
            '/cabinet?&department=outstaff&sort=team&sort_direction=desc',
            VASIN_EN_HEADERS,
            {
                'columns': [],
                'page': 1,
                'total': 6,
                'limit': 30,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'nlo',
                        'login': 'nlo',
                        'first_name': 'Vladimir',
                        'last_name': 'Vladimirov',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'F team',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'katya',
                        'login': 'katya',
                        'first_name': 'Kate',
                        'last_name': 'Belkina',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'E team',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'valera',
                        'login': 'valera',
                        'first_name': 'Valery',
                        'last_name': 'Levin',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'D team',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'vavan',
                        'login': 'vavan',
                        'first_name': 'Vladimir',
                        'last_name': 'Nikolaev',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'C team',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'pirozhochek',
                        'login': 'pirozhochek',
                        'first_name': 'Dmitry',
                        'last_name': 'Bobrov',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'B team',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'vasin',
                        'login': 'vasin',
                        'first_name': 'Ilya',
                        'last_name': 'Vasin',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'A team',
                    },
                ],
            },
        ),
        (
            '/cabinet?&logins=calltaxi_chief,valera',
            SLON_HEADERS,
            {
                'columns': [],
                'page': 1,
                'total': 2,
                'limit': 30,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'calltaxi_chief',
                        'department': 'calltaxi',
                        'first_name': 'first_name_1',
                        'last_name': 'last_name_1',
                        'login': 'calltaxi_chief',
                        'piece': False,
                        'team': '—',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'valera',
                        'login': 'valera',
                        'first_name': 'Валера',
                        'last_name': 'Левин',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'D-команда',
                    },
                ],
            },
        ),
        (
            '/cabinet?&logins=calltaxi_chief,valera',
            SLON_HEADERS,
            {
                'columns': [],
                'page': 1,
                'total': 2,
                'limit': 30,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'calltaxi_chief',
                        'department': 'calltaxi',
                        'first_name': 'first_name_1',
                        'last_name': 'last_name_1',
                        'login': 'calltaxi_chief',
                        'piece': False,
                        'team': '—',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'valera',
                        'login': 'valera',
                        'first_name': 'Валера',
                        'last_name': 'Левин',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'D-команда',
                    },
                ],
            },
        ),
        (
            '/cabinet?&countries=ru,en',
            SLON_HEADERS,
            {
                'columns': [],
                'page': 1,
                'total': 2,
                'limit': 30,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'calltaxi_chief',
                        'department': 'calltaxi',
                        'first_name': 'first_name_1',
                        'last_name': 'last_name_1',
                        'login': 'calltaxi_chief',
                        'piece': False,
                        'team': '—',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'valera',
                        'login': 'valera',
                        'first_name': 'Валера',
                        'last_name': 'Левин',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'D-команда',
                    },
                ],
            },
        ),
        (
            '/cabinet?&piece=False',
            SLON_HEADERS,
            {
                'columns': [],
                'page': 1,
                'total': 1,
                'limit': 30,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'calltaxi_chief',
                        'department': 'calltaxi',
                        'first_name': 'first_name_1',
                        'last_name': 'last_name_1',
                        'login': 'calltaxi_chief',
                        'piece': False,
                        'team': '—',
                    },
                ],
            },
        ),
        (
            '/cabinet?&half_time_work=False',
            SLON_HEADERS,
            {
                'columns': [],
                'page': 1,
                'total': 1,
                'limit': 30,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'valera',
                        'login': 'valera',
                        'first_name': 'Валера',
                        'last_name': 'Левин',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'D-команда',
                    },
                ],
            },
        ),
        (
            '/cabinet?&assigned_lines=line_1',
            SLON_HEADERS,
            {
                'columns': [],
                'page': 1,
                'total': 1,
                'limit': 30,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'valera',
                        'login': 'valera',
                        'first_name': 'Валера',
                        'last_name': 'Левин',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'D-команда',
                    },
                ],
            },
        ),
        (
            '/cabinet?&available_lines=line_1',
            SLON_HEADERS,
            {
                'columns': [],
                'page': 1,
                'total': 1,
                'limit': 30,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'valera',
                        'login': 'valera',
                        'first_name': 'Валера',
                        'last_name': 'Левин',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'D-команда',
                    },
                ],
            },
        ),
        (
            '/cabinet?&can_choose_from_lines=False',
            SLON_HEADERS,
            {
                'columns': [],
                'page': 1,
                'total': 1,
                'limit': 30,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'valera',
                        'login': 'valera',
                        'first_name': 'Валера',
                        'last_name': 'Левин',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'D-команда',
                    },
                ],
            },
        ),
        (
            '/cabinet?&can_choose_except_lines=False',
            SLON_HEADERS,
            {
                'columns': [],
                'page': 1,
                'total': 1,
                'limit': 30,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'valera',
                        'login': 'valera',
                        'first_name': 'Валера',
                        'last_name': 'Левин',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'D-команда',
                    },
                ],
            },
        ),
        (
            '/cabinet?&work_off_shift=False',
            SLON_HEADERS,
            {
                'columns': [],
                'page': 1,
                'total': 1,
                'limit': 30,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'valera',
                        'login': 'valera',
                        'first_name': 'Валера',
                        'last_name': 'Левин',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'D-команда',
                    },
                ],
            },
        ),
        (
            '/cabinet?&languages=ru,en',
            SLON_HEADERS,
            {
                'columns': [],
                'page': 1,
                'total': 2,
                'limit': 30,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'calltaxi_chief',
                        'department': 'calltaxi',
                        'first_name': 'first_name_1',
                        'last_name': 'last_name_1',
                        'login': 'calltaxi_chief',
                        'piece': False,
                        'team': '—',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'valera',
                        'login': 'valera',
                        'first_name': 'Валера',
                        'last_name': 'Левин',
                        'department': 'outstaff',
                        'piece': False,
                        'team': 'D-команда',
                    },
                ],
            },
        ),
        (
            '/cabinet',
            JUSTMARK0_HEADERS,
            {
                'page': 1,
                'total': 3,
                'limit': 30,
                'columns': [
                    {
                        'column_name': 'widget_shared_bo',
                        'translation': 'widget_shared_bo',
                    },
                    {
                        'column_name': 'widget_shared_reserve',
                        'translation': 'widget_shared_reserve',
                    },
                ],
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'cargo_callcenter_user',
                        'login': 'cargo_callcenter_user',
                        'first_name': 'first_name_13',
                        'last_name': 'last_name_13',
                        'department': 'bo_reserve',
                        'team': 'cargo-callcenter',
                        'piece': True,
                        'widget_shared_bo': '51.54',
                        'widget_shared_reserve': '150',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'justmark0',
                        'login': 'justmark0',
                        'first_name': 'Марк',
                        'last_name': 'Николсон',
                        'department': 'bo_reserve',
                        'team': 'cargo-callcenter',
                        'piece': True,
                        'widget_shared_bo': '50.54',
                        'widget_shared_reserve': '100',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'support_taxi_user',
                        'login': 'support_taxi_user',
                        'first_name': 'first_name_12',
                        'last_name': 'last_name_12',
                        'department': 'bo_reserve',
                        'team': 'Саппорт Такси',
                        'piece': True,
                        'widget_shared_bo': '46.54',
                    },
                ],
            },
        ),
        (
            '/cabinet',
            INTERNATIONALTAXI_CHIEF_HEADERS,
            {
                'page': 1,
                'total': 2,
                'limit': 30,
                'columns': [
                    {
                        'column_name': 'widget_internationaltaxi_avgtph',
                        'translation': 'widget_internationaltaxi_avgtph',
                    },
                    {
                        'column_name': 'widget_internationaltaxi_sumactions',
                        'translation': 'widget_internationaltaxi_sumactions',
                    },
                    {
                        'column_name': 'widget_internationaltaxi_tph',
                        'translation': 'widget_internationaltaxi_tph',
                    },
                    {
                        'column_name': 'widget_internationaltaxi_workhours',
                        'translation': 'widget_internationaltaxi_workhours',
                    },
                ],
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'internationaltaxi_chief',
                        'login': 'internationaltaxi_chief',
                        'first_name': 'internationaltaxi_chief',
                        'last_name': 'internationaltaxi_chief',
                        'department': 'internationaltaxi',
                        'team': '—',
                        'piece': False,
                        'widget_internationaltaxi_avgtph': '600.0',
                        'widget_internationaltaxi_sumactions': '300',
                        'widget_internationaltaxi_tph': '11.33',
                        'widget_internationaltaxi_workhours': '7.5',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'internationaltaxi_user',
                        'login': 'internationaltaxi_user',
                        'first_name': 'internationaltaxi_user',
                        'last_name': 'internationaltaxi_user',
                        'department': 'internationaltaxi',
                        'team': '—',
                        'piece': False,
                        'widget_internationaltaxi_avgtph': '600.0',
                        'widget_internationaltaxi_sumactions': '35',
                        'widget_internationaltaxi_tph': '4.29',
                        'widget_internationaltaxi_workhours': '3.5',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.config(AGENT_USE_PIECEWORK_FOR_RESERVE=True)
async def test_cabinet(
        web_app_client,
        mock_piecework_calculation_load,
        mock_picework_reserve_current,
        url,
        headers,
        expected_data,
):
    response = await web_app_client.get(url, headers=headers)
    assert response.status == 200
    content = await response.json()
    assert content == expected_data


@pytest.mark.config(AGENT_WIDGETS_SETTINGS=CONFIG)
@pytest.mark.parametrize(
    'headers,expected_data',
    [
        (WEBALEX_HEADERS, []),
        (
            ORANGEVL_HEADERS,
            [
                {
                    'id': 'ba36777b3d4d4d40944c43fe008117e1',
                    'date_dismiss': '2021-11-01',
                    'head': {
                        'login': 'orangevl',
                        'first_name': 'Семён',
                        'last_name': 'Решетняк',
                    },
                    'user': {
                        'login': 'vasin',
                        'first_name': 'Илья',
                        'last_name': 'Васин',
                    },
                },
                {
                    'id': '078bdc7fae2c4a8b86ab2d64cb39bfe9',
                    'date_dismiss': '2021-11-02',
                    'head': {
                        'login': 'orangevl',
                        'first_name': 'Семён',
                        'last_name': 'Решетняк',
                    },
                    'user': {
                        'login': 'pirozhochek',
                        'first_name': 'Дмитрий',
                        'last_name': 'Бобров',
                    },
                },
            ],
        ),
        (
            ORANGEVL_EN_HEADERS,
            [
                {
                    'id': 'ba36777b3d4d4d40944c43fe008117e1',
                    'date_dismiss': '2021-11-01',
                    'head': {
                        'login': 'orangevl',
                        'first_name': 'Simon',
                        'last_name': 'Reshetnyak',
                    },
                    'user': {
                        'login': 'vasin',
                        'first_name': 'Ilya',
                        'last_name': 'Vasin',
                    },
                },
                {
                    'id': '078bdc7fae2c4a8b86ab2d64cb39bfe9',
                    'date_dismiss': '2021-11-02',
                    'head': {
                        'login': 'orangevl',
                        'first_name': 'Simon',
                        'last_name': 'Reshetnyak',
                    },
                    'user': {
                        'login': 'pirozhochek',
                        'first_name': 'Dmitry',
                        'last_name': 'Bobrov',
                    },
                },
            ],
        ),
    ],
)
async def test_dismiss_users(web_app_client, headers, expected_data):
    response = await web_app_client.get(
        '/cabinet/dismissed_users', headers=headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_data


@pytest.mark.config(AGENT_WIDGETS_SETTINGS=CONFIG)
@pytest.mark.translations(
    agent={
        'dismiss_reason_money_is_tight': {
            'ru': 'Недостаточный уровень ЗП',
            'en': 'Insufficient level of salary',
        },
        'dismiss_type_own_wish': {
            'ru': 'По собственному желанию',
            'en': 'Of your own free will',
        },
        'dismiss_type_agreement_of_the_parties': {
            'ru': 'По соглашению сторон',
            'en': 'By agreement of the parties',
        },
    },
)
async def test_dismiss_form(web_app_client):
    response = await web_app_client.get(
        '/cabinet/dismissed_user/form', headers=WEBALEX_HEADERS,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'dismissed_reasons': [
            {'key': 'money_is_tight', 'name': 'Недостаточный уровень ЗП'},
        ],
        'dismissed_type': [
            {'key': 'own_wish', 'name': 'По собственному желанию'},
            {
                'key': 'agreement_of_the_parties',
                'name': 'По соглашению сторон',
            },
        ],
    }


@pytest.mark.config(AGENT_WIDGETS_SETTINGS=CONFIG)
@pytest.mark.parametrize(
    'headers,body,status,expected_result',
    [
        (WEBALEX_HEADERS, {}, 400, {}),
        (
            WEBALEX_HEADERS,
            {
                'id': 'ba36777b3d4d4d40944c43fe008117e1',
                'dismissed_type': 'type',
                'dismissed_reason': 'reason',
                'comment': 'comment',
                'recommendation_score': 1,
            },
            409,
            {},
        ),
        (
            ORANGEVL_HEADERS,
            {
                'id': 'ba36777b3d4d4d40944c43fe008117e1',
                'dismissed_type': 'type',
                'dismissed_reason': 'reason',
                'comment': 'comment',
                'recommendation_score': 1,
            },
            201,
            {'id': 'ba36777b3d4d4d40944c43fe008117e1'},
        ),
        (
            ORANGEVL_HEADERS,
            {
                'id': '078bdc7fae2c4a8b86ab2d64cb39bfe9',
                'dismissed_type': 'type',
                'dismissed_reason': 'reason',
                'comment': 'comment',
                'recommendation_score': 1,
            },
            201,
            {'id': '078bdc7fae2c4a8b86ab2d64cb39bfe9'},
        ),
    ],
)
async def test_dismiss_send_feedback(
        web_app_client, web_context, headers, body, status, expected_result,
):
    response = await web_app_client.post(
        '/cabinet/dismissed_user/feedback', headers=headers, json=body,
    )
    assert response.status == status
    if status == 201:
        content = await response.json()
        assert content['id'] == body['id']

        async with web_context.pg.slave_pool.acquire() as conn:
            res = await conn.fetch(
                'SELECT * FROM agent.dismissed_users where id = \'%s\''
                % body['id'],
            )
            assert res[0]['status'] == 'completed'
            assert res[0]['completed_at'] is not None

        async with web_context.pg.slave_pool.acquire() as conn:
            res = await conn.fetch(
                'SELECT * FROM agent.dismiss_feedback where id = \'%s\''
                % body['id'],
            )
            assert res[0]['id'] == body['id']
            assert res[0]['reason'] == body['dismissed_reason']
            assert res[0]['type'] == body['dismissed_type']
            assert res[0]['comment'] == body['comment']
            assert (
                res[0]['recommendation_score'] == body['recommendation_score']
            )

        response_double = await web_app_client.post(
            '/cabinet/dismissed_user/feedback', headers=headers, json=body,
        )

        assert response_double.status == 409


@pytest.mark.config(
    AGENT_WIDGETS_SETTINGS=CONFIG,
    AGENT_PROJECT_SETTINGS={
        'default': {},
        'lavkasupport': {'piecework_tariff': 'grocery'},
        'taxisupport_cc': {'piecework_tariff': 'asterisk-support-taxi'},
    },
)
@pytest.mark.now('2020-12-16T00:00:00+0000')
@pytest.mark.parametrize(
    'headers,expected_result',
    [
        (
            CALLTAXI_CHIEF_HEADERS,
            {
                'page': 1,
                'total': 4,
                'limit': 30,
                'columns': [
                    {
                        'column_name': 'widget_calltaxi_basic_score',
                        'translation': 'widget_calltaxi_basic_score',
                    },
                    {
                        'column_name': 'widget_calltaxi_callsall',
                        'translation': 'widget_calltaxi_callsall',
                    },
                    {
                        'column_name': 'widget_calltaxi_callstrip',
                        'translation': 'widget_calltaxi_callstrip',
                    },
                    {
                        'column_name': 'widget_calltaxi_convert',
                        'translation': 'widget_calltaxi_convert',
                    },
                    {
                        'column_name': 'widget_calltaxi_discipline',
                        'translation': 'widget_calltaxi_discipline',
                    },
                    {
                        'column_name': 'widget_calltaxi_qa',
                        'translation': 'widget_calltaxi_qa',
                    },
                ],
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'calltaxi_chief',
                        'login': 'calltaxi_chief',
                        'first_name': 'first_name_1',
                        'last_name': 'last_name_1',
                        'department': 'calltaxi',
                        'team': '—',
                        'piece': False,
                        'widget_calltaxi_callsall': '20',
                        'widget_calltaxi_callstrip': '22',
                        'widget_calltaxi_convert': '110.0',
                        'widget_calltaxi_qa': '1.04',
                        'widget_calltaxi_discipline': '10.0',
                        'widget_calltaxi_basic_score': '62.5',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'calltaxi_support',
                        'login': 'calltaxi_support',
                        'first_name': 'first_name_2',
                        'last_name': 'last_name_2',
                        'department': 'calltaxi',
                        'team': '—',
                        'piece': True,
                        'widget_calltaxi_callsall': '10',
                        'widget_calltaxi_callstrip': '11',
                        'widget_calltaxi_convert': '110.0',
                        'widget_calltaxi_qa': '1.04',
                        'widget_calltaxi_discipline': '10.0',
                    },
                    {
                        'avatar': (
                            AVATAR_TEMPLATE % 'calltaxi_support_with_null_data'
                        ),
                        'login': 'calltaxi_support_with_null_data',
                        'first_name': 'first_name_7',
                        'last_name': 'last_name_7',
                        'department': 'calltaxi',
                        'team': '—',
                        'piece': False,
                        'widget_calltaxi_discipline': '100.0',
                    },
                    {
                        'avatar': (
                            AVATAR_TEMPLATE % 'calltaxi_support_without_data'
                        ),
                        'login': 'calltaxi_support_without_data',
                        'first_name': 'first_name_6',
                        'last_name': 'last_name_6',
                        'department': 'calltaxi',
                        'team': '—',
                        'piece': False,
                    },
                ],
            },
        ),
        (
            DIRECTSUPPORT_CHIEF_HEADERS,
            {
                'page': 1,
                'total': 4,
                'limit': 30,
                'columns': [
                    {
                        'column_name': 'widget_directsupport_fcalls',
                        'translation': 'widget_directsupport_fcalls',
                    },
                    {
                        'column_name': 'widget_directsupport_goal1',
                        'translation': 'widget_directsupport_goal1',
                    },
                    {
                        'column_name': 'widget_directsupport_goal2',
                        'translation': 'widget_directsupport_goal2',
                    },
                    {
                        'column_name': 'widget_directsupport_iscore',
                        'translation': 'widget_directsupport_iscore',
                    },
                    {
                        'column_name': 'widget_directsupport_nofcalls',
                        'translation': 'widget_directsupport_nofcalls',
                    },
                    {
                        'column_name': 'widget_directsupport_pos_oscore',
                        'translation': 'widget_directsupport_pos_oscore',
                    },
                    {
                        'column_name': 'widget_directsupport_skip',
                        'translation': 'widget_directsupport_skip',
                    },
                    {
                        'column_name': 'widget_directsupport_upsale',
                        'translation': 'widget_directsupport_upsale',
                    },
                    {
                        'column_name': 'widget_directsupport_wfm',
                        'translation': 'widget_directsupport_wfm',
                    },
                ],
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'directsupport_chief',
                        'login': 'directsupport_chief',
                        'first_name': 'first_name_3',
                        'last_name': 'last_name_3',
                        'department': 'directsupport',
                        'team': '—',
                        'piece': False,
                        'widget_directsupport_fcalls': '13.0',
                        'widget_directsupport_goal1': '12.0',
                        'widget_directsupport_goal2': '15.0',
                        'widget_directsupport_iscore': '17.0',
                        'widget_directsupport_nofcalls': '14.0',
                        'widget_directsupport_pos_oscore': '16.0',
                        'widget_directsupport_skip': '11.0',
                        'widget_directsupport_upsale': '18.0',
                        'widget_directsupport_wfm': '10.0',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'directsupport_support',
                        'login': 'directsupport_support',
                        'first_name': 'first_name_4',
                        'last_name': 'last_name_4',
                        'department': 'directsupport',
                        'team': '—',
                        'piece': False,
                        'widget_directsupport_fcalls': '15.0',
                        'widget_directsupport_goal1': '14.0',
                        'widget_directsupport_goal2': '17.0',
                        'widget_directsupport_iscore': '19.0',
                        'widget_directsupport_nofcalls': '16.0',
                        'widget_directsupport_pos_oscore': '18.0',
                        'widget_directsupport_skip': '13.0',
                        'widget_directsupport_upsale': '20.0',
                        'widget_directsupport_wfm': '12.0',
                    },
                    {
                        'avatar': (
                            AVATAR_TEMPLATE
                            % 'directsupport_support_with_null_data'
                        ),
                        'login': 'directsupport_support_with_null_data',
                        'first_name': 'first_name_8',
                        'last_name': 'last_name_8',
                        'department': 'directsupport',
                        'team': '—',
                        'piece': False,
                    },
                    {
                        'avatar': (
                            AVATAR_TEMPLATE
                            % 'directsupport_support_without_data'
                        ),
                        'login': 'directsupport_support_without_data',
                        'first_name': 'first_name_5',
                        'last_name': 'last_name_5',
                        'department': 'directsupport',
                        'team': '—',
                        'piece': False,
                    },
                ],
            },
        ),
        (
            COMDELIVERY_CHIEF_HEADERS,
            {
                'page': 1,
                'total': 3,
                'limit': 30,
                'columns': [
                    {
                        'column_name': 'widget_comdelivery_algorithm',
                        'translation': 'widget_comdelivery_algorithm',
                    },
                    {
                        'column_name': 'widget_comdelivery_callssccs',
                        'translation': 'widget_comdelivery_callssccs',
                    },
                    {
                        'column_name': 'widget_comdelivery_contracts',
                        'translation': 'widget_comdelivery_contracts',
                    },
                    {
                        'column_name': 'widget_comdelivery_deliverysccs',
                        'translation': 'widget_comdelivery_deliverysccs',
                    },
                    {
                        'column_name': 'widget_comdelivery_donetasks',
                        'translation': 'widget_comdelivery_donetasks',
                    },
                    {
                        'column_name': 'widget_comdelivery_health',
                        'translation': 'widget_comdelivery_health',
                    },
                    {
                        'column_name': 'widget_comdelivery_hygiene',
                        'translation': 'widget_comdelivery_hygiene',
                    },
                    {
                        'column_name': 'widget_comdelivery_listedclients',
                        'translation': 'widget_comdelivery_listedclients',
                    },
                    {
                        'column_name': 'widget_comdelivery_quality',
                        'translation': 'widget_comdelivery_quality',
                    },
                    {
                        'column_name': 'widget_comdelivery_tov',
                        'translation': 'widget_comdelivery_tov',
                    },
                ],
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'comdelivery_chief',
                        'login': 'comdelivery_chief',
                        'first_name': 'first_name_9',
                        'last_name': 'last_name_9',
                        'department': 'comdelivery',
                        'team': '—',
                        'piece': False,
                        'widget_comdelivery_algorithm': '30.0',
                        'widget_comdelivery_callssccs': '61',
                        'widget_comdelivery_contracts': '123',
                        'widget_comdelivery_deliverysccs': '15',
                        'widget_comdelivery_donetasks': '20',
                        'widget_comdelivery_health': '95.4',
                        'widget_comdelivery_hygiene': '40.0',
                        'widget_comdelivery_listedclients': '321',
                        'widget_comdelivery_quality': '4.5',
                        'widget_comdelivery_tov': '5.7',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'comdelivery_support1',
                        'login': 'comdelivery_support1',
                        'first_name': 'first_name_11',
                        'last_name': 'last_name_11',
                        'department': 'comdelivery',
                        'team': '—',
                        'piece': False,
                        'widget_comdelivery_algorithm': '30.0',
                        'widget_comdelivery_callssccs': '40',
                        'widget_comdelivery_contracts': '120',
                        'widget_comdelivery_deliverysccs': '16',
                        'widget_comdelivery_donetasks': '21',
                        'widget_comdelivery_health': '95.4',
                        'widget_comdelivery_hygiene': '40.0',
                        'widget_comdelivery_listedclients': '322',
                        'widget_comdelivery_quality': '4.6',
                        'widget_comdelivery_tov': '5.8',
                    },
                    {
                        'avatar': (
                            AVATAR_TEMPLATE
                            % 'comdelivery_support_with_null_data'
                        ),
                        'login': 'comdelivery_support_with_null_data',
                        'first_name': 'first_name_10',
                        'last_name': 'last_name_10',
                        'department': 'comdelivery',
                        'team': '—',
                        'piece': False,
                    },
                ],
            },
        ),
        (
            LAVKASUPPORT_CHIEF_HEADERS,
            {
                'page': 1,
                'total': 2,
                'limit': 30,
                'columns': [
                    {
                        'column_name': 'widget_lavkasupport_norm',
                        'translation': 'widget_lavkasupport_norm',
                    },
                ],
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'lavkasupport_chief',
                        'login': 'lavkasupport_chief',
                        'first_name': 'lavkasupport_chief',
                        'last_name': 'lavkasupport_chief',
                        'department': 'lavkasupport',
                        'team': '—',
                        'piece': False,
                        'widget_lavkasupport_norm': '2160.0',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'lavkasupport_user',
                        'login': 'lavkasupport_user',
                        'first_name': 'lavkasupport_user',
                        'last_name': 'lavkasupport_user',
                        'department': 'lavkasupport',
                        'team': '—',
                        'piece': False,
                        'widget_lavkasupport_norm': '4500.0',
                    },
                ],
            },
        ),
        (
            TAXISUPPORT_CC_CHIEF_HEADERS,
            {
                'page': 1,
                'total': 2,
                'limit': 30,
                'columns': [
                    {
                        'column_name': 'widget_taxisupport_cc_norm',
                        'translation': 'widget_taxisupport_cc_norm',
                    },
                ],
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'taxisupport_cc_chief',
                        'login': 'taxisupport_cc_chief',
                        'first_name': 'taxisupport_cc_chief',
                        'last_name': 'taxisupport_cc_chief',
                        'department': 'taxisupport_cc',
                        'team': '—',
                        'piece': False,
                        'widget_taxisupport_cc_norm': '2160.0',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'taxisupport_cc_user',
                        'login': 'taxisupport_cc_user',
                        'first_name': 'taxisupport_cc_user',
                        'last_name': 'taxisupport_cc_user',
                        'department': 'taxisupport_cc',
                        'team': '—',
                        'piece': False,
                        'widget_taxisupport_cc_norm': '4500.0',
                    },
                ],
            },
        ),
    ],
)
async def test_columns(
        mock_piecework_calc_load, web_app_client, headers, expected_result,
):
    response = await web_app_client.get('/cabinet', headers=headers)
    assert response.status == 200
    content = await response.json()
    assert content == expected_result


@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'calltaxi': {
            'enable_chatterbox': False,
            'main_permission': 'user_calltaxi',
        },
        'support_taxi': {
            'enable_chatterbox': False,
            'main_permission': 'user_support_taxi',
        },
        'cargo_callcenter': {
            'enable_chatterbox': False,
            'main_permission': 'read_users_cargo_callcenter',
        },
    },
)
@pytest.mark.config(AGENT_WIDGETS_SETTINGS=CONFIG)
@pytest.mark.parametrize(
    'url,headers,expected_response',
    [
        (
            '/cabinet?version=2&project=calltaxi',
            {'X-Yandex-Login': 'superuser', 'Accept-Language': 'ru-ru'},
            {
                'columns': [
                    {
                        'column_name': 'widget_calltaxi_basic_score',
                        'translation': 'widget_calltaxi_basic_score',
                    },
                    {
                        'column_name': 'widget_calltaxi_callsall',
                        'translation': 'widget_calltaxi_callsall',
                    },
                    {
                        'column_name': 'widget_calltaxi_callstrip',
                        'translation': 'widget_calltaxi_callstrip',
                    },
                    {
                        'column_name': 'widget_calltaxi_convert',
                        'translation': 'widget_calltaxi_convert',
                    },
                    {
                        'column_name': 'widget_calltaxi_discipline',
                        'translation': 'widget_calltaxi_discipline',
                    },
                    {
                        'column_name': 'widget_calltaxi_qa',
                        'translation': 'widget_calltaxi_qa',
                    },
                ],
                'limit': 30,
                'page': 1,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'calltaxi_chief',
                        'department': 'calltaxi',
                        'first_name': 'first_name_1',
                        'last_name': 'last_name_1',
                        'login': 'calltaxi_chief',
                        'piece': False,
                        'team': '—',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'valera',
                        'department': 'outstaff',
                        'first_name': 'Валера',
                        'last_name': 'Левин',
                        'login': 'valera',
                        'piece': False,
                        'team': 'D-команда',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'vavan',
                        'department': 'outstaff',
                        'first_name': 'Владимир',
                        'last_name': 'Николаев',
                        'login': 'vavan',
                        'piece': False,
                        'team': 'C-команда',
                    },
                ],
                'total': 3,
            },
        ),
        (
            '/cabinet?version=2&project=support_taxi',
            {'X-Yandex-Login': 'superuser', 'Accept-Language': 'ru-ru'},
            {
                'columns': [],
                'limit': 30,
                'page': 1,
                'results': [
                    {
                        'avatar': AVATAR_TEMPLATE % 'justmark0',
                        'department': 'bo_reserve',
                        'first_name': 'Марк',
                        'last_name': 'Николсон',
                        'login': 'justmark0',
                        'piece': True,
                        'team': 'cargo-callcenter',
                    },
                    {
                        'avatar': AVATAR_TEMPLATE % 'support_taxi_user',
                        'department': 'bo_reserve',
                        'first_name': 'first_name_12',
                        'last_name': 'last_name_12',
                        'login': 'support_taxi_user',
                        'piece': True,
                        'team': 'Саппорт Такси',
                    },
                ],
                'total': 2,
            },
        ),
        (
            '/cabinet?version=2',
            {'X-Yandex-Login': 'superuser', 'Accept-Language': 'ru-ru'},
            {'columns': [], 'limit': 30, 'page': 1, 'results': [], 'total': 0},
        ),
    ],
)
async def test_cabinet_2_version(
        web_app_client, url, headers, expected_response,
):
    response = await web_app_client.get(url, headers=headers)
    assert response.status == 200
    content = await response.json()
    assert content == expected_response
