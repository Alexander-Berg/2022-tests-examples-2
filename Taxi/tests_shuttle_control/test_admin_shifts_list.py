# pylint: disable=import-error
import json

# pylint: disable=import-only-modules, import-error, redefined-outer-name
import pytest


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
@pytest.mark.now('2020-01-17T18:17:38+0000')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_main(taxi_shuttle_control, mockserver, load_json):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        assert dict(request.args) == {'consumer': 'shuttle-control'}
        assert json.loads(request.get_data())['projection'] == [
            'data.car_id',
            'data.phone_pd_ids',
            'data.full_name.first_name',
            'data.full_name.middle_name',
            'data.full_name.last_name',
            'data.uuid',
            'data.license.pd_id',
        ]
        return load_json('driver_profiles_response.json')

    response = await taxi_shuttle_control.get(
        '/admin/shuttle-control/v1/shifts/list',
        params={
            'route_name': 'route1',
            'date_from': '2000-01-17T18:17:38+0000',
            'date_to': '2050-01-17T18:17:38+0000',
        },
    )
    assert response.status_code == 200
    sorted_response = sorted(
        response.json(), key=lambda x: x['template_shift_id'],
    )
    assert sorted_response == [
        {
            'template_shift_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775',
            'max_simultaneous_subscriptions': 10,
            'in_operation_since': '2020-05-28T10:40:55+00:00',
            'deprecated_since': '2021-05-28T10:40:55+00:00',
            'shifts': sorted_response[0]['shifts'],
        },
    ]

    assert (
        sorted(sorted_response[0]['shifts'], key=lambda x: x['shift_id'])
        == [
            {
                'shift_id': '427a330d-2506-464a-accf-346b31e288b6',
                'starts_at': '2020-01-16T17:00:00+03:00',
                'ends_at': '2020-01-16T19:00:00+03:00',
                'subscribed_drivers': [],
                'subscriptions_hash': '0',
            },
            {
                'shift_id': '427a330d-2506-464a-accf-346b31e288b7',
                'starts_at': '2020-01-17T13:00:00+03:00',
                'ends_at': '2020-01-17T17:00:00+03:00',
                'subscribed_drivers': [],
                'subscriptions_hash': '0',
            },
            {
                'shift_id': '427a330d-2506-464a-accf-346b31e288b8',
                'starts_at': '2020-01-17T17:00:00+03:00',
                'ends_at': '2020-01-17T21:00:00+03:00',
                'subscribed_drivers': [
                    {
                        'dbid_uuid': '111_888',
                        'name': 'Sergey Viktorovich Ivanov',
                    },
                ],
                'subscriptions_hash': '2902211550890660726',
            },
            {
                'shift_id': '427a330d-2506-464a-accf-346b31e288c2',
                'starts_at': '2020-01-16T17:00:00+03:00',
                'ends_at': '2020-01-16T19:00:00+03:00',
                'subscribed_drivers': [
                    {
                        'dbid_uuid': '111_889',
                        'name': 'Sergey Viktorovich Komarov',
                    },
                ],
                'subscriptions_hash': '2902211550890660725',
            },
        ]
    )


@pytest.mark.now('2020-01-17T18:17:38+0000')
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passenger',
        },
        'route2': {
            'driver': 'shuttle_control.routes.route2.name_for_driver',
            'passenger': 'shuttle_control.routes.route2.name_for_passenger',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_time_range(taxi_shuttle_control, mockserver, load_json):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles(request):
        assert dict(request.args) == {'consumer': 'shuttle-control'}
        assert json.loads(request.get_data())['projection'] == [
            'data.car_id',
            'data.phone_pd_ids',
            'data.full_name.first_name',
            'data.full_name.middle_name',
            'data.full_name.last_name',
            'data.uuid',
            'data.license.pd_id',
        ]
        return load_json('driver_profiles_response.json')

    response = await taxi_shuttle_control.get(
        '/admin/shuttle-control/v1/shifts/list',
        params={
            'route_name': 'route2',
            'date_from': '2020-01-10T14:00:00+0000',
            'date_to': '2020-01-15T14:00:00+0000',
        },
    )
    assert response.status_code == 200
    sorted_response = response.json()
    assert sorted_response == [
        {
            'template_shift_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            'max_simultaneous_subscriptions': 10,
            'in_operation_since': '2020-05-28T10:40:55+00:00',
            'personal_goal': {'payout_amount': 50, 'trips_target': 30},
            'shifts': sorted_response[0]['shifts'],
        },
    ]

    assert (
        sorted(sorted_response[0]['shifts'], key=lambda x: x['shift_id'])
        == [
            {
                'shift_id': '427a330d-2506-464a-accf-346b31e288c1',
                'starts_at': '2020-01-12T17:00:00+03:00',
                'ends_at': '2020-01-12T19:00:00+03:00',
                'subscribed_drivers': [
                    {
                        'dbid_uuid': '111_888',
                        'name': 'Sergey Viktorovich Ivanov',
                    },
                    {
                        'dbid_uuid': '111_889',
                        'name': 'Sergey Viktorovich Komarov',
                    },
                ],
                'subscriptions_hash': '7800322948621125284',
            },
        ]
    )


@pytest.mark.now('2020-01-17T18:17:38+0000')
@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'route1': {
            'driver': 'shuttle_control.routes.route1.name_for_driver',
            'passenger': 'shuttle_control.routes.route1.name_for_passenger',
        },
        'route2': {
            'driver': 'shuttle_control.routes.route2.name_for_driver',
            'passenger': 'shuttle_control.routes.route2.name_for_passenger',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_time_range_error(taxi_shuttle_control, mockserver, load_json):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles_return_error(request):
        assert dict(request.args) == {'consumer': 'shuttle-control'}
        assert json.loads(request.get_data())['projection'] == [
            'data.car_id',
            'data.phone_pd_ids',
            'data.full_name.first_name',
            'data.full_name.middle_name',
            'data.full_name.last_name',
            'data.uuid',
            'data.license.pd_id',
        ]
        return {'code': '400', 'message': 'ERROR'}

    response = await taxi_shuttle_control.get(
        '/admin/shuttle-control/v1/shifts/list',
        params={
            'route_name': 'route2',
            'date_from': '2020-01-10T14:00:00+0000',
            'date_to': '2020-01-15T14:00:00+0000',
        },
    )
    assert response.status_code == 200
    sorted_response = response.json()
    assert sorted_response == [
        {
            'template_shift_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730777',
            'max_simultaneous_subscriptions': 10,
            'in_operation_since': '2020-05-28T10:40:55+00:00',
            'personal_goal': {'payout_amount': 50, 'trips_target': 30},
            'shifts': sorted_response[0]['shifts'],
        },
    ]

    assert (
        sorted(sorted_response[0]['shifts'], key=lambda x: x['shift_id'])
        == [
            {
                'shift_id': '427a330d-2506-464a-accf-346b31e288c1',
                'starts_at': '2020-01-12T17:00:00+03:00',
                'ends_at': '2020-01-12T19:00:00+03:00',
                'subscribed_drivers': [
                    {'dbid_uuid': '111_888', 'name': 'Name is not found'},
                    {'dbid_uuid': '111_889', 'name': 'Name is not found'},
                ],
                'subscriptions_hash': '7800322948621125284',
            },
        ]
    )
