import pytest


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_misc_couriers',
    consumers=['cargo-misc/couriers'],
    clauses=[],
    default_value={'car_category': 'courier'},
)
@pytest.mark.parametrize(
    'create_request, expected_code',
    [
        (
            {
                'operation_id': '87654321',
                'park_id': 'park_id',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'middle_name': 'middle_name',
                'phone': '+70000000001',
                'birth_date': '1900-01-01',
                'courier_type': 'walking_courier',
                'hiring_source': 'selfreg',
            },
            200,
        ),
        (
            {
                'operation_id': '8765432',
                'park_id': 'park_id',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'middle_name': 'middle_name',
                'phone': '+70000000001',
                'birth_date': '1900-01-01',
                'courier_type': 'walking_courier',
            },
            400,
        ),
        (
            {
                'operation_id': '87654321',
                'park_id': 'park_id',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'middle_name': 'middle_name',
                'phone': '70000000001',
                'birth_date': '1900-01-01',
                'courier_type': 'walking_courier',
            },
            400,
        ),
        (
            {
                'operation_id': '87654321',
                'park_id': 'park_id',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'middle_name': 'middle_name',
                'phone': '+7000000000',
                'birth_date': '1900-01-01',
                'courier_type': 'walking_courier',
            },
            400,
        ),
        (
            {
                'operation_id': '12345678',
                'park_id': 'park_id',
                'full_name': 'last_name first_name middle-name',
                'phone': '+70000000002',
                'birth_date': '1900-01-01',
                'courier_type': 'walking_courier',
                'balance_limit': '1337',
            },
            200,
        ),
        (
            {
                'operation_id': '12345678',
                'park_id': 'park_id',
                'full_name': 'last_name first_name middle_name',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'middle_name': 'middle_name',
                'phone': '+70000000002',
                'birth_date': '1900-01-01',
                'courier_type': 'walking_courier',
            },
            400,
        ),
        (
            {
                'operation_id': '12345678',
                'park_id': 'park_id',
                'first_name': 'first_name',
                'middle_name': 'middle_name',
                'phone': '+70000000002',
                'birth_date': '1900-01-01',
                'courier_type': 'walking_courier',
            },
            400,
        ),
        (
            {
                'operation_id': '12345678',
                'park_id': 'park_id',
                'full_name': 'last_name first_name middle-name',
                'phone': '+70000000002',
                'birth_date': '1900-01',
                'courier_type': 'walking_courier',
            },
            400,
        ),
        (
            {
                'operation_id': '12345678',
                'park_id': 'park_id',
                'full_name': 'last_name first_name middle-name',
                'phone': '+70000000002',
                'birth_date': '1900-01-111',
                'courier_type': 'walking_courier',
            },
            400,
        ),
        (
            {
                'operation_id': '12345678',
                'park_id': 'park_id',
                'full_name': 'last_name first_name middle-name',
                'phone': '+70000000002',
                'birth_date': '1900-01-01',
                'courier_type': 'unknowntype',
            },
            400,
        ),
        (
            {
                'operation_id': '87654321',
                'park_id': 'park_id',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'middle_name': 'middle_name',
                'phone': '+79955020519',
                'birth_date': '1965-09-25',
                'courier_type': 'walking_courier',
                'hiring_source': 'selfreg',
            },
            400,
        ),
        # Correct 'Беларусь' phone number
        (
            {
                'operation_id': '12345677',
                'park_id': 'park_id',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'middle_name': 'middle_name',
                'phone': '+375456789012',
                'birth_date': '1900-01-01',
                'courier_type': 'walking_courier',
                'hiring_source': 'selfreg',
            },
            200,
        ),
        # Check that phone number validation of not-cashed сountries failed
        (
            {
                'operation_id': '12345677',
                'park_id': 'park_id',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'middle_name': 'middle_name',
                'phone': '+12345678901',
                'birth_date': '1900-01-01',
                'courier_type': 'walking_courier',
                'hiring_source': 'selfreg',
            },
            400,
        ),
        # Test successful courier profile creation with passport uid
        (
            {
                'operation_id': '87654321',
                'park_id': 'park_id',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'middle_name': 'middle_name',
                'phone': '+70000000001',
                'passport_uid': '1122334455',
                'birth_date': '1900-01-01',
                'courier_type': 'walking_courier',
                'hiring_source': 'selfreg',
            },
            200,
        ),
        # Test failed courier profile creation with passport uid
        (
            {
                'operation_id': '87654321',
                'park_id': 'park_id',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'middle_name': 'middle_name',
                'phone': '+70000000001',
                'passport_uid': '9988776655',
                'birth_date': '1900-01-01',
                'courier_type': 'walking_courier',
                'hiring_source': 'selfreg',
            },
            400,
        ),
        # Test successful courier profile creation with defined uid
        (
            {
                'operation_id': '87654321',
                'park_id': 'park_id',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'middle_name': 'middle_name',
                'phone': '+70000000001',
                'passport_uid': '1122334455',
                'birth_date': '1900-01-01',
                'courier_type': 'walking_courier',
                'hiring_source': 'selfreg',
                'courier_id': '1111122222333334444455555',
            },
            200,
        ),
    ],
)
async def test_create_courier(
        taxi_cargo_misc,
        mockserver,
        mocker_fleet_parks_list,
        stq,
        stq_runner,
        pgsql,
        create_request,
        expected_code,
):
    expected_balance_limit = create_request.get('balance_limit', '5')
    park_id = create_request.get('park_id')

    mocker_fleet_parks_list(park_id)

    @mockserver.json_handler('/parks/courier/car-create')
    def _create_car(request):
        return {'id': 'car_id'}

    @mockserver.json_handler('/parks/internal/driver-profiles/create')
    def _create_profile(request):
        profile = request.json['driver_profile']
        balance_limit = request.json['accounts'][0]['balance_limit']
        assert balance_limit == expected_balance_limit
        assert profile['profession_id'] == 'walking-courier'
        if profile['phones'][0] == '+79955020519':
            return mockserver.make_response(
                json={
                    'error': {
                        'code': 'duplicate_phone',
                        'text': 'duplicate_phone',
                    },
                },
                status=400,
            )
        if (
                'platform_uid' in profile
                and profile['platform_uid'] == '9988776655'
        ):
            return mockserver.make_response(
                json={
                    'error': {
                        'code': 'duplicate_platform_uid',
                        'text': 'duplicate_platform_uid',
                    },
                },
                status=400,
            )
        if 'hiring_source' in create_request:
            assert profile['hiring_source'] == create_request['hiring_source']
        if 'passport_uid' in create_request:
            assert profile['platform_uid'] == create_request['passport_uid']
        response = {
            'driver_profile': {
                'id': 'driver_id',
                'park_id': 'some_string',
                'first_name': 'some_string',
                'last_name': 'some_string',
                'phones': ['+70000000000'],
                'hire_date': '2020-01-01T00:00:00Z',
                'driver_license': {
                    'country': 'rus',
                    'expiration_date': '2035-01-01T00:00:00Z',
                    'issue_date': '2018-01-01T00:00:00Z',
                    'number': '123456',
                    'normalized_number': '123456',
                },
                'providers': [],
                'work_status': 'working',
            },
        }
        if 'platform_uid' in profile:
            response['driver_profile']['platform_uid'] = profile[
                'platform_uid'
            ]
        return response

    @mockserver.json_handler('/parks/driver-profiles/car-bindings')
    def _bind_car(request):
        return {}

    @mockserver.json_handler('/tags/v1/upload')
    def _tags(request):
        assert request.json['tags'] == [
            {'name': 'walking_courier', 'match': {'id': 'park_id_driver_id'}},
        ]
        return {}

    response = await taxi_cargo_misc.post(
        '/couriers/v1/create', json=create_request,
    )
    assert response.status_code == expected_code
    response = await taxi_cargo_misc.post(
        '/couriers/v1/create', json=create_request,
    )
    assert response.status_code == expected_code

    if expected_code == 200:
        assert response.json() == {
            'park_id': 'park_id',
            'driver_id': 'driver_id',
            'car_id': 'car_id',
        }

        cursor = pgsql['cargo_claims'].conn.cursor()
        cursor.execute('SELECT driver_id, car_id FROM cargo_misc.couriers')
        values = list(cursor)
        assert len(values) == 1
        assert values[0][0] == 'driver_id'
        assert values[0][1] == 'car_id'


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_misc_couriers',
    consumers=['cargo-misc/couriers'],
    clauses=[],
    default_value={'car_category': 'courier'},
)
@pytest.mark.parametrize(
    'full_name, expected_last_name, expected_first_name, '
    'expected_middle_name, code',
    [
        ('last first middle', 'last', 'first', 'middle', 200),
        ('last    first', 'last', 'first', None, 200),
        ('first', None, 'first', None, 400),
        (
            'last first second middle something',
            None,
            'last first second middle something',
            None,
            400,
        ),
    ],
)
async def test_courier_add_full_name(
        taxi_cargo_misc,
        mockserver,
        mocker_fleet_parks_list,
        stq,
        stq_runner,
        pgsql,
        full_name,
        expected_last_name,
        expected_first_name,
        expected_middle_name,
        code,
):
    mocker_fleet_parks_list(park_id='some_string')

    @mockserver.json_handler('/parks/courier/car-create')
    def _create_car(request):
        return {'id': 'car_id'}

    @mockserver.json_handler('/parks/driver-profiles/car-bindings')
    def _bind_car(request):
        return {}

    @mockserver.json_handler('/parks/internal/driver-profiles/create')
    def _create_profile(request):
        driver_profile = request.json['driver_profile']
        assert driver_profile['first_name'] == expected_first_name
        assert driver_profile['last_name'] == expected_last_name
        assert driver_profile.get('middle_name', None) == expected_middle_name

        accounts = request.json['accounts']
        assert accounts == [{'type': 'current', 'balance_limit': '5'}]

        return {
            'driver_profile': {
                'id': 'driver_id',
                'park_id': 'some_string',
                'first_name': 'some_string',
                'last_name': 'some_string',
                'phones': ['+70000000000'],
                'hire_date': '2020-01-01T00:00:00Z',
                'driver_license': {
                    'country': 'rus',
                    'expiration_date': '2035-01-01T00:00:00Z',
                    'issue_date': '2018-01-01T00:00:00Z',
                    'number': '123456',
                    'normalized_number': '123456',
                },
                'providers': [],
                'work_status': 'working',
            },
        }

    @mockserver.json_handler('/tags/v1/upload')
    def _tags(request):
        return {}

    response = await taxi_cargo_misc.post(
        '/couriers/v1/create',
        json={
            'operation_id': '12345678',
            'park_id': 'some_string',
            'full_name': full_name,
            'phone': '+70000000001',
            'birth_date': '1900-01-01',
            'courier_type': 'walking_courier',
        },
    )
    assert response.status_code == code


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_misc_couriers',
    consumers=['cargo-misc/couriers'],
    clauses=[
        {
            'title': 'Enabled',
            'predicate': {
                'init': {
                    'set': ['blr'],
                    'arg_name': 'country_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
            'value': {'car_category': 'limousine'},
        },
    ],
    default_value={'car_category': 'courier'},
)
@pytest.mark.parametrize(
    'country_id, expected_code', [('blr', 200), ('rus', 200), ('blr', 500)],
)
async def test_create_courier_with_exp(
        taxi_cargo_misc,
        mockserver,
        mocker_fleet_parks_list,
        country_id,
        expected_code,
):
    create_request = {
        'operation_id': '87654321',
        'park_id': 'park_id',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'middle_name': 'middle_name',
        'phone': '+70000000001',
        'birth_date': '1900-01-01',
        'courier_type': 'walking_courier',
        'hiring_source': 'selfreg',
    }
    park_id = create_request.get('park_id')
    mocker_fleet_parks_list(
        park_id if expected_code == 200 else None, country_id,
    )

    @mockserver.json_handler('/parks/courier/car-create')
    def _create_car(request):
        assert (
            request.json['category'] == ['limousine']
            if country_id == 'blr'
            else ['courier']
        )
        return {'id': 'car_id'}

    @mockserver.json_handler('/parks/driver-profiles/car-bindings')
    def _bind_car(request):
        return {}

    @mockserver.json_handler('/parks/internal/driver-profiles/create')
    def _create_profile(request):
        return {
            'driver_profile': {
                'id': 'driver_id',
                'park_id': park_id,
                'first_name': 'some_string',
                'last_name': 'some_string',
                'phones': ['+70000000000'],
                'hire_date': '2020-01-01T00:00:00Z',
                'driver_license': {
                    'country': country_id,
                    'expiration_date': '2035-01-01T00:00:00Z',
                    'issue_date': '2018-01-01T00:00:00Z',
                    'number': '123456',
                    'normalized_number': '123456',
                },
                'providers': [],
                'work_status': 'working',
            },
        }

    @mockserver.json_handler('/tags/v1/upload')
    def _tags(request):
        return {}

    response = await taxi_cargo_misc.post(
        '/couriers/v1/create', json=create_request,
    )
    assert response.status_code == expected_code
