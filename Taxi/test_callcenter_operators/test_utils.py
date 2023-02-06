import copy

from callcenter_operators import models
from callcenter_operators.storage.postgresql import db

TEL_BASE_RESPONSE = {
    'PARAM': {},
    'TYPE': 'REPLY',
    'STATUSCODE': 200,
    'STATUSDESC': None,
    'STATUS': 'TRUE',
}


def _make_tel_queues(status, queues):
    if status == models.TelState.DISCONNECTED:
        return {}
    if status == models.TelState.CONNECTED:
        result = dict()
        for queue in queues:
            result[queue] = {
                'STATUS': 1,
                'VENDPAUSED': '0',
                'PRIOR': 1,
                'CURPRIOR': '1',
            }
        return result
    result = dict()
    for queue in queues:
        result[queue] = {
            'STATUS': 1,
            'VENDPAUSED': '1',
            'PRIOR': 1,
            'CURPRIOR': '1',
        }
    return result


def make_show_response(status, queues):
    return {
        **TEL_BASE_RESPONSE,
        'DATA': {
            'CALLCENTERID': 'cc1',
            'QUEUES': _make_tel_queues(status, queues),
        },
        'STATUSMSG': 'SUCCESS',
    }


def make_auth_headers(operator):
    return {
        'X-Yandex-Login': operator['login'],
        'X-Yandex-UID': operator['uid'],
    }


def make_tel_response():
    return {**TEL_BASE_RESPONSE, 'DATA': False, 'STATUSMSG': ''}


async def get_operators(yandex_uids, context):
    pool = await db.OperatorsRepo.get_ro_pool(context)
    async with pool.acquire() as conn:
        query = (
            'SELECT '
            'operators_access.id, '
            'operators_access.yandex_uid as yandex_uid, '
            'yandex_login, '
            'operator_id::VARCHAR as agent_id, '
            'first_name, '
            'middle_name, '
            'last_name, '
            'callcenter_id, '
            'supervisor_login, '
            'phone_number, '
            'state, '
            'working_domain, '
            'current_info.sub_status, '
            'current_info.status, '
            'current_info.metaqueues, '
            'operators_access.updated_at as local_updated_at, '
            'staff_login, '
            'staff_login_state, '
            'timezone, '
            'mentor_login, '
            'employment_date, '
            'name_in_telephony, '
            'COALESCE(operators_roles.roles, \'{}\') as roles '
            'FROM callcenter_auth.operators_access '
            'LEFT JOIN callcenter_auth.current_info '
            'ON operators_access.id = current_info.id '
            'LEFT JOIN callcenter_auth.operators_roles '
            'ON operators_access.yandex_uid = operators_roles.yandex_uid '
            'WHERE operators_access.yandex_uid = ANY($1)'
        )
        operator_records = await conn.fetch(query, yandex_uids)
        return operator_records


async def get_operator(yandex_uid, context):
    result = await get_operators([yandex_uid], context)
    if result is None:
        return None
    return result[0]


def make_bad_tel_response():
    tel_response = copy.deepcopy(TEL_BASE_RESPONSE)
    tel_response['STATUSCODE'] = 500
    return {**tel_response, 'DATA': False, 'STATUSMSG': ''}


def create_json_filter(**kwargs):
    filter_body = {}
    if kwargs.get('callcenters'):
        filter_body['callcenters'] = kwargs['callcenters']
    if kwargs.get('states'):
        filter_body['states'] = kwargs['states']
    if kwargs.get('supervisors'):
        filter_body['supervisors'] = kwargs['supervisors']
    if kwargs.get('mentors'):
        filter_body['mentors'] = kwargs['mentors']
    if kwargs.get('statuses'):
        filter_body['statuses'] = kwargs['statuses']
    if kwargs.get('substatuses'):
        filter_body['substatuses'] = kwargs['substatuses']
    if kwargs.get('queues'):
        filter_body['queues'] = kwargs['queues']
    if kwargs.get('roles'):
        filter_body['roles'] = kwargs['roles']
    if kwargs.get('logins_names_agent_ids'):
        filter_body['logins_names_agent_ids'] = kwargs[
            'logins_names_agent_ids'
        ]
    json_body = {}
    if filter_body:
        json_body['filter'] = filter_body
    if kwargs.get('project'):
        json_body['project'] = kwargs['project']
    return json_body
