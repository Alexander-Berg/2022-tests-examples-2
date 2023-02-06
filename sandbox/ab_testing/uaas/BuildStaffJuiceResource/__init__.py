# coding: utf-8

import requests
import json
import time
import logging

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from sandbox import sdk2

from sandbox.projects.ab_testing import (
    STAFF_JUICE_RESOURCE,
)

from sandbox.projects.common.nanny import nanny

import sandbox.common.types.task as ctt


class StaffNode(object):
    def __init__(self, value=None, time_in=None, time_out=None, node_type=None, children=None, **attrs):
        self.value = value
        self.time_in = time_in
        self.time_out = time_out
        self.type = node_type
        self.children = children or set()
        self.attrs = dict(**attrs)

    def nodes(self):
        """
        :return: List of all nodes in subtree
        """
        this = {
            'value': self.value,
            'time_in': self.time_in,
            'time_out': self.time_out,
            'type': self.type,
        }
        this.update(self.attrs)

        result = list()
        result.append(this)
        for child in self.children:
            result.extend(child.nodes())

        return result


class StaffGroupNode(StaffNode):
    def __init__(self, value, **attrs):
        if not value:
            raise ValueError('name of group must be non empty')

        super(StaffGroupNode, self).__init__(
            value='group:{}'.format(value),  # 'group:' prefix required according AB-Adminka rules.
            node_type='group',
            **attrs
        )


class StaffPersonNode(StaffNode):
    def __init__(self, value, **attrs):
        if not value:
            raise ValueError('name of person must be non empty')

        super(StaffPersonNode, self).__init__(
            value=value,
            node_type='person',
            **attrs
        )


def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


class BuildStaffJuiceResource(nanny.ReleaseToNannyTask2, sdk2.Task):
    """
    Task creates juice with staff objects: person, groups
    Also it gets puid (Passport uid) for every person. Person may have up to 2 puid.
    One exists always and mean puid on '.yandex-team.ru' domain (internal_puid).
    The second puid connected with yandex login which personal for everyone. It can be gotten via Blackbox API.
    For this case fit even NOT production BLACKBOX env (mimino). It contains all required info such user puid.
    More about API details:
        blackbox: https://doc.yandex-team.ru/blackbox/
        staff-api: https://staff-api.yandex-team.ru/v3
    """

    DEFAULT_TIMEOUT = 10

    STATUS_BY_RELEASE_TYPE = {
        'testing': ctt.ReleaseStatus.TESTING,
        'stable': ctt.ReleaseStatus.STABLE,
    }

    class Parameters(sdk2.Parameters):
        blackbox_api_url = sdk2.parameters.String(
            'Blackbox api url',
            default='https://blackbox-mimino.yandex.net/blackbox',
            required=True
        )
        tvm_api_url = sdk2.parameters.String(
            'TVM api url',
            default='https://tvm-api.yandex.net/2',
            required=True
        )
        staff_api_url = sdk2.parameters.String(
            'Staff api url',
            default='https://staff-api.yandex-team.ru/v3',
            required=True
        )
        blackbox_client_id = sdk2.parameters.Integer('Blackbox client id', default=239, required=True)
        self_client_id = sdk2.parameters.Integer('Self client id', default=2011974, required=True)
        tvm_secret_vault_name = sdk2.parameters.String('TVM secret vault name', required=True)
        oauth_token_vault_name = sdk2.parameters.String('OAuth token vault name', required=True)
        release_on_success = sdk2.parameters.Bool('Release if the task complete success', default=False, required=True)
        with release_on_success.value[True]:
            release_status = sdk2.parameters.String(
                'Release type',
                choices=[
                    ('testing', 'testing'),
                    ('stable', 'stable'),
                ],
                default='testing',
                required=True
            )

    def get_service_ticket(self):
        from ticket_parser2.api.v1 import ServiceContext

        with requests_retry_session() as tvmapi_session:
            response = tvmapi_session.get(
                '{}/keys?lib_version=2.3.0'.format(self.Parameters.tvm_api_url),
                timeout=self.DEFAULT_TIMEOUT
            )
            tvm_keys = response.content
            tvm_secret = sdk2.Vault.data(self.Parameters.tvm_secret_vault_name)

            ts = int(time.time())
            service_context = ServiceContext(self.Parameters.self_client_id, tvm_secret, tvm_keys)
            sign = service_context.sign(ts, self.Parameters.blackbox_client_id)

            response = tvmapi_session.post(
                '{}/ticket'.format(self.Parameters.tvm_api_url),
                data={
                    'grant_type': 'client_credentials',
                    'src': self.Parameters.self_client_id,
                    'dst': self.Parameters.blackbox_client_id,
                    'ts': ts,
                    'sign': sign,
                },
                timeout=self.DEFAULT_TIMEOUT
            )

            response_json = response.json()
            service_ticket = response_json[str(self.Parameters.blackbox_client_id)]['ticket']

        return service_ticket

    def get_staff_objects(self, object_type, params):
        if object_type not in ['persons', 'groups']:
            raise ValueError('Got unexpected staff obj type: {}'.format(object_type))

        token = sdk2.Vault.data(self.Parameters.oauth_token_vault_name)

        objects = []
        with requests_retry_session() as staffapi_session:
            last_id = -1
            staffapi_session.headers = {
                'Authorization': 'OAuth {}'.format(token),
                'Keep-Alive': 'True',
            }
            staffapi_session.params = {
                '_nopage': 1,
                '_sort': 'id',
            }
            staffapi_session.params.update(params)
            while True:
                staffapi_session.params['_query'] = 'id>{}'.format(last_id)
                result = staffapi_session.get(
                    '{url}/{object_type}'.format(
                        url=self.Parameters.staff_api_url,
                        object_type=object_type,
                    ),
                    timeout=self.DEFAULT_TIMEOUT
                ).json()['result']

                if result:
                    last_id = result[-1]['id']
                    objects.extend(result)
                else:
                    break

        return objects

    def get_personid2node_map(self, persons, service_ticket):
        """
        :param persons: List[person]
        :param service_ticket: str
        :return: Map personid -> StaffPersonNode
        service_ticket required for blackbox communicate
        """
        ret = dict()
        with requests_retry_session() as blackboxapi_session:
            blackboxapi_session.headers = {
                'X-Ya-Service-Ticket': service_ticket,
                'Keep-Alive': 'True'
            }
            blackboxapi_session.params = {
                'method': 'userinfo',
                'format': 'json',
                'userip': '12.12.12.12',
                'sid': 669,
                'login': None
            }
            for person in persons:
                personid = person['id']
                login = person['login']
                internal_puid = person['uid']
                external_puid = None

                login = requests.utils.quote(login, safe='@')
                blackboxapi_session.params['login'] = login
                response = blackboxapi_session.get(
                    self.Parameters.blackbox_api_url,
                    timeout=BuildStaffJuiceResource.DEFAULT_TIMEOUT,
                ).json()
                external_puid = response['users'][0]['uid'].get('value')
                if external_puid is None:
                    logging.error('no found external puid for {}'.format(login))

                ret[personid] = StaffPersonNode(
                    value=login,
                    internal_puid=int(internal_puid),
                    external_puid=int(external_puid) if external_puid else None,
                )

        return ret

    @staticmethod
    def get_groupid2node_map(groups):
        return {
            group['id']: StaffGroupNode(value=group['url'])
            for group in groups
        }

    def dfs(self, node):
        if not node:
            return

        self.visited.add(node)
        self.dfs_timer += 1
        node.time_in = self.dfs_timer
        for child in node.children:
            if child not in self.visited:
                self.dfs(child)

        self.dfs_timer += 1
        node.time_out = self.dfs_timer

    @staticmethod
    def build_staff_tree_and_get_roots(persons, groups, personid2node, groupid2node):
        roots = list()
        for group in groups:
            groupid = group['id']
            parentid = group.get('parent', {}).get('id')
            node = groupid2node[groupid]

            if not parentid:
                # Nodes which have not parent are roots
                roots.append(node)
            else:
                parentnode = groupid2node[parentid]
                parentnode.children.add(node)

        # fill groups with persons
        for person in persons:
            personid = person['id']
            person_node = personid2node[personid]
            for group in person['groups']:
                groupid = group['group']['id']
                group_node = groupid2node.get(groupid)
                if group_node:
                    group_node.children.add(person_node)

        return roots

    def on_execute(self):
        self.dfs_timer = 0
        self.visited = set()

        service_ticket = self.get_service_ticket()
        persons = self.get_staff_objects(
            object_type='persons',
            params={
                '_fields': 'yandex.login,login,uid,id,groups.group.id',
                'official.is_robot': 'False',
                'official.is_dismissed': 'False',
            }
        )
        groups = self.get_staff_objects(
            object_type='groups',
            params={
                '_fields': 'url,id,parent.id',
                'type': 'department',
            }
        )

        logging.info('persons count = {}, groups count = {}'.format(len(persons), len(groups)))

        personid2node = self.get_personid2node_map(
            persons=persons,
            service_ticket=service_ticket
        )
        groupid2node = BuildStaffJuiceResource.get_groupid2node_map(
            groups=groups
        )
        roots = self.build_staff_tree_and_get_roots(
            persons=persons,
            groups=groups,
            personid2node=personid2node,
            groupid2node=groupid2node,
        )

        result = list()
        for root in roots:
            # now we try set time_in and time_out for each node using dfs
            self.dfs(root)
            # get all nodes as list of objects
            result.extend(root.nodes())

        with open('staff_juice.json', mode='w') as f:
            json.dump(result, f)

        sdk2.ResourceData(STAFF_JUICE_RESOURCE(
            self,
            'staff_juice',
            'staff_juice.json',
        ))

    def on_success(self, prev_status):
        sdk2.Task.on_success(self, prev_status)
        if self.Parameters.release_on_success:
            status = self.STATUS_BY_RELEASE_TYPE[self.Parameters.release_status]
            super(BuildStaffJuiceResource, self).on_release(
                dict(
                    releaser=self.author,
                    release_status=status,
                    release_subject='Releasing UaaS staff juice resource',
                    release_comments='Releasing UaaS staff juice resource',
                )
            )
            self.mark_released_resources(status)

