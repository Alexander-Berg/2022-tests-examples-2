import pytest

from tests_fleet_users import utils


ENDPOINT = 'fleet/users/v1/users'

PARK_ID = 'park_id'
USER_ID = 'user_id1'

UID_SUPER = '111'


def build_params(user_id=USER_ID):
    return {'user_id': user_id}


def build_headers(park_id=PARK_ID, provider='yandex', uid='100'):
    return {
        'X-Park-ID': park_id,
        'X-Ya-User-Ticket': 'user_ticket',
        'X-Ya-User-Ticket-Provider': provider,
        'X-Yandex-UID': uid,
        'X-Remote-IP': '1.2.3.4',
    }


def build_request(
        group_id='admin', is_enabled=True, name='Disp Dispovich', phone=None,
):
    return {
        'group_id': group_id,
        'is_enabled': is_enabled,
        'name': name,
        'phone': phone,
    }


@pytest.fixture(name='dac_parks_users_put')
def _mock_dac_parks_users_put(mockserver):
    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users')
    def _mock(request):
        return request.json

    return _mock


GROUPS_NAME = {
    'admin': 'Administrators',
    'super': 'Superusers',
    'dispatcher': 'Dispatchers',
}

IS_ENABLED_STR = {True: 'True', False: 'False'}


def build_body_logging(
        old_user,
        group_id='admin',
        is_enabled=True,
        name='Disp Dispovich',
        provider='yandex',
        author_uid='100',
):
    body = {
        'park_id': PARK_ID,
        'change_info': {'object_type': 'Taximeter.Core.Models.User'},
    }
    if provider == 'yandex':
        body['author'] = {'user_ip': '1.2.3.4'}
        if author_uid == UID_SUPER:
            body['author']['display_name'] = 'author_super'
            body['author']['dispatch_user_id'] = 'author_id_super'
        else:
            body['author']['display_name'] = 'author'
            body['author']['dispatch_user_id'] = 'author_id'
    elif provider == 'yandex_team':
        body['author'] = {
            'dispatch_user_id': '',
            'display_name': 'Techsupport',
            'user_ip': '1.2.3.4',
        }
    diff = []
    if old_user['is_enabled'] != is_enabled:
        diff.append(
            {
                'field': 'Enable',
                'new': IS_ENABLED_STR[is_enabled],
                'old': IS_ENABLED_STR[old_user['is_enabled']],
            },
        )
    if old_user['group_id'] != group_id:
        diff.append(
            {
                'field': 'Group',
                'new': GROUPS_NAME[group_id],
                'old': GROUPS_NAME[old_user['group_id']],
            },
        )
    if old_user['user_name'] != name:
        diff.append(
            {'field': 'Name', 'new': name, 'old': old_user['user_name']},
        )
    body['change_info']['diff'] = diff
    return body


@pytest.mark.parametrize(
    'user_id, phone',
    [('user_id1', '+71231231212'), ('user_id2', '+74564564545')],
)
@pytest.mark.parametrize('group_id', ['admin', 'dispatcher'])
@pytest.mark.parametrize('is_enabled', [True, False])
@pytest.mark.parametrize('name', ['Disp Dispovich', 'Dispa Dispovna'])
@pytest.mark.parametrize('provider', ['yandex', 'yandex_team'])
async def test_success_local_editing(
        taxi_fleet_users,
        pgsql,
        dac_parks_users_list,
        dac_parks_group_list,
        personal_phones_store,
        mock_fleet_parks_list,
        mockserver,
        user_id,
        phone,
        group_id,
        is_enabled,
        name,
        provider,
):

    old_user = utils.get_user_by_id(pgsql, PARK_ID, user_id)

    @mockserver.json_handler('/driver-work-rules/service/v1/change-logger')
    def _mock_change_logger(request):
        body = request.json
        body.pop('entity_id')
        body['change_info'].pop('object_id')
        assert body == build_body_logging(
            old_user, group_id, is_enabled, name, provider,
        )
        return {}

    request = build_request(group_id, is_enabled, name, phone)
    response = await taxi_fleet_users.put(
        ENDPOINT,
        params=build_params(user_id),
        headers=build_headers(provider=provider),
        json=request,
    )

    assert response.status == 200
    request.pop('phone')
    assert response.json() == request

    new_user = utils.get_user_by_id(pgsql, PARK_ID, user_id)
    assert new_user['is_enabled'] == is_enabled
    assert new_user['group_id'] == group_id
    assert new_user['user_name'] == name


@pytest.mark.parametrize(
    'user_id, phone, group_id, provider, author_uid, author_roles',
    [
        ('user_id1', '+71231231212', 'super', 'yandex_team', '100', ['Admin']),
        (
            'user_id1',
            '+71231231212',
            'super',
            'yandex_team',
            '100',
            ['PartnerSupport'],
        ),
        (
            'user_id_super',
            '+77777777777',
            'admin',
            'yandex_team',
            '100',
            ['Admin'],
        ),
        (
            'user_id_super',
            '+77777777777',
            'admin',
            'yandex_team',
            '100',
            ['PartnerSupport'],
        ),
        ('user_id_super', '+77777777777', 'super', 'yandex', '111', []),
        ('user_id_super', '+77777777777', 'super', 'yandex_team', '100', []),
    ],
)
async def test_success_local_editing_super(
        taxi_fleet_users,
        pgsql,
        dac_parks_group_list,
        personal_phones_store,
        mock_fleet_parks_list,
        mockserver,
        user_id,
        phone,
        group_id,
        provider,
        author_uid,
        author_roles,
):

    old_user = utils.get_user_by_id(pgsql, PARK_ID, user_id)

    @mockserver.json_handler('/driver-work-rules/service/v1/change-logger')
    def _mock_change_logger(request):
        body = request.json
        body.pop('entity_id')
        body['change_info'].pop('object_id')
        assert body == build_body_logging(
            old_user,
            group_id=group_id,
            provider=provider,
            author_uid=author_uid,
        )
        return {}

    @mockserver.json_handler(
        '/dispatcher-access-control/v1/parks/users/platform/roles',
    )
    def _mock_dac_roles(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        return {'roles': author_roles}

    author_info = {
        '100': {
            'name': 'author',
            'id': 'author_id',
            'is_superuser': False,
            'group_id': 'admin',
        },
        '111': {
            'name': 'author_super',
            'id': 'author_id_super',
            'is_superuser': True,
            'group_id': 'super',
        },
    }

    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def _mock(request):
        assert request.json == {
            'query': {'park': {'id': PARK_ID}},
            'offset': 0,
        }
        return {
            'offset': 0,
            'users': [
                {
                    'id': author_info[author_uid]['id'],
                    'park_id': PARK_ID,
                    'passport_uid': author_uid,
                    'display_name': author_info[author_uid]['name'],
                    'is_enabled': True,
                    'is_confirmed': True,
                    'is_superuser': author_info[author_uid]['is_superuser'],
                    'is_multifactor_authentication_required': True,
                    'is_usage_consent_accepted': False,
                    'group_id': author_info[author_uid]['group_id'],
                },
            ],
        }

    request = build_request(group_id, phone=phone)
    response = await taxi_fleet_users.put(
        ENDPOINT,
        params=build_params(user_id),
        headers=build_headers(provider=provider, uid=author_uid),
        json=request,
    )

    assert response.status == 200
    request.pop('phone')
    assert response.json() == request

    new_user = utils.get_user_by_id(pgsql, PARK_ID, user_id)
    assert new_user['group_id'] == group_id


@pytest.mark.parametrize(
    'user_id, provider, phone',
    [
        ('user_id_dac', 'yandex', '+71231231212'),
        ('user_id_dac', 'yandex_team', '+71231231212'),
        ('user_id_dac', 'yandex', None),
        ('user_id_dac', 'yandex_team', None),
        ('user_id3', 'yandex', '+77897897878'),
        ('user_id3', 'yandex_team', '+77897897878'),
    ],
)
async def test_success_dac_editing(
        taxi_fleet_users,
        mockserver,
        personal_phones_store,
        mock_fleet_parks_list,
        user_id,
        provider,
        phone,
):
    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def _mock_dac_parks_users_list(request):
        assert request.json == {
            'query': {'park': {'id': 'park_id1'}},
            'offset': 0,
        }
        return {
            'offset': 0,
            'users': [
                {
                    'id': 'user_id_dac',
                    'park_id': 'park_id1',
                    'passport_uid': '100',
                    'display_name': 'author',
                    'is_enabled': True,
                    'is_confirmed': False,
                    'is_superuser': False,
                    'is_multifactor_authentication_required': True,
                    'is_usage_consent_accepted': False,
                },
            ],
        }

    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users')
    def _mock_dac_parks_users(request):
        assert request.headers['X-Ya-User-Ticket-Provider'] == provider
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.headers['X-Yandex-UID'] == '100'
        assert request.headers['X-Remote-IP'] == '1.2.3.4'
        assert request.args['park_id'] == 'park_id1'
        assert request.args['user_id'] == user_id
        request_body = {
            'group_id': 'admin',
            'is_enabled': True,
            'is_superuser': False,
            'name': 'Disp Dispovich',
        }
        if phone:
            request_body['phone'] = phone
        response_body = build_request()
        response_body['is_superuser'] = False
        if phone:
            response_body['phone'] = phone
        return response_body

    request = build_request(phone=phone)
    response = await taxi_fleet_users.put(
        ENDPOINT,
        params=build_params(user_id=user_id),
        headers=build_headers(park_id='park_id1', provider=provider),
        json=request,
    )

    assert response.status == 200
    if not phone:
        request.pop('phone')
    assert response.json() == request


@pytest.mark.parametrize(
    'error_code, error_status',
    [
        ('user_not_found', 404),
        ('group_not_found', 400),
        ('no_access', 400),
        ('is_not_support', 400),
        ('superuser_exists', 400),
    ],
)
async def test_error_dac_editing(
        taxi_fleet_users,
        mockserver,
        error_code,
        error_status,
        personal_phones_store,
        mock_fleet_parks_list,
):
    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def _mock_dac_parks_users_list(request):
        assert request.json == {
            'query': {'park': {'id': 'park_id1'}},
            'offset': 0,
        }
        return {
            'offset': 0,
            'users': [
                {
                    'id': 'user_id_dac',
                    'park_id': 'park_id1',
                    'passport_uid': '100',
                    'display_name': 'author',
                    'is_enabled': True,
                    'is_confirmed': False,
                    'is_superuser': False,
                    'is_multifactor_authentication_required': True,
                    'is_usage_consent_accepted': False,
                },
            ],
        }

    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users')
    def _mock_dac_parks_users(request):
        assert request.headers['X-Ya-User-Ticket-Provider'] == 'yandex'
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.headers['X-Yandex-UID'] == '100'
        assert request.headers['X-Remote-IP'] == '1.2.3.4'
        assert request.args['park_id'] == 'park_id1'
        assert request.args['user_id'] == 'user_id_dac'
        return mockserver.make_response(
            status=400, json={'code': error_code, 'message': ''},
        )

    request = build_request()
    response = await taxi_fleet_users.put(
        ENDPOINT,
        params=build_params('user_id_dac'),
        headers=build_headers(park_id='park_id1'),
        json=request,
    )

    assert response.status == error_status

    local_error_codes = {
        'user_not_found': 'user_not_found',
        'group_not_found': 'group_not_found',
        'no_access': 'cannot_update_director',
        'is_not_support': 'cannot_assign_director',
        'superuser_exists': 'director_exists',
    }

    assert response.json() == {
        'code': local_error_codes[error_code],
        'message': '',
    }


async def test_error_local_editing_group_not_found(
        taxi_fleet_users,
        mockserver,
        dac_parks_users_list,
        dac_parks_group_list,
        personal_phones_store,
        mock_fleet_parks_list,
):
    @mockserver.json_handler('/driver-work-rules/service/v1/change-logger')
    def _mock_change_logger(request):
        return {}

    request = build_request(group_id='invalid_group', phone='+71231231212')
    response = await taxi_fleet_users.put(
        ENDPOINT, params=build_params(), headers=build_headers(), json=request,
    )

    assert response.status == 400
    assert response.json()['code'] == 'group_not_found'

    assert _mock_change_logger.times_called == 0


@pytest.mark.parametrize('group_id', ['admin', None])
async def test_error_local_editing_cannot_update_director(
        taxi_fleet_users,
        mockserver,
        dac_parks_group_list,
        group_id,
        personal_phones_store,
        mock_fleet_parks_list,
):
    @mockserver.json_handler('/driver-work-rules/service/v1/change-logger')
    def _mock_change_logger(request):
        return {}

    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def _mock(request):
        assert request.json == {
            'query': {'park': {'id': PARK_ID}},
            'offset': 0,
        }
        return {
            'offset': 0,
            'users': [
                {
                    'id': 'author_id',
                    'park_id': PARK_ID,
                    'passport_uid': '100',
                    'display_name': 'author',
                    'is_enabled': True,
                    'is_confirmed': False,
                    'is_superuser': False,
                    'is_multifactor_authentication_required': True,
                    'is_usage_consent_accepted': False,
                    'group_id': group_id,
                },
            ],
        }

    request = build_request(phone='+77777777777')
    response = await taxi_fleet_users.put(
        ENDPOINT,
        params=build_params(user_id='user_id_super'),
        headers=build_headers(),
        json=request,
    )

    assert response.status == 400
    assert response.json()['code'] == 'cannot_update_director'

    assert _mock_change_logger.times_called == 0


@pytest.mark.parametrize('provider', ['yandex', 'yandex_team'])
async def test_error_local_editing_cannot_assign_director(
        taxi_fleet_users,
        mockserver,
        dac_parks_users_list,
        dac_parks_group_list,
        personal_phones_store,
        mock_fleet_parks_list,
        provider,
):
    @mockserver.json_handler('/driver-work-rules/service/v1/change-logger')
    def _mock_change_logger(request):
        return {}

    @mockserver.json_handler(
        '/dispatcher-access-control/v1/parks/users/platform/roles',
    )
    def _mock_dac_roles(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        return {'roles': ['Basic']}

    request = build_request(group_id='super', phone='+71231231212')
    response = await taxi_fleet_users.put(
        ENDPOINT,
        params=build_params(),
        headers=build_headers(provider=provider),
        json=request,
    )

    assert response.status == 400
    assert response.json()['code'] == 'cannot_assign_director'

    assert _mock_change_logger.times_called == 0


async def test_error_local_editing_director_exists(
        taxi_fleet_users,
        mockserver,
        dac_parks_users_list,
        dac_parks_group_list,
        personal_phones_store,
        mock_fleet_parks_list,
):
    @mockserver.json_handler('/driver-work-rules/service/v1/change-logger')
    def _mock_change_logger(request):
        return {}

    @mockserver.json_handler(
        '/dispatcher-access-control/v1/parks/users/platform/roles',
    )
    def _mock_dac_roles(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        return {'roles': ['Admin']}

    request = build_request(group_id='super', phone='+71231231212')
    response = await taxi_fleet_users.put(
        ENDPOINT,
        params=build_params(),
        headers=build_headers(provider='yandex_team'),
        json=request,
    )

    assert response.status == 400
    assert response.json()['code'] == 'director_exists'

    assert _mock_change_logger.times_called == 0


@pytest.mark.parametrize('user_id', ['user_id1', 'user_id3'])
@pytest.mark.parametrize('phone', [None, '+74564564545'])
async def test_error_cannot_change_phone(
        taxi_fleet_users,
        mockserver,
        dac_parks_users_list,
        dac_parks_group_list,
        personal_phones_store,
        mock_fleet_parks_list,
        user_id,
        phone,
):
    @mockserver.json_handler('/driver-work-rules/service/v1/change-logger')
    def _mock_change_logger(request):
        return {}

    request = build_request(phone=phone)
    response = await taxi_fleet_users.put(
        ENDPOINT,
        params=build_params(user_id=user_id),
        headers=build_headers(provider='yandex'),
        json=request,
    )

    assert response.status == 400
    assert response.json()['code'] == 'cannot_change_phone'

    assert _mock_change_logger.times_called == 0
