# noqa: E501 pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name, duplicate-code
import json

import aiohttp
import aiohttp.web
import pytest

import callcenter_operators.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from test_callcenter_operators import params

pytest_plugins = ['callcenter_operators.generated.service.pytest_plugins']
AC_DEFAULT_PROVIDER = 'yandex'


def _find_param_in_url(url, param):
    start = url.find(param) + len(param)
    if start == len(param) - 1:
        return None
    finish = url.find('&', start)
    if finish == -1:
        finish = len(url)
    found_param = url[start:finish]
    return found_param


@pytest.fixture
def mock_connect_create_user(mock_connect):
    @mock_connect('/v6/users/')
    def _request(request, *args, **kwargs):
        name = request.json.get('name')
        if name:
            middle = name.get('middle')
            if middle:
                assert middle.startswith('middlename')
        return aiohttp.web.json_response(
            {'id': 123456789, 'gender': None, 'nickname': 'test_answer'},
            status=201,
        )

    return _request


@pytest.fixture
def mock_connect_change_user_info(mock_connect):
    uids = ['uid2', 'uid3', 'uid6', 'uid7', 'uid1']
    for uid in uids:

        @mock_connect(f'/v6/users/{uid}/')
        def _request(*args, **kwargs):
            return aiohttp.web.json_response()

    # return mock for uid1
    return _request


@pytest.fixture
def mock_passport(mockserver):
    class Context:
        @staticmethod
        @mockserver.json_handler('/blackbox', prefix=True)
        async def handle_urls(request, *args, **kwargs):
            login = _find_param_in_url(request.url, 'login=')
            if login is None:
                request_uid = _find_param_in_url(request.url, 'uid=')
                if request_uid in params.NEOPHONISH_UIDS:
                    body = {'users': [{'uid': {'value': request_uid}}]}
                else:
                    body = {'users': [{}]}
                return aiohttp.web.Response(text=json.dumps(body))
            if login not in params.PASSPORT_MAPPING:
                body = {'users': [{'login': {'value': login}}]}
                return aiohttp.web.Response(text=json.dumps(body))
            uid = params.PASSPORT_MAPPING[login]
            body = {
                'users': [{'login': {'value': login}, 'uid': {'value': uid}}],
            }
            return aiohttp.web.Response(text=json.dumps(body))

    return Context()


@pytest.fixture
def mock_access_control_users(mockserver):
    class Context:
        user_groups = {
            'uid1': {
                'operators',
                'account_managers',
                'support_operators',
                'group_that_not_in_cc',
            },
            'uid2': {'g1', 'g2', 'g3'},
            'uid6': {'group_to_delete'},
            'uid_to_delete': {},
        }

        @staticmethod
        def reset_user_groups():
            Context.user_groups = {
                'uid1': {
                    'operators',
                    'account_managers',
                    'support_operators',
                    'group_that_not_in_cc',
                },
                'uid2': {'g1', 'g2', 'g3'},
                'uid6': {'group_to_delete'},
                'uid_to_delete': {},
            }

        @staticmethod
        @mockserver.json_handler('/access-control/v1/admin/users/bulk-create/')
        async def handle_create(request, *args, **kwargs):
            request_users = request.json['users']
            created_users = []
            existing_users = []
            for user in request_users:
                if user['provider_user_id'] not in Context.user_groups.keys():
                    Context.user_groups[user['provider_user_id']] = set()
                    created_users.append(user['provider_user_id'])
                else:
                    existing_users.append(user['provider_user_id'])
            return {
                'created_users': [
                    {'provider': AC_DEFAULT_PROVIDER, 'provider_user_id': uid}
                    for uid in created_users
                ],
                'existing_users': [
                    {'provider': AC_DEFAULT_PROVIDER, 'provider_user_id': uid}
                    for uid in existing_users
                ],
                'invalid_users': [],
            }

        @staticmethod
        @mockserver.json_handler('/access-control/v1/admin/users/bulk-delete/')
        async def handle_delete(request, *args, **kwargs):
            users = request.json['users']
            deleted_users = []
            for user in users:
                if Context.user_groups.pop(user['provider_user_id'], False):
                    deleted_users.append(user)
            return {'deleted_users': deleted_users, 'errors': []}

        @staticmethod
        @mockserver.json_handler(
            '/access-control/v1/admin/users/bulk-add-to-system/',
        )
        async def handle_add(request, *args, **kwargs):
            request_users = request.json['users']
            request_groups = request.json['groups']
            for user in request_users:
                Context.user_groups[user['provider_user_id']].update(
                    set(request_groups),
                )
            return {
                'invalid_users': [],
                'non_existing_users': [],
                'non_existing_groups': [],
            }

        @staticmethod
        @mockserver.json_handler(
            '/access-control/v1/admin/groups/users/bulk-detach/',
        )
        async def handle_detach(request, *args, **kwargs):
            request_users = request.json['users']
            for users_groups_link in request_users:
                gslug = users_groups_link['group_slug']
                uid = users_groups_link['user']['provider_user_id']
                Context.user_groups[uid].discard(gslug)
            return {
                'detached_users': [
                    {
                        'user': users_groups_link['user'],
                        'group_slug': users_groups_link['group_slug'],
                    }
                    for users_groups_link in request_users
                ],
            }

        @staticmethod
        @mockserver.json_handler(
            '/access-control/v1/admin/groups/users/retrieve/',
        )
        async def handle_retrieve(request, *args, **kwargs):
            uids = request.json['filters']['provider_user_ids']
            return {
                'users': [
                    {
                        'provider': 'yandex',
                        'provider_user_id': uid,
                        'groups': [
                            {
                                'id': 101,
                                'name': group,
                                'slug': group,
                                'system': 'call_center',
                            }
                            for group in groups
                        ],
                    }
                    for (uid, groups) in Context.user_groups.items()
                    if uid in uids
                ],
            }

    return Context()


@pytest.fixture
def mock_set_status_cc_queues(mock_callcenter_queues):
    class Context:
        @staticmethod
        @mock_callcenter_queues('/v2/sip_user/state')
        async def handle_urls(request, *args, **kwargs):
            if request.method == 'GET':
                raise NotImplementedError
            req = request.json
            return req

    return Context()


@pytest.fixture(autouse=True)
def mock_cc_reg_reg_handler(mock_callcenter_reg):
    class Context:
        @staticmethod
        @mock_callcenter_reg('/v1/reg_groups')
        async def handle_urls(request, *args, **kwargs):
            return {
                'reg_groups': [
                    {
                        'group_name': 'ru',
                        'regs': ['reg1', 'reg2'],
                        'reg_domain': 'yandex.ru',
                    },
                ],
            }

    return Context()


@pytest.fixture
def mock_telephony_api_empty(mockserver):
    class Context:
        @staticmethod
        @mockserver.json_handler('/yandex-tel/', prefix=True)
        async def handle_urls(request, *args, **kwargs):
            return {
                'PARAM': {'REQ': ''},
                'DATA': '',
                'TYPE': 'REPLY',
                'STATUSCODE': 200,
                'STATUSMSG': 'DONE',
                'STATUSDESC': None,
                'STATUS': 'TRUE',
            }

    return Context()


@pytest.fixture
def mock_telephony_api_exception(mockserver):
    class Context:
        @staticmethod
        @mockserver.json_handler('/yandex-tel/', prefix=True)
        async def handle_urls(request, *args, **kwargs):
            return {
                'DATA': False,
                'TYPE': 'REPLY',
                'STATUSCODE': 500,
                'STATUSMSG': 'ERROR',
                'STATUSDESC': None,
                'STATUS': 'TRUE',
            }

    return Context()


@pytest.fixture
def mock_telephony_api(mockserver):
    class Context:
        @staticmethod
        @mockserver.json_handler('/yandex-tel/', prefix=True)
        async def handle_urls(request, *args, **kwargs):
            return {
                'PARAM': {
                    'REQ': {
                        'USERTYPE': 50,
                        'USERNAME': 'keke2',
                        'FIRSTNAME': 'f1',
                        'LASTNAME': 'l1',
                        'FIRSTNAMEENG': 'fe1',
                        'LASTNAMEENG': 'le1',
                        'EMAIL': 'a@a.aa',
                        'WORKPHONE': '1234567891',
                        'ISTECH': 1,
                        'ISROBOT': 0,
                        'ISACTIVE': 1,
                        'REALM': 'taxi.yandex.ru',
                    },
                },
                'DATA': True,
                'TYPE': 'REPLY',
                'STATUSCODE': 200,
                'STATUSMSG': 'OK',
                'STATUSDESC': None,
                'STATUS': 'TRUE',
            }

    return Context()


@pytest.fixture(autouse=True)
def mock_mvp_tel_handlers(mockserver):
    class Context:
        @staticmethod
        @mockserver.json_handler(
            '/yandex-tel/mod.cipt-call-center/api/callcenter/MVP/',
            prefix=True,
        )
        async def mvp_handlers(request, *args, **kwargs):
            return {**params.BASE_TEL_RESPONSE, 'DATA': False, 'STATUSMSG': ''}

    return Context()


@pytest.fixture
def mock_telephony_api_full(mockserver):
    # Online on test1 queue
    class Context:
        @staticmethod
        @mockserver.json_handler('/yandex-tel/', prefix=True)
        def tel_handle(request):
            if 'show/work_phone' in request.path_qs.lower():
                return {
                    **params.BASE_TEL_RESPONSE,
                    'DATA': {},
                    'STATUSMSG': '',
                }
            if 'show' in request.path_qs.lower():
                return {
                    **params.BASE_TEL_RESPONSE,
                    'STATUSMSG': 'SUCCESS',
                    'DATA': {
                        'CALLCENTERID': 'cc1',
                        'QUEUES': {
                            'test1': {
                                'STATUS': 1,
                                'VENDPAUSED': '1',
                                'PRIOR': 1,
                                'CURPRIOR': '1',
                            },
                            'test2': {
                                'STATUS': 0,
                                'VENDPAUSED': '0',
                                'PRIOR': 1,
                                'CURPRIOR': '1',
                            },
                        },
                    },
                }
            if 'user/_create/process' in request.path_qs.lower():
                return {
                    **params.BASE_TEL_RESPONSE,
                    'DATA': False,
                    'STATUSMSG': '',
                }
            if '/delete' in request.path_qs.lower():
                return {
                    **params.BASE_TEL_RESPONSE,
                    'DATA': False,
                    'STATUSMSG': '',
                }
            if 'mvp' in request.path_qs.lower():
                return {
                    **params.BASE_TEL_RESPONSE,
                    'DATA': False,
                    'STATUSMSG': '',
                }
            raise NotImplementedError

    return Context()


@pytest.fixture
def mock_save_status(mock_callcenter_stats, mock_callcenter_reg):
    class Context:
        @staticmethod
        @mock_callcenter_stats('/operators/save_status')
        async def handle_urls(*args, **kwargs):
            return aiohttp.web.Response(status=200)

        @staticmethod
        @mock_callcenter_reg('/v1/sip_user/status')
        async def save_status_cc_reg(*args, **kwargs):
            return {}

    return Context()


@pytest.fixture
def mock_save_queues(mock_callcenter_queues):
    class Context:
        @staticmethod
        @mock_callcenter_queues('/v1/sip_user/queues')
        async def handle_urls(*args, **kwargs):
            return aiohttp.web.Response(status=200)

    return Context()


@pytest.fixture
def mock_operators_status(mock_callcenter_stats):
    class Context:
        @staticmethod
        @mock_callcenter_stats('/v2/operators/status')
        async def handle_urls(request, *args, **kwargs):
            body = {'statuses': []}
            for agent_id in request.json['agent_ids']:
                status = (
                    params.CALLCENTER_STATS_OPERATORS_STATUS_BY_AGENT_ID.get(
                        agent_id,
                    )
                )
                if status:
                    body['statuses'].append(status)
            return aiohttp.web.Response(status=200, body=json.dumps(body))

    return Context()


@pytest.fixture(name='mock_system_info')
def _mock_system_info(mock_callcenter_queues, taxi_config):
    class Context:
        @staticmethod
        @mock_callcenter_queues('/v1/queues/list')
        async def handle_urls(request, *args, **kwargs):
            metaqueues = list()
            subclusters = list()
            queues = list()
            for item in taxi_config.get('CALLCENTER_METAQUEUES'):
                metaqueues.append(item['name'])
                queues_item = {
                    'metaqueue': item['name'],
                    'subclusters': list(),
                }
                for subcluster in item['allowed_clusters']:
                    subclusters.append(subcluster)
                    queues_item['subclusters'].append(
                        {
                            'name': subcluster,
                            'enabled_for_call_balancing': True,
                            'enabled_for_sip_users_balancing': True,
                            'enabled': True,
                        },
                    )
                queues.append(queues_item)
            metaqueues = list(set(metaqueues))
            subclusters = list(set(subclusters))
            return {
                'metaqueues': metaqueues,
                'subclusters': subclusters,
                'queues': queues,
            }

    return Context()
