import inspect

import pytest

from taxi import config
from taxi.conf import settings
from taxi.external import passport


@pytest.mark.parametrize(
    'replace,phone,uid,text,kwargs,sender,route,from_uid,identity', [
    # By default, only phone and text is accepted
    ('123', '+79223334444', 'abc', 'hello, world', {}, 'Yandex.Taxi',
     None, None, None),
    # Unicode is supported
    ('1', '+79223334444', 'barbaz', u'\u041e\u043f!', {}, 'Yandex.Taxi',
     None, None, None),
    # Phone number is not validated
    ('123', 'invalid number', 'uid', 'hello, world', {}, 'Yandex.Taxi',
     None, None, None),
    # Additional parameters: route and sender
    ('123', '+79223334444', 'uid2', 'hello, world',
     {'route': 'critical', 'sender': 'taxi'}, 'taxi', 'critical', None, None),
    # Additional parameters: from_uid
    ('123', '+79223334444', 'abc', 'hello, world',
     {'from_uid': '123456'}, 'Yandex.Taxi', None, '123456', None),
    # Additional parameters: identity
    ('123', '+79223334444', 'abc', 'hello, world',
     {'identity': None}, 'Yandex.Taxi', None, None, None),
    ('123', '+79223334444', 'abc', 'hello, world',
     {'identity': 'taxi_manual'}, 'Yandex.Taxi', None, None, 'taxi_manual'),
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.config(
    PASSPORT_SMS_DEFAULT_ROUTE='taxi-test',
    PASSPORT_BASE_SMS_URL='http://passport'
)
@pytest.inline_callbacks
def test_send_sms_ok(
        replace, phone, uid, text, kwargs, sender, route, from_uid, identity,
        mock, asyncenv, load, areq_request, monkeypatch):
    @areq_request
    def requests_request(method, url, **kwargs):
        body = load('sendsms_ok.xml').replace('REPLACE', replace)
        return areq_request.response(200, body=body)

    if route is None:
        route = yield config.PASSPORT_SMS_DEFAULT_ROUTE.get()

    # Send message to uid
    message_id = yield passport.send_sms_to_uid(
        uid, text, 'test', log_extra=None, **kwargs
    )
    assert message_id == replace

    call = requests_request.call
    assert call['args'][0].upper() == 'GET'
    assert call['args'][1] == 'http://passport/sendsms'
    assert call['kwargs'].get('exponential_backoff')
    assert call['kwargs'].get('timeout') == settings.PASSPORT_TIMEOUT
    assert call['kwargs'].get('params', {}).pop('route', None) == route
    assert call['kwargs'].get('params', {}).pop('from_uid', None) == from_uid
    assert call['kwargs'].get('params', {}).pop('identity', None) == identity
    assert call['kwargs'].get('params') == {
        'sender': sender,
        'text': text,
        'uid': uid,
        'utf8': '1',
    }

    assert not requests_request.calls


@pytest.mark.parametrize('code,body_or_filename,replace,exception', [
    # 403, DONTKNOWYOU or NORIGHTS
    (200, 'sendsms_error.xml', 'DONTKNOWYOU', passport.PermissionDeniedError),
    (200, 'sendsms_error.xml', 'NORIGHTS', passport.PermissionDeniedError),
    (403, 'sendsms_ok.xml', '111', passport.PermissionDeniedError),

    # BADFROMUID, BADPHONE, NOCURRENT, NOPHONE, NOROUTE, NOSENDER,
    # NOTEXT, NOUID
    (200, 'sendsms_error.xml', 'BADFROMUID', passport.InvalidRequestError),
    (200, 'sendsms_error.xml', 'BADPHONE', passport.InvalidRequestError),
    (200, 'sendsms_error.xml', 'NOCURRENT', passport.InvalidRequestError),
    (200, 'sendsms_error.xml', 'NOPHONE', passport.InvalidRequestError),
    (200, 'sendsms_error.xml', 'NOROUTE', passport.InvalidRequestError),
    (200, 'sendsms_error.xml', 'NOSENDER', passport.InvalidRequestError),
    (200, 'sendsms_error.xml', 'NOTEXT', passport.InvalidRequestError),
    (200, 'sendsms_error.xml', 'NOUID', passport.InvalidRequestError),

    # LIMITEXCEEDED, UIDLIMITEXCEEDED
    (200, 'sendsms_error.xml', 'LIMITEXCEEDED',
     passport.SMSLimitExceededError),
    (200, 'sendsms_error.xml', 'UIDLIMITEXCEEDED',
     passport.SMSLimitExceededError),

    # PERMANENTBLOCK, PHONEBLOCKED
    (200, 'sendsms_error.xml', 'PERMANENTBLOCK',
     passport.SMSReceipientBlockedError),
    (200, 'sendsms_error.xml', 'PHONEBLOCKED',
     passport.SMSReceipientBlockedError),

    # 5XX, INTERROR
    (500, 'sendsms_ok.xml', '123', passport.InternalError),
    (599, 'sendsms_ok.xml', '123', passport.InternalError),
    (200, 'sendsms_error.xml', 'INTERROR', passport.InternalError),

    # Body in unknown format, code except 200, 403, 5XX
    (200, '<bla><dang>2</dang></bla>', None, passport.InvalidResponseError),
    (400, 'sendsms_ok.xml', '123', passport.InvalidResponseError),
    (404, 'sendsms_ok.xml', '123', passport.InvalidResponseError),
])
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_send_sms_error(
        code, body_or_filename, replace, exception,
        mock, asyncenv, areq_request, load):
    @areq_request
    def requests_request(method, url, **kwargs):
        if body_or_filename.endswith('.xml'):
            body = load(body_or_filename).replace('REPLACE', replace)
        else:
            body = body_or_filename
        return areq_request.response(code, body=body)

    with pytest.raises(exception):
        yield passport.send_sms_to_uid(uid='12345', text='some text',
                                       tvm_src_service='test')


@pytest.mark.parametrize('uid,sender,code,filename,answer', [
    # Uid exists, default sender, only confirmed phones are displayed
    ('123', None, 200, 'userphones_ok.xml', [
        {'phone': '+79223335555', 'default': True},
        {'phone': '+79223336666', 'blocked': True},
        {'phone': '+79223337777', 'blocked': True},
        {'phone': '+79223338888'},
    ]),
    # Uid exists, empty answer
    ('123', 'taxi', 200, 'userphones_empty.xml', []),

    # 5XX, INTERROR
    ('123', 'taxi', 500, 'userphones_empty.xml', passport.InternalError),
    ('123', 'taxi', 599, 'userphones_empty.xml', passport.InternalError),
    ('INTERROR', None, 200, 'userphones_error.xml', passport.InternalError),

    # 403, DONTKNOWYOU, NORIGHTS
    ('123', 'taxi', 403, 'userphones_empty.xml',
     passport.PermissionDeniedError),
    ('DONTKNOWYOU', None, 200, 'userphones_error.xml',
     passport.PermissionDeniedError),
    ('NORIGHTS', None, 200, 'userphones_error.xml',
     passport.PermissionDeniedError),

    # Unknown format of response
    ('123', None, 200, '<a><b>text</b></a>', passport.InvalidResponseError),
    # Any code except 200, 403 and 5XX
    ('123', None, 400, 'userphones_ok.xml', passport.InvalidResponseError),

    # Any other error is interpreted as request error
    ('NOUID', None, 200, 'userphones_error.xml',
     passport.InvalidRequestError),
    ('UNKNOWN', None, 200, 'userphones_error.xml',
     passport.InvalidRequestError),
])
@pytest.mark.config(
    PASSPORT_BASE_SMS_URL='http://passport'
)
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_get_uid_phones(
        uid, sender, code, filename, answer,
        mock, asyncenv, load, areq_request, monkeypatch):
    @areq_request
    def requests_request(method, url, **kwargs):
        if filename.endswith('.xml'):
            body = load(filename).replace('REPLACE', uid)
        else:
            body = filename
        return areq_request.response(code, body=body)

    # Some error occured
    if inspect.isclass(answer) and issubclass(answer, Exception):
        with pytest.raises(answer):
            yield passport.get_uid_phones(uid, 'test', sender, log_extra=None)
    else:
        if sender is None:
            response = yield passport.get_uid_phones(
                uid, 'test', log_extra=None)
        else:
            response = yield passport.get_uid_phones(
                uid, 'test', sender=sender, log_extra=None
            )
        assert answer == response

        call = requests_request.call
        assert call['args'][0].upper() == 'GET'
        assert call['args'][1] == 'http://passport/userphones'
        assert call['kwargs'].get('exponential_backoff')
        assert call['kwargs'].get('timeout') == settings.PASSPORT_TIMEOUT
        assert call['kwargs'].get('params') == {
            'sender': sender or 'Yandex.Taxi',
            'uid': uid,
        }


@pytest.inline_callbacks
def test_get_info_by_token_ok(mock, asyncenv, areq_request, load):

    @areq_request
    def requests_request(method, url, **kwargs):
        return areq_request.response(200, body=load('bb_ok.json'))

    info = yield passport.get_info_by_token(
        'token1', '1.2.3.4', 'test', log_extra=None
    )
    assert info == {
        'uid': '3000062912',
        'login': 'test',
        'is_staff': False,
        'scopes': [
            'direct:api-1month',
            'metrika:write',
            'direct:api-3month',
            'metrika:read',
            'fotki:write',
        ]
    }
