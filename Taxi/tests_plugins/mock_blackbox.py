import pytest


def _convert_phones(phones):
    res = []
    for index, phone in enumerate(phones):
        attrs = {}
        default = phone.startswith('*')
        if default:
            phone = phone[1:]
            attrs['107'] = '1'
        attrs['102'] = phone
        res.append({'id': str(index), 'attributes': attrs})
    return res


def _valid_token_info(uid, phones, scope, login, uber_id, issue_time):
    return {
        'uid': {'value': uid},
        'login': login,
        'status': {'value': 'VALID'},
        'oauth': {'scope': scope, 'issue_time': issue_time},
        'aliases': {'10': 'phonish', '16': uber_id},
        'phones': _convert_phones(phones),
    }


def _invalid_token_info():
    return {'status': {'value': 'INVALID', 'id': 5}, 'error': 'expired_token'}


class BlackboxContext:
    def __init__(self):
        self.tokens = {}
        self.sessionids = {}

    def set_token_info(
            self,
            token,
            uid,
            phones=['+71111111111'],
            scope='yataxi:read yataxi:write yataxi:pay',
            login='login',
            uber_id='uber_id',
            issue_time='2018-05-30 12:34:56',
    ):
        self.tokens[token] = _valid_token_info(
            uid, phones, scope, login, uber_id, issue_time,
        )

    def set_sessionid_info(
            self,
            sessionid,
            uid,
            phones=['+71111111111'],
            scope='yataxi:read yataxi:write yataxi:pay',
            login='login',
            uber_id='uber_id',
            issue_time='2018-05-30 12:34:56',
    ):
        self.sessionids[sessionid] = _valid_token_info(
            uid, phones, scope, login, uber_id, issue_time,
        )

    def set_invalid_token(self, token):
        self.tokens[token] = _invalid_token_info()


@pytest.fixture
def blackbox_service(mockserver):
    context = BlackboxContext()
    context.set_token_info('test_token', '123')

    def mock_blackbox_oauth(context, request):
        assert request.args.get('format') == 'json'
        assert request.args.get('dbfields') == 'subscription.suid.669'
        assert request.args.get('aliases') == '1,10,16'
        assert request.args.get('getphones') == 'bound'
        assert (
            request.args.get('phone_attributes') == '102,107,4'
            or request.args.get('phone_attributes') == '102,107'
        )
        token = request.args.get('oauth_token')
        if token not in context.tokens:
            raise RuntimeError('Unknown token %r' % token)
        return context.tokens[token]

    def mock_blackbox_sessionid(context, request):
        assert request.args.get('format') == 'json'
        assert request.args.get('dbfields') == 'subscription.suid.669'
        assert request.args.get('getphones') == 'bound'
        assert request.args.get('phone_attributes') == '102,107'
        sessionid = request.args.get('sessionid')
        if sessionid not in context.sessionids:
            raise RuntimeError('unknown sessionid %r' % sessionid)
        return context.sessionids[sessionid]

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        method = request.args.get('method')
        if method == 'oauth':
            return mock_blackbox_oauth(context, request)
        elif method == 'sessionid':
            return mock_blackbox_sessionid(context, request)
        raise RuntimeError('Unsupported blackbox method %r' % (method,))

    return context
