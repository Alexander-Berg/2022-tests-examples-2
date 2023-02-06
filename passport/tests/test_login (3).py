import gen_totp
import utils
from time import sleep

ip_counter = 0


def test_one_login(host, time_to_test, login, expected_status, key, length, type, secret_id=0):
    global ip_counter
    now = utils.get_timestamp()
    totp = gen_totp.gen_totp(length, type, key, time_to_test)
    request_part = 'userip=0.0.0.%d&login=%s&password=%s' % (ip_counter, login, totp)
    ip_counter += 1
    if secret_id > 0:
        request_part += '&secret_id=%d' % secret_id

    request, response = utils.do_request(host, 'login', request_part)

    actual_status = utils.get_status_from_resp(response)
    if actual_status != expected_status:
        print("Fail")
        print("Time: %d = %d + %d" % (time_to_test, time_to_test / 30 * 30, time_to_test % 30))
        print("Now : %d = %d + %d" % (now, now / 30 * 30, now % 30))
        print("User: %s" % login)
        print("Totp: %s" % totp)
        print("Expected: %s" % expected_status)
        print("Actual: %s" % actual_status)
        print("Request: %s" % request)
        print("")
        print("Output:")
        print(response)
        raise Exception("login test failed")


def test_case_login(host, login, key, length, type):
    now = utils.get_timestamp()

    test_one_login(host, now - 95, login, 'INVALID', key, length, type)  # out of window
    test_one_login(host, now - 45, login, 'VALID', key, length, type)
    sleep(2)
    test_one_login(host, now - 45, login, 'INVALID', key, length, type)  # reuse valid totp
    test_one_login(host, now + 95, login, 'INVALID', key, length, type)  # out of window
    test_one_login(host, now + 25, login, 'VALID', key, length, type)
    sleep(2)
    test_one_login(host, now - 27, login, 'INVALID', key, length, type)  # last valid check time is in future
    test_one_login(host, now - 10, login, 'INVALID', key, length, type)  # last valid check time is in future


def test_method_login_v12(host):
    key = '0123456789abcdef'
    test_case_login(host, 'super.2fa', key, 8, gen_totp.HotpType.Letters)
    print('"Login" v12 test with letters: passed.')

    test_case_login(host, 'liker.2fa.2', key, 12, gen_totp.HotpType.Digits)
    print('"Login" v12 test with digits: passed.')


def test_method_login_v3(host):
    now = utils.get_timestamp()
    secret = '0123456789abcdef'

    # addr.master - uid 71001 - has 1 secret
    pin = '4455'
    test_case_login(host, 'addr.master', utils.get_secret_key(pin, secret), 8, gen_totp.HotpType.Letters)

    # liker.2fa.3 - uid 4001595721 - has 3 secrets
    pin = '1234567890123456'
    test_one_login(
        host, now - 45, 'liker.2fa.3', 'VALID', utils.get_secret_key(pin, secret), 12, gen_totp.HotpType.Digits
    )

    secret = 'abcdef9876543210'
    test_one_login(
        host, now - 14, 'liker.2fa.3', 'VALID', utils.get_secret_key(pin, secret), 12, gen_totp.HotpType.Digits
    )

    secret = '7#3 1337 $3(R337'
    test_one_login(
        host, now + 37, 'liker.2fa.3', 'VALID', utils.get_secret_key(pin, secret), 12, gen_totp.HotpType.Digits
    )

    # last valid login time - in future: +37
    secret = "abcdef9876543210"
    test_one_login(
        host, now + 10, 'liker.2fa.3', 'INVALID', utils.get_secret_key(pin, secret), 8, gen_totp.HotpType.Letters
    )

    # method=login with secret_id
    # 'liker.2fa.4 ',- uid 4001784375 - has 3 secrets
    now = utils.get_timestamp()
    pin = '0123456789'
    secret = '0123456789abcdef'
    test_one_login(
        host, now - 45, 'liker.2fa.4', 'VALID', utils.get_secret_key(pin, secret), 8, gen_totp.HotpType.Letters, 12345
    )
    test_one_login(
        host, now - 14, 'liker.2fa.4', 'INVALID', utils.get_secret_key(pin, secret), 8, gen_totp.HotpType.Letters, 45678
    )
    test_one_login(
        host,
        now - 14,
        'liker.2fa.4',
        'INVALID',
        utils.get_secret_key(pin, secret),
        8,
        gen_totp.HotpType.Letters,
        951753,
    )

    secret = 'abcdef9876543210'
    test_one_login(
        host, now - 14, 'liker.2fa.4', 'VALID', utils.get_secret_key(pin, secret), 8, gen_totp.HotpType.Letters, 45678
    )
    test_one_login(
        host, now + 17, 'liker.2fa.4', 'INVALID', utils.get_secret_key(pin, secret), 8, gen_totp.HotpType.Letters, 12345
    )
    test_one_login(
        host,
        now + 17,
        'liker.2fa.4',
        'INVALID',
        utils.get_secret_key(pin, secret),
        8,
        gen_totp.HotpType.Letters,
        951753,
    )

    secret = '7#3 1337 $3(R337'
    test_one_login(
        host, now + 17, 'liker.2fa.4', 'VALID', utils.get_secret_key(pin, secret), 8, gen_totp.HotpType.Letters, 951753
    )
    test_one_login(
        host, now + 47, 'liker.2fa.4', 'INVALID', utils.get_secret_key(pin, secret), 8, gen_totp.HotpType.Letters, 12345
    )
    test_one_login(
        host, now + 47, 'liker.2fa.4', 'INVALID', utils.get_secret_key(pin, secret), 8, gen_totp.HotpType.Letters, 45678
    )

    print('"Login" v3 test: passed.')


def check(blackbox_host):
    test_method_login_v12(blackbox_host)
    test_method_login_v3(blackbox_host)
