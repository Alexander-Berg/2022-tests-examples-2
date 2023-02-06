import pytest

from tests_fleet_users import utils

ENDPOINT = 'fleet/users/v1/users'

PARK_ID = 'park_id'
UID = '100'


def build_headers(park_id=PARK_ID, passport_uid=UID, provider='yandex'):
    return {
        'X-Park-ID': park_id,
        'X-Ya-User-Ticket': 'user_ticket',
        'X-Ya-User-Ticket-Provider': provider,
        'X-Yandex-UID': passport_uid,
        'X-Remote-IP': '1.2.3.4',
    }


def build_request(
        name='Диспетчеров Диспетчер', phone='+71231231212', group_id='admin',
):
    return {'name': name, 'phone': phone, 'group_id': group_id}


def check_response(request, user_id):
    response = {
        'user_id': user_id,
        'is_enabled': True,
        'is_confirmed': False,
        'group_id': request['group_id'],
        'name': request['name'],
        'phone': request['phone'],
        'is_multifactor_authentication_required': False,
        'created_at': '2019-01-01T01:00:00+00:00',
    }
    if request['group_id'] == 'admin':
        response['group_name'] = 'Administrators'
    elif request['group_id'] == 'super':
        response['group_name'] = 'Superusers'
    return response


@pytest.mark.now('2019-01-01T01:00:00+00:00')
async def test_success(
        taxi_fleet_users,
        personal_phones_store,
        dac_parks_group_list,
        dac_parks_users_list,
        fleet_parks_shard,
        mock_fleet_parks_list,
        pgsql,
        mockserver,
):
    @mockserver.json_handler('/driver-work-rules/service/v1/change-logger')
    def _mock_change_logger(request):
        body = request.json
        body.pop('entity_id')
        body['change_info'].pop('object_id')
        assert body == {
            'park_id': PARK_ID,
            'change_info': {
                'object_type': 'Taximeter.Core.Models.User',
                'diff': [
                    {'field': 'Enable', 'new': 'True', 'old': ''},
                    {'field': 'Group', 'new': 'Administrators', 'old': ''},
                    {
                        'field': 'Name',
                        'new': 'Диспетчеров Диспетчер',
                        'old': '',
                    },
                    {'field': 'Phones', 'new': '+71231231212', 'old': ''},
                ],
            },
            'author': {
                'dispatch_user_id': 'author_id',
                'display_name': 'author',
                'user_ip': '1.2.3.4',
            },
        }
        return {}

    request_body = build_request()
    response = await taxi_fleet_users.post(
        ENDPOINT, headers=build_headers(), json=request_body,
    )

    assert response.status == 200
    user_id = response.json().get('user_id', '')
    assert response.json() == check_response(request_body, user_id)

    utils.check_created_user(pgsql, request_body, PARK_ID)


@pytest.mark.now('2019-01-01T01:00:00+00:00')
async def test_success_superuser(
        taxi_fleet_users,
        personal_phones_store,
        dac_parks_group_list,
        dac_parks_users_list,
        dac_parks_users_platform_roles,
        fleet_parks_shard,
        mock_fleet_parks_list,
        pgsql,
        mockserver,
):
    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def _mock_dac_parks_users_list(request):
        assert request.json == {
            'query': {'park': {'id': 'park_id'}},
            'offset': 0,
        }
        return {
            'offset': 0,
            'users': [
                {
                    'id': 'author_id',
                    'park_id': PARK_ID,
                    'passport_uid': UID,
                    'display_name': 'author',
                    'is_enabled': True,
                    'is_confirmed': False,
                    'is_superuser': False,
                    'is_multifactor_authentication_required': True,
                    'is_usage_consent_accepted': False,
                },
            ],
        }

    @mockserver.json_handler('/driver-work-rules/service/v1/change-logger')
    def _mock_change_logger(request):
        body = request.json
        body.pop('entity_id')
        body['change_info'].pop('object_id')
        assert body == {
            'park_id': PARK_ID,
            'change_info': {
                'object_type': 'Taximeter.Core.Models.User',
                'diff': [
                    {'field': 'Enable', 'new': 'True', 'old': ''},
                    {'field': 'Group', 'new': 'Superusers', 'old': ''},
                    {
                        'field': 'Name',
                        'new': 'Диспетчеров Диспетчер',
                        'old': '',
                    },
                    {'field': 'Phones', 'new': '+71231231212', 'old': ''},
                ],
            },
            'author': {
                'dispatch_user_id': '',
                'display_name': 'Techsupport',
                'user_ip': '1.2.3.4',
            },
        }
        return {}

    request_body = build_request(group_id='super')
    response = await taxi_fleet_users.post(
        ENDPOINT,
        headers=build_headers(provider='yandex_team'),
        json=request_body,
    )

    assert response.status == 200
    user_id = response.json().get('user_id', '')
    assert response.json() == check_response(request_body, user_id)

    utils.check_created_user(pgsql, request_body, PARK_ID)


@pytest.mark.now('2019-01-01T01:00:00+00:00')
async def test_success_by_yandexteam(
        taxi_fleet_users,
        personal_phones_store,
        dac_parks_group_list,
        dac_parks_users_list,
        fleet_parks_shard,
        mock_fleet_parks_list,
        pgsql,
        mockserver,
):
    @mockserver.json_handler('/driver-work-rules/service/v1/change-logger')
    def _mock_change_logger(request):
        body = request.json
        body.pop('entity_id')
        body['change_info'].pop('object_id')
        assert body == {
            'park_id': PARK_ID,
            'change_info': {
                'object_type': 'Taximeter.Core.Models.User',
                'diff': [
                    {'field': 'Enable', 'new': 'True', 'old': ''},
                    {'field': 'Group', 'new': 'Administrators', 'old': ''},
                    {
                        'field': 'Name',
                        'new': 'Диспетчеров Диспетчер',
                        'old': '',
                    },
                    {'field': 'Phones', 'new': '+71231231212', 'old': ''},
                ],
            },
            'author': {
                'dispatch_user_id': '',
                'display_name': 'Techsupport',
                'user_ip': '1.2.3.4',
            },
        }
        return {}

    request_body = build_request()
    response = await taxi_fleet_users.post(
        ENDPOINT,
        headers=build_headers(provider='yandex_team'),
        json=request_body,
    )

    assert response.status == 200
    user_id = response.json().get('user_id', '')
    assert response.json() == check_response(request_body, user_id)

    utils.check_created_user(pgsql, request_body, PARK_ID)


@pytest.mark.config(
    PARKS_MODIFICATIONS_WITH_ABSENT_USER_NAME={
        'enabled': True,
        'log_default_name': 'No name',
    },
)
@pytest.mark.now('2019-01-01T01:00:00+00:00')
async def test_success_author_no_name(
        mockserver,
        taxi_fleet_users,
        personal_phones_store,
        dac_parks_group_list,
        fleet_parks_shard,
        mock_fleet_parks_list,
        pgsql,
):
    @mockserver.json_handler('/driver-work-rules/service/v1/change-logger')
    def _mock_change_logger(request):
        body = request.json
        body.pop('entity_id')
        body['change_info'].pop('object_id')
        assert body == {
            'park_id': PARK_ID,
            'change_info': {
                'object_type': 'Taximeter.Core.Models.User',
                'diff': [
                    {'field': 'Enable', 'new': 'True', 'old': ''},
                    {'field': 'Group', 'new': 'Administrators', 'old': ''},
                    {
                        'field': 'Name',
                        'new': 'Диспетчеров Диспетчер',
                        'old': '',
                    },
                    {'field': 'Phones', 'new': '+71231231212', 'old': ''},
                ],
            },
            'author': {
                'dispatch_user_id': 'author_id',
                'display_name': 'No name',
                'user_ip': '1.2.3.4',
            },
        }
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
                    'passport_uid': UID,
                    'is_enabled': True,
                    'is_confirmed': False,
                    'is_superuser': False,
                    'is_multifactor_authentication_required': True,
                    'is_usage_consent_accepted': False,
                },
            ],
        }

    request_body = build_request()
    response = await taxi_fleet_users.post(
        ENDPOINT, headers=build_headers(), json=request_body,
    )

    assert response.status == 200
    user_id = response.json().get('user_id', '')
    assert response.json() == check_response(request_body, user_id)

    utils.check_created_user(pgsql, request_body, PARK_ID)


async def test_failed_user_with_phone_id_exist(
        taxi_fleet_users,
        personal_phones_store,
        dac_parks_group_list,
        dac_parks_users_list,
        mock_fleet_parks_list,
        pgsql,
):
    response = await taxi_fleet_users.post(
        ENDPOINT,
        headers=build_headers(park_id=PARK_ID),
        json=build_request(phone='+74564564545'),
    )

    assert response.status == 400
    assert response.json() == {
        'code': 'non_confirmed_user_already_exists',
        'message': 'Non-confirmed user already exists in park',
    }
    assert utils.get_users_count(pgsql) == 5


async def test_failed_group_not_found(
        mockserver,
        taxi_fleet_users,
        dac_parks_users_list,
        pgsql,
        mock_fleet_parks_list,
):
    @mockserver.json_handler('/dispatcher-access-control/v1/parks/groups/list')
    def _mock(request):
        return {'groups': []}

    response = await taxi_fleet_users.post(
        ENDPOINT, headers=build_headers(), json=build_request(),
    )

    assert response.status == 400
    assert response.json() == {
        'code': 'group_not_found',
        'message': 'Group was not found',
    }
    assert utils.get_users_count(pgsql) == 5


async def test_failed_park_not_found(
        mockserver, taxi_fleet_users, pgsql, mock_fleet_parks_list,
):
    response = await taxi_fleet_users.post(
        ENDPOINT, headers=build_headers(park_id='222'), json=build_request(),
    )

    assert response.status == 400
    assert response.json() == {
        'code': 'park_not_found',
        'message': 'Park not found',
    }
    assert utils.get_users_count(pgsql) == 5


async def test_failed_superuser_no_yandex_team(
        taxi_fleet_users,
        dac_parks_group_list,
        dac_parks_users_list,
        mock_fleet_parks_list,
        pgsql,
):
    request_body = build_request(group_id='super')
    response = await taxi_fleet_users.post(
        ENDPOINT, headers=build_headers(), json=request_body,
    )

    assert response.status == 400
    assert response.json() == {
        'code': 'cannot_create_director',
        'message': 'Not YandexTeam user',
    }
    assert utils.get_users_count(pgsql) == 5


async def test_failed_director_already_exists(
        mockserver,
        taxi_fleet_users,
        dac_parks_group_list,
        mock_fleet_parks_list,
        dac_parks_users_platform_roles,
        pgsql,
):
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
                    'passport_uid': UID,
                    'display_name': 'author',
                    'is_enabled': True,
                    'is_confirmed': False,
                    'group_id': 'super',
                    'is_superuser': True,
                    'is_multifactor_authentication_required': True,
                    'is_usage_consent_accepted': False,
                },
            ],
        }

    request_body = build_request(group_id='super')
    response = await taxi_fleet_users.post(
        ENDPOINT,
        headers=build_headers(provider='yandex_team'),
        json=request_body,
    )

    assert response.status == 400
    assert response.json() == {
        'code': 'director_already_exists',
        'message': 'Director already exists',
    }
    assert utils.get_users_count(pgsql) == 5
