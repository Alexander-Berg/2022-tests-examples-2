# pylint: disable=import-error
import json

# pylint: disable=import-error
import pytest


@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'archive_main_route': {
            'driver': (
                'shuttle_control.routes.archive_main_route.name_for_driver'
            ),
            'passenger': (
                'shuttle_control.routes.archive_main_route.name_for_passenger'
            ),
        },
        'main_route': {
            'driver': 'shuttle_control.routes.main_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.main_route.name_for_passenger'
            ),
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_admin_history_by_single_field(
        taxi_shuttle_control, mockserver, load_json,
):
    @mockserver.json_handler('/zalogin/v1/internal/phone-info')
    def _mock_zalogin(request):
        assert dict(request.args) == {'phone_id': 'user_phone_id'}
        return {'items': [{'yandex_uid': '0123456777', 'type': 'portal'}]}

    @mockserver.json_handler('/user-api/user_phones/by_number/retrieve')
    def _mock_user_api(request):
        assert request.json == {
            'phone': '+79998887766',
            'type': 'yandex',
            'primary_replica': False,
        }
        return load_json('user_phones_response.json')

    @mockserver.json_handler('/personal/v1/driver_licenses/find')
    def _mock_personal(request):
        assert request.json == {
            'value': 'ВУ000111222',
            'primary_replica': False,
        }
        return {'id': 'driver_license_pd_id', 'value': 'ВУ000111222'}

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_license',
    )
    def _mock_driver_profiles(request):
        assert request.json == load_json(
            'driver_profiles_by_license_request.json',
        )
        assert dict(request.args) == {'consumer': 'shuttle-control'}
        return load_json('driver_profiles_by_license_response.json')

    state_items = load_json('state_history_items.json')
    archive_items = load_json('archive_history_items.json')

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/admin/booking/list',
        headers={'Accept-Language': 'en'},
        json={'driver_license': 'ВУ000111222'},
    )
    assert response.status_code == 200
    assert _mock_driver_profiles.times_called == 1
    assert response.json() == {'items': [state_items[1]]}

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/admin/booking/list',
        headers={'Accept-Language': 'en'},
        json={'user_phone': '+79998887766'},
    )
    assert response.status_code == 200
    assert _mock_user_api.times_called == 1
    assert _mock_zalogin.times_called == 1
    assert response.json() == {'items': [archive_items[1]]}

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/admin/booking/list',
        headers={'Accept-Language': 'en'},
        json={'order_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775'},
    )
    assert response.status_code == 200
    assert response.json() == {'items': [state_items[1]]}

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/admin/booking/list',
        headers={'Accept-Language': 'en'},
        json={'order_id': '2fef68c0-25d0-4174-9dd0-bdd1b3730775'},
    )
    assert response.status_code == 200
    assert response.json() == {'items': [archive_items[1]]}

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/admin/booking/list',
        headers={'Accept-Language': 'en'},
        json={'user_uid': '0123456789'},
    )
    assert response.status_code == 200
    assert response.json() == {'items': state_items}

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/admin/booking/list',
        headers={'Accept-Language': 'en'},
        json={'shuttle_status': 'driving'},
    )
    assert response.status_code == 200
    assert response.json() == {'items': [state_items[0]]}

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/admin/booking/list',
        headers={'Accept-Language': 'en'},
        json={'created_to': '2020-05-18T15:20:00+0000'},
    )
    assert response.status_code == 200
    assert response.json() == {'items': [state_items[1], archive_items[1]]}

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/admin/booking/list',
        headers={'Accept-Language': 'en'},
        json={'created_from': '2020-05-18T15:20:00+0000'},
    )
    assert response.status_code == 200
    assert response.json() == {'items': [state_items[0], archive_items[0]]}

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/admin/booking/list',
        headers={'Accept-Language': 'en'},
        json={'shuttle_status': 'finished'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [archive_items[0], state_items[1], archive_items[1]],
    }


@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'archive_main_route': {
            'admin': (
                'shuttle_control.routes.archive_main_route.name_for_admin'
            ),
            'driver': (
                'shuttle_control.routes.archive_main_route.name_for_driver'
            ),
            'passenger': (
                'shuttle_control.routes.archive_main_route.name_for_passenger'
            ),
        },
        'main_route': {
            'driver': 'shuttle_control.routes.main_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.main_route.name_for_passenger'
            ),
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_admin_history_no_searchable_fields(
        taxi_shuttle_control, mockserver, load_json,
):
    @mockserver.json_handler('/zalogin/v1/internal/phone-info')
    def _mock_zalogin(request):
        assert dict(request.args) == {'phone_id': 'user_phone_id'}
        return {'items': []}

    @mockserver.json_handler('/user-api/user_phones/by_number/retrieve')
    def _mock_user_api(request):
        assert request.json == {
            'phone': '+79998887766',
            'type': 'yandex',
            'primary_replica': False,
        }
        return load_json('user_phones_response.json')

    @mockserver.json_handler('/personal/v1/driver_licenses/find')
    def _mock_personal(request):
        assert request.json == {
            'value': 'ВУ000111222',
            'primary_replica': False,
        }
        return {'id': 'driver_license_pd_id', 'value': 'ВУ000111222'}

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_license',
    )
    def _mock_driver_profiles(request):
        assert request.json == load_json(
            'driver_profiles_by_license_request.json',
        )
        assert dict(request.args) == {'consumer': 'shuttle-control'}
        return load_json('driver_profiles_by_license_response_empty.json')

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/admin/booking/list',
        headers={'Accept-Language': 'en'},
        json={'skip': 0, 'limit': 50},
    )
    assert response.status_code == 200
    assert response.json() == {'items': []}

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/admin/booking/list',
        headers={'Accept-Language': 'en'},
        json={'skip': 0, 'limit': 50, 'user_phone': '+79998887766'},
    )
    assert response.status_code == 200
    assert response.json() == {'items': []}

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/admin/booking/list',
        headers={'Accept-Language': 'en'},
        json={'skip': 0, 'limit': 50, 'driver_license': 'ВУ000111222'},
    )
    assert response.status_code == 200
    assert response.json() == {'items': []}


@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'archive_main_route': {
            'driver': (
                'shuttle_control.routes.archive_main_route.name_for_driver'
            ),
            'passenger': (
                'shuttle_control.routes.archive_main_route.name_for_passenger'
            ),
        },
        'main_route': {
            'driver': 'shuttle_control.routes.main_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.main_route.name_for_passenger'
            ),
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_admin_history_combined(taxi_shuttle_control, load_json):
    state_items = load_json('state_history_items.json')

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/admin/booking/list',
        headers={'Accept-Language': 'en'},
        json={'user_uid': '0123456789', 'shuttle_status': 'driving'},
    )
    assert response.status_code == 200
    assert response.json() == {'items': [state_items[0]]}

    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/admin/booking/list',
        headers={'Accept-Language': 'en'},
        json={
            'user_uid': '0123456789',
            'created_to': '2020-05-18T15:20:00+0000',
            'created_from': '2020-05-18T14:59:00+0000',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'items': [state_items[1]]}


@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'archive_main_route': {
            'admin': (
                'shuttle_control.routes.archive_main_route.name_for_admin'
            ),
            'driver': (
                'shuttle_control.routes.archive_main_route.name_for_driver'
            ),
            'passenger': (
                'shuttle_control.routes.archive_main_route.name_for_passenger'
            ),
        },
        'main_route': {
            'driver': 'shuttle_control.routes.main_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.main_route.name_for_passenger'
            ),
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_admin_history_item(taxi_shuttle_control, mockserver, load_json):
    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _mock_fleet_vehicles(request):
        assert json.loads(request.get_data()) == {
            'id_in_set': ['park_01_car_02'],
        }
        assert dict(request.args) == {'consumer': 'shuttle-control'}
        return load_json('fleet_vehicles_response.json')

    @mockserver.json_handler('/fleet-parks/v1/parks/contacts/retrieve')
    def _mock_fleet_parks_contacts(request):
        assert dict(request.args) == {'park_id': 'park_01'}
        return load_json('fleet_parks_contacts_response.json')

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks_list(request):
        assert json.loads(request.get_data()) == {
            'query': {'park': {'ids': ['park_01']}},
        }
        return load_json('fleet_parks_list_response.json')

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        assert dict(request.args) == {'consumer': 'shuttle-control'}
        assert json.loads(request.get_data()) == {
            'id_in_set': ['park_01_uuid_1'],
            'projection': [
                'data.car_id',
                'data.phone_pd_ids',
                'data.full_name.first_name',
                'data.full_name.middle_name',
                'data.full_name.last_name',
                'data.uuid',
                'data.license.pd_id',
            ],
        }
        return load_json('driver_profiles_response.json')

    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def _mock_parks_replica(request):
        assert json.loads(request.get_data()) == {
            'id_in_set': ['clid_01'],
            'projection': [
                'data.name',
                'data.long_name',
                'data.phone_pd_id',
                'data.email_pd_id',
                'data.legal_address',
                'data.ogrn',
            ],
        }
        assert dict(request.args) == {'consumer': 'shuttle-control'}
        return load_json('parks_replica_response.json')

    @mockserver.json_handler('/user-api/v3/userinfo')
    def _mock_v3_userinfo(request):
        assert json.loads(request.get_data()) == {'yandex_uid': '0123456666'}
        return {
            'id': 'user_id_3',
            'token_only': True,
            'authorized': True,
            'application': 'android',
            'application_version': '4.8.1.0',
            'phone': {'id': 'some_id', 'personal_id': 'user_id_3_phone_pd_id'},
        }

    @mockserver.json_handler('/user-api/user_emails/get')
    def _mock_emails(request):
        assert json.loads(request.get_data()) == {
            'yandex_uids': ['0123456666'],
            'primary_replica': False,
        }
        return {
            'items': [
                {
                    'id': 'user_id_3',
                    'yandex_uid': '0123456666',
                    'personal_email_id': 'user_id_3_email_pd_id',
                },
            ],
        }

    order_id = '2fef68c7-25d0-4174-9dd0-bdd1b3730776'
    response = await taxi_shuttle_control.get(
        '/internal/shuttle-control/v1/admin/booking/item?id=' + order_id,
        headers={'Accept-Language': 'en'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('history_item_response.json')


@pytest.mark.now('2020-05-18T17:00:00+00:00')
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'archive_main_route': {
            'driver': (
                'shuttle_control.routes.archive_main_route.name_for_driver'
            ),
            'passenger': (
                'shuttle_control.routes.archive_main_route.name_for_passenger'
            ),
        },
        'main_route': {
            'driver': 'shuttle_control.routes.main_route.name_for_driver',
            'passenger': (
                'shuttle_control.routes.main_route.name_for_passenger'
            ),
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main_2.sql'])
async def test_admin_history_item_common_passengers(
        taxi_shuttle_control, mockserver, load_json,
):
    @mockserver.json_handler('/user-api/v3/userinfo')
    def _mock_v3_userinfo(request):
        return {'id': 'some_id', 'token_only': True, 'authorized': True}

    @mockserver.json_handler('/user-api/user_emails/get')
    def _mock_emails(request):
        return {'items': [{'id': 'some_id'}]}

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _mock_fleet_vehicles(request):
        assert json.loads(request.get_data()) == {
            'id_in_set': ['park_01_car_02'],
        }
        assert dict(request.args) == {'consumer': 'shuttle-control'}
        return load_json('fleet_vehicles_response.json')

    @mockserver.json_handler('/fleet-parks/v1/parks/contacts/retrieve')
    def _mock_fleet_parks_contacts(request):
        assert dict(request.args) == {'park_id': 'park_01'}
        return load_json('fleet_parks_contacts_response.json')

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks_list(request):
        assert json.loads(request.get_data()) == {
            'query': {'park': {'ids': ['park_01']}},
        }
        return load_json('fleet_parks_list_response.json')

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        assert dict(request.args) == {'consumer': 'shuttle-control'}
        assert json.loads(request.get_data()) == {
            'id_in_set': ['park_01_uuid_1'],
            'projection': [
                'data.car_id',
                'data.phone_pd_ids',
                'data.full_name.first_name',
                'data.full_name.middle_name',
                'data.full_name.last_name',
                'data.uuid',
                'data.license.pd_id',
            ],
        }
        return load_json('driver_profiles_response.json')

    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def _mock_parks_replica(request):
        assert json.loads(request.get_data()) == {
            'id_in_set': ['clid_01'],
            'projection': [
                'data.name',
                'data.long_name',
                'data.phone_pd_id',
                'data.email_pd_id',
                'data.legal_address',
                'data.ogrn',
            ],
        }
        assert dict(request.args) == {'consumer': 'shuttle-control'}
        return load_json('parks_replica_response.json')

    archive_order_id = '2fef68d7-25d0-4174-9dd0-bdd1b3730776'
    response = await taxi_shuttle_control.get(
        '/internal/shuttle-control/v1/admin/booking/item?id='
        + archive_order_id,
        headers={'Accept-Language': 'en'},
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'archive_history_item_common_passengers_response.json',
    )

    state_order_id = '2fef68c9-25f0-4174-9fd0-bdd1b3730776'
    response = await taxi_shuttle_control.get(
        '/internal/shuttle-control/v1/admin/booking/item?id=' + state_order_id,
        headers={'Accept-Language': 'en'},
    )
    actual = response.json()
    for item in actual['user_info']['common_passengers']:
        ticket = item.get('ticket', None)
        assert ticket is not None
        item.pop('ticket')
    ticket = actual['order_info']['ticket']
    assert ticket is not None
    actual['order_info'].pop('ticket')
    actual['order_info']['status_updates'] = []
    assert response.status_code == 200
    assert actual == load_json(
        'state_history_item_common_passengers_response.json',
    )
