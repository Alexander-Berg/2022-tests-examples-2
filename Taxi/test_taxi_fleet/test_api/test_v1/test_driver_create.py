import aiohttp.web
import pytest


async def test_success(
        web_app_client, mock_parks, headers, load_json, mockserver,
):
    stub = load_json('success.json')

    @mockserver.json_handler('/parks/driver-profiles/create')
    def _mock_parks(request):
        assert request.json == stub['parks_request']
        assert request.query['driver_profile_id'] is not None
        assert 'X-Idempotency-Token' in request.headers
        return aiohttp.web.json_response(stub['parks_response'])

    @mockserver.json_handler(
        '/cashbox-integration/v1/drivers/receipts/autocreation',
    )
    def _mock_cashbox_integration(request):
        return {
            'autocreation': {
                'driver_id': request.query['driver_id'],
                'is_enabled': True,
            },
        }

    response = await web_app_client.post(
        '/api/v1/drivers/create',
        headers={**headers, 'X-Idempotency-Token': 'a1-b2-c3-d4'},
        json={
            'accounts': {'balance_limit': '50'},
            'driver_profile': {
                'first_name': 'Taras',
                'last_name': 'Samotkin',
                'middle_name': 'Lopot',
                'phones': ['+123'],
                'driver_license': {
                    'country': 'rus',
                    'number': '09aу213265',
                    'birth_date': '1939-09-02',
                    'expiration_date': '2028-11-18',
                    'issue_date': '2018-12-18',
                },
                'work_rule_id': 'rule_zero',
                'providers': [],
                'hire_date': '2018-11-20',
                'bank_accounts': [],
                'identifications': [],
                'tax_identification_number': '123',
                'primary_state_registration_number': '123',
                'address': 'my address',
                'car_id': '4ad32bc7560149r98ac12cg7a75c321',
                'check_message': 'my check message',
                'comment': 'my comment',
                'deaf': True,
                'email': 'test@yandex.ru',
                'fire_date': '2018-12-19',
                'payment_service_id': '12345',
                'emergency_person_contacts': [{'phone': '+89123'}],
                'balance_deny_onlycard': True,
                'signalq_details': {
                    'employee_number': '123',
                    'unit': 'South',
                    'subunit': 'PodSouth',
                },
                'permit_number': 'super_taxi_driver_license_2',
                'automatic_receipt_creation': True,
            },
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
    assert _mock_cashbox_integration.times_called == 1
    request = _mock_cashbox_integration.next_call()['request']
    assert request.method == 'POST'
    assert request.json == {'is_enabled': True}
    assert request.query['park_id'] == '7ad36bc7560449998acbe2c57a75c293'


async def test_bad_request(
        web_app_client, mock_parks, headers, load_json, mockserver,
):
    stub = load_json('bad_request.json')

    @mockserver.json_handler('/parks/driver-profiles/create')
    def _mock_parks(request):
        assert request.json == stub['parks_request']
        assert request.query['driver_profile_id'] is not None
        assert 'X-Idempotency-Token' in request.headers
        return aiohttp.web.json_response(stub['parks_response'], status=400)

    @mockserver.json_handler(
        '/cashbox-integration/v1/drivers/receipts/autocreation',
    )
    def _mock_cashbox_integration(request):
        return {
            'autocreation': {
                'driver_id': request.query['driver_id'],
                'is_enabled': True,
            },
        }

    response = await web_app_client.post(
        '/api/v1/drivers/create',
        headers={**headers, 'X-Idempotency-Token': 'a1-b2-c3-d4'},
        json={
            'accounts': {'balance_limit': '50'},
            'driver_profile': {
                'first_name': 'Taras',
                'last_name': 'Samotkin',
                'middle_name': 'Lopot',
                'phones': ['+123'],
                'driver_license': {
                    'country': 'rus',
                    'number': '09aу213265',
                    'birth_date': '1939-09-02',
                    'expiration_date': '2028-11-18',
                    'issue_date': '2018-12-18',
                },
                'work_rule_id': 'rule_zero',
                'providers': [],
                'hire_date': '2018-11-20',
                'bank_accounts': [],
                'identifications': [],
                'tax_identification_number': '123',
                'primary_state_registration_number': '123',
                'address': 'my address',
                'car_id': '4ad32bc7560149r98ac12cg7a75c321',
                'check_message': 'my check message',
                'comment': 'my comment',
                'deaf': True,
                'email': 'test@yandex.ru',
                'fire_date': '2018-12-19',
                'payment_service_id': '12345',
                'emergency_person_contacts': [{'phone': '+89123'}],
                'balance_deny_onlycard': True,
                'signalq_details': {
                    'employee_number': '123',
                    'unit': 'South',
                    'subunit': 'PodSouth',
                },
                'permit_number': 'super_taxi_driver_license_2',
                'automatic_receipt_creation': True,
                'profession_id': 'auto-courier',
            },
        },
    )

    assert response.status == 400

    data = await response.json()
    assert data == stub['service_response']
    assert _mock_cashbox_integration.times_called == 1
    request = _mock_cashbox_integration.next_call()['request']
    assert request.method == 'POST'
    assert request.json == {'is_enabled': True}
    assert request.query['park_id'] == '7ad36bc7560449998acbe2c57a75c293'


async def test_pass_rule_id_success(
        web_app_client, mock_parks, headers, load_json, mockserver,
):
    stub = load_json('success.json')

    @mockserver.json_handler('/parks/driver-profiles/create')
    def _mock_parks(request):
        assert request.json == stub['parks_request']
        assert request.query['driver_profile_id'] is not None
        assert 'X-Idempotency-Token' in request.headers
        return aiohttp.web.json_response(stub['parks_response'])

    @mockserver.json_handler(
        '/cashbox-integration/v1/drivers/receipts/autocreation',
    )
    def _mock_cashbox_integration(request):
        return {
            'autocreation': {
                'driver_id': request.query['driver_id'],
                'is_enabled': True,
            },
        }

    contractor_rules_by_id_stub = load_json(
        'success_contractors_rules_by_id.json',
    )

    @mockserver.json_handler(
        'contractor-instant-payouts/v1/contractors/rules/by-id',
    )
    async def _v1_contractors_rules_by_id(request):
        stub_park_id = contractor_rules_by_id_stub['park_id']
        assert request.query['park_id'] == stub_park_id
        assert request.json == contractor_rules_by_id_stub['request']
        return aiohttp.web.json_response(
            contractor_rules_by_id_stub['response'], status=204,
        )

    response = await web_app_client.post(
        '/api/v1/drivers/create',
        headers={**headers, 'X-Idempotency-Token': 'a1-b2-c3-d4'},
        json={
            'instant_payouts': {'rule_id': '00000000000100010001000000000000'},
            'accounts': {'balance_limit': '50'},
            'driver_profile': {
                'first_name': 'Taras',
                'last_name': 'Samotkin',
                'middle_name': 'Lopot',
                'phones': ['+123'],
                'driver_license': {
                    'country': 'rus',
                    'number': '09aу213265',
                    'birth_date': '1939-09-02',
                    'expiration_date': '2028-11-18',
                    'issue_date': '2018-12-18',
                },
                'work_rule_id': 'rule_zero',
                'providers': [],
                'hire_date': '2018-11-20',
                'bank_accounts': [],
                'identifications': [],
                'tax_identification_number': '123',
                'primary_state_registration_number': '123',
                'address': 'my address',
                'car_id': '4ad32bc7560149r98ac12cg7a75c321',
                'check_message': 'my check message',
                'comment': 'my comment',
                'deaf': True,
                'email': 'test@yandex.ru',
                'fire_date': '2018-12-19',
                'payment_service_id': '12345',
                'emergency_person_contacts': [{'phone': '+89123'}],
                'balance_deny_onlycard': True,
                'signalq_details': {
                    'employee_number': '123',
                    'unit': 'South',
                    'subunit': 'PodSouth',
                },
                'permit_number': 'super_taxi_driver_license_2',
                'automatic_receipt_creation': True,
            },
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
    assert _mock_cashbox_integration.times_called == 1
    request = _mock_cashbox_integration.next_call()['request']
    assert request.method == 'POST'
    assert request.json == {'is_enabled': True}
    assert request.query['park_id'] == '7ad36bc7560449998acbe2c57a75c293'


async def test_pass_rule_id_bad_request(
        web_app_client, mock_parks, headers, load_json, mockserver,
):
    stub = load_json('invalid_rule_id.json')

    contractor_rules_by_id_stub = load_json(
        'error_contractors_rules_by_id.json',
    )

    @mockserver.json_handler(
        'contractor-instant-payouts/v1/contractors/rules/by-id',
    )
    async def _v1_contractors_rules_by_id(request):
        stub_park_id = contractor_rules_by_id_stub['park_id']
        assert request.query['park_id'] == stub_park_id
        assert request.json == contractor_rules_by_id_stub['request']
        return aiohttp.web.json_response(
            contractor_rules_by_id_stub['response'], status=400,
        )

    response = await web_app_client.post(
        '/api/v1/drivers/create',
        headers={**headers, 'X-Idempotency-Token': 'a1-b2-c3-d4'},
        json={
            'instant_payouts': {'rule_id': '00000000000100010001000000000000'},
            'accounts': {'balance_limit': '50'},
            'driver_profile': {
                'first_name': 'Taras',
                'last_name': 'Samotkin',
                'middle_name': 'Lopot',
                'phones': ['+123'],
                'driver_license': {
                    'country': 'rus',
                    'number': '09aу213265',
                    'birth_date': '1939-09-02',
                    'expiration_date': '2028-11-18',
                    'issue_date': '2018-12-18',
                },
                'work_rule_id': 'rule_zero',
                'providers': [],
                'hire_date': '2018-11-20',
                'bank_accounts': [],
                'identifications': [],
                'tax_identification_number': '123',
                'primary_state_registration_number': '123',
                'address': 'my address',
                'car_id': '4ad32bc7560149r98ac12cg7a75c321',
                'check_message': 'my check message',
                'comment': 'my comment',
                'deaf': True,
                'email': 'test@yandex.ru',
                'fire_date': '2018-12-19',
                'payment_service_id': '12345',
                'emergency_person_contacts': [{'phone': '+89123'}],
                'balance_deny_onlycard': True,
                'signalq_details': {
                    'employee_number': '123',
                    'unit': 'South',
                    'subunit': 'PodSouth',
                },
                'permit_number': 'super_taxi_driver_license_2',
                'automatic_receipt_creation': True,
            },
        },
    )

    assert response.status == 400

    data = await response.json()
    assert data == stub['service_response']


@pytest.mark.config(OPTEUM_CARD_DRIVER_HIRING_TYPE={'enable': True})
async def test_validate_hiring_type_success(
        web_app_client, mock_parks, headers, load_json, mockserver,
):
    stub = load_json('success_validate_hiring_type.json')

    @mockserver.json_handler('/parks/driver-profiles/create')
    def _mock_parks(request):
        assert request.json == stub['parks_request']
        assert request.query['driver_profile_id'] is not None
        assert 'X-Idempotency-Token' in request.headers
        return aiohttp.web.json_response(stub['parks_response'])

    @mockserver.json_handler(
        '/cashbox-integration/v1/drivers/receipts/autocreation',
    )
    def _mock_cashbox_integration(request):
        return {
            'autocreation': {
                'driver_id': request.query['driver_id'],
                'is_enabled': True,
            },
        }

    response = await web_app_client.post(
        '/api/v1/drivers/create',
        headers={**headers, 'X-Idempotency-Token': 'a1-b2-c3-d4'},
        json={
            'accounts': {'balance_limit': '50'},
            'driver_profile': {
                'first_name': 'Taras',
                'last_name': 'Samotkin',
                'middle_name': 'Lopot',
                'phones': ['+123'],
                'driver_license': {
                    'country': 'rus',
                    'number': '09aу213265',
                    'birth_date': '1939-09-02',
                    'expiration_date': '2028-11-18',
                    'issue_date': '2018-12-18',
                },
                'work_rule_id': 'rule_zero',
                'providers': [],
                'hire_date': '2018-11-20',
                'bank_accounts': [],
                'identifications': [],
                'tax_identification_number': '123',
                'primary_state_registration_number': '123',
                'address': 'my address',
                'car_id': '4ad32bc7560149r98ac12cg7a75c321',
                'check_message': 'my check message',
                'comment': 'my comment',
                'deaf': True,
                'email': 'test@yandex.ru',
                'fire_date': '2018-12-19',
                'payment_service_id': '12345',
                'emergency_person_contacts': [{'phone': '+89123'}],
                'balance_deny_onlycard': True,
                'automatic_receipt_creation': True,
            },
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
    assert _mock_cashbox_integration.times_called == 1
    request = _mock_cashbox_integration.next_call()['request']
    assert request.method == 'POST'
    assert request.json == {'is_enabled': True}
    assert request.query['park_id'] == '7ad36bc7560449998acbe2c57a75c293'


@pytest.mark.config(
    OPTEUM_CARD_DRIVER_REQUIRED_FIELDS={
        'enable': True,
        'fields': ['middle_name'],
        'enable_backend': True,
    },
)
async def test_validation_required_fields(web_app_client, mock_parks, headers):
    response = await web_app_client.post(
        '/api/v1/drivers/create',
        headers={**headers, 'X-Idempotency-Token': 'a1-b2-c3-d4'},
        json={
            'accounts': {'balance_limit': '50'},
            'driver_profile': {
                'first_name': 'Taras',
                'last_name': 'Samotkin',
                'phones': ['+123'],
                'driver_license': {
                    'country': 'rus',
                    'number': '09aу213265',
                    'birth_date': '1939-09-02',
                    'expiration_date': '2028-11-18',
                    'issue_date': '2018-12-18',
                },
                'work_rule_id': 'rule_zero',
                'providers': [],
                'hire_date': '2018-11-20',
                'bank_accounts': [],
                'identifications': [],
                'tax_identification_number': '123',
                'primary_state_registration_number': '123',
                'address': 'my address',
                'car_id': '4ad32bc7560149r98ac12cg7a75c321',
                'check_message': 'my check message',
                'comment': 'my comment',
                'deaf': True,
                'email': 'test@yandex.ru',
                'fire_date': '2018-12-19',
                'payment_service_id': '12345',
                'emergency_person_contacts': [{'phone': '+89123'}],
                'balance_deny_onlycard': True,
            },
        },
    )

    assert response.status == 400

    data = await response.json()
    assert data == {'code': 'REQUIRED_FIELDS', 'message': 'Bad request'}
