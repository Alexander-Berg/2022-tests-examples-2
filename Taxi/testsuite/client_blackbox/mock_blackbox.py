import dataclasses
import datetime
import json
import typing

import pytest


_TOKEN_MARKER = 'passport_token'
_TEAM_TOKEN_MARKER = 'passport_team_token'
_SESSION_MARKER = 'passport_session'
_TEAM_SESSION_MARKER = 'passport_team_session'

_RAISE_500_CRED = 'raise_500'


@dataclasses.dataclass(frozen=True)
class Phone:
    number: str
    default: bool
    confirmation_time: typing.Optional[datetime.datetime]
    secured: bool
    is_bank: bool


def make_phone(
        phone,
        default=False,
        confirmation_time=None,
        secured=False,
        is_bank=False,
):
    return Phone(
        number=phone,
        default=default,
        confirmation_time=confirmation_time,
        secured=secured,
        is_bank=is_bank,
    )


@dataclasses.dataclass(frozen=True)
class Email:
    address: str
    confirmation_time: typing.Optional[datetime.datetime]


def pytest_configure(config):
    config.addinivalue_line('markers', f'{_TOKEN_MARKER}: passport token')
    config.addinivalue_line(
        'markers', f'{_TEAM_TOKEN_MARKER}: passport team token',
    )
    config.addinivalue_line('markers', f'{_SESSION_MARKER}: passport session')
    config.addinivalue_line(
        'markers', f'{_TEAM_SESSION_MARKER}: passport team session',
    )


def make_email(address, confirmation_time=None):
    return Email(address=address, confirmation_time=confirmation_time)


def _convert_phones(phones):
    res = []
    for index, phone in enumerate(phones):
        attrs = {}
        if phone.default:
            attrs['107'] = '1'
        if phone.confirmation_time:
            attrs['4'] = str(int(phone.confirmation_time.timestamp()))
        if phone.secured:
            attrs['108'] = '1'
        if phone.is_bank:
            attrs['109'] = '1'
        attrs['102'] = phone.number
        res.append({'id': str(index), 'attributes': attrs})
    return res


def _convert_emails(emails):
    res = []
    for index, email in enumerate(emails):
        attrs = {}
        if email.confirmation_time:
            attrs['3'] = str(int(email.confirmation_time.timestamp()))
        attrs['1'] = email.address
        res.append({'id': str(index), 'attributes': attrs})
    return res


def _valid_token_info(
        uid,
        phones,
        emails,
        scope,
        login,
        login_id,
        uber_id,
        issue_time,
        user_ticket,
        has_plus_cashback,
        account_type='phonish',
        account_2fa_on=None,
        account_sms_2fa_on=None,
        client_id='',
        staff_login='',
        status='VALID',
):
    data = {
        'uid': {'value': uid},
        'login': login,
        'login_id': login_id,
        'status': {'value': status},
        'oauth': {
            'scope': scope,
            'issue_time': issue_time,
            'client_id': client_id,
        },
        'aliases': {'16': uber_id, '13': staff_login},
        'phones': _convert_phones(phones),
        'emails': _convert_emails(emails),
        'user_ticket': user_ticket,
        'attributes': {
            '200': account_sms_2fa_on,
            '1003': account_2fa_on,
            '1025': has_plus_cashback,
        },
    }
    if account_type == 'phonish':
        data['aliases']['10'] = 'phonish'
    elif account_type == 'narod':
        data['aliases']['4'] = 'subscription.login.4'
    elif account_type == 'portal':
        data['aliases']['1'] = 'accounts.login'
    elif account_type == 'neophonish':
        data['aliases']['21'] = 'abba'
    elif account_type == 'lite':
        data['aliases']['5'] = 'subscription.login.33'
    elif account_type == 'social':
        data['aliases']['6'] = 'subscription.login.58'
    elif account_type == 'pdd':
        data['aliases']['7'] = 'subscription.login.2'
    else:
        assert False, f'Bad account type {account_type}'
    return data


def _invalid_token_info():
    return {'status': {'value': 'INVALID', 'id': 5}, 'error': 'expired_token'}


def _valid_user_ticket_info(uid, login):
    return {'users': [{'uid': {'value': uid}, 'login': login}]}


def _invalid_user_ticket_info():
    return {
        'exception': {'value': 'ACCESS_DENIED', 'id': 1},
        'error': 'ticket not found',
    }


def _invalid_user_info():
    return {
        'exception': {'value': 'ACCESS_DENIED', 'id': 1},
        'error': 'email not found',
    }


class BlackboxContext:
    def __init__(self):
        self.tokens = {}
        self.sessionids = {}
        self.user_tickets = {}
        self.user_info = {}
        self.strict_phone_attributes = False

    def set_token_info(
            self,
            token,
            uid,
            phones=None,
            emails=None,
            scope='yataxi:read yataxi:write yataxi:pay',
            login='login',
            login_id='login_id',
            uber_id='uber_id',
            issue_time='2018-05-30 12:34:56',
            user_ticket='test_user_ticket',
            has_plus_cashback=None,
            account_type='phonish',
            account_2fa_on=None,
            account_sms_2fa_on=None,
            strict_phone_attributes=False,
            client_id='',
            staff_login='',
    ):
        if phones is None:
            phones = [make_phone('+71111111111')]
        if emails is None:
            emails = []
        self.tokens[token] = _valid_token_info(
            uid,
            phones,
            emails,
            scope,
            login,
            login_id,
            uber_id,
            issue_time,
            user_ticket,
            has_plus_cashback,
            account_type,
            account_2fa_on,
            account_sms_2fa_on,
            client_id,
            staff_login,
        )
        self.strict_phone_attributes = strict_phone_attributes

    def set_sessionid_info(
            self,
            sessionid,
            uid,
            phones=None,
            emails=None,
            scope='yataxi:read yataxi:write yataxi:pay',
            login='login',
            login_id='login_id',
            uber_id='uber_id',
            issue_time='2018-05-30 12:34:56',
            user_ticket='test_user_ticket',
            has_plus_cashback=None,
            account_type='phonish',
            account_2fa_on=None,
            account_sms_2fa_on=None,
            strict_phone_attributes=False,
            staff_login='',
            status='VALID',
    ):
        if phones is None:
            phones = [make_phone('+71111111111')]
        if emails is None:
            emails = []
        self.sessionids[sessionid] = _valid_token_info(
            uid,
            phones,
            emails,
            scope,
            login,
            login_id,
            uber_id,
            issue_time,
            user_ticket,
            has_plus_cashback,
            account_type,
            account_2fa_on,
            account_sms_2fa_on,
            staff_login=staff_login,
            status=status,
        )
        self.strict_phone_attributes = strict_phone_attributes

    def set_invalid_token(self, token):
        self.tokens[token] = _invalid_token_info()

    def set_user_ticket_info(self, user_ticket, uid, login):
        self.user_tickets[user_ticket] = _valid_user_ticket_info(uid, login)

    def set_user_info(self, uid, login):
        self.user_info[login] = _valid_user_ticket_info(uid, login)


@pytest.fixture(name='blackbox_service')
def _blackbox_service(mockserver, request):
    context = BlackboxContext()
    team_context = BlackboxContext()
    context.set_token_info('test_token', '123')

    def _get_mock_info(markers, key):
        for marker in markers:
            data = marker.kwargs.get(key)
            if data:
                info = {
                    'phones': [make_phone('+71111111111')],
                    'emails': [],
                    'scope': 'yataxi:read yataxi:write yataxi:pay',
                    'login': 'login',
                    'login_id': 'login_id',
                    'uber_id': 'uber_id',
                    'issue_time': '2018-05-30 12:34:56',
                    'user_ticket': 'test_user_ticket',
                    'has_plus_cashback': None,
                    'account_type': 'phonish',
                    'account_2fa_on': None,
                    'account_sms_2fa_on': None,
                }
                info.update(data)
                return _valid_token_info(**info)
        return None

    def _get_mock_session(ctx, sessionid):
        if ctx is context:
            mrk_name = _SESSION_MARKER
        else:
            mrk_name = _TEAM_SESSION_MARKER
        markers = request.node.iter_markers(mrk_name)
        return _get_mock_info(markers, sessionid)

    def _get_mock_token(ctx, token):
        if ctx is context:
            mrk_name = _TOKEN_MARKER
        else:
            mrk_name = _TEAM_TOKEN_MARKER
        markers = request.node.iter_markers(mrk_name)
        return _get_mock_info(markers, token)

    def _remove_phones(session):
        session = dict(session)
        del session['phones']
        return session

    # removes all phone attributes that are not in requested attributes
    def _remove_extra_phone_attributes(session, requested_attributes):
        session = dict(session)
        for phone in session['phones']:
            if 'attributes' in phone:
                phone['attributes'] = {
                    k: v
                    for k, v in phone['attributes'].items()
                    if k in requested_attributes
                }
        return session

    def mock_blackbox_oauth(context, params):
        assert params.get('format') == 'json'
        assert params.get('dbfields') == 'subscription.suid.669'
        assert params.get('aliases') == 'all'
        assert params.get('get_user_ticket') == 'yes'
        token = params.get('oauth_token')
        if token == _RAISE_500_CRED:
            return mockserver.make_response('Invalid', status=500)

        info = context.tokens.get(token)
        if not info:
            info = _get_mock_token(context, token)
        if not info:
            return mockserver.make_response(
                json.dumps(_invalid_token_info()), status=200,
            )
        if 'phone_attributes' in params:
            assert params.get('getphones') == 'bound'
            assert params.get('phone_attributes') in [
                '102,107,4,108',
                '102,107',
                '107,4,108',
                '107,4',
                '107,4,109',
                '102,109',
                '4',
            ]
            if context.strict_phone_attributes:
                return _remove_extra_phone_attributes(
                    info, set(params.get('phone_attributes').split(',')),
                )
            return info
        return _remove_phones(info)

    def mock_blackbox_sessionid(context, params):
        assert params.get('format') == 'json'
        assert params.get('dbfields') == 'subscription.suid.669'
        assert params.get('get_user_ticket') == 'yes'
        sessionid = params.get('sessionid')
        if sessionid == _RAISE_500_CRED:
            return mockserver.make_response('Invalid', status=500)

        session = context.sessionids.get(sessionid)
        if not session:
            session = _get_mock_session(context, sessionid)
        if not session:
            return mockserver.make_response(
                json.dumps(_invalid_token_info()), status=200,
            )

        if 'phone_attributes' in params:
            assert params.get('getphones') == 'bound'
            assert params.get('phone_attributes') in [
                '102,107,4,108',
                '107',
                '108',
                '107,4,108',
                '107,4,108,109',
                '102,109',
            ]
            if context.strict_phone_attributes:
                return _remove_extra_phone_attributes(
                    session, set(params.get('phone_attributes').split(',')),
                )
            return session
        return _remove_phones(session)

    def mock_blackbox_user_ticket(context, params):
        assert params.get('format') == 'json'
        user_ticket = params.get('user_ticket')
        if user_ticket not in context.user_tickets:
            return _invalid_user_ticket_info()
        return context.user_tickets[user_ticket]

    def mock_blackbox_userinfo(context, params):
        assert params.get('format') == 'json'
        assert 'userip' in params
        user_email = params.get('login')
        if user_email not in context.user_info:
            return _invalid_user_info()
        return context.user_info[user_email]

    def _do_mock_blackbox(context, request):
        params = {**request.args, **request.form}
        method = params.get('method')
        if method == 'oauth':
            return mock_blackbox_oauth(context, params)
        if method == 'sessionid':
            return mock_blackbox_sessionid(context, params)
        if method == 'user_ticket':
            return mock_blackbox_user_ticket(context, params)
        if method == 'userinfo':
            return mock_blackbox_userinfo(context, params)
        raise RuntimeError('Unsupported blackbox method %r' % (method,))

    @mockserver.json_handler('/blackbox')
    def _mock_blackbox(request):
        return _do_mock_blackbox(context, request)

    @mockserver.json_handler('/blackbox-team')
    def _mock_blackbox_team(request):
        return _do_mock_blackbox(team_context, request)

    return context
