# -*- coding: utf-8 -*-
import base64


TEST_UID = 1
TEST_PDD_UID = 1130000000000001
TEST_LOGIN = 'user1'
TEST_PDD_DOMAIN = 'okna.ru'
TEST_PDD_LOGIN = 'user1@okna.ru'
TEST_IP = '127.0.0.1'
TEST_HOST = 'passport.yandex.ru'
TEST_COOKIE = 'Session_id=0:old-session;yandexuid=testyandexuid;sessionid2=0:old-sslsession'
TEST_USER_AGENT = 'curl'
TEST_COOKIE_AGE = 123
TEST_RETPATH = 'https://passport.yandex.by/profile/access'
TEST_PDD_RETPATH = 'https://mail.yandex.ru/for/okna.ru'
TEST_PDD_CORRECTED_RETPATH = 'https://mail.yandex.ru'
TEST_TOTP_SECRET = b'secret' + b'0' * 10
TEST_APP_SECRET = base64.b32encode(TEST_TOTP_SECRET).decode().rstrip('=')
TEST_APP_SECRET_CONTAINER = 'ONSWG4TFOQYDAMBQGAYDAMBQGAAAAAAAAAAAAAJ7TE'
TEST_PIN_LENGTH = 4
TEST_ENCRYPTED_SECRET = 'encrypted_secret'
TEST_ENCRYPTED_JUNK_SECRET = 'junk_secret'
TEST_TOTP_CHECK_TIME = 142
TEST_OTP = 'my_otp'
