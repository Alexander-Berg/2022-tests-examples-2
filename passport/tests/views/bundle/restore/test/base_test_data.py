# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
import time

from passport.backend.api.views.bundle.restore.base import (
    RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
    RESTORE_METHOD_SEMI_AUTO_FORM,
)
import passport.backend.core.authtypes as authtypes
from passport.backend.core.compare import compress_string_factor
from passport.backend.core.compare.test.compare import compared_user_agent
from passport.backend.core.models.phones.faker import TEST_DATE as TEST_PHONE_ACTION_DEFAULT_DATE  # noqa
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.types.phone_number.phone_number import PhoneNumber
from passport.backend.utils.time import (
    datetime_to_unixtime,
    parse_datetime,
)
import six
from six.moves.urllib.parse import quote


USUAL_2FA_RESTORE_METHODS = [
    RESTORE_METHOD_PHONE_AND_2FA_FACTOR,
    RESTORE_METHOD_SEMI_AUTO_FORM,
]

DEFAULT_DATE_FORMAT = '%Y-%m-%d'

TEST_ADMIN_NAME = 'admin_login'
TEST_ADMIN_COMMENT = 'admin comment'

TEST_DOMAIN = 'testdomain.com'
TEST_RETPATH = 'http://test.yandex.ru'
TEST_PDD_RETPATH = u'%s/for/%s/' % (TEST_RETPATH, TEST_DOMAIN)
TEST_CLEANED_PDD_RETPATH = u'http://test.yandex.ru/'
TEST_GLOBAL_LOGOUT_DATETIME = DatetimeNow(
    convert_to_datetime=True,
    timestamp=datetime.fromtimestamp(1),
)

TEST_SOCIAL_LOGIN = 'uid-12345'
TEST_SOCIAL_NAME = u'Имя'
TEST_SOCIAL_PROFILE_ID = 1
TEST_SOCIAL_PROVIDER = 'fb'
TEST_SOCIAL_DISPLAY_NAME = {
    'name': TEST_SOCIAL_NAME,
    'social': {
        'profile_id': TEST_SOCIAL_PROFILE_ID,
        'provider': TEST_SOCIAL_PROVIDER,
    },
}

TEST_ACCOUNT_DELETION_RESTORE_POSSIBLE_PERIOD = timedelta(days=10) - timedelta(hours=1)

TEST_EMAIL = 'vpupk@in.me'
TEST_EMAILS = sorted(['login@yandex.ru', 'login@yandex.kz', 'login@ya.ru'])
TEST_EMAILS_IN_TRACK = ' '.join(sorted('login@yandex.kz login@ya.ru login@yandex.ru'.split()))
TEST_EMAILS_WITH_PHONE_ALIASES = sorted(TEST_EMAILS + ['79123456789@yandex.ru', '79123456789@yandex.kz', '79123456789@ya.ru'])
TEST_OPERATION_TTL = timedelta(seconds=300)
TEST_PHONE = '+79993456789'
TEST_PHONE_OBJECT = PhoneNumber.parse(TEST_PHONE)
TEST_PHONE_LOCAL_FORMAT = '8-(999)-345-6789'
TEST_PHONE_MASKED_FOR_STATBOX = '+79993******'
TEST_PHONE_MASKED_FOR_EMAIL = '+7 999 ***-**-89'
TEST_PHONE2 = '+79993456766'
TEST_PHONE2_OBJECT = PhoneNumber.parse(TEST_PHONE2)
TEST_PHONE_OLD_SCHEME_VALIDATION_DATE = datetime(2000, 1, 2, 10, 11, 30)
TEST_PHONE_DUMP = {
    'international': '+7 999 345-67-89',
    'e164': '+79993456789',
    'original': '+79993456789',

    'masked_international': '+7 999 ***-**-89',
    'masked_e164': '+7999*****89',
    'masked_original': '+7999*****89',
}
TEST_PHONE_DUMP_MASKED = {
    'masked_international': '+7 999 ***-**-89',
    'masked_e164': '+7999*****89',
    'masked_original': '+7999*****89',
}
TEST_PHONE_DUMP_WITH_LOCAL_FORMAT = dict(
    TEST_PHONE_DUMP,
    original=TEST_PHONE_LOCAL_FORMAT,
    masked_original='8-(999)-***-**89',
)
TEST_PHONE_DUMP_2 = {
    'international': '+7 999 345-67-66',
    'e164': TEST_PHONE2,
    'original': TEST_PHONE2,

    'masked_international': '+7 999 ***-**-66',
    'masked_e164': '+7999*****66',
    'masked_original': '+7999*****66',
}
TEST_VALIDATION_CODE = 657196
TEST_VALIDATION_CODE_2 = 123456
TEST_DEVICE_ID_1 = '66530E20-0BD7-4C46-9F57-88058D91A123'
TEST_DEVICE_ID_2 = '65b32e0724f86f10377baf613489d123'
TEST_IP = '37.9.127.175'
TEST_IP_2 = '37.9.127.100'
TEST_IP_3 = '192.168.0.1'
TEST_IP_4 = '10.10.10.10'
TEST_IP_AS_SUBNET = '37.9.64.0/18'
TEST_IP_AS_LIST = ['as13238']
TEST_HOST = 'passport-test.yandex.ru'
TEST_HOST_TR = 'passport-test.yandex.com.tr'
TEST_DEFAULT_LOGIN = 'login'
TEST_USER_ENTERED_LOGIN = 'Login'
TEST_RESTORABLE_EMAIL = '%s@gmail.com' % TEST_DEFAULT_LOGIN
TEST_PIN = '0123'
TEST_PIN_2 = '0124'
TEST_OTP = 'abcd'
TEST_DEFAULT_UID = 1
TEST_PDD_UID = 1130000000000001
TEST_DEFAULT_FIRSTNAME = u'Петр'
TEST_DEFAULT_FIRSTNAME_INEXACT = u'Pertr'
TEST_DEFAULT_LASTNAME = u'Петров'
TEST_DEFAULT_LASTNAME_INEXACT = u'Petroff'
TEST_DEFAULT_NAMES = u', '.join([TEST_DEFAULT_FIRSTNAME, TEST_DEFAULT_LASTNAME])
TEST_DEFAULT_BIRTHDAY = '2000-10-01'
TEST_DEFAULT_REGISTRATION_DATETIME = '2010-10-10 10:20:30'
TEST_DEFAULT_REGISTRATION_TIMESTAMP = datetime_to_unixtime(parse_datetime(TEST_DEFAULT_REGISTRATION_DATETIME))
TEST_DEFAULT_REGISTRATION_TIMESTAMP_DAY = TEST_DEFAULT_REGISTRATION_TIMESTAMP - TEST_DEFAULT_REGISTRATION_TIMESTAMP % timedelta(days=1).total_seconds()
TEST_DEFAULT_ENTERED_REGISTRATION_DATE = '2010-10-10'
TEST_DEFAULT_ENTERED_REGISTRATION_DATE_WITH_TZ = '2010-10-10 MSD+0400'
TEST_DEFAULT_REGISTRATION_DATE_FACTOR = 1.0
TEST_DEFAULT_REGISTRATION_COUNTRY = u'Россия'
TEST_REGISTRATION_COUNTRY_ID = 225
TEST_REGISTRATION_CITY = u'Москва'
TEST_REGISTRATION_CITY_ID = 213
TEST_REGISTRATION_CITY_2 = u'Санкт-Петербург'
TEST_REGISTRATION_CITY_ID_2 = 2
TEST_DEFAULT_PASSWORD = 'qwerty'
TEST_PASSWORD_AUTH_DATE = '2010-10-10'
TEST_PASSWORD_AUTH_DATE_WITH_TZ = '2010-10-10 MSD+0400'
TEST_PASSWORD_AUTH_FOUND_FACTOR = [0, -1, -1]
TEST_PASSWORD_EQUALS_CURRENT_FACTOR = [0, -1, -1]
TEST_PASSWORD_AUTH_DATE_FACTOR = [-1, -1, -1]
TEST_PHONE_ID = 1
TEST_PHONE_ID2 = 2
TEST_PHONE_ID3 = 3
TEST_PHONE_BOUND = datetime.fromtimestamp(12345)
TEST_PHONE_SECURED = datetime.fromtimestamp(123456)
TEST_PHONE_CONFIRMED = datetime.fromtimestamp(1234567)
TEST_PHONE_OPERATION_START_DELTA = timedelta(seconds=60)
TEST_OPERATION_ID1 = 1
TEST_OPERATION_ID2 = 2
TEST_PERSISTENT_TRACK_ID = '52bf429537106213b295c3efa00ce2c1'
TEST_EMAIL_RESTORATION_KEY = '%s%x' % (TEST_PERSISTENT_TRACK_ID, TEST_DEFAULT_UID)
TEST_PDD_EMAIL_RESTORATION_KEY = '%s%x' % (TEST_PERSISTENT_TRACK_ID, TEST_PDD_UID)
TEST_RESTORATION_KEY_CREATE_TIMESTAMP = str(int(time.time() - 3600))
TEST_PDD_DOMAIN = 'fakedomain.com'
TEST_PDD_LOGIN = 'login@%s' % TEST_PDD_DOMAIN
TEST_PDD_DOMAIN_NOT_SERVED = 'not_served_domain.com'
TEST_PDD_LOGIN_NOT_SERVED = 'login@%s' % TEST_PDD_DOMAIN_NOT_SERVED
TEST_PDD_CYRILLIC_LOGIN = u'login@окна.рф'
TEST_PDD_CYRILLIC_DOMAIN = u'окна.рф'
TEST_PDD_CYRILLIC_DOMAIN_PUNYCODE = TEST_PDD_CYRILLIC_DOMAIN.encode('idna').decode('utf8')
TEST_PDD_CYRILLIC_LOGIN_PUNYCODE = u'login@%s' % TEST_PDD_CYRILLIC_DOMAIN_PUNYCODE
TEST_LITE_LOGIN = 'login@lite.com'
TEST_DEFAULT_HINT_QUESTION = '99:question'
TEST_DEFAULT_HINT_QUESTION_TEXT = 'question'
TEST_HINT_QUESTION_TEXT_2 = u'Вопрос 2'
TEST_HINT_QUESTION_2 = u'99:Вопрос 2'
TEST_DEFAULT_HINT_ANSWER = 'answer'
TEST_INVALID_HINT_ANSWER = TEST_DEFAULT_HINT_ANSWER + 'r'
TEST_HINT_ANSWER_2 = u'ответ 2'
TEST_DELIVERY_ADDRESS_1 = {
    u'building': u'16',
    u'city': u'moscow',
    u'entrance': u'',
    u'metro': u'',
    u'zip': u'',
    u'flat': u'',
    u'firstname': u'',
    u'country': u'\u0420\u043e\u0441\u0441\u0438\u044f',
    u'cargolift': u'',
    u'floor': u'',
    u'comment': u'',
    u'fathersname': u'',
    u'phone': u'',
    u'street': u'tolstoy',
    u'lastname': u'',
    u'suite': u'',
    u'intercom': u'',
    u'phone_extra': u'',
    u'email': u'',
}
TEST_DELIVERY_ADDRESS_2 = {
    u'building': u'16',
    u'city': u'\u0418\u0432\u0430\u043d\u043e\u0432\u043e',
    u'entrance': u'',
    u'metro': u'',
    u'zip': u'',
    u'flat': u'',
    u'firstname': u'',
    u'country': u'rf',
    u'cargolift': u'',
    u'floor': u'',
    u'comment': u'',
    u'fathersname': u'',
    u'phone': u'',
    u'street': u'tolstoy',
    u'lastname': u'',
    u'suite': u'10c4',
    u'intercom': u'',
    u'phone_extra': u'',
    u'email': u'',
}
TEST_DEFAULT_COMPARE_REASONS = 'InitialComparator.equal'
TEST_DEFAULT_COMPARE_REASONS_V1 = 'InitialComparator.equal, InitialComparator.equal'
TEST_DEFAULT_LASTNAME_COMPARE_REASONS = 'InitialComparator.equal'
TEST_COMPARE_REASONS_NO_MATCH = 'FuzzyComparatorBase.no_match'
TEST_COMPARE_REASONS_NO_MATCH_V1 = 'FuzzyComparatorBase.no_match, FuzzyComparatorBase.no_match'
TEST_TOKEN = 'd15ead21da6d473b985a05f09f377ded'
TEST_CONTACT_REASON = u'Забыл пароль'
TEST_CONTACT_EMAIL = u'vasia@пупкин.рф'
TEST_RESTORE_ID = '7F,29496,1407927194.47,1,d2f90ceb577b9615b7de94b8f76516827f'
TEST_RESTORE_ID_QUOTED = quote(TEST_RESTORE_ID)
TEST_ADM_FORM_DATA_URL = 'https://localhost/adm/form/%(restore_id)s'
TEST_DEFAULT_QUESTIONS = [
    {'id': 99, 'text': 'my question'},
    {'id': 0, 'text': u'текст'},
    {'id': 99, 'text': 'my other question'},
]
TEST_REQUEST_SOURCE = 'restore'
TEST_TENSORNET_NEGATIVE_THRESHOLD = 0.3
TEST_TENSORNET_POSITIVE_THRESHOLD = 0.8
TEST_TENSORNET_THRESHOLDS = {
    TEST_REQUEST_SOURCE: (TEST_TENSORNET_NEGATIVE_THRESHOLD, TEST_TENSORNET_POSITIVE_THRESHOLD),
}
TEST_FAMILY_ID = 'f42'

TEST_SOCIAL_TASK_ID = '0123456789abcdef'
TEST_SOCIAL_TASK_ID_2 = '0123456789abcdef2'
TEST_SOCIAL_TASK_ID_3 = '0123456789abcdef3'
TEST_SOCIAL_LINK = 'http://vk.com/omg1234?test1=1&test2=2'
TEST_TRACK_ID = 'd2f90ceb577b9615b7de94b8f76516827f'

TEST_DEFAULT_NAMES_FACTOR = {
    'lastname': [
        [u'initial_equal', -1],
        [u'symbol_shrink', -1],
        [u'distance', -1],
        [u'xlit_used', -1],
        [u'aggressive_shrink', -1],
        [u'aggressive_equal', -1],
    ],
    'firstname': [
        [u'initial_equal', -1],
        [u'symbol_shrink', -1],
        [u'distance', -1],
        [u'xlit_used', -1],
        [u'aggressive_shrink', -1],
        [u'aggressive_equal', -1],
    ],
}
TEST_DEFAULT_NAMES_FACTOR_MATCH = {
    'lastname': [
        [u'initial_equal', 1],
        [u'symbol_shrink', -1],
        [u'distance', -1],
        [u'xlit_used', -1],
        [u'aggressive_shrink', -1],
        [u'aggressive_equal', -1],
    ],
    'firstname': [
        [u'initial_equal', -1],
        [u'symbol_shrink', -1],
        [u'distance', -1],
        [u'xlit_used', -1],
        [u'aggressive_shrink', -1],
        [u'aggressive_equal', -1],
    ],
}
TEST_DEFAULT_NAMES_FACTOR_MATCH_V1 = {
    'lastname': [
        [u'initial_equal', 1],
        [u'symbol_shrink', -1],
        [u'distance', -1],
        [u'xlit_used', -1],
        [u'aggressive_shrink', -1],
        [u'aggressive_equal', -1],
    ],
    'firstname': [
        [u'initial_equal', 1],
        [u'symbol_shrink', -1],
        [u'distance', -1],
        [u'xlit_used', -1],
        [u'aggressive_shrink', -1],
        [u'aggressive_equal', -1],
    ],
    'reversed': 0,
}
TEST_NAMES_FACTOR_NO_MATCH_BOTH_EMPTY = {
    'lastname': [
        [u'initial_equal', 0],
        [u'symbol_shrink', -1],
        [u'distance', -1],
        [u'xlit_used', -1],
        [u'aggressive_shrink', -1],
        [u'aggressive_equal', -1],
    ],
    'firstname': [
        [u'initial_equal', 0],
        [u'symbol_shrink', -1],
        [u'distance', -1],
        [u'xlit_used', -1],
        [u'aggressive_shrink', -1],
        [u'aggressive_equal', -1],
    ],
}
TEST_DEFAULT_NAMES_FACTOR_NO_MATCH = {
    'firstname': [
        [u'initial_equal', 0],
        [u'symbol_shrink', 1.0],
        [u'distance', 0.5],
        [u'xlit_used', 0],
        [u'aggressive_shrink', 1.0],
        [u'aggressive_equal', 0],
    ],
    'lastname': [
        [u'initial_equal', 0],
        [u'symbol_shrink', 1.0],
        [u'distance', 0.5],
        [u'xlit_used', 0],
        [u'aggressive_shrink', 1.0],
        [u'aggressive_equal', 0],
    ],
}
TEST_DEFAULT_NAMES_FACTOR_NO_MATCH_V1 = dict(
    TEST_DEFAULT_NAMES_FACTOR_NO_MATCH,
    reversed=0,
)


def factors_to_statbox_dict(prefix, factors):
    def factors_list_to_statbox_dict(prefix, factors):
        return {
            prefix: compress_string_factor([value for name, value in factors]),
        }
    data = {}
    for key, subfactors in factors.items():
        nested_key = '%s_%s' % (prefix, key)
        if isinstance(subfactors, list):
            data.update(factors_list_to_statbox_dict(nested_key, subfactors))
        else:
            data.update({nested_key: str(subfactors)})
    return data


TEST_DEFAULT_STATBOX_ACCOUNT_FACTOR = factors_to_statbox_dict(
    'names_account_factor',
    TEST_DEFAULT_NAMES_FACTOR_MATCH,
)
TEST_DEFAULT_STATBOX_ACCOUNT_FACTOR_V1 = factors_to_statbox_dict(
    'names_account_factor',
    TEST_DEFAULT_NAMES_FACTOR_MATCH_V1,
)
TEST_DEFAULT_STATBOX_ACCOUNT_FACTOR_NO_MATCH = factors_to_statbox_dict(
    'names_account_factor',
    TEST_DEFAULT_NAMES_FACTOR_NO_MATCH,
)
TEST_DEFAULT_STATBOX_ACCOUNT_FACTOR_NO_MATCH_V1 = factors_to_statbox_dict(
    'names_account_factor',
    TEST_DEFAULT_NAMES_FACTOR_NO_MATCH_V1,
)
TEST_DEFAULT_STATBOX_HISTORY_FACTOR = factors_to_statbox_dict(
    'names_history_factor',
    TEST_DEFAULT_NAMES_FACTOR_MATCH,
)
TEST_DEFAULT_STATBOX_HISTORY_FACTOR_V1 = factors_to_statbox_dict(
    'names_history_factor',
    TEST_DEFAULT_NAMES_FACTOR_MATCH_V1,
)
TEST_DEFAULT_STATBOX_HISTORY_FACTOR_NO_MATCH = factors_to_statbox_dict(
    'names_history_factor',
    TEST_DEFAULT_NAMES_FACTOR_NO_MATCH,
)
TEST_DEFAULT_STATBOX_HISTORY_FACTOR_NO_MATCH_V1 = factors_to_statbox_dict(
    'names_history_factor',
    TEST_DEFAULT_NAMES_FACTOR_NO_MATCH_V1,
)


TEST_DEFAULT_STRING_FACTOR = [
    [u'initial_equal', -1],
    [u'symbol_shrink', -1],
    [u'distance', -1],
    [u'xlit_used', -1],
]
TEST_COMPRESSED_STRING_FACTOR = '-1, -1, -1, -1'
TEST_DEFAULT_STRING_FACTOR_MATCH = [
    [u'initial_equal', 1],
    [u'symbol_shrink', -1],
    [u'distance', -1],
    [u'xlit_used', -1],
]
TEST_COMPRESSED_STRING_FACTOR_MATCH = '1, -1, -1, -1'
TEST_DEFAULT_STRING_FACTOR_INEXACT_MATCH = [
    [u'initial_equal', 0],
    [u'symbol_shrink', 1.0],
    [u'distance', 0.8],
    [u'xlit_used', -1],
]
TEST_COMPRESSED_STRING_FACTOR_INEXACT_MATCH = '0, 1.00, 0.80, -1'
TEST_DEFAULT_STRING_FACTOR_EMPTY_NO_MATCH = [
    [u'initial_equal', 0],
    [u'symbol_shrink', -1],
    [u'distance', -1],
    [u'xlit_used', -1],
]
TEST_COMPRESSED_STRING_FACTOR_EMPTY_NO_MATCH = '0, -1, -1, -1'


TEST_OTRS_MESSAGE_NO_PHOTO = '''Content-Type: multipart/mixed; boundary="%(boundary_0)s"
MIME-Version: 1.0
Subject: %(subject)s
From: vasia@xn--h1adkfax.xn--p1ai
Sender: restore@passport.yandex.ru
To: %(to)s
Date: Mon, 07 Jul 2014 12:55:11 +0400
Reply-To: vasia@xn--h1adkfax.xn--p1ai
%(headers)s

--%(boundary_0)s
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: base64

%(body)s
--%(boundary_0)s--
'''


TEST_OTRS_MESSAGE_WITH_PHOTO = '''Content-Type: multipart/mixed; boundary="%(boundary_0)s"
MIME-Version: 1.0
Subject: %(subject)s
From: vasia@xn--h1adkfax.xn--p1ai
Sender: restore@passport.yandex.ru
To: %(to)s
Date: Mon, 07 Jul 2014 12:55:11 +0400
Reply-To: vasia@xn--h1adkfax.xn--p1ai
%(headers)s

--%(boundary_0)s
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: base64

%(body)s
--%(boundary_0)s
Content-Type: application/octet-stream
MIME-Version: 1.0
Content-Transfer-Encoding: base64
Content-Disposition: attachment;filename={possible_quote}%(photo_file_name_escaped)s{possible_quote}

%(photo_file_contents)s
--%(boundary_0)s--
'''.format(
    possible_quote='"' if six.PY2 else '',
)

TEST_HEADERS_WITH_APPID = '''X-OTRS-fromfeedback: fio-%(request_source)s
X-AppID: %(app_id)s
X-OTRS-Pass-Login: %(login)s
X-Address: %(ip)s'''

TEST_HEADERS_WITHOUT_APPID = '''X-OTRS-fromfeedback: fio-%(request_source)s
X-OTRS-Pass-Login: %(login)s
X-Address: %(ip)s'''


TEST_BODY_TEMPLATE = u'''%(disable_login_message)s%(real_reason)sЛогин: %(login)s
Фамилия: %(lastname)s
Имя: %(firstname)s
Дата рождения: %(birthday)s

Контрольный вопрос: %(question)s
Дополнительный электронный адрес: %(emails)s
Номер телефона: %(phone_numbers)s

Дата регистрации: %(registration_date)s
Город регистрации: %(registration_city)s
Страна регистрации: %(registration_country)s

Мои адреса: %(delivery_addresses)s
Социальные профили: %(social_accounts)s
Исходящие адреса: %(outbound_emails)s
Папки в Почте:  %(email_folders)s
Адрес сборщика: %(email_collectors)s
Белый список: %(email_whitelist)s
Черный список: %(email_blacklist)s

Дополнительная информация: %(contact_reason)s

----

Link to form data: %(adm_form_data_url)s'''


TRANSLATIONS_QUESTIONS = {
    'ru': {'11': u'Ваш любимый учитель'},
    'en': {'11': u'Your favourite teacher'},
}


SESSION = {
    'session': {
        'domain': '.yandex.ru',
        'expires': 0,
        'value': '2:session',
    },
    'sslsession': {
        'domain': '.yandex.ru',
        'expires': 1370874827,
        'value': '2:sslsession',
    },
}

EXPECTED_SESSIONID_COOKIE = 'Session_id=%(value)s; Domain=%(domain)s; Secure; HttpOnly; Path=/' % SESSION['session']
EXPECTED_SESSIONID_SECURE_COOKIE = (
    'sessionid2=%(value)s; Domain=%(domain)s; '
    'Expires=Mon, 10 Jun 2013 14:33:47 GMT; Secure; HttpOnly; Path=/'
) % SESSION['sslsession']

TEST_COOKIE_AGE = 123456
TEST_COOKIE_TIMESTAMP = 1383144488
TEST_COOKIE_L = (
    'VFUrAHh8fkhQfHhXW117aH4GB2F6UlZxWmUHQmEBdxwEHhZBDyYxVUYCIxEcJEYfFTpdBF9dGRMuJHU4HwdSNQ=='
    '.%s.1002323.298169.6af3100a8920a270bd9a933bbcd48181'
) % TEST_COOKIE_TIMESTAMP

TEST_COOKIE_L_INFO = {
    'uid': TEST_DEFAULT_UID,
    'login': TEST_DEFAULT_LOGIN,
}

COOKIE_YP_VALUE = '1692607429.udn.bG9naW4%3D%0A'
EXPECTED_YP_COOKIE = u'yp=%s; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % COOKIE_YP_VALUE

COOKIE_YS_VALUE = 'udn.bG9naW4%3D%0A'
EXPECTED_YS_COOKIE = u'ys=%s; Domain=.yandex.ru; Path=/' % COOKIE_YS_VALUE

COOKIE_L_VALUE = TEST_COOKIE_L
EXPECTED_L_COOKIE = u'L=%s; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/' % COOKIE_L_VALUE

EXPECTED_YANDEX_LOGIN_COOKIE = 'yandex_login=%s; Domain=.yandex.ru; Secure; Path=/' % TEST_DEFAULT_LOGIN
EXPECTED_YANDEX_LOGIN_PDD_COOKIE = 'yandex_login=%s; Domain=.yandex.ru; Secure; Path=/' % TEST_PDD_LOGIN

TEST_YANDEXUID_COOKIE = 'yandexuid'
TEST_YANDEX_GID_COOKIE = 'yandex_gid'
TEST_FUID01_COOKIE = 'fuid'
TEST_COOKIE_MY = 'YycCAAYA'
COOKIE_MY_VALUE_WITH_AUTH_SESSION_POLICY_PERMANENT = 'YycCAAY2AQEA'
TEST_SESSIONID = '0:old-session'
TEST_SSL_SESSIONID = '0:old-sslsession'

TEST_SESSIONID_COOKIE = 'Session_id=%s;' % TEST_SESSIONID

TEST_USER_COOKIES = 'Session_id=%s; yandexuid=%s; yandex_gid=%s; fuid01=%s; my=%s; L=%s;' % (
    TEST_SESSIONID,
    TEST_YANDEXUID_COOKIE,
    TEST_YANDEX_GID_COOKIE,
    TEST_FUID01_COOKIE,
    TEST_COOKIE_MY,
    TEST_COOKIE_L,
)

TEST_NON_AUTH_COOKIES = 'yandexuid=%s; yandex_gid=%s; fuid01=%s;' % (
    TEST_YANDEXUID_COOKIE,
    TEST_YANDEX_GID_COOKIE,
    TEST_FUID01_COOKIE,
)

TEST_PASSWORD = 'aaa1bbbccc'
TEST_PASSWORD_2 = 'aaa2bbbccc'
TEST_PASSWORD_QUALITY_OLD = 20
TEST_PASSWORD_QUALITY = 80
TEST_PASSWORD_QUALITY_VERSION = 3
TEST_OLD_SERIALIZED_PASSWORD = '1:$1$4GcNYVh5$4bdwYxUKcvcYHUXbnGFOA1'

TEST_AUTH_ID = '123:1422501443:126'
TEST_OLD_AUTH_ID = '123:0000000:555'
TEST_SESSION_TTL = 1
TEST_SESSION_UID = 123

TEST_USER_AGENT = 'curl'
TEST_USER_AGENT_2 = 'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'
TEST_USER_AGENT_3 = 'Mozilla/5.0 (rv:31.0) Gecko/20100101 Firefox/31.0'
TEST_USER_AGENT_2_PARSED = compared_user_agent(os='windows xp', yandexuid=TEST_YANDEXUID_COOKIE, browser='firefox')
TEST_USER_AGENT_2_PARSED_WITHOUT_YANDEXUID = compared_user_agent(os='windows xp', yandexuid=None, browser='firefox')
TEST_USER_AGENT_4 = 'Opera/9.80 (J2ME/MIDP; Opera Mini/6.5.26955/27.1573; U; ru) Presto/2.8.119 Version/11.10'

TEST_EMPTY_UA = compared_user_agent(os=None, browser=None, yandexuid=None)
TEST_DEFAULT_UA = compared_user_agent(os=None, browser=None, yandexuid=TEST_YANDEXUID_COOKIE)
TEST_FULL_UA_LIST = [TEST_USER_AGENT_2_PARSED]
TEST_LIMITED_UA_LIST = [compared_user_agent(os=None, yandexuid=TEST_YANDEXUID_COOKIE, browser='firefox')]

TEST_MAIL_DB_ID = 'mdb000'
TEST_MAIL_SUID = 3232

TEST_AVATAR_KEY = '0/0-0'
TEST_AVATAR_SIZE = 'islands_xxl'

TEST_APP_ID = 'app-id'


def build_auth_info(status='successful', timestamp=1, authtype=authtypes.AUTH_TYPE_IMAP):
    return {'status': status, 'timestamp': timestamp, 'authtype': authtype}


TEST_DEFAULT_AUTH_INFO = build_auth_info(timestamp=TEST_DEFAULT_REGISTRATION_TIMESTAMP_DAY)
