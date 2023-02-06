import collections

import pytest


def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


@pytest.fixture(name='parks')
def _parks(mockserver):
    class ParksContext:
        def __init__(self):
            self.stats = collections.defaultdict(int)

    context = ParksContext()

    @mockserver.json_handler('/parks/driver-profiles/car-bindings')
    def _bind_car(request):
        return {}

    @mockserver.json_handler('/parks/courier/car-create')
    def _create_car(request):
        return {'id': 'car1'}

    @mockserver.json_handler('/parks/internal/driver-profiles/create')
    def _create_profile(request):
        assert 'courier_app' in request.json['driver_profile']
        accounts = request.json['accounts']
        assert accounts == [{'type': 'current', 'balance_limit': '0'}]
        context.stats['created'] += 1
        return {
            'driver_profile': {
                'id': 'driver1',
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

    @mockserver.json_handler('/parks/internal/driver-profiles/profile')
    def _update_profile(request):
        context.stats['updated'] += 1
        return {
            'driver_profile': {
                'id': 'driver1',
                'park_id': 'park1',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'phones': ['phone'],
            },
        }

    @mockserver.json_handler('/parks/internal/driver-profiles/personal')
    def _update_personal(request):
        context.stats['personal'] += 1
        return {
            'driver_profile': {
                'id': 'driver1',
                'park_id': 'park1',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'phones': ['+7'],
            },
        }

    return context


@pytest.fixture(name='driver_mode_subscription')
def _driver_mode_subscription(mockserver):
    class DriverModeSubscriptionContext:
        def __init__(self):
            self.orders_provider = None

        def set_orders_provider(self, orders_provider):
            self.orders_provider = orders_provider

    context = DriverModeSubscriptionContext()

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/reset')
    def _reset_mode(request):
        if context.orders_provider == 'retail':
            assert request.json['supported_display_modes'] == [
                'eda_retail_pickers',
            ]
        else:
            assert request.json['supported_display_modes'] == ['courier']
        return {
            'active_mode': 'some_mode',
            'active_mode_type': 'some_type',
            'active_since': '2020-01-01T00:00:00-00:00',
        }

    return context


EDA_LEGACY_WORKING = {
    'park_id': 'park1',
    'courier_id': 'courier1',
    'courier_app': 'taximeter',
    'transport_type': 'pedestrian',
    'full_name': 'first_name middle_name last_name',
    'phone': '+70000000001',
    'orders_provider': 'eda',
    'work_status': 'working',
    'birth_date': '1990-02-03',
}
EDA_WORKING = {
    'park_id': 'park1',
    'courier_id': 'courier2',
    'courier_app': 'taximeter',
    'transport_type': 'pedestrian',
    'first_name': 'first_name',
    'middle_name': 'middle_name',
    'last_name': 'last_name',
    'phone': '+70000000001',
    'orders_provider': 'eda',
    'work_status': 'working',
    'birth_date': '1990-02-03',
}
LAVKA_WORKING = {
    'park_id': 'park1',
    'courier_id': 'courier3',
    'courier_app': 'taximeter',
    'transport_type': 'pedestrian',
    'first_name': 'first_name',
    'middle_name': 'middle_name',
    'last_name': 'last_name',
    'phone': '+70000000001',
    'orders_provider': 'lavka',
    'work_status': 'working',
    'birth_date': '1990-02-03',
}
LAVKA_ROVER = {
    'park_id': 'park1',
    'courier_id': 'courier3',
    'courier_app': 'taximeter',
    'transport_type': 'rover',
    'first_name': 'first_name',
    'middle_name': 'middle_name',
    'last_name': 'last_name',
    'phone': '+70000000001',
    'orders_provider': 'lavka',
    'work_status': 'working',
    'birth_date': '1990-02-03',
}
LAVKA_FIRED = {
    'park_id': 'park1',
    'courier_id': 'courier4',
    'courier_app': 'taximeter',
    'transport_type': 'pedestrian',
    'first_name': 'first_name',
    'middle_name': 'middle_name',
    'last_name': 'last_name',
    'phone': '+70000000001',
    'orders_provider': 'lavka',
    'work_status': 'fired',
    'birth_date': '1990-02-03',
}
RETAIL_PICKER = {
    'park_id': 'park1',
    'courier_id': 'courier2',
    'courier_app': 'taximeter',
    'transport_type': 'pedestrian',
    'first_name': 'first_name',
    'middle_name': 'middle_name',
    'last_name': 'last_name',
    'phone': '+70000000001',
    'orders_provider': 'retail',
    'work_status': 'working',
    'birth_date': '1990-02-03',
}
ENERGIZER_PICKER = {
    'park_id': 'park1',
    'courier_id': 'courier2',
    'courier_app': 'taximeter',
    'transport_type': 'pedestrian',
    'first_name': 'first_name',
    'middle_name': 'middle_name',
    'last_name': 'last_name',
    'phone': '+70000000001',
    'orders_provider': 'taxi',
    'work_status': 'working',
    'car_category': 'scooters',
    'birth_date': '1990-02-03',
}


@pytest.mark.parametrize(
    ('create_request', 'profiles', 'stats', 'expected_code'),
    [
        pytest.param(
            {
                'park_id': 'park1',
                'courier_id': 'courier4',
                'transport_type': 'pedestrian',
                'full_name': 'first_name middle_name last_name',
                'phone': '+70000000001',
                'orders_provider': 'eda',
            },
            None,
            {},
            400,
            id='courier_app field is missing -> bad request',
        ),
        pytest.param(LAVKA_FIRED, None, {}, 404, id='lavka fired profile'),
        pytest.param(
            EDA_LEGACY_WORKING,
            None,
            {'created': 1},
            200,
            id='eda profile with legacy name',
        ),
        pytest.param(EDA_WORKING, None, {'created': 1}, 200, id='eda profile'),
        pytest.param(
            {**EDA_WORKING, 'full_name': 'first_name middle_name last_name'},
            None,
            {'created': 1},
            200,
            id='mixed names',
        ),
        pytest.param(
            LAVKA_WORKING, None, {'created': 1}, 200, id='lavka profile',
        ),
        pytest.param(
            LAVKA_ROVER, None, {'created': 1}, 200, id='rover profile',
        ),
        pytest.param(
            RETAIL_PICKER, None, {'created': 1}, 200, id='picker profile',
        ),
        pytest.param(
            ENERGIZER_PICKER,
            None,
            {'created': 1},
            200,
            id='energizer profile',
        ),
        pytest.param(
            {**LAVKA_WORKING, 'orders_provider': 'kafka'},
            None,
            {},
            400,
            id='invalid provider',
        ),
        pytest.param(
            {**EDA_WORKING, 'phone': '70000000001'},
            None,
            {},
            400,
            id='invalid phone',
        ),
        pytest.param(
            {**EDA_WORKING, 'phone': '+7000000000'},
            None,
            {},
            400,
            id='invalid phone',
        ),
        pytest.param(
            {**EDA_LEGACY_WORKING, 'full_name': 'first_name'},
            None,
            {},
            400,
            id='invalid name',
        ),
        pytest.param(
            EDA_WORKING,
            [EDA_WORKING],
            {'updated': 1, 'personal': 1},
            200,
            id='update eda profile',
        ),
        pytest.param(
            EDA_WORKING,
            [{**EDA_WORKING, 'park_id': 'park2'}],
            {'created': 1, 'updated': 1},
            200,
            id='create and disable',
        ),
        pytest.param(
            EDA_WORKING,
            [EDA_WORKING, {**EDA_WORKING, 'park_id': 'park2'}],
            {'updated': 2, 'personal': 1},
            200,
            id='update and disable',
        ),
        pytest.param(
            merge_dicts(EDA_WORKING, {'deaf': True}),
            [EDA_WORKING],
            {'updated': 1, 'personal': 1},
            200,
            id='update deaf flag not existing in profile',
        ),
        pytest.param(
            merge_dicts(EDA_WORKING, {'deaf': True}),
            [merge_dicts(EDA_WORKING, {'deaf': False})],
            {'updated': 1, 'personal': 1},
            200,
            id='update deaf flag existing in profile',
        ),
        pytest.param(
            merge_dicts(EDA_WORKING, {'has_health_card': True}),
            [EDA_WORKING],
            {'updated': 1, 'personal': 1},
            200,
            id='update has_health_card flag not existing in profile',
        ),
        pytest.param(
            merge_dicts(EDA_WORKING, {'has_health_card': True}),
            [merge_dicts(EDA_WORKING, {'has_health_card': False})],
            {'updated': 1, 'personal': 1},
            200,
            id='update has_health_card flag existing in profile',
        ),
        pytest.param(
            merge_dicts(EDA_WORKING, {'fixed_shifts_enabled': True}),
            [EDA_WORKING],
            {'updated': 1, 'personal': 1},
            200,
            id='update fixed_shifts_enabled flag not existing in profile',
        ),
        pytest.param(
            merge_dicts(EDA_WORKING, {'fixed_shifts_enabled': True}),
            [merge_dicts(EDA_WORKING, {'fixed_shifts_enabled': False})],
            {'updated': 1, 'personal': 1},
            200,
            id='update fixed_shifts_enabled flag existing in profile',
        ),
        pytest.param(
            LAVKA_FIRED,
            [{**LAVKA_FIRED, 'work_status': 'working'}],
            {'updated': 1, 'personal': 1},
            200,
            id='disable existing profile',
        ),
        pytest.param(
            LAVKA_FIRED,
            [{**LAVKA_FIRED, 'park_id': 'park2'}],
            {},
            404,
            id='skip existing profile',
        ),
        pytest.param(
            {**LAVKA_FIRED, 'work_status': 'working'},
            [LAVKA_FIRED],
            {'updated': 1, 'personal': 1},
            200,
            id='enable existing profile',
        ),
    ],
)
async def test_sync_courier(
        taxi_cargo_misc,
        parks,
        driver_profiles,
        contractor_profession,
        driver_mode_subscription,
        mockserver,
        create_request,
        profiles,
        stats,
        expected_code,
):
    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        assert request.json['provider_id'] == 'cargo-misc'
        property_tag_map = {
            'use_health_card': 'medical_card',
            'fixed_shifts_enabled': 'fixed_shifts',
        }

        for property_name in list(property_tag_map):
            tag_name = property_tag_map[property_name]
            if property_name in create_request:
                if create_request[property_name]:
                    tags = request.json['append']
                else:
                    tags = request.json['remove']

                assert tags is not None

                assert tags[0]['entity_type'] == 'dbid_uuid'
                tag_found = False
                for tag_description in tags[0]['tags']:
                    if tag_description['name'] == tag_name:
                        assert (
                            tag_description['entity']
                            == create_request['park_id'] + '_driver1'
                        )
                        tag_found = True
                assert tag_found
        return {}

    if profiles:
        driver_profiles.set_profiles(profiles)

    driver_mode_subscription.set_orders_provider(
        create_request['orders_provider'],
    )

    response = await taxi_cargo_misc.post(
        '/couriers/eats/v1/sync', json=create_request,
    )
    assert response.status_code == expected_code
    if response.status_code == 200:
        assert response.json() == {
            'park_id': create_request['park_id'],
            'driver_id': 'driver1',
            'car_id': 'car1',
        }
        update_profession_times = 0 if stats.get('created', 0) else 1
        assert (
            contractor_profession.handler.times_called
            == update_profession_times
        )
    assert parks.stats == stats


async def test_update_courier(
        taxi_cargo_misc,
        parks,
        contractor_profession,
        driver_profiles,
        driver_mode_subscription,
):
    driver_profiles.set_profiles([LAVKA_WORKING])
    driver_mode_subscription.set_orders_provider(
        LAVKA_WORKING['orders_provider'],
    )

    response = await taxi_cargo_misc.post(
        '/couriers/eats/v1/sync',
        json={**LAVKA_WORKING, 'courier_app': 'eats', 'switch_app': False},
    )
    assert response.status_code == 200
    if response.status_code == 200:
        assert response.json() == {
            'park_id': LAVKA_WORKING['park_id'],
            'driver_id': 'driver1',
            'car_id': 'car1',
        }
        assert contractor_profession.handler.times_called == 1
    assert parks.stats


async def test_sync_is_readonly_eats_courier(taxi_cargo_misc, mockserver):
    @mockserver.json_handler(
        '/driver-profiles/v1/courier/profiles/retrieve_by_eats_id',
    )
    def _retrieve_by_eats_id(request):
        assert request.json == {
            'eats_courier_id_in_set': ['courier2'],
            'projection': ['data.is_readonly'],
        }
        return {
            'courier_by_eats_id': [
                {
                    'eats_courier_id': 'courier2',
                    'profiles': [
                        {
                            'park_driver_profile_id': 'park1_driver1',
                            'data': {'is_readonly': True},
                        },
                    ],
                },
            ],
        }

    response = await taxi_cargo_misc.post(
        '/couriers/eats/v1/sync', json=EDA_WORKING,
    )
    assert response.status_code == 400
