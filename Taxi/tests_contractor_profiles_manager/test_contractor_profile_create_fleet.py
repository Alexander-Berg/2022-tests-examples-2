import pytest


FLEET_PARKS_RESPONSE = 'fleet_parks_response_success.json'

REQUEST_JSON = {
    'account': {
        'balance_limit': '50',
        'work_rule_id': 'rule_zero',
        'payment_service_id': '12345',
        'block_orders_on_balance_below_limit': True,
    },
    'person': {
        'full_name': {
            'first_name': 'Taras',
            'last_name': 'Samotkin',
            'middle_name': 'Lopot',
        },
        'contact_info': {
            'address': 'my address',
            'email': 'test@yandex.ru',
            'phone': '+123',
        },
        'driver_license': {
            'country': 'rus',
            'number': '09aу213265',
            'birth_date': '1939-09-02',
            'expiry_date': '2028-11-18',
            'issue_date': '2018-12-18',
        },
    },
    'profile': {
        'hire_date': '2018-11-20',
        'comment': 'my comment',
        'feedback': 'my check message',
    },
    'car_id': '4ad32bc7560149r98ac12cg7a75c321',
    'order_provider': {'platform': False, 'partner': False},
}


async def test_success(
        taxi_contractor_profiles_manager, load_json, mockserver, headers,
):
    stub = load_json('success.json')

    @mockserver.json_handler('/parks/driver-profiles/create')
    def _mock_parks(request):
        assert request.json == stub['parks_request']
        assert 'X-Idempotency-Token' in request.headers
        return mockserver.make_response(
            json=stub['parks_response'], status=200,
        )

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def _fleet_parks(request):
        assert request.json['query'] == {
            'park': {'ids': ['7ad36bc7560449998acbe2c57a75c293']},
        }
        fleet_parks = load_json(FLEET_PARKS_RESPONSE)
        return mockserver.make_response(
            json=fleet_parks['response'], status=200,
        )

    response = await taxi_contractor_profiles_manager.post(
        '/fleet/contractor-profiles-manager/v1/contractor-profile',
        headers={
            **headers,
            'X-Idempotency-Token': '123e4567-e89b-12d3-a456-426655440000',
        },
        json=REQUEST_JSON,
    )

    assert response.status == 200

    data = response.json()
    assert data == stub['service_response']


async def test_bad_request(
        taxi_contractor_profiles_manager, load_json, mockserver, headers,
):
    stub = load_json('bad_request.json')

    @mockserver.json_handler('/parks/driver-profiles/create')
    def _mock_parks(request):
        assert request.json == stub['parks_request']
        assert 'X-Idempotency-Token' in request.headers
        return mockserver.make_response(
            json=stub['parks_response'], status=400,
        )

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def _fleet_parks(request):
        assert request.json['query'] == {
            'park': {'ids': ['7ad36bc7560449998acbe2c57a75c293']},
        }
        fleet_parks = load_json(FLEET_PARKS_RESPONSE)
        return mockserver.make_response(
            json=fleet_parks['response'], status=200,
        )

    response = await taxi_contractor_profiles_manager.post(
        '/fleet/contractor-profiles-manager/v1/contractor-profile',
        headers={
            **headers,
            'X-Idempotency-Token': '123e4567-e89b-12d3-a456-426655440000',
        },
        json=REQUEST_JSON,
    )

    assert response.status == 400

    data = response.json()
    assert data == stub['service_response']


@pytest.mark.config(
    OPTEUM_CARD_DRIVER_REQUIRED_FIELDS={
        'enable': True,
        'fields': ['middle_name'],
        'enable_backend': True,
        'cities': [],
        'countries': [],
        'dbs': [],
        'dbs_disable': [],
        'enable_support': False,
        'enable_support_users': [],
    },
)
async def test_validation_required_fields(
        taxi_contractor_profiles_manager, load_json, mockserver, headers,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def _fleet_parks(request):
        assert request.json['query'] == {
            'park': {'ids': ['7ad36bc7560449998acbe2c57a75c293']},
        }
        fleet_parks = load_json(FLEET_PARKS_RESPONSE)
        return mockserver.make_response(
            json=fleet_parks['response'], status=200,
        )

    req_json = REQUEST_JSON
    req_json['person']['full_name'].pop('middle_name')
    response = await taxi_contractor_profiles_manager.post(
        '/fleet/contractor-profiles-manager/v1/contractor-profile',
        headers={
            **headers,
            'X-Idempotency-Token': '123e4567-e89b-12d3-a456-426655440000',
        },
        json=req_json,
    )

    assert response.status == 400

    data = response.json()
    assert data == {
        'code': '400',
        'message': 'missing_required_field_middle_name',
    }
