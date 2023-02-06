# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from eats_enrollment_in_hub_plugins import *  # noqa: F403 F401


SERVICE_KEY_SET = 'eats-enrollment-in-hub'

COURIER_DATA = {
    'courier': {
        'id': 1234567,
        'first_name': 'first_name',
        'last_name': 'last_name',
        'phone_number': '5eb48fee85134dc6bc00d592ecfe7df4',
        'billing_type': 'courier_service',
        'courier_type': 'bicycle',
        'registration_country': {'name': 'Россия', 'code': 'RU'},
        'work_region': {'id': 1, 'currency': {'code': 'RUB', 'sign': '₽'}},
        'work_status': 'active',
        'work_status_updated_at': '2021-06-09T22:10:00+0000',
        'project_type': 'eda',
    },
}

HIRING_RESPONCE = {
    'code': 'SUCCESS',
    'message': 'Данные приняты.',
    'details': {'accepted_fields': ['Status', 'hub_address', 'hub date']},
}


@pytest.fixture
def mock_get_courier_profile(mockserver, request):
    @mockserver.json_handler(
        '/couriers-core/api/v1/general-information/couriers/000000',
    )
    def _mock_get_courier_profile_samara(request):
        COURIER_DATA['courier']['work_region']['timezone'] = 'Europe/Samara'
        COURIER_DATA['courier']['work_region']['name'] = 'Самара'
        COURIER_DATA['courier']['external_id'] = 'test_external_id'
        return mockserver.make_response(status=200, json=COURIER_DATA)

    @mockserver.json_handler(
        '/couriers-core/api/v1/general-information/couriers/111111',
    )
    def _mock_get_courier_profile_moscow(request):
        COURIER_DATA['courier']['work_region']['timezone'] = 'Europe/Moscow'
        COURIER_DATA['courier']['work_region']['name'] = 'Москва'
        COURIER_DATA['courier']['external_id'] = 'test_external_id'
        return mockserver.make_response(status=200, json=COURIER_DATA)

    @mockserver.json_handler(
        '/couriers-core/api/v1/general-information/couriers/555555',
    )
    def _mock_get_courier_without_external(request):
        COURIER_DATA['courier']['work_region']['timezone'] = 'Europe/Moscow'
        COURIER_DATA['courier']['work_region']['name'] = 'Москва'
        COURIER_DATA['courier']['external_id'] = ''
        return mockserver.make_response(status=200, json=COURIER_DATA)

    @mockserver.json_handler(
        '/couriers-core/api/v1/general-information/couriers/666666',
    )
    def _mock_get_courier_profile_error(request):
        return mockserver.make_response('error', 400)


@pytest.fixture
def mock_hiring_api_update(mockserver, request):
    @mockserver.json_handler('/hiring-api/v1/tickets/update')
    def _mock_hiring_api_update(request):
        return mockserver.make_response(status=200, json=HIRING_RESPONCE)

    mock_hiring_api_update.send_handle = _mock_hiring_api_update
    return mock_hiring_api_update


@pytest.fixture(name='mock_driver_app_profile')
def _mock_driver_app_profile(mockserver):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_driver_app_profile_retrieve(request):
        return mockserver.make_response(
            status=200,
            json={
                'profiles': [
                    {
                        'park_driver_profile_id': 'park_id_uuid0',
                        'data': {'locale': 'ru'},
                    },
                ],
            },
        )

    return _mock_driver_app_profile_retrieve


@pytest.fixture
def mock_general_sms_send(mockserver):
    @mockserver.json_handler('/ucommunications/general/sms/send')
    def _mock_general_sms_send(request):
        # assert request.json == {}
        return {'message': '', 'code': '200'}

    return _mock_general_sms_send
