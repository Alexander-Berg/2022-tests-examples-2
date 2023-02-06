# -*- coding: utf-8 -*-
from passport.backend.api.tests.views.bundle.restore.semi_auto.base.test_step_base import (
    BaseTestMultiStepWithCommitUtils,
    eq_,
)
from passport.backend.api.tests.views.bundle.restore.test.base_fixtures import one_day_match_env
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    build_auth_info,
    TEST_DEFAULT_BIRTHDAY,
    TEST_DEFAULT_FIRSTNAME,
    TEST_DEFAULT_LASTNAME,
    TEST_DEFAULT_LASTNAME_INEXACT,
    TEST_DEFAULT_REGISTRATION_COUNTRY,
    TEST_DELIVERY_ADDRESS_2,
    TEST_IP,
    TEST_IP_2,
    TEST_IP_3,
    TEST_IP_4,
    TEST_PDD_UID,
    TEST_REGISTRATION_CITY,
    TEST_REGISTRATION_CITY_ID,
    TEST_REGISTRATION_COUNTRY_ID,
    TEST_SOCIAL_TASK_ID,
    TEST_USER_AGENT_2_PARSED,
    TEST_YANDEXUID_COOKIE,
)
from passport.backend.api.views.bundle.restore.factors import (
    ANSWERS_ENTITY_NAME,
    BIRTHDAYS_ENTITY_NAME,
    NAMES_ENTITY_NAME,
    PERSONAL_AND_RECOVERY_MAX_ANALYZED_CHANGES,
    PHONE_NUMBERS_ENTITY_NAME,
    RESTORE_METHODS_CHANGE_INDICES,
)
from passport.backend.core import authtypes
from passport.backend.core.builders.historydb_api.faker.historydb_api import events_info_interval_point
from passport.backend.core.builders.social_api.faker.social_api import (
    profile_item,
    task_data_response,
)
from passport.backend.core.compare import (
    BIRTHDAYS_FACTOR_FULL_MATCH,
    BIRTHDAYS_FACTOR_INEXACT_MATCH,
    FACTOR_BOOL_MATCH,
    FACTOR_BOOL_NO_MATCH,
    FACTOR_FLOAT_MATCH,
    FACTOR_FLOAT_NO_MATCH,
    FACTOR_NOT_SET,
    STRING_FACTOR_MATCH,
    STRING_FACTOR_NO_MATCH,
    UA_FACTOR_FULL_MATCH,
)
from passport.backend.core.compare.test.compare import (
    compare_uas_factor,
    compared_user_agent,
)
from passport.backend.core.historydb.events import PASSWORD_CHANGE_TYPE_FORCED
from passport.backend.core.test.test_utils.utils import with_settings_hosts


ANSWER_FACTORS_COUNT = len(RESTORE_METHODS_CHANGE_INDICES)


"""
В данных анкеты содержится следующая информация:
 * Общая информация об анкете, информация о параметрах
 * Блоки данных, содержащие введенные значения (поле entered), найденные в сервисах значения
 (поля account, history, actual), значения факторов (factor), индексы найденных совпадений (indices).
 Если индексы совпадений представляют собой пары, то первое значение - номер значения во входных данных (entered),
  второе значение - номер значения в данных сервиса.
 Найденные в сервисах значения могут содержать в себе информацию об интервалах актуальности (interval/intervals).
 Каждый интервал содержит начальную и конечную точку, каждая точка содержит timestamp (может иметь значение None),
  и может содержать поля user_ip, user_agent, yandexuid (если удалось выяснить значения).
"""
EXPECTED_DOCUMENTED_FACTORS = {
    # Общая информация об анкете
    'is_for_learning': False,  # Признак того, что анкета используется для обучения
    'restore_status': 'pending',
    'tensornet_estimate': 0.0,  # Оценка, полученная с использованием обученной формулы
    'tensornet_status': True,  # Признак успешности вызова TensorNet
    'decision_source': 'basic_formula',  # Источник решения по анкете. Другие варианты - tensornet, unconditional
    'request_info': {
        'real_reason': 'restore',
        'language': 'ru',
        'last_step': 'final_info',
        'contact_email': u'vasia@пупкин.рф',
        'contact_reason': u'Забыл пароль',
        'request_source': 'restore',
        'is_unconditional_pass': False,  # Признак безусловной проверки
        'user_enabled': True,  # Признак требования заблокированности
    },
    'version': 'multistep.4.3',  # Версия анкеты

    # Признаки успешности выполнения вызовов API
    'auths_aggregated_runtime_api_status': True,
    'historydb_api_events_status': True,

    # Шаг 1
    'names': {
        'account': [
            {
                'firstname': u'Петр',
                'lastname': u'Петров',
                'interval': {
                    'end': {
                        'timestamp': 2,
                        'user_ip': '37.9.127.100',
                        'yandexuid': '123',
                    },
                    'start': {
                        'timestamp': 1,
                        'user_ip': '37.9.127.175',
                        'yandexuid': '123',
                    },
                },
            },
            {
                'firstname': u'Петр',
                'lastname': 'Petroff',
                'interval': {
                    'end': None,
                    'start': {
                        'timestamp': 2,
                        'user_ip': '37.9.127.100',
                        'yandexuid': '123',
                    },
                },
            },
        ],
        'indices': {
            'current': (
                (0, 1),  # Индексы лучших имени и фамилии из введенных вариантов
                1,  # Индекс в истории (указывает на самое последнее значение)
            ),
            'registration': (
                (0, 1),
                0,
            ),
            'intermediate': None,
        },
        'entered': {
            'lastnames': [  # Варианты фамилии
                'B',
                'P',
            ],
            'firstnames': [  # Варианты имени
                'A',
            ],
        },
        'factor': {
            'current': [0, 0],  # Совпадение с текущими ФИ - пара факторов для введенных имени и фамилии
            'intermediate': [-1, -1],  # Лучшее совпадение с промежуточными ФИ - пара факторов для введенных имени и фамилии
            'intermediate_depth': -1,  # Фактор глубины для лучшего промежуточного совпадения - если совпадение найдено
            'registration': [0, 0],  # Совпадение с регистрационными ФИ - пара факторов для введенных имени и фамилии
            'change_count': 1,  # Число смен ФИ в истории (первичное задание не считается)
            'change_depth': [  # Глубина для первой и двух последних смен
                1.0,
                -1,
                1.0,
            ],
            'change_ip_eq_reg': [  # Совпадение IP смен с IP регистрации
                0,
                -1,
                0,
            ],
            'change_subnet_eq_reg': [  # Совпадение subnet смен с subnet регистрации
                1,
                -1,
                1,
            ],
            'change_ua_eq_reg': [  # Совпадение UA смен с UA регистрации
                3,
                -1,
                3,
            ],
            'change_ip_eq_user': [  # Совпадение IP смен с IP пользователя
                0,
                -1,
                0,
            ],
            'change_subnet_eq_user': [  # Совпадение subnet смен с subnet пользователя
                1,
                -1,
                1,
            ],
            'change_ua_eq_user': [  # Совпадение UA смен с UA пользователя
                0,
                -1,
                0,
            ],
        },
    },
    'birthday': {
        'account': [
            {
                'value': '2011-11-11',
                'interval': {
                    'end': {
                        'timestamp': None,
                    },
                    'start': {
                        'timestamp': 1,
                        'user_ip': '37.9.127.175',
                        'yandexuid': '123',
                    },
                },
            },
            {
                'value': '2000-10-01',
                'interval': {
                    'end': None,
                    'start': {
                        'timestamp': None,
                    },
                },
            },
        ],
        'indices': {
            'current': 1,
            'registration': 0,
            'intermediate': None,
        },
        'entered': '2012-01-01',
        'factor': {  # Описание факторов аналогично факторам names
            'intermediate': -1,
            'intermediate_depth': -1,  # Фактор глубины для лучшего промежуточного совпадения - если совпадение найдено
            'registration': 1,  # Означает неточное совпадение (без учета года)
            'current': 2,  # Означает точное совпадение
            'change_count': 1,
            'change_depth': [
                -1,
                -1,
                -1,
            ],
            'change_ip_eq_user': [
                -1,
                -1,
                -1,
            ],
            'change_subnet_eq_user': [
                -1,
                -1,
                -1,
            ],
            'change_ua_eq_user': [
                0,
                -1,
                0,
            ],
            'change_ip_eq_reg': [
                -1,
                -1,
                -1,
            ],
            'change_subnet_eq_reg': [
                -1,
                -1,
                -1,
            ],
            'change_ua_eq_reg': [
                0,
                -1,
                0,
            ],
        },
    },
    'passwords': {
        'actual': {
            'last_change_request': {  # Информация о последнем принуждении к смене пароля
                'admin': 'alexco',
                'comment': 'broken',
                'change_required': True,  # Признак, было ли принуждение выставлено или снято
                'origin_info': {
                    'timestamp': 1,
                    'user_ip': '37.9.127.175',
                    'yandexuid': '123',
                },
            },
            'last_change': {  # Информация о последней смене пароля, выполненной пользователем
                'origin_info': {
                    'user_ip': '37.9.127.175',
                    'timestamp': 1000,
                    'yandexuid': 'yandexuid',
                },
                'change_type': 'forced',  # Тип смены; другие значения - voluntary, restore
            },
            'change_ip_first_auth': [{  # Информация о первой авторизации с IP последней смены
                'timestamp': 500,
                'status': 'successful',
                'authtype': 'imap',
            }],
            'change_subnet_first_auth': [{  # Информация о первой авторизации с subnet последней смены
                'timestamp': 10,
                'status': 'successful',
                'authtype': 'imap',
            }],
            'change_ua_first_auth': [{  # Информация о первой авторизации с UA последней смены
                'timestamp': 10,
                'status': 'successful',
                'authtype': 'imap',
            }],
        },
        'auth_date_entered': '2010-10-10 MSD+0400',  # Формат даты '%Y-%m-%d %Z%z'. Часовой пояс определяется по IP пользователя.
        'api_statuses': [  # Список признаков успешности вызова API поиска паролей в HistoryDB.
            True,
        ],
        'indices': [  # Номера лучших подходящих интервалов актуальности для найденных в истории паролей
            None,
        ],
        'intervals': [  # Список интервалов актуальности для введенных вариантов пароля. Содержит пары Unix timestamp;
                        # если вариант пароля актуален, второе значение в паре None.
            [],
        ],
        'factor': {
            'entered_count': 1,  # Число введенных вариантов пароля
            'auth_found': [  # Список факторов-признаков того, найдена ли авторизация паролем в истории.
                             # Если поиск не выполнялся, значение -1. Всегда 3 элемента.
                0,
                -1,
                -1,
            ],
            'auth_date': [  # Список факторов нечеткого сравнения дат (по одному для каждого варианта пароля), значение от 0.0 до 1.0,
                            # либо -1, если не было сравнения. Всегда 3 элемента.
                -1,
                -1,
                -1,
            ],
            'equals_current': [  # Список факторов-признаков того, совпадает ли введенный пароль с текущим.
                                 # Если поиск не выполнялся, значение -1. Всегда 3 элемента.
                0,
                -1,
                -1,
            ],
            'first_auth_depth': [  # Глубина заведения пароля, если он был найден, для каждого из введенных вариантов
                -1,
                -1,
                -1,
            ],
            'change_count': 0,  # Число смен пароля
            'forced_change_pending': 1,  # Признак того, требуется ли принудительная смена
            'last_change_is_forced_change': -1,  # Признак того, что последняя смена - принудительная
            'change_depth': [-1],  # Глубина последней смены
            'change_ip_first_auth_depth': [-1],  # Глубина первой авторизации с IP последней смены
            'change_subnet_first_auth_depth': [0.0],  # Глубина первой авторизации с subnet последней смены
            'change_ua_first_auth_depth': [0.0],  # Глубина первой авторизации с UA последней смены
            'change_ip_eq_user': [-1],  # Фактор совпадения IP последней смены с пользовательским
            'change_subnet_eq_user': [-1],  # Фактор совпадения subnet последней смены с пользовательским
            'change_ua_eq_user': [-1],  # Фактор совпадения UA последней смены с пользовательским
        },
    },

    # Шаг 2
    'emails': {
        'history': [  # Значения отсортированы в порядке первого появления email в истории
            {
                'value': 'email_2@ya.ru',
                'intervals': [
                    {
                        'end': None,
                        'start': {
                            'timestamp': 1,
                            'user_ip': '37.9.127.175',
                            'yandexuid': '123',
                        },
                    },
                ],
            },
            {
                'value': 'email_3@ya.ru',
                'intervals': [
                    {
                        'end': {
                            'timestamp': 5,
                            'user_ip': '37.9.127.175',
                            'yandexuid': '123',
                        },
                        'start': {
                            'timestamp': 2,
                            'user_ip': '37.9.127.175',
                            'yandexuid': '123',
                        },
                    },
                ],
            },
            {
                'value': u'ва@силий@xn--80atjc.xn--p1ai',
                'intervals': [
                    {
                        'end': None,
                        'start': {
                            'timestamp': 3,
                            'user_ip': '37.9.127.175',
                            'yandexuid': '123',
                        },
                    },
                ],
            },
            {
                'value': u'email_5@.рф',
                'intervals': [
                    {
                        'end': None,
                        'start': {
                            'timestamp': 4,
                            'user_ip': '37.9.127.175',
                            'yandexuid': '123',
                        },
                    },
                ],
            },
        ],
        'matches': [
            'email_3@ya.ru',
            'email_2@ya.ru',
            u'ва@силий@xn--80atjc.xn--p1ai',
            u'email_5@.рф',
        ],
        'entered': [
            'email_2@ya.ru',
            'email_3@ya.ru',
            u'ва@силий@xn--80atjc.xn--p1ai',
            u'email_5@.рф',
        ],
        'factor': {
            'matches_count': 4,
            'history_count': 4,
            'entered_count': 4,
        },
        'match_indices': [
            (
                0,
                1,
            ),
            (
                1,
                0,
            ),
            (
                2,
                2,
            ),
            (
                3,
                3,
            ),
        ],
    },
    'answer': {
        'history': [  # Список КВ/КО из истории - упорядочен по времени появления КВ
            {
                'question': '1:qqq',
                'answers': [  # Список КО для КВ - упорядочен по времени появления КО
                    {
                        'value': u'КО',
                        'intervals': [
                            {
                                'end': {
                                    'timestamp': 3,
                                    'user_ip': '37.9.127.175',
                                    'yandexuid': '123',
                                },
                                'start': {
                                    'timestamp': 2,
                                    'user_ip': '37.9.127.175',
                                    'yandexuid': '123',
                                },
                            },
                        ],
                    },
                ],
            },
            {
                'question': '99:my question',
                'answers': [
                    {
                        'value': u'КО',
                        'intervals': [
                            {
                                'end': {
                                    'timestamp': 4,
                                    'user_ip': '37.9.127.175',
                                    'yandexuid': '123',
                                },
                                'start': {
                                    'timestamp': 3,
                                    'user_ip': '37.9.127.175',
                                    'yandexuid': '123',
                                },
                            },
                        ],
                    },
                    {
                        'value': u'ответ',
                        'intervals': [
                            {
                                'end': {
                                    'timestamp': 6,
                                    'user_ip': '37.9.127.175',
                                    'yandexuid': '123',
                                },
                                'start': {
                                    'timestamp': 4,
                                    'user_ip': '37.9.127.175',
                                    'yandexuid': '123',
                                },
                            },
                        ],
                    },
                    {
                        'value': 'answer',
                        'intervals': [
                            {
                                'end': None,
                                'start': {
                                    'timestamp': 6,
                                    'user_ip': '37.9.127.175',
                                    'yandexuid': '123',
                                },
                            },
                        ],
                    },
                ],
            },
        ],
        'indices': {
            'best': (
                1,
                1,
            ),
        },
        'entered': {
            'question': '99:my question',
            'answer': u'ответ',
        },
        'factor': {
            'current': 0,  # Простой строковый фактор для совпадения с текущими КВ/КО на аккаунте
            'best': 2,  # Простой строковый фактор для лучшего совпадения. Если КО не введен, либо ничего не найдено, значение -1.
            'change_count': 3,  # Число смен в истории
            'change_depth': [  # Фактор глубины времени для последних трех смен
                -1,
                -1,
                -1,
            ],
            'change_ip_eq_user': [  # Признак совпадения IP смен с пользовательским
                1,
                1,
                1,
            ],
            'change_subnet_eq_user': [  # Признак совпадения subnet смен с пользовательским
                1,
                1,
                1,
            ],
            'change_ua_eq_user': [  # Признак совпадения UA смен с пользовательским
                0,
                0,
                0,
            ],
            # Факторы смены для найденных совпадений - для первого и последнего по времени задания значений
            # Пользователь вводит одно значение, однако оно может быть задано несколько раз
            'match_depth': [1.0, 1.0],
            'match_ip_eq_reg': [-1, -1],
            'match_ip_eq_user': [0, 1],
            'match_subnet_eq_reg': [-1, -1],
            'match_subnet_eq_user': [1, 1],
            'match_ua_eq_reg': [0, 0],
            'match_ua_eq_user': [0, 3],
            'match_ip_first_auth_depth': [-1, 0.7],  # Глубина первой авторизации с IP задания совпавшего значения (первого и посл.)
            'match_subnet_first_auth_depth': [-1, 1.0],
            'match_ua_first_auth_depth': [0.0, -1],
        },
        'actual': {
            # Информация о найденных авторизациях для окружений, в которых были заданы совпавшие значения
            # (первое и последнее по времени совпавшее значение)
            'match_ip_first_auth': [None, {'status': 'successful', 'timestamp': 500, 'authtype': 'imap'}],
            'match_subnet_first_auth': [None, {'status': 'successful', 'timestamp': 10, 'authtype': 'imap'}],
            'match_ua_first_auth': [{'status': 'successful', 'timestamp': 10, 'authtype': 'imap'}, None],
        },
    },
    'phone_numbers': {
        'history': [
            {
                'value': '79117654321',
                'intervals': [
                    {
                        'end': None,
                        'start': {
                            'timestamp': 1,
                            'user_ip': '37.9.127.175',
                            'yandexuid': '123',
                        },
                    },
                ],
            },
            {
                'value': '79111234567',
                'intervals': [
                    {
                        'end': {
                            'timestamp': 3,
                            'user_ip': '37.9.127.175',
                            'yandexuid': '123',
                        },
                        'start': {
                            'timestamp': 2,
                            'user_ip': '37.9.127.175',
                            'yandexuid': '123',
                        },
                    },
                    {
                        'end': None,
                        'start': {
                            'timestamp': 4,
                            'user_ip': '37.9.127.175',
                            'yandexuid': '123',
                        },
                    },
                ],
            },
        ],
        'matches': [
            '79111234567',
        ],
        'entered': [
            '89111234567',
            '79111234567',
            '79111234568',
        ],
        'factor': {
            'matches_count': 1,
            'history_count': 2,
            'entered_count': 3,
            # Факторы смены для найденных совпадений - для первого и последнего по времени задания значений
            # Аналогично КО
            'match_depth': [1.0, 1.0],  # Обычный фактор глубины для времени задания
            'match_ip_eq_reg': [-1, -1],
            'match_ip_eq_user': [1, 1],
            'match_subnet_eq_reg': [-1, -1],
            'match_subnet_eq_user': [1, 1],
            'match_ua_eq_reg': [0, 0],
            'match_ua_eq_user': [0, 0],
            'match_ip_first_auth_depth': [-1, -1],
            'match_subnet_first_auth_depth': [-1, -1],
            'match_ua_first_auth_depth': [-1, -1],
            # Факторы смены - аналогично КВ/КО
            'change_count': 2,
            'change_depth': [
                -1,
                1,
                1,
            ],
            'change_ip_eq_user': [
                -1,
                1,
                1,
            ],
            'change_subnet_eq_user': [
                -1,
                1,
                1,
            ],
            'change_ua_eq_user': [
                -1,
                0,
                0,
            ],
        },
        'actual': {
            # Информация о найденных авторизациях для окружений, в которых были заданы совпавшие значения
            # (первое и последнее по времени совпавшее значение)
            'match_ip_first_auth': [None, None],
            'match_subnet_first_auth': [None, None],
            'match_ua_first_auth': [None, None],
        },
        'match_indices': [
            (
                0,
                1,
            ),
        ],
    },

    # Шаг 3
    'registration_date': {
        'account': '2010-10-10 10:20:30',
        'entered': '2010-10-10 MSD+0400',
        'factor': 1,  # Фактор неточного сравнения дат. Значение от 0.0 до 1.0.
    },
    'registration_city': {
        'history_id': 213,
        'history': u'Москва',
        'entered_id': None,
        'entered': None,
        'factor': {
            'text': 0,  # Простой строковый фактор
            'id': 0,  # Признак совпадения ID Геобазы
        },
    },
    'registration_country': {
        'history_id': 225,
        'history': u'Россия',
        'entered_id': None,
        'entered': 'ru',
        'factor': {
            'text': 2,  # Простой строковый фактор
            'id': 0,  # Признак совпадения ID Геобазы
        },
    },
    'registration_ip': '37.9.127.175',

    # Шаг 4
    'social_accounts': {
        'entered_accounts': [  # Информация о введенных в форму соц. аккаунтах (без привязки к Яндексу)
            {
                'provider': {
                    'name': 'google',
                    'id': 5,
                    'code': 'gg',
                },
                'firstname': 'Firstname',
                'userid': '57575757575',
                'avatar': {
                    '0x0': 'https://lh3.googleusercontent.com/-XdUIqdskCWA/AAAAAAAAAAI/AAAAAAAAAAA/2252rscbv5M/photo.jpg',
                },
                'lastname': 'Lastname',
                'username': 'some.user',
                'email': 'some-mail@example.com',
                'links': [
                    'https://plus.google.com/118320684662584130204',
                ],
                'gender': 'm',
            },
        ],
        'entered_profiles': [  # Информация о соответствующих введенным соц. аккаунтам соц. профилям в Яндексе
            {
                'provider': 'facebook',
                'provider_code': 'fb',
                'addresses': [
                    'http://www.facebook.com/profile.php?id=%(userid)s',
                    'http://www.facebook.com/some.user',
                ],
                'uid': 1130000000000001,
                'userid': '57575757575',
                'profile_id': 123,
                'allow_auth': True,
                'username': 'some.user',
            },
        ],
        'account_profiles': [],  # Информация о соц. профилях аккаунта, к которому восстанавливаем доступ
        'api_status': True,  # Успешность вызова соц. апи
        'factor': {
            'matches_count': 0,
            'entered_accounts_count': 1,
            'entered_profiles_count': 1,
            'account_profiles_count': 0,
        },
    },
    'services': {
        'matches': [
            'mail',
            'metrika',
            'disk',
        ],
        'account': [
            'mail',
            'metrika',
            'disk',
        ],
        'entered': [
            'mail',
            'metrika',
            'disk',
            'yandsearch',
        ],
        'factor': {
            'matches_count': 4,
            'account_count': 4,
            'entered_count': 5,
        },
    },


    # Шаг 5
    'email_collectors': {
        'actual': [
            'mail1@mail.com',
            'mail2@mail.ru',
        ],
        'matches': [
            'mail1@mail.com',
        ],
        'api_status': 1,
        'entered': [
            'mail2@mail.com',
        ],
        'factor': {
            'matches_count': 1,
            'actual_count': 2,
            'entered_count': 1,
        },
    },
    'email_folders': {
        'actual': [
            u'Папка',
        ],
        'matches': [
            u'Папка',
        ],
        'api_status': True,
        'entered': [
            u'Папка1',
            u'Папка2',
            'Papka',
        ],
        'factor': {
            'matches_count': 1,
            'actual_count': 1,
            'entered_count': 3,
        },
    },
    'email_blacklist': {
        'actual': [
            'vasia@xn--80a1acny.xn--p1ai',
            u'вася@xn--80a1acny.xn--p1ai',
        ],
        'matches': [
            'vasia@xn--80a1acny.xn--p1ai',
        ],
        'api_status': 1,
        'entered': [
            u'вася@почта.рф',
        ],
        'factor': {
            'matches_count': 1,
            'actual_count': 2,
            'entered_count': 1,
        },
    },
    'delivery_addresses': {
        'matches': [
            {
                'firstname': '',
                'street': 'tolstoy',
                'suite': '10c4',
                'floor': '',
                'lastname': '',
                'email': '',
                'fathersname': '',
                'city': u'Иваново',
                'metro': '',
                'intercom': '',
                'phone_extra': '',
                'country': 'rf',
                'cargolift': '',
                'entrance': '',
                'phone': '',
                'zip': '',
                'comment': '',
                'building': '16',
                'flat': '',
            },
        ],
        'account': [
            {
                'firstname': '',
                'street': 'tolstoy',
                'suite': '10c4',
                'floor': '',
                'lastname': '',
                'email': '',
                'fathersname': '',
                'city': u'Иваново',
                'metro': '',
                'intercom': '',
                'phone_extra': '',
                'country': 'rf',
                'cargolift': '',
                'entrance': '',
                'phone': '',
                'zip': '',
                'comment': '',
                'building': '16',
                'flat': '',
            },
        ],
        'entered': [
            {
                'firstname': '',
                'street': 'tolstoy',
                'suite': '10c4',
                'floor': '',
                'lastname': '',
                'email': '',
                'fathersname': '',
                'city': u'Иваново',
                'metro': '',
                'intercom': '',
                'phone_extra': '',
                'country': 'rf',
                'cargolift': '',
                'entrance': '',
                'phone': '',
                'zip': '',
                'comment': '',
                'building': '16',
                'flat': '',
            },
        ],
        'factor': {
            'matches_count': 1,
            'account_count': 1,
            'entered_count': 1,
        },
    },
    'email_whitelist': {
        'actual': [
            'mail1@mail.ru',
            'mail2@mail.ru',
        ],
        'matches': [
            'mail1@mail.ru',
            'mail2@mail.ru',
        ],
        'api_status': 1,
        'entered': [
            'mail1@mail.com',
            'mail1@mail.ru',
        ],
        'factor': {
            'matches_count': 2,
            'actual_count': 2,
            'entered_count': 2,
        },
    },
    'outbound_emails': {
        'actual': [
            'vasia@xn--80a1acny.xn--p1ai',
            u'вася@xn--80a1acny.xn--p1ai',
        ],
        'matches': [
            'vasia@xn--80a1acny.xn--p1ai',
        ],
        'api_status': 1,
        'entered': [
            u'вася@почта.рф',
        ],
        'factor': {
            'matches_count': 1,
            'actual_count': 2,
            'entered_count': 1,
        },
    },
    'restore_attempts': {
        'attempts': [],
        'factor': {
            'has_recent_positive_decision': False,
        },
    },
    # Шаг 6
    'user_env_auths': {  # Данные о поиске окружения пользователя в истории авторизаций и не только
        'actual': {
            'gathered_auths_count': 3,  # Сколько авторизаций было вынуто из истории за год
            'ip_first_auth': None,  # Информация о первой авторизации с IP пользователя
            'ip_last_auth': None,  # Информация о последней авторизации с IP пользователя
            'subnet_first_auth': None,  # Информация о первой авторизации с subnet пользователя
            'subnet_last_auth': None,  # Информация о последней авторизации с subnet пользователя
            'ua_first_auth': {  # Информация о первой авторизации с UA пользователя
                'timestamp': 10,
                'status': 'ses_create',
                'authtype': 'web',
            },
            'ua_last_auth': {  # Информация о последней авторизации с UA пользователя
                'timestamp': 1000,
                'status': 'successful',
                'authtype': 'imap',
            },
            'ip': '37.9.127.175',  # IP пользователя
            'subnet': '37.9.64.0/18',  # subnet пользователя
            'ua': {  # UA пользователя
                'os.name': 'windows xp',
                'yandexuid': 'yandexuid',
                'browser.name': 'firefox',
            },
        },
        'registration': {  # Информация об окружении при регистрации аккаунта
            'ip': None,
            'subnet': None,
            'ua': {
                'os.name': None,
                'yandexuid': None,
                'browser.name': None,
            },
        },
        'factor': {
            'auths_limit_reached': 0,  # Признак того, что был достигнут лимит по числу авторизаций при запросе истории
            'ip_eq_reg': -1,  # Признак совпадения IP пользователя с регистрационным
            'subnet_eq_reg': -1,  # Признак совпадения subnet пользователя с регистрационным
            'ua_eq_reg': 0,  # Признак совпадения UA пользователя с регистрационным
            'ip_auth_interval': -1,  # Фактор для временного интервала IP
            'subnet_auth_interval': -1,  # Фактор для временного интервала subnet
            'ua_auth_interval': 0.5,  # Фактор для временного интервала UA
            'ip_first_auth_depth': -1,  # Фактор глубины для первой авторизации с IP пользователя
            'subnet_first_auth_depth': -1,  # Фактор глубины для первой авторизации с subnet пользователя
            'ua_first_auth_depth': 1,  # Фактор глубины для первой авторизации с UA пользователя
        },
    },
    'aggregated': {  # Данные по аггрегированным факторам
        'matches': {
            # Найденные совпадения для смены в один день
            # персональных данных и средств восстановления, сгруппированные попарно по сменам данных
            'personal_and_recovery_change_one_day': [
                # Найденные смены сравниваются каждая с каждой, поэтому максимальное число элементов - 4
                # (две последние смены для ФИО и ДР, и две смены для КО и телефона)
                {
                    'envs': [  # Всегда пара смен, в пределах одного дня
                        {
                            'timestamp': 1000,
                            'entity': 'names',  # Название персональных данных, которые были изменены.
                            'ip': '37.9.127.175',
                            'subnet': '37.9.64.0/18',
                            'ua': {'os.name': None, 'yandexuid': '123', 'browser.name': None},
                            # Информация о найденной первой авторизации с IP/подсети/UA смены
                            'ip_first_auth_info': {'status': 'successful', 'timestamp': 500, 'authtype': 'imap'},
                            'subnet_first_auth_info': {'status': 'successful', 'timestamp': 10, 'authtype': 'imap'},
                            'ua_first_auth_info': None,
                        },
                        {
                            'timestamp': 1000,
                            'entity': 'phone_numbers',
                            'ip': '37.9.127.175',
                            'subnet': '37.9.64.0/18',
                            'ua': {'os.name': None, 'yandexuid': '123', 'browser.name': None},
                            'ip_first_auth_info': {'status': 'successful', 'timestamp': 10, 'authtype': 'imap'},
                            'subnet_first_auth_info': {'status': 'successful', 'timestamp': 10, 'authtype': 'imap'},
                            'ua_first_auth_info': None,
                        },
                    ],
                    'fields': ['ip', 'subnet'],  # Совпавшие компоненты окружений, всегда как минимум одно значение
                },
                {
                    'envs': [
                        {
                            'timestamp': 1000,
                            'entity': 'birthday',
                            'ip': '192.168.0.1',
                            'subnet': None,
                            'ua': {'os.name': 'windows xp', 'yandexuid': 'yandexuid', 'browser.name': 'firefox'},
                            'ip_first_auth_info': None,
                            'subnet_first_auth_info': None,
                            'ua_first_auth_info': {'status': 'successful', 'timestamp': 10, 'authtype': 'imap'},
                        },
                        {
                            'timestamp': 1000,
                            'entity': 'answer',
                            'ip': '10.10.10.10',
                            'subnet': None,
                            'ua': {'os.name': 'windows xp', 'yandexuid': 'yandexuid', 'browser.name': 'firefox'},
                            'ip_first_auth_info': None,
                            'subnet_first_auth_info': None,
                            'ua_first_auth_info': {'status': 'successful', 'timestamp': 10, 'authtype': 'imap'},
                        },
                    ],
                    'fields': ['ua'],
                },
            ],
            # Найденные совпадения для смены в один день
            # пароля и персональных данных, сгруппированные попарно по сменам данных
            'password_and_personal_change_one_day': [],
            # Найденные совпадения для смены в один день
            # средств восстановления и пароля, сгруппированные попарно по сменам данных
            'password_and_recovery_change_one_day': [],
        },
        'factor': {
            # Факторы для окружения смены в один день
            # пароля и персональных данных
            'password_and_personal_change_one_day': {
                'ip_match': 0,  # Выявлено совпадение по IP для смен в один день
                'ua_match': 0,  # Выявлено совпадение по UA для смен в один день
                'subnet_match': 0,  # Выявлено совпадение по subnet для смен в один день
                # Факторы сравнения найденного окружения смен в один день и регистрационного окружения
                'ip_eq_reg': -1,
                'subnet_eq_reg': -1,
                'ua_eq_reg': -1,
                # Факторы сравнения найденного окружения смен в один день и пользовательского окружения
                'ip_eq_user': -1,
                'subnet_eq_user': -1,
                'ua_eq_user': -1,
                'ip_first_auth_depth': [  # Глубина IP окружения найденной смены в один день
                    -1,
                    -1,
                    -1,
                ],
                'subnet_first_auth_depth': [  # Глубина subnet окружения найденной смены в один день
                    -1,
                    -1,
                    -1,
                ],
                'ua_first_auth_depth': [  # Глубина UA окружения найденной смены в один день
                    -1,
                    -1,
                    -1,
                ],

            },
            # Факторы для окружения смены в один день
            # персональных данных и средств восстановления
            'personal_and_recovery_change_one_day': {
                'ip_match': 0,  # Выявлено совпадение по IP для смен в один день
                'subnet_match': 1,  # Выявлено совпадение по subnet для смен в один день
                'ua_match': 1,  # Выявлено совпадение по UA для смен в один день
                # Факторы сравнения найденного окружения смен в один день и регистрационного окружения
                'ip_eq_reg': -1,
                'subnet_eq_reg': -1,
                'ua_eq_reg': 0,
                # Факторы сравнения найденного окружения смен в один день и пользовательского окружения
                'ip_eq_user': 1,
                'subnet_eq_user': 0,
                'ua_eq_user': 5,
                'ip_first_auth_depth': [  # Глубина IP окружения найденной смены в один день
                    1.0,
                    0.8,
                    -1,
                    -1,
                ],
                'subnet_first_auth_depth': [  # Глубина subnet окружения найденной смены в один день
                    1.0,
                    -1,
                    -1,
                    -1,
                ],
                'ua_first_auth_depth': [  # Глубина UA окружения найденной смены в один день
                    1.0,
                    -1,
                    -1,
                    -1,
                ],
            },
            # Факторы для окружения смены в один день
            # пароля и средств восстановления
            'password_and_recovery_change_one_day': {
                'ip_match': 0,  # Выявлено совпадение по IP для смен в один день
                'ua_match': 0,  # Выявлено совпадение по UA для смен в один день
                'subnet_match': 0,  # Выявлено совпадение по subnet для смен в один день
                # Факторы сравнения найденного окружения смен в один день и регистрационного окружения
                'ip_eq_reg': -1,
                'subnet_eq_reg': -1,
                'ua_eq_reg': -1,
                # Факторы сравнения найденного окружения смен в один день и пользовательского окружения
                'ip_eq_user': -1,
                'subnet_eq_user': -1,
                'ua_eq_user': -1,
                'ip_first_auth_depth': [  # Глубина IP окружения найденной смены в один день
                    -1,
                    -1,
                    -1,
                ],
                'subnet_first_auth_depth': [  # Глубина subnet окружения найденной смены в один день
                    -1,
                    -1,
                    -1,
                ],
                'ua_first_auth_depth': [  # Глубина UA окружения найденной смены в один день
                    -1,
                    -1,
                    -1,
                ],
            },
        },
    },
}


@with_settings_hosts()
class DataDocumentationTestCase(BaseTestMultiStepWithCommitUtils):
    def test(self):
        """Тест для документирования формата данных"""
        factors = self.make_step_1_factors(
            real_reason='restore',
            firstnames_entered=['A'],
            lastnames_entered=['B', 'P'],
            names_account=[
                {
                    'firstname': TEST_DEFAULT_FIRSTNAME,
                    'lastname': TEST_DEFAULT_LASTNAME,
                    'interval': {
                        'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1),
                        'end': events_info_interval_point(user_ip=TEST_IP_2, timestamp=2),
                    },
                },
                {
                    'firstname': TEST_DEFAULT_FIRSTNAME,
                    'lastname': TEST_DEFAULT_LASTNAME_INEXACT,
                    'interval': {
                        'start': events_info_interval_point(user_ip=TEST_IP_2, timestamp=2),
                        'end': None,
                    },
                },
            ],
            names_current_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
            names_current_index=((0, 1), 1),
            names_registration_factor=[STRING_FACTOR_NO_MATCH, STRING_FACTOR_NO_MATCH],
            names_registration_index=((0, 1), 0),
            names_factor_change_count=1,
            names_factor_change_depth=[FACTOR_FLOAT_MATCH, FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
            names_factor_change_ip_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
            names_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
            names_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
            names_factor_change_ip_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
            names_factor_change_subnet_eq_reg=[FACTOR_BOOL_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_MATCH],
            names_factor_change_ua_eq_reg=[compare_uas_factor('yandexuid'), FACTOR_NOT_SET, compare_uas_factor('yandexuid')],
            birthday_entered='2012-01-01',
            birthday_account=[
                {
                    'value': '2011-11-11',
                    'interval': {
                        'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1),
                        # ДР более не актуальна, но подробностей мы не знаем
                        'end': {'timestamp': None},
                    },
                },
                {
                    'value': TEST_DEFAULT_BIRTHDAY,
                    'interval': {
                        'start': {'timestamp': None},
                        'end': None,
                    },
                },
            ],
            birthday_current_factor=BIRTHDAYS_FACTOR_FULL_MATCH,
            birthday_current_index=1,
            birthday_registration_factor=BIRTHDAYS_FACTOR_INEXACT_MATCH,
            birthday_registration_index=0,
            birthday_factor_change_count=1,
            birthday_factor_change_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
            birthday_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH],
            passwords_last_change_request={
                'comment': u'broken',
                'admin': u'alexco',
                'origin_info': events_info_interval_point(user_ip=TEST_IP, timestamp=1),
                'change_required': True,
            },
            passwords_factor_forced_change_pending=FACTOR_BOOL_MATCH,
            passwords_last_change={
                'origin_info': events_info_interval_point(
                    user_ip=TEST_IP,
                    timestamp=1000,
                    yandexuid=TEST_YANDEXUID_COOKIE,
                ),
                'change_type': PASSWORD_CHANGE_TYPE_FORCED,
            },
        )

        self.make_step_2_factors(
            factors,
            phone_numbers_entered=['89111234567', '79111234567', '79111234568'],
            phone_numbers_history=[
                {
                    'value': '79117654321',
                    'intervals': [
                        {'start': events_info_interval_point(user_ip=TEST_IP, timestamp=1), 'end': None},
                    ],
                },
                {
                    'value': '79111234567',
                    'intervals': [
                        {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                            'end': events_info_interval_point(user_ip=TEST_IP, timestamp=3),
                        },
                        {
                            'start': events_info_interval_point(user_ip=TEST_IP, timestamp=4),
                            'end': None,
                        },
                    ],
                },
            ],
            phone_numbers_matches=['79111234567'],
            phone_numbers_match_indices=[(0, 1)],
            phone_numbers_factor_entered_count=3,
            phone_numbers_factor_history_count=2,
            phone_numbers_factor_matches_count=1,
            phone_numbers_factor_change_count=2,
            phone_numbers_factor_change_depth=[FACTOR_NOT_SET, FACTOR_FLOAT_MATCH, FACTOR_FLOAT_MATCH],
            phone_numbers_factor_change_ip_eq_user=[FACTOR_NOT_SET, FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
            phone_numbers_factor_change_subnet_eq_user=[FACTOR_NOT_SET, FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
            phone_numbers_factor_change_ua_eq_user=[FACTOR_NOT_SET, FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
            phone_numbers_factor_match_depth=[FACTOR_FLOAT_MATCH, FACTOR_FLOAT_MATCH],
            phone_numbers_factor_match_ip_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
            phone_numbers_factor_match_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
            phone_numbers_factor_match_ua_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
            phone_numbers_factor_match_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
            emails_entered=[
                u'email_2@ya.ru',
                u'email_3@ya.ru',
                u'ва@силий@xn--80atjc.xn--p1ai',
                u'email_5@.рф',
            ],
            emails_history=[
                {
                    'value': u'email_2@ya.ru',
                    'intervals': [{'start': events_info_interval_point(user_ip=TEST_IP), 'end': None}],
                },
                {
                    'value': u'email_3@ya.ru',
                    'intervals': [{
                        'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                        'end': events_info_interval_point(user_ip=TEST_IP, timestamp=5),
                    }],
                },
                {
                    'value': u'ва@силий@xn--80atjc.xn--p1ai',
                    'intervals': [{'start': events_info_interval_point(user_ip=TEST_IP, timestamp=3), 'end': None}],
                },
                {
                    'value': u'email_5@.рф',
                    'intervals': [{'start': events_info_interval_point(user_ip=TEST_IP, timestamp=4), 'end': None}],
                },
            ],
            emails_matches=[
                u'email_3@ya.ru',
                u'email_2@ya.ru',
                u'ва@силий@xn--80atjc.xn--p1ai',
                u'email_5@.рф',
            ],
            emails_match_indices=[(0, 1), (1, 0), (2, 2), (3, 3)],
            emails_factor_entered_count=4,
            emails_factor_history_count=4,
            emails_factor_matches_count=4,
            answer_question=u'99:my question',
            answer_entered=u'ответ',
            answer_index_best=(1, 1),
            answer_factor_best=STRING_FACTOR_MATCH,
            answer_factor_current=STRING_FACTOR_NO_MATCH,
            answer_factor_change_count=3,
            answer_factor_change_ip_eq_user=[FACTOR_BOOL_MATCH] * ANSWER_FACTORS_COUNT,
            answer_factor_change_subnet_eq_user=[FACTOR_BOOL_MATCH] * ANSWER_FACTORS_COUNT,
            answer_factor_change_ua_eq_user=[FACTOR_BOOL_NO_MATCH] * ANSWER_FACTORS_COUNT,
            answer_factor_match_depth=[FACTOR_FLOAT_MATCH, FACTOR_FLOAT_MATCH],
            answer_factor_match_ip_eq_user=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_MATCH],
            answer_factor_match_subnet_eq_user=[FACTOR_BOOL_MATCH, FACTOR_BOOL_MATCH],
            answer_factor_match_ua_eq_user=[FACTOR_BOOL_NO_MATCH, compare_uas_factor('yandexuid')],
            answer_factor_match_ua_eq_reg=[FACTOR_BOOL_NO_MATCH, FACTOR_BOOL_NO_MATCH],
            answer_history=[
                {
                    'question': u'1:qqq',
                    'answers': [
                        {
                            'value': u'КО',
                            'intervals': [
                                {
                                    'start': events_info_interval_point(user_ip=TEST_IP, timestamp=2),
                                    'end': events_info_interval_point(user_ip=TEST_IP, timestamp=3),
                                },
                            ],
                        },
                    ],
                },
                {
                    'question': u'99:my question',
                    'answers': [
                        {
                            'value': u'КО',
                            'intervals': [
                                {
                                    'start': events_info_interval_point(user_ip=TEST_IP, timestamp=3),
                                    'end': events_info_interval_point(user_ip=TEST_IP, timestamp=4),
                                },
                            ],
                        },
                        {
                            'value': u'ответ',
                            'intervals': [
                                {
                                    'start': events_info_interval_point(user_ip=TEST_IP, timestamp=4),
                                    'end': events_info_interval_point(user_ip=TEST_IP, timestamp=6),
                                },
                            ],
                        },
                        {
                            'value': u'answer',
                            'intervals': [
                                {
                                    'start': events_info_interval_point(user_ip=TEST_IP, timestamp=6),
                                    'end': None,
                                },
                            ],
                        },
                    ],
                },
            ],
        )

        ip_depth = [FACTOR_FLOAT_MATCH, 0.8, FACTOR_NOT_SET, FACTOR_NOT_SET]
        subnet_depth = [FACTOR_FLOAT_MATCH] + [FACTOR_NOT_SET] * (PERSONAL_AND_RECOVERY_MAX_ANALYZED_CHANGES - 1)
        ua_depth = [FACTOR_FLOAT_MATCH] + [FACTOR_NOT_SET] * (PERSONAL_AND_RECOVERY_MAX_ANALYZED_CHANGES - 1)
        self.make_step_3_factors(
            factors,
            registration_ip=TEST_IP,
            registration_country_entered=u'ru',
            registration_country_entered_id=None,
            registration_country_factor=STRING_FACTOR_MATCH,
            registration_country_factor_id=FACTOR_BOOL_NO_MATCH,
            registration_city_factor=STRING_FACTOR_NO_MATCH,
            registration_city_factor_id=FACTOR_BOOL_NO_MATCH,
            registration_city_history=TEST_REGISTRATION_CITY,
            registration_city_history_id=TEST_REGISTRATION_CITY_ID,
            registration_country_history=TEST_DEFAULT_REGISTRATION_COUNTRY,
            registration_country_history_id=TEST_REGISTRATION_COUNTRY_ID,
            ua_first_auth=build_auth_info(authtype=authtypes.AUTH_TYPE_WEB, status='ses_create', timestamp=10),
            ua_last_auth=build_auth_info(timestamp=1000),
            factor_ua_auth_interval=0.5,
            factor_ua_first_auth_depth=FACTOR_FLOAT_MATCH,
            user_agent=TEST_USER_AGENT_2_PARSED,
            ip_first_auth=None,
            ip_last_auth=None,
            subnet_first_auth=None,
            subnet_last_auth=None,
            factor_ip_auth_interval=FACTOR_NOT_SET,
            factor_ip_first_auth_depth=FACTOR_NOT_SET,
            factor_subnet_auth_interval=FACTOR_NOT_SET,
            factor_subnet_first_auth_depth=FACTOR_NOT_SET,
            gathered_auths_count=3,
            personal_and_recovery_subnet_match=FACTOR_BOOL_MATCH,
            personal_and_recovery_ua_match=FACTOR_BOOL_MATCH,
            personal_and_recovery_ip_eq_user=FACTOR_BOOL_MATCH,
            personal_and_recovery_subnet_eq_user=FACTOR_BOOL_NO_MATCH,
            personal_and_recovery_ua_eq_user=UA_FACTOR_FULL_MATCH,
            personal_and_recovery_ua_eq_reg=FACTOR_BOOL_NO_MATCH,
            personal_and_recovery_ip_first_auth_depth=ip_depth,
            personal_and_recovery_subnet_first_auth_depth=subnet_depth,
            personal_and_recovery_ua_first_auth_depth=ua_depth,
            personal_and_recovery_matches=[
                {
                    'envs': [
                        one_day_match_env(
                            timestamp=1000,
                            entity=NAMES_ENTITY_NAME,
                            ua=compared_user_agent(os=None, browser=None, yandexuid='123'),
                            ip_first_auth_info=build_auth_info(timestamp=500),
                            subnet_first_auth_info=build_auth_info(timestamp=10),
                        ),
                        one_day_match_env(
                            timestamp=1000,
                            entity=PHONE_NUMBERS_ENTITY_NAME,
                            ua=compared_user_agent(os=None, browser=None, yandexuid='123'),
                            ip_first_auth_info=build_auth_info(timestamp=10),
                            subnet_first_auth_info=build_auth_info(timestamp=10),
                        ),
                    ],
                    'fields': ['ip', 'subnet'],
                },
                {
                    'envs': [
                        one_day_match_env(
                            timestamp=1000,
                            entity=BIRTHDAYS_ENTITY_NAME,
                            ip=TEST_IP_3,
                            subnet=None,
                            ua_first_auth_info=build_auth_info(timestamp=10),
                        ),
                        one_day_match_env(
                            timestamp=1000,
                            entity=ANSWERS_ENTITY_NAME,
                            ip=TEST_IP_4,
                            subnet=None,
                            ua_first_auth_info=build_auth_info(timestamp=10),
                        ),
                    ],
                    'fields': ['ua'],
                },
            ],
            passwords_factor_change_ip_first_auth_depth=[FACTOR_NOT_SET],  # т.к. IP появился после того как была сделана смена
            passwords_factor_change_subnet_first_auth_depth=[FACTOR_FLOAT_NO_MATCH],
            passwords_factor_change_ua_first_auth_depth=[FACTOR_FLOAT_NO_MATCH],
            passwords_change_ip_first_auth=[build_auth_info(timestamp=500)],
            passwords_change_subnet_first_auth=[build_auth_info(timestamp=10)],
            passwords_change_ua_first_auth=[build_auth_info(timestamp=10)],
            answer_factor_match_ip_first_auth_depth=[FACTOR_NOT_SET, 0.7],
            answer_factor_match_subnet_first_auth_depth=[FACTOR_NOT_SET, FACTOR_FLOAT_MATCH],
            answer_factor_match_ua_first_auth_depth=[FACTOR_FLOAT_NO_MATCH, FACTOR_NOT_SET],
            answer_match_ip_first_auth=[None, build_auth_info(timestamp=500)],
            answer_match_subnet_first_auth=[None, build_auth_info(timestamp=10)],
            answer_match_ua_first_auth=[build_auth_info(timestamp=10), None],
        )

        task_data = task_data_response(task_id=TEST_SOCIAL_TASK_ID)

        self.make_step_4_factors(
            factors,
            social_accounts_entered_accounts=[task_data['profile']],
            social_accounts_entered_profiles=[profile_item(uid=TEST_PDD_UID)],
            social_accounts_factor_entered_accounts_count=1,
            social_accounts_factor_entered_profiles_count=1,
            services_entered=[u'mail', u'metrika', u'disk', u'yandsearch'],
            services_account=[u'mail', u'metrika', u'disk'],
            services_matches=[u'mail', u'metrika', u'disk'],
            services_factor_entered_count=5,
            services_factor_account_count=4,
            services_factor_matches_count=4,
        )

        self.make_step_5_factors(
            factors,
            delivery_addresses_entered=[TEST_DELIVERY_ADDRESS_2],
            delivery_addresses_account=[TEST_DELIVERY_ADDRESS_2],
            delivery_addresses_matches=[TEST_DELIVERY_ADDRESS_2],
            delivery_addresses_factor_entered_count=1,
            delivery_addresses_factor_account_count=1,
            delivery_addresses_factor_matches_count=1,
            email_folders_entered=[u'Папка1', u'Папка2', u'Papka'],
            email_folders_actual=[u'Папка'],
            email_folders_matches=[u'Папка'],
            email_folders_factor_entered_count=3,
            email_folders_factor_actual_count=1,
            email_folders_factor_matches_count=1,
            email_blacklist_actual=['vasia@xn--80a1acny.xn--p1ai', u'вася@xn--80a1acny.xn--p1ai'],
            email_blacklist_entered=[u'вася@почта.рф'],
            email_blacklist_matches=[u'vasia@xn--80a1acny.xn--p1ai'],
            email_blacklist_factor_actual_count=2,
            email_blacklist_factor_entered_count=1,
            email_blacklist_factor_matches_count=1,
            email_whitelist_actual=['mail1@mail.ru', 'mail2@mail.ru'],
            email_whitelist_entered=['mail1@mail.com', 'mail1@mail.ru'],
            email_whitelist_matches=['mail1@mail.ru', 'mail2@mail.ru'],
            email_whitelist_factor_actual_count=2,
            email_whitelist_factor_entered_count=2,
            email_whitelist_factor_matches_count=2,
            email_collectors_entered=['mail2@mail.com'],
            email_collectors_actual=['mail1@mail.com', 'mail2@mail.ru'],
            email_collectors_matches=['mail1@mail.com'],
            email_collectors_factor_entered_count=1,
            email_collectors_factor_actual_count=2,
            email_collectors_factor_matches_count=1,
            outbound_emails_entered=[u'вася@почта.рф'],
            outbound_emails_actual=[u'vasia@xn--80a1acny.xn--p1ai', u'вася@xn--80a1acny.xn--p1ai'],
            outbound_emails_matches=[u'vasia@xn--80a1acny.xn--p1ai'],
            outbound_emails_factor_entered_count=1,
            outbound_emails_factor_actual_count=2,
            outbound_emails_factor_matches_count=1,
        )

        self.make_step_6_factors(
            factors,
        )

        eq_(
            factors,
            EXPECTED_DOCUMENTED_FACTORS,
        )
