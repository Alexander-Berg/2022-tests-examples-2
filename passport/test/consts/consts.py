# -*- coding: utf-8 -*-

from datetime import datetime

from passport.backend.core.types.account.account import PDD_UID_BOUNDARY
from passport.backend.core.types.phone_number.phone_number import PhoneNumber


TEST_UID = TEST_UID1 = 123
TEST_LOGIN = TEST_LOGIN1 = 'login'
TEST_FIRSTNAME1 = u'Платон'
TEST_LASTNAME1 = u'Афинский'
TEST_DISPLAY_NAME1 = {'name': TEST_LASTNAME1}
TEST_BIRTHDATE1 = '1990-01-02'

TEST_DISPLAY_LOGIN1 = 'Log in #1'

TEST_FIRSTNAME2 = u'Деметр'
TEST_LASTNAME2 = u'Палестинский'
TEST_BIRTHDATE2 = '1993-07-14'
TEST_LOGIN2 = 'login2'

TEST_UID2 = 234
TEST_UID3 = 345
TEST_UID4 = 456

TEST_DEFAULT_AVATAR1 = 'groupid1/avatar1'
TEST_DEFAULT_AVATAR2 = 'groupid2/avatar2'

TEST_DEVICE_ID1 = 'device_id1'
TEST_DEVICE_IFV1 = 'device_ifv1'
TEST_DEVICE_NAME1 = 'device_name1'

TEST_COUNTRY_CODE1 = 'ua'
TEST_CITY1 = u'Киев'
TEST_TIMEZONE1 = 'Europe/Kiev'

TEST_APPLICATION_ID1 = 4571

TEST_CONFIRMATION_CODE1 = '1234'
TEST_CONFIRMATION_CODE2 = '2345'

TEST_CONSUMER1 = 'consumer1'

TEST_CONSUMER_IP1 = '127.0.0.1'

TEST_FAMILY_ID1 = 'f1'

TEST_PASSWORD1 = 'pas123!'
TEST_PASSWORD_HASH1 = '1:pass1'

TEST_DATETIME1 = datetime(2015, 3, 1, 12, 2, 4)
TEST_DATETIME2 = datetime(2015, 4, 2, 5, 7, 1)

TEST_NEOPHONISH_LOGIN1 = 'nphne-test1'

TEST_PHONE_NUMBER1 = PhoneNumber.parse('+79030915478')
TEST_PHONE_NUMBER2 = PhoneNumber.parse('+79030915400')

TEST_PHONE_NUMBER_FAKE1 = PhoneNumber.parse('+70000381931')
TEST_PHONE_NUMBER_FAKE2 = PhoneNumber.parse('+70000123456')

TEST_PHONE_OPERATION_ID1 = 35513
TEST_PHONE_OPERATION_ID2 = 51547

TEST_PHONISH_LOGIN1 = 'phne-test1'

TEST_PROCESS_UUID1 = 'process-uuid-1'

TEST_PROFILE_THRESHOLD1 = 0.6
TEST_PROFILE_GOOD_ESTIMATE1 = 0.1
TEST_PROFILE_BAD_ESTIMATE1 = TEST_PROFILE_THRESHOLD1 + 0.1

TEST_EMAIL1 = 'yehlo@isis.us'
TEST_EMAIL_ID1 = 911

TEST_EMAIL2 = 'benny@taliban.us'
TEST_EMAIL_ID2 = 111

TEST_KIDDISH_LOGIN1 = 'kid-12345a'
TEST_KIDDISH_LOGIN2 = 'kid-12345b'

TEST_MAILISH_LOGIN1 = TEST_EMAIL1

TEST_OAUTH_CLIENT_ID1 = 'fakeclid1'

TEST_PHONE_ID1 = 10
TEST_PHONE_ID2 = 20
TEST_PHONE_ID3 = 30

TEST_PDD_UID1 = PDD_UID_BOUNDARY + 1
TEST_PDD_LOGIN1 = 'pdd@doors.us'

TEST_REGISTRAION_DATETIME1 = '2000-01-02 00:00:00'

TEST_REQUEST_ID1 = 'request-id1'

TEST_RETPATH1 = 'https://www.yandex.ru/1/'
TEST_RETPATH2 = 'https://www.yandex.ru/2/'

TEST_SCHOLAR_LOGIN1 = u'вовочка777'

TEST_SOCIAL_AVATAR1 = {
    '0x0': 'https://pp.userapi.com/1.jpg',
    '50x50': 'https://pp.userapi.com/2.jpg',
    '200x0': 'https://pp.userapi.com/3.jpg',
}

TEST_SOCIAL_LOGIN1 = 'uid-test1'
TEST_SOCIAL_LOGIN2 = 'uid-test2'

TEST_SOCIAL_PROFILE_ID1 = 23456

TEST_SOCIAL_TASK_ID1 = '50c1a17a51d001'
TEST_SOCIAL_TASK_ID2 = '50c1a17a51d002'

TEST_TRACK_ID1 = '7ac1' * 8 + '7f'
TEST_TRACK_ID2 = '7ac2' * 8 + '7f'

TEST_UNIXTIME1 = 946674000
TEST_UNIXTIME2 = 978296400
TEST_UNIXTIME3 = 1009918800

TEST_USER_AGENT1 = 'curl'

TEST_USER_IP1 = '1.2.3.4'

TEST_USER_TICKET1 = 'userticket1'

TEST_YANDEX_EMAIL1 = TEST_LOGIN1 + '@yandex.ru'

TEST_YANDEX_TEAM_LOGIN1 = 'yndxandrey'

TEST_YANDEX_TOKEN1 = 'ytoken1'
TEST_YANDEX_AUTHORIZATION_CODE1 = '1234'
TEST_YANDEX_TOKEN_EXPIRES_IN1 = 30

TEST_YANDEXUID1 = 'yandexuid1'

TEST_8_DIGITS_IVORY_COAST_PHONE_NUMBER1 = PhoneNumber.parse('+22503123456', country='CI', allow_impossible=True)
TEST_10_DIGITS_IVORY_COAST_PHONE_NUMBER1 = PhoneNumber.parse('+2250103123456', country='CI', allow_impossible=True)


TEST_SCHOLAR_PASSWORD1 = 'король'

# Бинарный protobuf хранится в базе данных
TEST_PLUS_SUBSCRIBER_STATE1_PROTO = b'\n\r\x08o\x12\x03foo\x18\xd2\x85\xd8\xcc\x04\n\x03\x08\xde\x01\x10\xff\xf1\xd5\xd4\xaf\x9a\x878\x1a\x08\x08\xcd\x02\x12\x03bar'
# Его же Чёрный Ящик отдаёт как атрибут и заворачивает в standard base64
TEST_PLUS_SUBSCRIBER_STATE1_BASE64 = 'Cg0IbxIDZm9vGNKF2MwECgMI3gEQ//HV1K+ahzgaCAjNAhIDYmFy'
# Внутри модели аккаунта мы его храним как человеко-читаемый JSON и
# используем для простого строкового сравнения изменений аккаунта, а также для записи в разные логи
TEST_PLUS_SUBSCRIBER_STATE1_JSON = '{"AvailableFeatures":[{"End":1234567890,"Id":111,"Value":"foo"},{"Id":222}],"AvailableFeaturesEnd":31556889864403199,"FrozenFeatures":[{"Id":333,"Value":"bar"}]}'
