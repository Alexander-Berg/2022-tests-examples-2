import aiohttp.web
import pytest


async def test_success(
        web_app_client, mock_parks, headers, load_json, mockserver,
):
    stub = load_json('success.json')

    @mockserver.json_handler('/parks/driver-profiles/profile')
    async def _driver_update_profile(request):
        assert request.json == stub['parks_request_profile']
        return aiohttp.web.json_response(stub['parks_response_profile'])

    @mockserver.json_handler('/parks/driver-profiles/personal')
    async def _driver_update_personal(request):
        assert request.json == stub['parks_request_personal']
        return aiohttp.web.json_response(stub['parks_response_personal'])

    @mockserver.json_handler('/parks/driver-profiles/taximeter-disable-status')
    async def _driver_update_disable(request):
        assert request.json == stub['parks_request_disable']
        return aiohttp.web.json_response(stub['parks_response_disable'])

    @mockserver.json_handler('/parks/driver-profiles/retrieve')
    async def _driver_retrieve(request):
        assert request.json == stub['parks_retrieve']['request']
        return aiohttp.web.json_response(stub['parks_retrieve']['response'])

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
        '/api/v1/drivers/update',
        headers=headers,
        json={
            'driver_id': '4ad12bc7a60149t98ac12bg7a71c35f',
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
                'work_status': 'working',
                'providers': [],
                'hire_date': '2018-11-20',
                'bank_accounts': [],
                'identifications': [],
                'tax_identification_number': '123',
                'primary_state_registration_number': '123',
                'address': 'my address',
                'check_message': 'my check message',
                'comment': 'my comment',
                'deaf': True,
                'email': 'test@yandex.ru',
                'fire_date': '2018-12-19',
                'payment_service_id': '12345',
                'emergency_person_contacts': [{'phone': '+89123'}],
                'balance_deny_onlycard': True,
                'hiring_details': {
                    'hiring_date': '2019-01-01',
                    'hiring_type': 'commercial',
                },
                'permit_number': 'super_taxi_driver_license_0',
                'automatic_receipt_creation': True,
            },
            'taximeter_disable_status': {'disabled': False},
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
    assert _mock_cashbox_integration.times_called == 1
    request = _mock_cashbox_integration.next_call()['request']
    assert request.method == 'POST'
    assert request.json == {'is_enabled': True}
    assert request.query == {
        'park_id': '7ad36bc7560449998acbe2c57a75c293',
        'driver_id': '4ad12bc7a60149t98ac12bg7a71c35f',
    }


@pytest.mark.config(OPTEUM_CARD_DRIVER_HIRING_TYPE={'enable': True})
async def test_validate_hiring_type_success(
        web_app_client, mock_parks, headers, load_json, mockserver,
):

    stub = load_json('success_validate_hiring_type.json')

    @mockserver.json_handler('/parks/driver-profiles/profile')
    async def _driver_update_profile(request):
        assert request.json == stub['parks_request_profile']
        return aiohttp.web.json_response(stub['parks_response_profile'])

    @mockserver.json_handler('/parks/driver-profiles/personal')
    async def _driver_update_personal(request):
        assert request.json == stub['parks_request_personal']
        return aiohttp.web.json_response(stub['parks_response_personal'])

    @mockserver.json_handler('/parks/driver-profiles/taximeter-disable-status')
    async def _driver_update_disable(request):
        assert request.json == stub['parks_request_disable']
        return aiohttp.web.json_response(stub['parks_response_disable'])

    @mockserver.json_handler('/parks/driver-profiles/retrieve')
    async def _driver_retrieve(request):
        assert request.json == stub['parks_retrieve']['request']
        return aiohttp.web.json_response(stub['parks_retrieve']['response'])

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
        '/api/v1/drivers/update',
        headers=headers,
        json={
            'driver_id': '4ad12bc7a60149t98ac12bg7a71c35f',
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
                'work_status': 'working',
                'providers': [],
                'hire_date': '2018-11-20',
                'bank_accounts': [],
                'identifications': [],
                'tax_identification_number': '123',
                'primary_state_registration_number': '123',
                'address': 'my address',
                'check_message': 'my check message',
                'comment': 'my comment',
                'deaf': True,
                'email': 'test@yandex.ru',
                'fire_date': '2018-12-19',
                'payment_service_id': '12345',
                'emergency_person_contacts': [{'phone': '+89123'}],
                'balance_deny_onlycard': True,
                'hiring_details': {
                    'hiring_date': '2019-01-01',
                    'hiring_type': 'commercial',
                },
                'automatic_receipt_creation': True,
            },
            'taximeter_disable_status': {'disabled': False},
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
    assert _mock_cashbox_integration.times_called == 1
    request = _mock_cashbox_integration.next_call()['request']
    assert request.method == 'POST'
    assert request.json == {'is_enabled': True}
    assert request.query == {
        'park_id': '7ad36bc7560449998acbe2c57a75c293',
        'driver_id': '4ad12bc7a60149t98ac12bg7a71c35f',
    }


@pytest.mark.config(
    OPTEUM_CARD_DRIVER_REQUIRED_FIELDS={
        'enable': True,
        'fields': ['middle_name'],
        'enable_backend': True,
    },
)
async def test_validation_required_fields(
        web_app_client, mock_parks, headers, mockserver, load_json,
):

    stub = load_json('validation_required_fields.json')

    @mockserver.json_handler('/parks/driver-profiles/retrieve')
    async def _driver_retrieve(request):
        assert request.json == stub['parks_retrieve']['request']
        return aiohttp.web.json_response(stub['parks_retrieve']['response'])

    response = await web_app_client.post(
        '/api/v1/drivers/update',
        headers=headers,
        json={
            'driver_id': '4ad12bc7a60149t98ac12bg7a71c35f',
            'accounts': {'balance_limit': '50'},
            'driver_profile': {
                'first_name': 'Taras',
                'last_name': 'Samotkin',
                'phones': ['123'],
                'driver_license': {
                    'country': 'rus',
                    'number': '09aу213265',
                    'birth_date': '1939-09-02',
                    'expiration_date': '2028-11-18',
                    'issue_date': '2018-12-18',
                },
                'work_rule_id': 'rule_zero',
                'work_status': 'working',
                'providers': [],
                'hire_date': '2018-11-20',
                'bank_accounts': [],
                'identifications': [],
                'tax_identification_number': '123',
                'primary_state_registration_number': '123',
                'address': 'my address',
                'check_message': 'my check message',
                'comment': 'my comment',
                'deaf': True,
                'email': 'test@yandex.ru',
                'fire_date': '2018-12-19',
                'payment_service_id': '12345',
                'emergency_person_contacts': [{'phone': '+89123'}],
                'balance_deny_onlycard': True,
                'hiring_details': {
                    'hiring_date': '2019-01-01',
                    'hiring_type': 'commercial',
                },
            },
            'taximeter_disable_status': {'disabled': False},
        },
    )

    assert response.status == 400

    data = await response.json()
    assert data == {'code': 'REQUIRED_FIELDS', 'message': 'Bad request'}


@pytest.mark.config(
    OPTEUM_CARD_DRIVER_FIELDS_EDIT={
        'enable': True,
        'fields': ['middle_name'],
        'enable_backend': True,
    },
)
async def test_validation_disabled_fields(
        web_app_client, mock_parks, headers, mockserver, load_json,
):

    stub = load_json('validation_disabled_fields.json')

    @mockserver.json_handler('/parks/driver-profiles/retrieve')
    async def _driver_retrieve(request):
        assert request.json == stub['parks_retrieve']['request']
        return aiohttp.web.json_response(stub['parks_retrieve']['response'])

    response = await web_app_client.post(
        '/api/v1/drivers/update',
        headers=headers,
        json={
            'driver_id': '4ad12bc7a60149t98ac12bg7a71c35f',
            'accounts': {'balance_limit': '50'},
            'driver_profile': {
                'first_name': 'Taras',
                'last_name': 'Samotkin',
                'middle_name': 'New middle name',
                'phones': ['123'],
                'driver_license': {
                    'country': 'rus',
                    'number': '09aу213265',
                    'birth_date': '1939-09-02',
                    'expiration_date': '2028-11-18',
                    'issue_date': '2018-12-18',
                },
                'work_rule_id': 'rule_zero',
                'work_status': 'working',
                'providers': [],
                'hire_date': '2018-11-20',
                'bank_accounts': [],
                'identifications': [],
                'tax_identification_number': '123',
                'primary_state_registration_number': '123',
                'address': 'my address',
                'check_message': 'my check message',
                'comment': 'my comment',
                'deaf': True,
                'email': 'test@yandex.ru',
                'fire_date': '2018-12-19',
                'payment_service_id': '12345',
                'emergency_person_contacts': [{'phone': '+89123'}],
                'balance_deny_onlycard': True,
                'hiring_details': {
                    'hiring_date': '2019-01-01',
                    'hiring_type': 'commercial',
                },
            },
            'taximeter_disable_status': {'disabled': False},
        },
    )

    assert response.status == 400

    data = await response.json()
    assert data == {'code': 'FIELDS_EDIT', 'message': 'Bad request'}
