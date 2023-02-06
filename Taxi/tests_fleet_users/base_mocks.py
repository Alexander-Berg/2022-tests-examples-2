import pytest


PERSONAL_STORE = {
    '+71231231212': 'phone_id1',
    '+74564564545': 'phone_id2',
    '+77777777777': 'phone_id_super',
    '+77897897878': 'phone_id3',
}


@pytest.fixture(name='personal_phones_store')
def _mock_personal_phones_store(mockserver):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock(request):
        assert request.json['value'] in PERSONAL_STORE
        return {
            'id': PERSONAL_STORE[request.json['value']],
            'value': request.json['value'],
        }

    return _mock


PERSONAL_RETRIEVE = {'phone_id1': '+71231231212', 'phone_id2': '+74564564545'}


@pytest.fixture(name='personal_phones_retrieve')
def _mock_personal_phones_retrieve(mockserver):
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _mock(request):
        response = []
        for item in request.json['items']:
            assert item['id'] in PERSONAL_RETRIEVE
            response.append(
                {'id': item['id'], 'value': PERSONAL_RETRIEVE[item['id']]},
            )
        return {'items': response}

    return _mock


@pytest.fixture(name='dac_parks_group_list')
def _mock_dac_parks_group_list(mockserver):
    @mockserver.json_handler('/dispatcher-access-control/v1/parks/groups/list')
    def _mock(request):
        return {
            'groups': [
                {
                    'id': 'admin',
                    'name': 'Administrators',
                    'size': 10,
                    'is_super': False,
                },
                {
                    'id': 'super',
                    'name': 'Superusers',
                    'size': 1,
                    'is_super': True,
                },
                {
                    'id': 'dispatcher',
                    'name': 'Dispatchers',
                    'size': 10,
                    'is_super': False,
                },
            ],
        }

    return _mock


@pytest.fixture(name='dac_parks_users_list')
def _mock_dac_parks_users_list(mockserver):
    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def _mock(request):
        assert request.json == {
            'query': {'park': {'id': 'park_id'}},
            'offset': 0,
        }
        return {
            'offset': 0,
            'users': [
                {
                    'id': 'author_id',
                    'park_id': 'park_id',
                    'passport_uid': '100',
                    'display_name': 'author',
                    'is_enabled': True,
                    'is_confirmed': False,
                    'is_superuser': False,
                    'is_multifactor_authentication_required': True,
                    'is_usage_consent_accepted': False,
                },
                {
                    'id': 'author_id_super',
                    'park_id': 'park_id',
                    'passport_uid': '111',
                    'display_name': 'author_super',
                    'is_enabled': True,
                    'is_confirmed': False,
                    'is_superuser': True,
                    'is_multifactor_authentication_required': True,
                    'is_usage_consent_accepted': False,
                    'group_id': 'super',
                },
            ],
        }


@pytest.fixture(name='dac_parks_users_platform_roles')
def _mock_dac_parks_users_platform_roles(mockserver):
    @mockserver.json_handler(
        '/dispatcher-access-control/v1/parks/users/platform/roles',
    )
    def _mock(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        return {'roles': ['Admin']}
