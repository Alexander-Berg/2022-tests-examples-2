import gen_totp
from tool import TotpTool
import utils


# check if given substring is found in response secret given number of times
def check_contains_count(string_to_find, count, buffer, response, request):
    res = buffer.count(string_to_find)
    if res != count:
        print("Fail, substring count mismatch")
        print("Request: %s" % request)
        print("Expected: '%s' %s times. %s is present" % (string_to_find, count, res))
        print("")
        print("BB Output:")
        print(response)
        print("")
        print("Output:")
        print(buffer)
        raise Exception("edit_totp test failed")


# check if given substring is found in response secret
def check_contains(string_to_find, buffer, response, request):
    if string_to_find not in buffer:
        print("Fail, substring not found")
        print("Request: %s" % request)
        print("Expected: %s" % string_to_find)
        print("")
        print("BB Output:")
        print(response)
        print("")
        print("Output:")
        print(buffer)
        raise Exception("edit_totp test failed")


# check that there is no junk_secret in blackbox reply
def check_no_junk_secret(response, request):
    if 'junk_secret' in response:
        print("Fail, junk secret found")
        print("Request: %s" % request)
        print("Expected: no junk_secret in reply")
        print("")
        print("Output:")
        print(response)
        raise Exception("edit_totp test failed")


# check the contents of junk_secret in blackbox reply
def check_junk_secret(secret_count, uid, pin, strs_to_check, response, request):
    junk = utils.get_junk_from_resp(response)
    buffer = tool.decrypt(junk)

    check_contains_count('secrets', secret_count, buffer, response, request)

    check_contains('uid: %d' % uid, buffer, response, request)
    check_contains('pin: "%s"' % pin, buffer, response, request)

    for s in strs_to_check:
        check_contains(s, buffer, response, request)


# check single edit_totp invocation for error
def test_edit_totp_error(host, request_part, to_match):
    request, response = utils.do_request(host, 'edit_totp', request_part)
    error = utils.get_error_from_resp(response)
    if to_match not in error:
        print("Fail, error mismatch")
        print("Request: %s" % request)
        print("Expected: %s" % to_match)
        print("")
        print("Output:")
        print(response)
        raise Exception("edit_totp test failed")

    return response, request


# check the contents of secret_value in blackbox reply
def check_secret(secret_count, uid, pin, strs_to_check, response, request):
    secret_value = utils.get_secret_from_resp(response)
    buffer = tool.decrypt(secret_value)

    check_contains_count('secrets', secret_count, buffer, response, request)

    check_contains('uid: %d' % uid, buffer, response, request)
    check_contains('pin: "%s"' % pin, buffer, response, request)

    for s in strs_to_check:
        check_contains(s, buffer, response, request)


def test_one_edit_totp_create(host, uid, secret_id, secret, pin):
    key = utils.get_secret_key(pin, secret)
    now = utils.get_timestamp()
    totp = gen_totp.gen_totp(8, gen_totp.HotpType.Letters, key, now)

    # let's test that uppercased password gets lowercased
    request, response = utils.do_request(
        host,
        'edit_totp',
        'op=create&uid=%d&pin=%s&password=%s&secret_id=%d&secret=%s'
        % (uid, pin, totp.upper(), secret_id, utils.encode_base64(secret)),
    )
    check_no_junk_secret(response, request)

    check_secret(1, uid, pin, ['id: %d' % secret_id, 'secret: "%s"' % secret], response, request)


def test_one_edit_totp_add(host, uid, secret_id, secret, pin, to_match):
    key = utils.get_secret_key(pin, secret)
    now = utils.get_timestamp() + 58
    totp = gen_totp.gen_totp(8, gen_totp.HotpType.Letters, key, now)
    # let's test that spaces in password are removed
    request, response = utils.do_request(
        host,
        'edit_totp',
        'op=add&uid=%d&password=%s%%20%%20%s&secret_id=%d&secret=%s'
        % (uid, totp[:4], totp[4:], secret_id, utils.encode_base64(secret)),
    )
    check_no_junk_secret(response, request)

    check_secret(
        2,
        uid,
        pin,
        ['id: %d' % secret_id, 'secret: "%s"' % secret, to_match, 'secret: "0123456789abcdef"'],
        response,
        request,
    )

    return now


def test_one_edit_totp_delete_empty(host, uid, secret_id):
    request, response = utils.do_request(host, 'edit_totp', 'op=delete&uid=%d&secret_id=%d' % (uid, secret_id))
    check_no_junk_secret(response, request)
    secret = utils.get_status_from_resp(response)
    if len(secret) != 0:
        print("Fail, secret found")
        print("Request: %s" % request)
        print("Expected: No secret_value")
        print("")
        print("Output:")
        print(response)
        raise Exception("edit_totp test failed")


def test_one_edit_totp_delete(host, uid, pin, secret_id, remaining_id1, remaining_id2):
    request, response = utils.do_request(host, 'edit_totp', 'op=delete&uid=%d&secret_id=%d' % (uid, secret_id))
    check_no_junk_secret(response, request)

    check_secret(2, uid, pin, ['id: %d' % remaining_id1, 'id: %s' % remaining_id2], response, request)


def test_one_edit_totp_replace(host, uid, secret_id, secret, pin, old_secret_id, to_match):
    key = utils.get_secret_key(pin, secret)
    now = utils.get_timestamp() + 58
    totp = gen_totp.gen_totp(8, gen_totp.HotpType.Letters, key, now)
    request, response = utils.do_request(
        host,
        'edit_totp',
        'op=replace&uid=%d&password=%s&secret_id=%d&secret=%s&old_secret_id=%d'
        % (uid, totp, secret_id, utils.encode_base64(secret), old_secret_id),
    )
    check_no_junk_secret(response, request)

    to_check = ['id: %d' % secret_id, 'secret: "%s"' % secret]
    exp_count = 1
    for s in to_match:
        to_check.append('id: %d' % s)
        exp_count += 1
    check_secret(exp_count, uid, pin, to_check, response, request)


# tests for each operation


def test_create(host):
    test_one_edit_totp_create(host, 112233, 11500, '0123456789abcdef', '4455')
    test_one_edit_totp_create(host, 1, 555, 'zxcvb56789abcdef', '0123456789012345')
    test_one_edit_totp_create(host, 777, 1, '01234oq.vkabcdef', '0123456789')
    test_one_edit_totp_create(host, 14, 100500, '0123456789+)jasn', '4455997')

    print('"EditTotp" create test: passed.')


def test_add(host):
    now = test_one_edit_totp_add(host, 71001, 11500, '0123456789abcdefgh', '4455', 'id: 1177')

    key = utils.get_secret_key('1234567890123456', '0123456789abcdef')
    totp = gen_totp.gen_totp(8, gen_totp.HotpType.Letters, key, now)
    test_edit_totp_error(
        host,
        'op=add&uid=4001595721&secret_id=777777&secret=MDEyMzQ1Njc4OWFiY2RlZg==&password=%s' % totp,
        'Failed to add TOTP secret: maximum reached',
    )
    # 4001595721 777777 "0123456789abcdef" 1234567890123456 "id: 1177" "id: 123456" "id: 1337"
    # 1            2       3                4                      5     6            7

    print('"EditTotp" add test: passed.')


def test_delete(host):
    test_one_edit_totp_delete_empty(host, 71001, 1177)
    test_one_edit_totp_delete(host, 4001595721, 1234567890123456, 123456, 1177, 1337)
    test_one_edit_totp_delete(host, 4001595721, 1234567890123456, 1177, 123456, 1337)
    test_one_edit_totp_delete(host, 4001595721, 1234567890123456, 1337, 123456, 1177)

    print('"EditTotp" delete test: passed.')


def test_replace(host):
    test_one_edit_totp_replace(host, 71001, 11500, "0123456789abcdefxyz", '4455', 1177, [])
    test_one_edit_totp_replace(host, 71001, 1177, "0123456789abcdefxyz", '4455', 1177, [])
    test_one_edit_totp_replace(
        host, 4001595721, 777777, "0123456789abcdefxyz", '1234567890123456', 1177, [123456, 1337]
    )
    test_one_edit_totp_replace(
        host, 4001595721, 777777, "0123456789abcdefxyz", '1234567890123456', 1337, [123456, 1177]
    )
    test_one_edit_totp_replace(
        host, 4001595721, 777777, "0123456789abcdefxyz", '1234567890123456', 123456, [1337, 1177]
    )

    print('"EditTotp" replace test: passed.')


def test_errors(host):
    # Totp pwd check failed
    pin = '4455'
    secret = '0123456789abcdefgh'
    key = utils.get_secret_key(pin, secret)
    now = utils.get_timestamp() + 35
    totp = gen_totp.gen_totp(8, gen_totp.HotpType.Letters, key, now)

    # create/add/replace failed because of wrong secret, same id, junk replaced
    response, request = test_edit_totp_error(
        host,
        "uid=71001&op=create&pin=%s&password=%s&secret=%s&secret_id=1234"
        % (pin, totp, utils.encode_base64('wrong_secret')),
        "Totp check failed: password and pin do not match the secret",
    )
    check_junk_secret(1, 71001, '4455', ['id: 1234', 'secret: "wrong_secret"'], response, request)

    response, request = test_edit_totp_error(
        host,
        "uid=71001&op=add&password=%s&secret=%s&secret_id=1234" % (totp, utils.encode_base64('wrong_secret')),
        "Totp check failed: password and pin do not match the secret",
    )
    check_junk_secret(1, 71001, '4455', ['id: 1234', 'secret: "wrong_secret"'], response, request)

    response, request = test_edit_totp_error(
        host,
        "uid=71001&op=replace&password=%s&secret=%s&secret_id=1234&old_secret_id=1177"
        % (totp, utils.encode_base64('wrong_secret')),
        "Totp check failed: password and pin do not match the secret",
    )
    check_junk_secret(1, 71001, '4455', ['id: 1234', 'secret: "wrong_secret"'], response, request)

    print('"EditTotp" fail (wrong secret, junk replaced) test: passed.')

    # create/add/replace failed because of wrong secret, new id, added to junk
    response, request = test_edit_totp_error(
        host,
        "uid=71001&op=create&pin=%s&password=%s&secret=%s&secret_id=100500"
        % (pin, totp, utils.encode_base64('wrong_secret')),
        "Totp check failed: password and pin do not match the secret",
    )
    check_junk_secret(
        2,
        71001,
        '4455',
        ['id: 1234', 'secret: "fucking junk secret"', 'id: 100500', 'secret: "wrong_secret"'],
        response,
        request,
    )

    response, request = test_edit_totp_error(
        host,
        "uid=71001&op=add&password=%s&secret=%s&secret_id=100500" % (totp, utils.encode_base64('wrong_secret')),
        "Totp check failed: password and pin do not match the secret",
    )
    check_junk_secret(
        2,
        71001,
        '4455',
        ['id: 1234', 'secret: "fucking junk secret"', 'id: 100500', 'secret: "wrong_secret"'],
        response,
        request,
    )

    response, request = test_edit_totp_error(
        host,
        "uid=71001&op=replace&password=%s&secret=%s&secret_id=100500&old_secret_id=1177"
        % (totp, utils.encode_base64('wrong_secret')),
        "Totp check failed: password and pin do not match the secret",
    )
    check_junk_secret(
        2,
        71001,
        '4455',
        ['id: 1234', 'secret: "fucking junk secret"', 'id: 100500', 'secret: "wrong_secret"'],
        response,
        request,
    )

    print('"EditTotp" fail (wrong secret, add to junk) test: passed.')

    # create/add/replace failed because of wrong password, junk added
    response, request = test_edit_totp_error(
        host,
        "uid=71001&op=create&pin=%s&password=aa11bb22&secret=%s&secret_id=100500" % (pin, utils.encode_base64(secret)),
        "Totp check failed: password and pin do not match the secret",
    )
    check_junk_secret(
        2,
        71001,
        '4455',
        ['id: 1234', 'secret: "fucking junk secret"', 'id: 100500', 'secret: "0123456789abcdefgh"'],
        response,
        request,
    )

    response, request = test_edit_totp_error(
        host,
        "uid=71001&op=add&password=aa11bb22&secret=%s&secret_id=100500" % (utils.encode_base64(secret)),
        "Totp check failed: password and pin do not match the secret",
    )
    check_junk_secret(
        2,
        71001,
        '4455',
        ['id: 1234', 'secret: "fucking junk secret"', 'id: 100500', 'secret: "0123456789abcdefgh"'],
        response,
        request,
    )

    response, request = test_edit_totp_error(
        host,
        "uid=71001&op=replace&password=aa11bb22&secret=%s&secret_id=100500&old_secret_id=1177"
        % (utils.encode_base64(secret)),
        "Totp check failed: password and pin do not match the secret",
    )
    check_junk_secret(
        2,
        71001,
        '4455',
        ['id: 1234', 'secret: "fucking junk secret"', 'id: 100500', 'secret: "0123456789abcdefgh"'],
        response,
        request,
    )

    print('"EditTotp" fail (wrong pwd, junk added) test: passed.')

    # create failed because of wrong pin, new id, new pin, junk replaced
    response, request = test_edit_totp_error(
        host,
        "uid=71001&op=create&pin=9922&password=%s&secret=%s&secret_id=100500" % (totp, utils.encode_base64(secret)),
        "Totp check failed: password and pin do not match the secret",
    )
    check_junk_secret(1, 71001, '9922', ['id: 100500', 'secret: "0123456789abcdefgh"'], response, request)

    print('"EditTotp" fail (wrong pin, junk replaced) test: passed.')

    # Multiple additions of same secret_id, no junk
    response, request = test_edit_totp_error(
        host,
        "uid=71001&op=add&password=%s&secret=%s&secret_id=1177" % (totp, utils.encode_base64(secret)),
        "Secret id=1177 is duplicated. It was first added at",
    )
    check_no_junk_secret(response, request)

    print('"EditTotp" fail (Multiple additions, no junk) test: passed.')

    # test overflow of junk secrets, failed create/add/replace for user 4001595721
    # first, if id is the same, i.e. one secret replaced
    response, request = test_edit_totp_error(
        host,
        "uid=4001595721&op=create&pin=1234567890123456&password=%s&secret=%s&secret_id=123456"
        % (totp, utils.encode_base64('wrong_secret')),
        "Totp check failed: password and pin do not match the secret",
    )
    check_junk_secret(
        3,
        4001595721,
        '1234567890123456',
        [
            'id: 1177',
            'secret: "0123456789abcdef"',
            'id: 123456',
            'secret: "wrong_secret"',
            'id: 1337',
            'secret: "7#3 1337 $3(R337"',
        ],
        response,
        request,
    )

    response, request = test_edit_totp_error(
        host,
        "uid=4001595721&op=add&password=%s&secret=%s&secret_id=123456" % (totp, utils.encode_base64('wrong_secret')),
        "Totp check failed: password and pin do not match the secret",
    )
    check_junk_secret(
        3,
        4001595721,
        '1234567890123456',
        [
            'id: 1177',
            'secret: "0123456789abcdef"',
            'id: 123456',
            'secret: "wrong_secret"',
            'id: 1337',
            'secret: "7#3 1337 $3(R337"',
        ],
        response,
        request,
    )

    response, request = test_edit_totp_error(
        host,
        "uid=4001595721&op=replace&password=%s&secret=%s&secret_id=123456&old_secret_id=1177"
        % (totp, utils.encode_base64('wrong_secret')),
        "Totp check failed: password and pin do not match the secret",
    )
    check_junk_secret(
        3,
        4001595721,
        '1234567890123456',
        [
            'id: 1177',
            'secret: "0123456789abcdef"',
            'id: 123456',
            'secret: "wrong_secret"',
            'id: 1337',
            'secret: "7#3 1337 $3(R337"',
        ],
        response,
        request,
    )

    print('"EditTotp" fail (overflow of junks) test: passed.')

    # next, check if id changes, expect oldest one to be replaced
    response, request = test_edit_totp_error(
        host,
        "uid=4001595721&op=create&pin=1234567890123456&password=%s&secret=%s&secret_id=7777"
        % (totp, utils.encode_base64('wrong_secret')),
        "Totp check failed: password and pin do not match the secret",
    )
    check_junk_secret(
        3,
        4001595721,
        '1234567890123456',
        [
            'id: 123456',
            'secret: "abcdef9876543210"',
            'id: 7777',
            'secret: "wrong_secret"',
            'id: 1337',
            'secret: "7#3 1337 $3(R337"',
        ],
        response,
        request,
    )

    response, request = test_edit_totp_error(
        host,
        "uid=4001595721&op=add&password=%s&secret=%s&secret_id=7777" % (totp, utils.encode_base64('wrong_secret')),
        "Totp check failed: password and pin do not match the secret",
    )
    check_junk_secret(
        3,
        4001595721,
        '1234567890123456',
        [
            'id: 123456',
            'secret: "abcdef9876543210"',
            'id: 7777',
            'secret: "wrong_secret"',
            'id: 1337',
            'secret: "7#3 1337 $3(R337"',
        ],
        response,
        request,
    )

    response, request = test_edit_totp_error(
        host,
        "uid=4001595721&op=replace&password=%s&secret=%s&secret_id=7777&old_secret_id=1177"
        % (totp, utils.encode_base64('wrong_secret')),
        "Totp check failed: password and pin do not match the secret",
    )
    check_junk_secret(
        3,
        4001595721,
        '1234567890123456',
        [
            'id: 123456',
            'secret: "abcdef9876543210"',
            'id: 7777',
            'secret: "wrong_secret"',
            'id: 1337',
            'secret: "7#3 1337 $3(R337"',
        ],
        response,
        request,
    )

    print('"EditTotp" fail (check if changes) test: passed.')

    # Nothing to delete
    # no password check, no junk
    response, request = test_edit_totp_error(host, "uid=71001&op=delete&secret_id=100500", "No such secret id")
    check_no_junk_secret(response, request)
    print('"EditTotp" fail (no pwd check) test: passed.')

    # replacing missing id, no password check, no junk
    response, request = test_edit_totp_error(
        host,
        "uid=71001&op=replace&secret_id=100500&password=%s&secret=%s&old_secret_id=100500"
        % (totp, utils.encode_base64(key)),
        "No such secret id",
    )
    check_no_junk_secret(response, request)
    print('"EditTotp" fail (replace missing secret) test: passed.')

    print('"EditTotp" all error tests: passed.')


def check(blackbox_host, keys_dir='/etc/fastcgi2/available/blackbox_keys'):
    global tool
    tool = TotpTool(keys_dir)

    test_create(blackbox_host)
    test_add(blackbox_host)
    test_delete(blackbox_host)
    test_replace(blackbox_host)
    test_errors(blackbox_host)
