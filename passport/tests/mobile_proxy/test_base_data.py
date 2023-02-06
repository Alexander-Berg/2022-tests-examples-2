# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)

from passport.backend.core.services import get_service
from passport.backend.core.types.account.account import PDD_UID_BOUNDARY
from passport.backend.core.types.phone_number.phone_number import (
    mask_phone_number,
    PhoneNumber,
)
from passport.backend.utils.common import smart_str
from passport.backend.utils.time import datetime_to_integer_unixtime


TEST_HOST = 'passport-test.yandex.ru'
TEST_TR_HOST = 'passport-test.yandex.com.tr'
TEST_INVALID_HOST = 'passport-test.invalid.com'
TEST_CONSUMER = 'dev'
TEST_LOGIN = 'login'
TEST_LOGIN2 = 'login2'
TEST_LOGIN3 = 'login3'
TEST_CYRILLIC_LOGIN = u'василий'
TEST_OTHER_LOGIN = 'other_login'
TEST_USER_IP = '1.2.3.4'
TEST_USER_AGENT = 'curl'
TEST_ACCEPT_LANGUAGE = 'ru'
TEST_DISPLAY_LANGUAGE = 'ru'
TEST_LANGUAGE = 'ru'
TEST_REFERER = 'http://passportdev-python.yandex.ru/passport'

TEST_HINT_QUESTION = '99:Doroty\'s best friend'
TEST_HINT_QUESTION_ID = 99
TEST_HINT_QUESTION_TEXT = 'Doroty\'s best friend'
TEST_HINT_ANSWER = 'Toto'
TEST_HINT_ANSWER_MAX = 'a' * 30
TEST_ANSWER_CHECK_ERRORS_CAPTCHA_THRESHOLD = 3

TEST_PDD_UID = PDD_UID_BOUNDARY + 1
TEST_DOMAIN = 'okna.ru'
TEST_CYRILLIC_DOMAIN = u'окна.рф'
TEST_CYRILLIC_DOMAIN_IDNA = u'окна.рф'.encode('idna')
TEST_PDD_USERNAME = TEST_LOGIN
TEST_PDD_CYRILLIC_USERNAME = TEST_CYRILLIC_LOGIN
TEST_PDD_LOGIN = '%s@%s' % (TEST_PDD_USERNAME, TEST_DOMAIN)
TEST_PDD_CYRILLIC_LOGIN = u'%s@%s' % (TEST_PDD_CYRILLIC_USERNAME, TEST_CYRILLIC_DOMAIN)
TEST_PDD_DISPLAY_TEMPLATE = 't:%pdd_username%@%display_domain%'
TEST_PDD_DOMAIN_TEMPLATE = 't:%pdd_username%@%pdd_domain%'

TEST_UID = 1
TEST_UID1 = 11
TEST_UID2 = 2
TEST_UID3 = 3
TEST_SUID = 1
TEST_FIRSTNAME = 'Elon'
TEST_LASTNAME = 'Musk'
TEST_COUNTRY_CODE = 'ru'
TEST_CITY = 'Moscow'
TEST_BIRTHDAY = '1971-06-28'
TEST_DISPLAY_NAME = 'Mr_November'
TEST_DISPLAY_NAME_DATA = {
    u'default_avatar': u'',
    u'name': TEST_DISPLAY_NAME,
}
TEST_PASSPORT_DISPLAY_NAME_FROM_VARIANTS = 'p:Mr_November'
TEST_SOCIAL_DISPLAY_NAME_FROM_VARIANTS = u's:1:fb:Купер'
TEST_SOCIAL_NAME = u'Купер'
TEST_SOCIAL_PROFILE_ID = 1
TEST_SOCIAL_PROVIDER = 'fb'
TEST_GENDER = 1
TEST_TZ = 'Europe/Moscow'
TEST_AVATAR_URL_TEMPLATE = 'https://localhost/get-yapic/%s/%s'
TEST_AVATAR_KEY = '0/key0-0'

TEST_BLACKBOX_RESPONSE_ACCOUNT_DATA = {
    'uid': TEST_UID,
    'login': TEST_LOGIN,
    'display_name': {'name': TEST_DISPLAY_NAME},
    'firstname': TEST_FIRSTNAME,
    'lastname': TEST_LASTNAME,
    'birthdate': TEST_BIRTHDAY,
    'country': TEST_COUNTRY_CODE,
    'gender': TEST_GENDER,
    'language': TEST_LANGUAGE,
}

TEST_ACCOUNT_DATA = {
    u'account': {
        u'display_login': TEST_LOGIN,
        u'display_name': TEST_DISPLAY_NAME_DATA,
        u'login': TEST_LOGIN,
        u'person': {
            u'firstname': TEST_FIRSTNAME,
            u'lastname': TEST_LASTNAME,
            u'birthday': TEST_BIRTHDAY,
            u'country': TEST_COUNTRY_CODE,
            u'gender': TEST_GENDER,
            u'language': TEST_LANGUAGE,
        },
        u'uid': TEST_UID,
        u'is_2fa_enabled': False,
        u'is_rfc_2fa_enabled': False,
        u'is_yandexoid': False,
        u'is_workspace_user': False,
    },
}

TEST_INVALID_PASSWORD = 'wrong_password'
TEST_PASSWORD_QUALITY_VERSION = 3
TEST_PASSWORD = 'aaa1bbbccc'
TEST_PASSWORD_QUALITY = 80
TEST_PASSWORD_HASH = '1:$1$4GcNYVh5$4bdwYxUKcvcYHUXbnGFOA1'

TEST_WEAK_PASSWORD = 'qwerty'
TEST_WEAK_PASSWORD_QUALITY = 0
TEST_WEAK_PASSWORD_HASH = '1:$1$y0aXFE9w$JqrpPZ74WT1Hi/Mb53cTe.'

TEST_PASSWORD_UPDATE_TIMESTAMP = 123456789

TEST_PASSWORD_VERIFICATION_AGE = 10

TEST_OTHER_UID = 2
TEST_TRACK_TYPE = 'authorize'

TEST_PHONE_ID1 = 1
TEST_PHONE_NUMBER = PhoneNumber.parse('+79261234567')
TEST_PHONE_NUMBER_DUMPED = {
    u'international': TEST_PHONE_NUMBER.international,
    u'e164': TEST_PHONE_NUMBER.e164,
    u'original': TEST_PHONE_NUMBER.original,

    u'masked_original': mask_phone_number(TEST_PHONE_NUMBER.original),
    u'masked_international': mask_phone_number(TEST_PHONE_NUMBER.international),
    u'masked_e164': mask_phone_number(TEST_PHONE_NUMBER.e164),
}
TEST_PHONE_NUMBER_DUMPED_MASKED = {
    u'masked_original': mask_phone_number(TEST_PHONE_NUMBER.original),
    u'masked_international': mask_phone_number(TEST_PHONE_NUMBER.international),
    u'masked_e164': mask_phone_number(TEST_PHONE_NUMBER.e164),
}
TEST_PHONE_NUMBER1 = PhoneNumber.parse('+79026411724')
TEST_PHONE_NUMBER_DUMPED1 = {
    u'international': TEST_PHONE_NUMBER1.international,
    u'e164': TEST_PHONE_NUMBER1.e164,
    u'original': TEST_PHONE_NUMBER1.original,

    u'masked_original': mask_phone_number(TEST_PHONE_NUMBER1.original),
    u'masked_international': mask_phone_number(TEST_PHONE_NUMBER1.international),
    u'masked_e164': mask_phone_number(TEST_PHONE_NUMBER1.e164),
}
TEST_LOCAL_PHONE_NUMBER = PhoneNumber.parse('89261234567', 'RU')
TEST_LOCAL_PHONE_NUMBER_DUMPED = {
    u'international': TEST_LOCAL_PHONE_NUMBER.international,
    u'e164': TEST_LOCAL_PHONE_NUMBER.e164,
    u'original': TEST_LOCAL_PHONE_NUMBER.original,

    u'masked_original': mask_phone_number(TEST_LOCAL_PHONE_NUMBER.original),
    u'masked_international': mask_phone_number(TEST_LOCAL_PHONE_NUMBER.international),
    u'masked_e164': mask_phone_number(TEST_LOCAL_PHONE_NUMBER.e164),
}
TEST_NOT_EXIST_PHONE_NUMBER = PhoneNumber.parse('+79161234567')
TEST_NOT_EXIST_PHONE_NUMBER_DUMPED = {
    'international': TEST_NOT_EXIST_PHONE_NUMBER.international,
    'e164': TEST_NOT_EXIST_PHONE_NUMBER.e164,
    'original': TEST_NOT_EXIST_PHONE_NUMBER.original,

    'masked_international': mask_phone_number(TEST_NOT_EXIST_PHONE_NUMBER.international),
    'masked_e164': mask_phone_number(TEST_NOT_EXIST_PHONE_NUMBER.e164),
    'masked_original': mask_phone_number(TEST_NOT_EXIST_PHONE_NUMBER.original),
}
TEST_PHONE_ID2 = 2
TEST_OTHER_EXIST_PHONE_NUMBER = PhoneNumber.parse('+79361234567')
TEST_OTHER_EXIST_PHONE_NUMBER_DUMPED = {
    'international': TEST_OTHER_EXIST_PHONE_NUMBER.international,
    'e164': TEST_OTHER_EXIST_PHONE_NUMBER.e164,
    'original': TEST_OTHER_EXIST_PHONE_NUMBER.original,

    'masked_international': mask_phone_number(TEST_OTHER_EXIST_PHONE_NUMBER.international),
    'masked_e164': mask_phone_number(TEST_OTHER_EXIST_PHONE_NUMBER.e164),
    'masked_original': mask_phone_number(TEST_OTHER_EXIST_PHONE_NUMBER.original),
}
TEST_PHONE_CREATED_DT = datetime(2000, 1, 2, 12, 34, 56)
TEST_PHONE_CREATED_TS = datetime_to_integer_unixtime(TEST_PHONE_CREATED_DT)
TEST_PHONE_ID3 = 3
TEST_PHONE_ID4 = 4
TEST_OPERATION_STARTED_DT = datetime(2001, 5, 6, 7, 8, 9)
TEST_OPERATION_STARTED_TS = datetime_to_integer_unixtime(TEST_OPERATION_STARTED_DT)
TEST_OP_FINISHED_DT = datetime(2005, 2, 3, 1, 2, 3)
TEST_OP_FINISHED_TS = datetime_to_integer_unixtime(TEST_OP_FINISHED_DT)

TEST_SMS_TEXT = u'Ваш код подтверждения: %s. Наберите его в поле ввода.'
TEST_SMS_RETRIEVER_TEXT = u'{PREFIX}Ваш код для подтверждения: {code}.\n{hash}'

TEST_GPS_PACKAGE_NAME = 'com.yandex.passport.testapp1'
TEST_GPS_PACKAGE_HASH = 'gNNu9q4gcSd'
TEST_GPS_PUBLIC_KEY = 'public-key'

TEST_CONFIRMATION_CODE = '1234'
TEST_CONFIRMATION_CODE_1 = '5678'
TEST_SMS_VALIDATION_MAX_CHECKS_COUNT = 3

TEST_CONTACT_PHONE_NUMBER_SID = 89
TEST_SID_ADDED = '%s|%s' % (TEST_CONTACT_PHONE_NUMBER_SID, TEST_PHONE_NUMBER.digital)

TEST_OAUTH_SCOPE = 'oauth:grant_xtoken'
TEST_OAUTH_TOKEN = '123asd'
TEST_AUTH_HEADER = 'Oauth ' + TEST_OAUTH_TOKEN
TEST_OAUTH_TOKEN2 = 'abcd3232'

TEST_OPERATION_ID = 1
TEST_OPERATION_ID2 = 2

TEST_PORTAL_ALIAS_TYPE = 'portal'

TEST_PHONISH_LOGIN1 = 'phne-test1'

TEST_EMAIL = 'test-email1@yandex.ru'
TEST_EMAIL2 = 'test-email2@yandex.ru'

# Notifications
NOTIFICATIONS_URL_BEGIN = '<a href=\'%s\' target=\'_blank\'>'
NOTIFICATIONS_URL_END = '</a>'

TEST_BACKUP = 'abc123456def'
TEST_DATETIME_UPDATED = datetime(2016, 1, 1)
TEST_TIMESTAMP_UPDATED = datetime_to_integer_unixtime(TEST_DATETIME_UPDATED)

TEST_DEVICE_INFO = {
    'app_id': 'test-id',
    'app_platform': 'android',
    'os_version': '5.0.1',
    'manufacturer': 'samsung',
    'model': 'galaxy',
    'app_version': '1.2.3-4',
    'uuid': 'test-uuid',
    'deviceid': 'test-dev-id',
    'ifv': 'test-ifv',
    'device_name': u'Фыр-фыр-фыр',
    'device_id': 'hello-im-device',
}

TEST_DEVICE_INFO_DECODED = {k: smart_str(v) for k, v in TEST_DEVICE_INFO.items()}

TEST_CONSUMER1 = 'dev'
TEST_CONSUMER_IP1 = '127.0.0.1'

TEST_PERIOD_OF_PHONE_NUMBER_LOYALTY_PRACTICAL = timedelta(hours=12)

TEST_RETPATH = 'https://www.yandex.ru'
TEST_DEFAULT_RETPATH = 'https://passport-test.yandex.ru'

# Cookies
TEST_COOKIE_AGE = 123456
TEST_COOKIE_TIMESTAMP = 1383144488

TEST_SESSIONID_VALUE = 'sessionid'
TEST_SSL_SESSIONID_VALUE = '2:sslsession'
TEST_OLD_SESSIONID_VALUE = '0:old-session'
TEST_OLD_SSL_SESSIONID_VALUE = '0:old-sslsession'
TEST_L_VALUE = ('VFUrAHh8fkhQfHhXW117aH4GB2F6UlZxWmUHQmEBdxwEHhZBDyYxVUYCIxEcJEYfFTpdBF9dGRMuJHU4HwdSNQ=='
                '.%s.1002323.298169.6af3100a8920a270bd9a933bbcd48181') % TEST_COOKIE_TIMESTAMP
TEST_MY_WITH_AUTH_SESSION_POLICY_PERMANENT_VALUE = 'YycCAAY2AQEA'
TEST_FUID01_VALUE = 'fuid'
TEST_MY_VALUE = 'YycCAAYA'
TEST_YANDEX_GID_VALUE = 'yandex_gid'
TEST_YANDEXUID_VALUE = 'yandexuid'
TEST_YP_VALUE = '1692607429.udn.bG9naW4%3D%0A'
TEST_YS_VALUE = 'udn.bG9naW4%3D%0A'
TEST_LAH_VALUE = 'OG5EOF8wU_bOAGhjXFp7YXkHAGB9UVFyB2IACGZedV4DWl8FWXF5BgJXYFVzYQVKV3kFVlpaU0p2f31iRkZRYQ.1473090908.1002323.1.2fe2104fff29aa69e867d7d1ea601470'
TEST_ILAHU_VALUE = '1500000000'

TEST_COOKIE_YP = u'yp=%s; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; Path=/' % TEST_YP_VALUE
TEST_COOKIE_YS = u'ys=%s; Domain=.yandex.ru; Path=/' % TEST_YS_VALUE
TEST_COOKIE_L = u'L=%s; Domain=.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Path=/' % TEST_L_VALUE
TEST_COOKIE_YANDEX_LOGIN = 'yandex_login=%s; Domain=.yandex.ru; Secure; Path=/'
TEST_COOKIE_FUI01 = 'fuid01=%s; Domain=.yandex.ru; Path=/' % TEST_FUID01_VALUE
TEST_COOKIE_YANDEXUID = 'yandexuid=%s; Domain=.yandex.ru; Secure; Path=/' % TEST_YANDEXUID_VALUE
TEST_COOKIE_YANDEX_GID = 'yandex_gid=%s; Domain=.yandex.ru; Path=/' % TEST_YANDEX_GID_VALUE
TEST_COOKIE_MY = 'my=%s; Domain=.yandex.ru; Path=/' % TEST_MY_VALUE
COOKIE_LAH_TEMPLATE = u'lah=%s; Domain=.passport-test.yandex.ru; Expires=Tue, 19 Jan 2038 03:14:07 GMT; Secure; HttpOnly; Path=/'
TEST_COOKIE_LAH = COOKIE_LAH_TEMPLATE % TEST_LAH_VALUE
COOKIE_ILAHU_TEMPLATE = u'ilahu=%s; Domain=.passport-test.yandex.ru; Expires=Mon, 13 Jun 2033 03:14:07 GMT; Secure; HttpOnly; Path=/'
TEST_COOKIE_ILAHU = COOKIE_ILAHU_TEMPLATE % TEST_ILAHU_VALUE

TEST_EMPTY_SESSION_COOKIE = 'Session_id=;sessionid2='
TEST_COOKIE_SESSIONID = 'Session_id=%s;' % TEST_SESSIONID_VALUE

TEST_EMPTY_SESSIONID_COOKIE = 'Session_id=; Domain=.yandex.ru; HttpOnly; Path=/'
TEST_EMPTY_SESSIONID2_COOKIE = 'sessionid2=; Domain=.yandex.ru; Expires=Mon, 10 Jun 2013 14:33:47 GMT; Secure; HttpOnly; Path=/'

TEST_USER_COOKIE = 'Session_id=%s; sessionid2=%s; yandexuid=%s' % (
    TEST_SESSIONID_VALUE,
    TEST_SSL_SESSIONID_VALUE,
    TEST_YANDEXUID_VALUE,
)

TEST_MAIL_SERVICE = get_service(slug='mail')
TEST_MAIL_SID = 2

TEST_SOCIAL_LOGIN = 'uid-qwerty123'
TEST_SOCIAL_DISPLAY_NAME = {
    'name': 'Some User',
    'social': {
        'provider': 'fb',
        'profile_id': 123456,
    },
    'default_avatar': '',
}

TEST_PDD_ACCOUNT_DOMAIN_DATA = {
    'punycode': TEST_DOMAIN,
    'unicode': TEST_DOMAIN,
}

TEST_DOMAIN_ID = 1

TEST_EXTERNAL_EMAIL1 = 'joe@joe.us'
TEST_EXTERNAL_EMAIL2 = 'mo@mo.tr'
TEST_EXTERNAL_EMAIL3 = 'kill@theb.il'

TEST_EMAIL_ID1 = 3201
TEST_EMAIL_ID2 = 3202
TEST_EMAIL_ID3 = 3203

TEST_CONFIRMATION_CODE1 = '3232'
TEST_CONFIRMATION_CODE2 = '2323'

TEST_USER_IP1 = '1.2.3.4'

TEST_TR_RECOVERY_EMAIL = 'support-test@yandex-team.com.tr'
TEST_RECOVERY_EMAIL = 'support-test@yandex-team.ru'

TEST_CALL_SESSION_ID = '123-qwe'

TEST_PUBLIC_ID = 'test-public-id'
