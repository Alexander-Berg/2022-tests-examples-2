import pytest

JOB_NAME = 'eats-profiles-synchronizer'


@pytest.fixture(name='personal')
def _personal(mockserver):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _phone_retrieve(request):
        pd_id = request.json['id']
        return {'value': get_phone(pd_id), 'id': pd_id}


@pytest.fixture(name='eats_core')
def _eats_core(mockserver):
    class Context:
        def __init__(self):
            self.cursor = 'empty_cursor'
            self.profiles = []

        def set_data(self, cursor, profiles):
            self.cursor = cursor
            self.profiles = profiles

    ctx = Context()

    @mockserver.json_handler(
        '/eats-core-integration/server/api/v1/courier/profiles/update',
    )
    def _profiles_update(request):
        return {'cursor': ctx.cursor, 'profiles': ctx.profiles[:3]}

    return ctx


def get_settings(is_enabled):
    return {
        'enabled': is_enabled,
        'job-throttling-delay-ms': 1000,
        'sync-batch-size': 2,
        'profiles-batch-size': 3,
        'profiles-synchonize-size': 2,
    }


async def wait_iteration(taxi_cargo_misc, testpoint, enabled):
    @testpoint('eats-profiles-synchronizer-finished')
    def task_finished(arg):
        pass

    async with taxi_cargo_misc.spawn_task(
            'distlock/eats-profiles-synchronizer',
    ):
        finished = await task_finished.wait_call()
        assert finished['arg']['mode'] == enabled


def make_profile(
        seq_number,
        transport_type,
        provider,
        billing_type,
        courier_service_id=None,
        is_rover=False,
        is_dedicated_picker=False,
):
    profile = {
        'id': f'courier_id_{seq_number}',
        'full_name': 'Courier Name',
        'country_id': '35',
        'country_code': 'RU',
        'region_id': f'region_id_{seq_number}',
        'billing_type': billing_type,
        'transport_type': transport_type,
        'phone_pd_id': f'phone_pd_id_{seq_number}',
        'work_status': 'active',
        'orders_provider': provider,
        'is_rover': is_rover,
        'is_hard_of_hearing': False,
        'cursor': f'cursor_{seq_number}_0',
        'has_health_card': False,
        'has_own_bicycle': False,
        'has_terminal_for_payment_on_site': False,
        'is_dedicated_courier': False,
        'is_dedicated_picker': is_dedicated_picker,
        'is_picker': False,
        'is_storekeeper': False,
        'is_fixed_shifts_option_enabled': False,
        'started_work_at': '2001-04-01T10:00:00+03:00',
        'birthday': '1990-02-03',
    }
    if courier_service_id:
        profile['courier_service_id'] = courier_service_id

    return profile


def get_park(profile):
    mapping = {
        'courier_id_1': 'selfemployed_park_id',
        'courier_id_2': 'park_id_1',
        'courier_id_3': 'park_id_2',
    }
    return mapping[profile['id']]


def get_phone(pd_id):
    return pd_id[:5] + pd_id[11:]


def transform_orders_provider(orders_provider, is_picker):
    if orders_provider == 'shop':
        if is_picker:
            return 'retail'
        return 'eda'
    if orders_provider == 'scooter':
        return 'taxi'
    return orders_provider


def transform_transport(eats_profile):
    if eats_profile['is_rover']:
        return 'rover'
    if (
            eats_profile['orders_provider'] == 'shop'
            and eats_profile['is_dedicated_picker']
            or eats_profile['orders_provider'] == 'scooter'
    ):
        return 'pedestrian'
    return eats_profile['transport_type']


@pytest.mark.config(EATS_PROFILES_SYNCHRONIZER_SETTINGS=get_settings(False))
@pytest.mark.experiments3(filename='eats_courier_sync.json')
async def test_disabled(taxi_cargo_misc, mockserver, testpoint, pgsql):
    await wait_iteration(taxi_cargo_misc, testpoint, False)
    psql_cursor = pgsql['cargo_misc'].cursor()
    psql_cursor.execute('SELECT name, cursor FROM cargo_misc.cursors_storage')
    assert psql_cursor.rowcount == 0


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='eats_profile_synchronizer_settings',
    consumers=['cargo-misc/eats_profiles_synchronizer'],
    clauses=[],
    default_value={'courier_app': 'taximeter'},
)
@pytest.mark.experiments3(filename='eats_courier_sync.json')
@pytest.mark.config(EATS_PROFILES_SYNCHRONIZER_SETTINGS=get_settings(True))
async def test_empty_response(
        taxi_cargo_misc, mockserver, testpoint, pgsql, eats_core,
):
    await wait_iteration(taxi_cargo_misc, testpoint, True)
    psql_cursor = pgsql['cargo_misc'].cursor()
    psql_cursor.execute('SELECT name, cursor FROM cargo_misc.cursors_storage')
    rows = list(psql_cursor)
    assert rows[0] == (JOB_NAME, 'empty_cursor')


@pytest.mark.parametrize(
    'cursor, profiles',
    [
        pytest.param(
            'cursor_1606694403_0',
            [
                make_profile(1, 'pedestrian', 'eda', 'self_employed'),
                make_profile(
                    1606694402,
                    'bicycle',
                    'eda',
                    'courier_service',
                    'courier_service_id_1',
                ),
                make_profile(
                    1606694403,
                    'electric_bicycle',
                    'lavka',
                    'courier_service',
                    'courier_service_id_1',
                ),
            ],
            id='OK',
        ),
        pytest.param(
            'cursor_1606694404_0',
            [
                make_profile(
                    1606694401,
                    'pedestrian',
                    'eda',
                    'self_employed_nonresident',
                ),
                make_profile(
                    1606694402,
                    'bicycle',
                    'eda',
                    'courier_service',
                    'courier_service_id_1',
                ),
                make_profile(
                    1606694404,
                    'bicycle',
                    'eda',
                    'courier_service',
                    'courier_service_id_1',
                ),
                make_profile(
                    1606694403,
                    'electric_bicycle',
                    'lavka',
                    'courier_service',
                    'courier_service_id_1',
                ),
            ],
            id='Over limit',
        ),
        pytest.param(
            'cursor_1606694406_0',
            [
                make_profile(
                    1606694405,
                    'pedestrian',
                    'eda',
                    'self_employed',
                    'self_employed',
                ),
                make_profile(
                    1606694406,
                    'bicycle',
                    'eda',
                    'courier_service',
                    'courier_service_id_1',
                ),
            ],
            id='Skipped by exp',
        ),
        pytest.param(
            'cursor_1606694403_0',
            [
                make_profile(1, 'pedestrian', 'shop', 'self_employed'),
                make_profile(
                    1606694402,
                    'bicycle',
                    'shop',
                    'courier_service',
                    'courier_service_id_1',
                ),
                make_profile(
                    1606694403,
                    'electric_bicycle',
                    'lavka',
                    'courier_service',
                    'courier_service_id_1',
                ),
            ],
            id='Transform orders provider',
        ),
        pytest.param(
            'cursor_1606694403_0',
            [
                make_profile(1, 'pedestrian', 'lavka', 'self_employed'),
                make_profile(
                    1606694402,
                    'bicycle',
                    'lavka',
                    'courier_service',
                    'courier_service_id_1',
                    is_rover=True,
                ),
                make_profile(
                    1606694403,
                    'electric_bicycle',
                    'lavka',
                    'courier_service',
                    'courier_service_id_1',
                    is_rover=True,
                ),
            ],
            id='Rover',
        ),
        pytest.param(
            'cursor_1606694403_0',
            [
                make_profile(
                    1,
                    'bicycle',
                    'eats',
                    'courier_service',
                    'courier_service_id_1',
                    is_dedicated_picker=True,
                ),
                make_profile(
                    1606694402,
                    'bicycle',
                    'shop',
                    'courier_service',
                    'courier_service_id_1',
                    is_dedicated_picker=True,
                ),
                make_profile(
                    1606694403,
                    'electric_bicycle',
                    'shop',
                    'courier_service',
                    'courier_service_id_1',
                    is_dedicated_picker=True,
                ),
            ],
            id='Dedicated picker',
        ),
        pytest.param(
            'cursor_1606694403_0',
            [
                make_profile(
                    1,
                    'pedestrian',
                    'scooter',
                    'courier_service',
                    'courier_service_id_1',
                ),
                make_profile(
                    1606694402,
                    'bicycle',
                    'scooter',
                    'courier_service',
                    'courier_service_id_1',
                ),
                make_profile(
                    1606694403,
                    'electric_bicycle',
                    'scooter',
                    'courier_service',
                    'courier_service_id_1',
                ),
            ],
            id='energizer',
        ),
    ],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='eats_profile_synchronizer_settings',
    consumers=['cargo-misc/eats_profiles_synchronizer'],
    clauses=[
        {
            'title': 'Enabled',
            'predicate': {
                'init': {
                    'set': ['courier_id_1', 'courier_id_2', 'courier_id_3'],
                    'arg_name': 'courier_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
            'value': {'courier_app': 'taximeter', 'switch_app': True},
        },
    ],
)
@pytest.mark.config(EATS_PROFILES_SYNCHRONIZER_SETTINGS=get_settings(True))
@pytest.mark.experiments3(filename='eats_courier_sync.json')
@pytest.mark.now('2020-11-30T00:00:15+00:00')
async def test_worker_enabled(
        taxi_cargo_misc,
        taxi_cargo_misc_monitor,
        mockserver,
        testpoint,
        pgsql,
        eats_core,
        personal,
        cursor,
        profiles,
):
    eats_core.set_data(cursor, profiles)
    seen_profiles = []

    @mockserver.json_handler('/cargo-misc/couriers/eats/v1/sync')
    def _profiles_sync(request):
        seen_profiles.append(
            {
                'park_id': request.json['park_id'],
                'courier_id': request.json['courier_id'],
                'transport_type': request.json['transport_type'],
                'full_name': request.json['full_name'],
                'phone': request.json['phone'],
                'orders_provider': request.json['orders_provider'],
                'courier_app': request.json['courier_app'],
                'switch_app': request.json['switch_app'],
                'deaf': request.json['deaf'],
                'has_health_card': request.json['has_health_card'],
                'birth_date': request.json['birth_date'],
            },
        )
        return {
            'park_id': 'park_id',
            'driver_id': 'driver_id',
            'car_id': 'car_id',
        }

    await wait_iteration(taxi_cargo_misc, testpoint, True)
    metrics = await taxi_cargo_misc_monitor.get_metric('sync_statistic')

    # cursor_lag == mocked_now - response_cursor in secods
    assert metrics['cursor_lag'] == 1606694415 - int(cursor[7:-2])

    psql_cursor = pgsql['cargo_misc'].cursor()
    psql_cursor.execute('SELECT name, cursor FROM cargo_misc.cursors_storage')
    rows = list(psql_cursor)
    assert rows[0] == (JOB_NAME, cursor)
    assert len(profiles) >= len(seen_profiles)

    for taxi_profile, eats_profile in zip(seen_profiles, profiles):
        assert taxi_profile['park_id'] == get_park(eats_profile)
        assert taxi_profile['courier_id'] == eats_profile['id']
        assert taxi_profile['transport_type'] == transform_transport(
            eats_profile,
        )
        assert taxi_profile['full_name'] == eats_profile['full_name']
        assert taxi_profile['deaf'] == eats_profile['is_hard_of_hearing']
        assert (
            taxi_profile['has_health_card'] == eats_profile['has_health_card']
        )
        assert taxi_profile['phone'] == get_phone(eats_profile['phone_pd_id'])
        assert taxi_profile['orders_provider'] == transform_orders_provider(
            eats_profile['orders_provider'], eats_profile['is_picker'],
        )
        assert taxi_profile['courier_app'] == 'taximeter'
        assert taxi_profile['switch_app']
        assert taxi_profile['birth_date'] == eats_profile['birthday']
