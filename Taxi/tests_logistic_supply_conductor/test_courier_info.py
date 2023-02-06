import pytest


@pytest.fixture(name='driver_profiles_by_phone_request')
async def _driver_profiles_by_phone_request(mockserver, load_json):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
    )
    def _mock_handler(request):
        request_json = request.json
        if not request_json['driver_phone_in_set']:
            return mockserver.make_response(status=400)

        json = load_json('driver_profiles_retrieve_by_phone_response.json')
        profiles = [
            profile
            for profile in json['profiles_by_phone']
            if profile['driver_phone'] in request_json['driver_phone_in_set']
        ]
        return mockserver.make_response(json={'profiles_by_phone': profiles})


@pytest.fixture(name='driver_profiles_by_dbid_uuid_request')
async def _driver_profiles_by_dbid_uuid_request(mockserver, load_json):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_driver_profiles_retrive(request):
        request_json = request.json
        if not request_json['id_in_set']:
            return mockserver.make_response(status=400)

        json = load_json('driver_profiles_retrieve_by_dbid_uuid_response.json')
        profiles = [
            profile
            for profile in json['profiles_by_dbid_uuid']
            if profile['park_driver_profile_id'] in request_json['id_in_set']
        ]
        return mockserver.make_response(json={'profiles': profiles})


@pytest.fixture(name='driver_orders_request')
async def _driver_orders_request(mockserver, load_json):
    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    def _mock_driver_orders(request):
        response = load_json('driver_orders_retrieve_response.json')
        return mockserver.make_response(json=response)


@pytest.mark.parametrize(
    ('driver_phone', 'device_id', 'expected_response'),
    [
        (
            '92f78e99f7addaf79a4787c987e9f933',
            'DEVICE_ID_1',
            {'isActive': True},
        ),
        (
            '92f78e99f7addaf79a4787c987e9f933',
            'DEVICE_ID_2',
            {'isActive': False},
        ),
        (
            '92f78e99f7addaf79a4787c987e9f934',
            'DEVICE_ID_3',
            {'isActive': False},
        ),
        (
            '37c78e99f7addaf79a4787c987e9f933',
            'DEVICE_ID_4',
            {'isActive': False},
        ),
        (
            'ad12d1f1ddd042faab287d112b0874a2',
            'DEVICE_ID_5',
            {'isActive': False},
        ),
        (
            'e91ff2f21f874308a7ee10272347800b',
            'DEVICE_ID_6',
            {'isActive': False},
        ),
        ('UNKNOWN_DRIVER_PHONE', 'DEVICE_ID_7', {'isActive': False}),
    ],
)
@pytest.mark.config(
    DRIVER_STATUSES_CACHE_SETTINGS={
        '__default__': {
            'cache_enabled': True,
            'full_update_request_parts_count': 1,
            'last_revision_overlap_sec': 1,
        },
    },
)
@pytest.mark.tags_v2_index(
    tags_list=[
        (
            'dbid_uuid',
            'c3ad7a1fdc1a48ef9cb121f457e5a5e0_'
            '4a90810b6b2b446bbafa7f2f14fa2010',
            'walking_courier',
        ),
        (
            'dbid_uuid',
            'c3ad7a1fdc1a48ef9cb121f457e5a5e1_'
            '4a90810b6b2b446bbafa7f2f14fa2011',
            'walking_courier',
        ),
        (
            'dbid_uuid',
            'a3608f8f7ee84e0b9c21862beef7e48d_'
            '9d57d0c7268a4a8bb359aa5c61203279',
            'walking_courier',
        ),
        (
            'dbid_uuid',
            '929f5bc2f0f44c8595faaa818f4d3ab8_'
            '31d323d5532440de8a82ee2e2e2e7b5f',
            'walking_courier',
        ),
    ],
)
@pytest.mark.config(TAGS_INDEX={'enabled': True})
@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata_with_requirements.sql',
        'pg_workshift_rule_versions.sql',
        'pg_geoareas_small.sql',
        'pg_workshift_quotas.sql',
        'pg_workshift_slots.sql',
        'pg_workshift_slot_subscribers.sql',
    ],
)
@pytest.mark.now('2035-09-17T10:31:00+00:00')
@pytest.mark.config(
    LOGISTIC_SUPPLY_CONDUCTOR_COMPLETED_ORDER_SETTINGS={
        'days': 3,
        'enabled': True,
    },
)
async def test_courier_info(
        taxi_logistic_supply_conductor,
        driver_profiles_by_phone_request,
        driver_profiles_by_dbid_uuid_request,
        driver_orders_request,
        driver_status_request,
        driver_phone,
        device_id,
        expected_response,
):
    await taxi_logistic_supply_conductor.invalidate_caches()
    response = await taxi_logistic_supply_conductor.post(
        path='/internal/v1/courier/info/retrieve-by-phone'
        '?personal_phone_id=' + driver_phone + '&device_id=' + device_id,
    )
    assert response.status_code == 200
    assert response.json() == expected_response
