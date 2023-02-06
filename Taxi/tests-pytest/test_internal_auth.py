from twisted.internet import defer
import pytest

from taxi.core import async
from taxi.internal import auth


@pytest.inline_callbacks
def test_get_token_info(mock):
    @mock('taxi.external.passport.get_info_by_token')
    def get_info_by_token(token, user_ip, tvm_src_service, log_extra=None):
        response = {
            'uid': 'uid1', 'login': 'test1', 'is_staff': False,
            'scopes': ['scope1', 'scope2'],
        }
        return async.call(
            lambda: defer.succeed(response), lambda: response
        )

    token = yield auth.get_token_info('token1', '1.2.3.4', 'test', log_extra=None)

    assert token.yandex_uid == 'uid1'
    assert token.login == 'test1'
    assert not token.is_staff
    assert token.scopes == ['scope1', 'scope2']
    assert token.has_scope('scope1')
    assert not token.has_scope('unknown')
    assert token.has_scopes(['scope1', 'scope2'])
    assert not token.has_scopes(['scope1', 'scope2', 'scope3'])


@pytest.mark.parametrize('scopes,required_scopes,status', [
    (['foo', 'bar'], [], True),
    (['foo', 'bar'], ['foo'], True),
    (['foo', 'bar'], ['foo', 'bar'], True),
    (['foo', 'bar'], ['maurice'], False),
    (['foo', 'bar'], ['bar', 'maurice'], False),
    ([], ['foo'], False),
    ([], ['foo', 'bar'], False),
])
@pytest.inline_callbacks
def test_get_token_info_scope_check(mock, scopes, required_scopes, status):
    @mock('taxi.external.passport.get_info_by_token')
    @async.inline_callbacks
    def get_info_by_token(token, user_ip, tvm_src_service, log_extra=None):
        yield
        async.return_value({
            'uid': 'uid1', 'login': 'test1', 'is_staff': False,
            'scopes': scopes,
        })

    if status:
        token = yield auth.get_token_info(
            'token1', '1.2.3.4', 'test', required_scopes, log_extra=None)
        assert token.yandex_uid == 'uid1'
        assert token.login == 'test1'
        assert token.scopes == scopes
    else:
        with pytest.raises(auth.InvalidTokenError):
            yield auth.get_token_info(
                'token1', '1.2.3.4', 'test', required_scopes, log_extra=None)


@pytest.inline_callbacks
def test_get_session_info(patch):
    @patch('taxi.external.passport.get_info_by_sid')
    def get_info_by_sid(sessionid, user_ip, tvm_src_service, origin=None,
                        log_extra=None):
        response = {
            'uid': 'uid1', 'login': 'test1', 'is_staff': False,
        }
        return async.call(
            lambda: defer.succeed(response), lambda: response
        )

    token = yield auth.get_session_info('token1', '1.2.3.4', 'test',
                                        log_extra=None)

    assert token.yandex_uid == 'uid1'
    assert token.login == 'test1'
    assert not token.is_staff


@pytest.mark.parametrize('session_id,result', [
    (None, False),
    ('noauth:1479213979', False),
    ('3:1479229211:....', True),
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_is_session_authorized(session_id, result):
    assert auth.is_session_authorized(session_id) == result
