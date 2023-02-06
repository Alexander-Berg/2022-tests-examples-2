import pytest


ADMIN_GROUP_ID = 'admin_group_id'
DISPATCHER_GROUP_ID = 'dispatcher_group_id'
GROUPS = {
    ADMIN_GROUP_ID: 'admin_group_name',
    DISPATCHER_GROUP_ID: 'dispatcher_group_name',
}
ADMIN_GRANTS = {
    'write_grant_1': True,
    'read_grant_1': True,
    'read_grant_2': True,
    'company_write': True,
    'driver_write_common': True,
}
DISPATCHER_GRANTS = {
    'read_grant_1': True,
    'read_grant_2': True,
    'read_grant_3': True,
}


@pytest.fixture(name='dispatcher_access_control')
def dac_fixture(mockserver):
    class Context:
        ADMIN_USER_ID = 'admin_user'
        DISPATCHER_USER_ID = 'dispatcher_user'

        @staticmethod
        def make_users(init_park) -> dict:
            return {
                Context.ADMIN_USER_ID: {
                    'id': Context.ADMIN_USER_ID,
                    'group_id': ADMIN_GROUP_ID,
                    'passport_uid': 'ululu',
                    'is_enabled': True,
                    'is_usage_consent_accepted': True,
                    'display_name': 'admin',
                    'park_id': init_park,
                    'is_superuser': True,
                    'email': 'admin_email',
                    'phone': '+000',
                    'usage_consent_acceptance_date': (
                        '2019-01-01T00:00:00.000000+00:00'
                    ),
                    'is_confirmed': True,
                },
                Context.DISPATCHER_USER_ID: {
                    'id': Context.DISPATCHER_USER_ID,
                    'group_id': DISPATCHER_GROUP_ID,
                    'passport_uid': 'cawcawcaw',
                    'is_enabled': True,
                    'is_usage_consent_accepted': True,
                    'display_name': 'dispatcher',
                    'park_id': init_park,
                    'is_superuser': False,
                    'email': 'dispatcher_email',
                    'phone': '+123',
                    'usage_consent_acceptance_date': (
                        '2019-01-01T00:00:00.000000+00:00'
                    ),
                    'is_confirmed': True,
                },
            }

        def __init__(self):
            self.grants = {}
            self.groups = {}
            self.users = {}
            self.init_park = ''
            self.mock_groups_list = None
            self.mock_parks_grants_list = None
            self.mock_parks_grants_groups_list = None
            self.mock_sync_parks_groups = None
            self.mock_sync_parks_groups_grants = None
            self.mock_parks_groups_users_list = None
            self.mock_sync_parks_users = None

        def set_init_park(self, init_park):
            self.init_park = init_park
            self.grants[init_park] = {}
            self.grants[init_park][ADMIN_GROUP_ID] = ADMIN_GRANTS
            self.grants[init_park][DISPATCHER_GROUP_ID] = DISPATCHER_GRANTS
            self.groups[init_park] = GROUPS
            self.users[init_park] = Context.make_users(init_park)

        def set_user(self, park_id, user_id, data):
            local_data = dict(data)
            local_data['is_superuser'] = False
            if park_id not in self.users:
                self.users[park_id] = {}
            self.users[park_id][user_id] = local_data

        def get_user_data(self, park_id, user_id):
            if park_id not in self.users:
                return None
            return self.users[park_id].get(user_id)

        def get_users(self, park_id):
            result = []
            if park_id not in self.users:
                return result
            for _, user_data in self.users[park_id].items():
                result.append(user_data)
            return result

        def _try_init_grants(self, park_id, group_id):
            if park_id not in self.grants:
                self.grants[park_id] = {}
            elif group_id not in self.grants[park_id]:
                self.grants[park_id][group_id] = {}

        def set_grant(self, park_id, group_id, grant):
            self._try_init_grants(park_id, group_id)
            self.grants[park_id][group_id][grant] = True

        def set_grants(self, park_id, group_id, grants):
            self._try_init_grants(park_id, group_id)
            for grant in grants:
                self.grants[park_id][group_id][grant] = True

        def unset_grant(self, park_id, group_id, grant):
            self._try_init_grants(park_id, group_id)
            self.grants[park_id][group_id][grant] = False

        def unset_grants(self, park_id, group_id, grants):
            self._try_init_grants(park_id, group_id)
            for grant in grants:
                self.grants[park_id][group_id][grant] = False

        def get_grants(self, park_id, group_id):
            result = []
            for grant, value in (
                    self.grants.get(park_id, {}).get(group_id, {}).items()
            ):
                if value:
                    result.append(grant)
            return result

        def get_admin_grants(self, park_id):
            return self.get_grants(park_id, ADMIN_GROUP_ID)

        def get_dispatcher_grants(self, park_id):
            return self.get_grants(park_id, DISPATCHER_GROUP_ID)

        def create_group(self, park_id, group_id, group_name):
            self._try_init_grants(park_id, group_id)
            if park_id not in self.groups:
                self.groups[park_id] = {}
            self.groups[park_id][group_id] = group_name

        def get_group_name(self, park_id, group_id):
            return self.groups[park_id][group_id]

        def get_groups(self, park_id):
            result = []
            if park_id not in self.groups:
                return result
            for group_id, _ in self.groups[park_id].items():
                result.append(
                    {
                        'id': group_id,
                        'name': context.get_group_name(park_id, group_id),
                        'is_super': False,
                        'size': 0,
                    },
                )
            return result

        def delete_group(self, park_id, group_id):
            if park_id in self.groups:
                self.groups[park_id].pop(group_id)

        def delete_user(self, park_id, user_id):
            if park_id in self.users:
                self.users[park_id].pop(user_id)

    context = Context()

    @mockserver.json_handler('/dispatcher-access-control/v1/parks/groups/list')
    def _mock_groups_list(request):
        park_id = request.json['query']['park']['id']
        return mockserver.make_response(
            json={'groups': context.get_groups(park_id)}, status=200,
        )

    @mockserver.json_handler('/dispatcher-access-control/sync/v1/parks/groups')
    def _mock_sync_parks_groups(request):
        if request.method == 'PUT':
            park_id = request.query['park_id']
            group_id = request.query['group_id']
            group_name = request.json['name']
            context.create_group(park_id, group_id, group_name)
            return mockserver.make_response(
                json={'id': group_id, 'name': group_name, 'is_super': False},
                status=200,
            )

        if request.method == 'DELETE':
            query = dict(request.query)
            park_id = query['park_id']
            group_id = query['group_id']
            context.delete_group(park_id, group_id)
            return {}

        return mockserver.make_response(status=405)

    @mockserver.json_handler(
        '/dispatcher-access-control/sync/v1/parks/groups/grants',
    )
    def _mock_sync_parks_groups_grants(request):
        park_id = request.query['park_id']
        group_id = request.query['group_id']
        grants = request.json['grants']
        for grant in grants:
            grant_name = grant['id']
            if grant['state']:
                context.set_grant(park_id, group_id, grant_name)
            else:
                context.unset_grant(park_id, group_id, grant_name)

        return mockserver.make_response(
            json={
                'grants': [
                    {'id': grant, 'state': True}
                    for grant in context.get_grants(park_id, group_id)
                ],
            },
            status=200,
        )

    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def _mock_parks_groups_users_list(request):
        park_id = request.json['query']['park']['id']
        return mockserver.make_response(
            json={'users': context.get_users(park_id)}, status=200,
        )

    @mockserver.json_handler('/dispatcher-access-control/sync/v1/parks/users')
    def _mock_sync_parks_users(request):
        if request.method == 'PUT':
            query = dict(request.query)
            park_id = query['park_id']
            user_id = query['user_id']
            data = request.json
            context.set_user(park_id, user_id, data)
            return mockserver.make_response(
                json={
                    'email': request.json['email'],
                    'group_id': request.json['group_id'],
                    'is_enabled': request.json['is_enabled'],
                    'is_superuser': request.json['is_superuser'],
                },
                status=200,
            )

        if request.method == 'DELETE':
            query = dict(request.query)
            park_id = query['park_id']
            user_id = query['user_id']
            context.delete_user(park_id, user_id)
            return {}

        return mockserver.make_response(status=405)

    @mockserver.json_handler('/dispatcher-access-control/v1/parks/grants/list')
    def _mock_parks_grants_list(request):
        park_id = request.json['query']['park']['id']
        group_ids = [group['id'] for group in context.get_groups(park_id)]

        grants = set()
        for group_id in group_ids:
            for grant in context.get_grants(park_id, group_id):
                grants.add(grant)

        return mockserver.make_response(
            json={'grants': [{'id': grant} for grant in grants]}, status=200,
        )

    @mockserver.json_handler(
        '/dispatcher-access-control/v1/parks/grants/groups/list',
    )
    def _mock_parks_grants_groups_list(request):
        park_id = request.json['query']['park']['id']
        group_ids = [group['id'] for group in context.get_groups(park_id)]

        groups = [
            {
                'group_id': group_id,
                'grants': [
                    {'id': grant}
                    for grant in context.get_grants(park_id, group_id)
                ],
            }
            for group_id in group_ids
        ]
        return mockserver.make_response(json={'groups': groups}, status=200)

    context.mock_groups_list = _mock_groups_list

    context.mock_parks_grants_list = _mock_parks_grants_list
    context.mock_parks_grants_groups_list = _mock_parks_grants_groups_list

    context.mock_sync_parks_groups = _mock_sync_parks_groups
    context.mock_sync_parks_groups_grants = _mock_sync_parks_groups_grants

    context.mock_parks_groups_users_list = _mock_parks_groups_users_list
    context.mock_sync_parks_users = _mock_sync_parks_users

    return context
