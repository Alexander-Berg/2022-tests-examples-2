import asyncio
import random
import string
import typing
import uuid

from aiohttp import web

RESPONSE_SESSION_ID_XML_RESULT = (
    """
<?xml version="1.0" encoding="UTF-8"?>
<doc>
    <status>VALID</status>
    <auth>
        <secure>1</secure>
    </auth>
    <dbfield id="login">login</dbfield>
</doc>
""".strip()
)

RESPONSE_XML_RESULT = (
    """
<?xml version="1.0" encoding="UTF-8"?>
<doc>
    <status>INVALID</status>
</doc>
""".strip()
)

EATERS_DATA: typing.Dict = {
    '3:user:666': {
        'phones_attributes_102': '+79682777666',
        'emails_attributes_1': 'dddddd@ddd.ddd',
        'uid_value': '666',
        'display_name_name': 'Иван Говнов',
        'display_name_public_name': 'Иван Г.',
    },
    '3:user:333': {
        'phones_attributes_102': '+79682777450',
        'emails_attributes_1': 'cccccc@ccc.ccc',
        'uid_value': '333',
        'display_name_name': 'Козьма Прутков',
        'display_name_public_name': 'Козьма П.',
    },
    '3:user:111': {
        'phones_attributes_102': '+79999999999',
        'emails_attributes_1': 'dddddd@ddd.ddd',
        'uid_value': '111',
        'display_name_name': 'noname noname',
        'display_name_public_name': 'noname n.',
    },
    '3:user:555': {
        'phones_attributes_102': '+79682777000',
        'emails_attributes_1': 'test@test.ru',
        'uid_value': '555',
        'display_name_name': 'User Test',
        'display_name_public_name': 'User Test',
    },
}


def generate_eaters_data(user_data: typing.Dict) -> typing.Dict:
    return {
        'users': [
            {
                'aliases': {'10': 'phne-4pvm324n'},
                'dbfields': {'subscription.suid.669': ''},
                'have_hint': False,
                'have_password': False,
                'id': '4031979996',
                'karma': {'value': 0},
                'karma_status': {'value': 0},
                'login': '',
                'phones': [
                    {
                        'attributes': {
                            '102': user_data['phones_attributes_102'],
                            '107': '1',
                            '4': '1556681858',
                            '108': '0',
                        },
                        'id': '557f191e810c19729de860ea',
                    },
                ],
                'emails': [
                    {
                        'attributes': {
                            '1': user_data['emails_attributes_1'],
                            '3': '1556681858',
                        },
                        'id': '557f191e810c19729de860eb',
                    },
                ],
                'uid': {
                    'hosted': False,
                    'lite': False,
                    'value': user_data['uid_value'],
                },
                'display_name': {
                    'name': user_data['display_name_name'],
                    'public_name': user_data['display_name_public_name'],
                },
            },
        ],
    }


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self._tokens = {}
        self._session_ids = {}
        self._phones = set()
        self._logins = {}
        self._uids = {}
        self._client_mode = False
        self.router.add_get('/blackbox', self.handle_blackbox)
        self.router.add_get('/blackbox/', self.handle_blackbox)
        self.router.add_post('/blackbox', self.handle_blackbox)
        self.router.add_post('/blackbox/', self.handle_blackbox)
        self.router.add_post('/control', self.handle_control)
        self.router.add_post('/client_mode', self.handle_client_mode)

    async def handle_client_mode(self, request):
        request_data = await request.json()
        self._client_mode = request_data['value']
        return web.Response()

    async def handle_control(self, request):
        request_data = await request.json()
        data = {
            'method': request_data['method'],
            'status': request_data.get('status', 'VALID'),
            'uid': request_data.get(
                'uid', str(random.randint(0, 2 ** 32 - 2)),
            ),
            'login': request_data.get('login'),
            'is_staff': request_data.get('is_staff', False),
            'scope': request_data.get(
                'scope', 'yataxi:read yataxi:write yataxi:pay',
            ),
            'sleep': request_data.get('sleep'),
            'response_code': request_data.get('response_code', 200),
            'phone': request_data.get('phone'),
            'phones': request_data.get('phones', []),
        }
        if data['phone'] == 'random':
            for _ in range(100000):
                phone = '+7' + ''.join(
                    [random.choice(string.digits) for _ in range(10)],
                )
                if phone[2] != '9' and phone not in self._phones:
                    break
            else:
                raise RuntimeError('can not generate phone')
            self._phones.add(phone)
            data['phone'] = phone
        if request_data['method'] == 'oauth':
            token = request_data.get('token', uuid.uuid4().hex)
            data['token'] = token
            self._tokens[token] = data
        elif request_data['method'] == 'session_id':
            session_id = request_data.get('session_id', uuid.uuid4().hex)
            data['session_id'] = session_id
            self._session_ids[session_id] = data
        elif request_data['method'] == 'userinfo':
            self._logins[request_data['login']] = data
        self._uids[data['uid']] = data
        return web.json_response(data)

    async def handle_blackbox(self, request):
        params = {**request.query, **await request.post()}
        response_format = params.get('format')
        if response_format != 'json':
            return await self.handle_blackbox_xml_response(params)

        method = params.get('method')
        if self._client_mode:
            result = {
                'status': {'value': 'VALID'},
                'uid': {'value': '4294967295'},
                'login': 'user',
                'oauth': {'scope': 'yataxi:read yataxi:write yataxi:pay'},
                'phones': self._convert_phones('+79999999999', []),
                'dbfields': {'subscription.suid.669': '1'},
                'aliases': {'10': 'phne-edcsaypw'},
                'user_ticket': 'user_ticket',
            }
            if method in ('userinfo', 'user_ticket'):
                result = {'users': [result]}
            return web.json_response(result)
        if method == 'oauth' and 'oauth_token' in params:
            return await self._response(
                self._tokens.get(params['oauth_token']),
            )
        if method == 'sessionid' and 'sessionid' in params:
            return await self._response(
                self._session_ids.get(params['sessionid']),
            )
        if method == 'userinfo' and 'login' in params:
            return await self._response(
                self._logins.get(params['login'].split('@', 1)[0]),
            )
        if method == 'user_ticket' and 'user_ticket' in params:
            if params['user_ticket'] in EATERS_DATA:
                user_ticket: str = params['user_ticket']
                return web.json_response(
                    generate_eaters_data(EATERS_DATA[user_ticket]), status=200,
                )
            yandex_uid = None
            if 'uid' in params:
                yandex_uid = params['uid']
            else:
                splited_request = params['user_ticket'].split('_')
                if len(splited_request) == 3:
                    yandex_uid = splited_request[2]
            if yandex_uid is not None:
                return await self._response(
                    self._uids.get(yandex_uid), method='user_ticket',
                )
        return await self._response()

    async def handle_blackbox_xml_response(self, params):
        method = params.get('method')
        if method == 'sessionid' and 'sessionid' in params:
            return self._response_xml_session_id()
        return await self._response_xml()

    async def _response(self, data=None, method=None):
        if data is None:
            data = {'status': 'INVALID'}
        method = method or data.get('method')
        result = {
            'status': {'value': data['status']},
            'aliases': {'10': 'phne-edcsaypw'},
            'user_ticket': 'user_ticket',
        }
        if data.get('uid') is not None:
            result['uid'] = {'value': data['uid']}
            result['user_ticket'] += '_' + data['uid']
        if data.get('login') is not None:
            result['login'] = data['login']
        if data.get('scope') is not None:
            result['oauth'] = {'scope': data['scope']}
        if data.get('phone') is not None or data.get('phones'):
            result['phones'] = self._convert_phones(
                data['phone'], data['phones'],
            )
        if data.get('is_staff'):
            result['dbfields'] = {'subscription.suid.669': '1'}
        if data.get('sleep') is not None:
            await asyncio.sleep(data['sleep'])
        if method in ('userinfo', 'user_ticket'):
            result = {'users': [result]}
        return web.json_response(result, status=data.get('response_code', 200))

    def _response_xml_session_id(self):
        return web.Response(
            body=RESPONSE_SESSION_ID_XML_RESULT,
            status=200,
            content_type='application/xml',
        )

    def _response_xml(self):
        return web.Response(
            body=RESPONSE_XML_RESULT,
            status=200,
            content_type='application/xml',
        )

    @staticmethod
    def _convert_phones(phone, phones):
        res = []
        if phone is not None:
            res.append({'id': '0', 'attributes': {'107': '1', '102': phone}})
        for index, phone_ in enumerate(phones, 1):
            res.append({'id': str(index), 'attributes': {'102': phone_}})
        return res
