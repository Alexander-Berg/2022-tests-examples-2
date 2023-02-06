import gen_totp
import utils


def test_bad_totp(host, uid, totp):

    request, response = utils.do_request(host, 'check_rfc_totp', 'uid=%d&totp=%s' % (uid, totp))

    if utils.get_status_from_resp(response) != 'INVALID':
        print("Fail, status is not INVALID")
        print("User: %s" % uid)
        print("Totp: %s" % totp)
        print("Request: %s" % request)
        print("")
        print("Output:")
        print(response)
        raise Exception("check_rfc_totp test failed")


def test_one_check(host, time_shift, uid, key, expected_status):
    now = utils.get_timestamp()
    time_to_test = now + time_shift
    totp = gen_totp.gen_rfc_totp(key, time_to_test)
    request, response = utils.do_request(host, 'check_rfc_totp', 'uid=%d&totp=%s' % (uid, totp))

    if utils.get_status_from_resp(response) != expected_status:
        print("Fail, status is not as expected")
        print("Time: %d (%d) = %d + %d" % (time_to_test, time_shift, time_to_test / 30 * 30, time_to_test % 30))
        print("Now : %d       = %d + %d" % (now, now / 30 * 30, now % 30))
        print("User: %s" % uid)
        print("Totp: %s" % totp)
        print("Expected: %s" % expected_status)
        print("Request: %s" % request)
        print("")
        print("Output:")
        print(response)
        raise Exception("check_rfc_totp test failed")

    if expected_status == 'VALID':
        time = int(utils.get_time_from_resp(response))
        expected_time = int(time_to_test / 30) * 30
        if expected_time != time:
            print("Fail")
            print("Time: %d (%d) = %d + %d" % (time_to_test, time_shift, time_to_test / 30 * 30, time_to_test % 30))
            print("Now : %d       = %d + %d" % (now, now / 30 * 30, now % 30))
            print("User: %s" % uid)
            print("Totp: %s" % totp)
            print("Expected: time %d" % expected_time)
            print("Request: %s" % request)
            print("")
            print("Output:")
            print(response)
            raise Exception("check_rfc_totp test failed")


def test_time_shift(host, uid, key):
    test_one_check(host, -65, uid, key, 'INVALID')  # out of window
    test_one_check(host, -29, uid, key, 'ALREADY_USED')
    test_one_check(host, +65, uid, key, 'INVALID')  # out of window
    test_one_check(host, -1, uid, key, 'ALREADY_USED')
    test_one_check(host, +26, uid, key, 'VALID')
    test_one_check(host, +26, uid, key, 'VALID')  # reuse valid totp


def check(blackbox_host):
    test_time_shift(blackbox_host, 4006854609, '0123456789abcdef')

    test_one_check(blackbox_host, 0, 71001, '', 'SECRET_NOT_FOUND')  # user with no secret

    test_one_check(blackbox_host, 0, 4006854609, '0123456789', 'INVALID')  # wrong secret
    test_bad_totp(blackbox_host, 4006854609, '123456')  # wrong password
    test_bad_totp(blackbox_host, 4006854609, 'INVALID')  # bad password format

    print('"CheckRfcTotp" test: passed.')
