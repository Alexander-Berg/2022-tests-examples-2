import pytest


PERSONAL_STORE = {
    'invalid_for_int_api_phone': 'invalid_for_int_api_personal_phone_id',
    'existing_phone': 'existing_personal_phone_id',
    'existing_phone1': 'existing_personal_phone_id1',
    'deleted_phone': 'deleted_personal_phone_id',
    'new_phone': 'new_personal_phone_id',
}


@pytest.fixture(name='personal_phones_store')
def _mock_personal_phones_store(mockserver):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock(request):
        if request.json['value'] == 'invalid_phone':
            return mockserver.make_response(
                status=400, json={'code': '', 'message': ''},
            )
        assert request.json['value'] in PERSONAL_STORE
        return {
            'id': PERSONAL_STORE[request.json['value']],
            'value': request.json['value'],
        }

    return _mock


PERSONAL_RETRIEVE = {
    'existing_personal_phone_id': 'existing_phone',
    'existing_personal_phone_id1': 'existing_phone1',
    'deleted_personal_phone_id': 'deleted_phone',
    'new_personal_phone_id': 'new_phone',
}


@pytest.fixture(name='personal_phones_retrieve')
def _mock_personal_phones_retrieve(mockserver):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock(request):
        assert request.json['id'] in PERSONAL_RETRIEVE
        return {
            'value': PERSONAL_RETRIEVE[request.json['id']],
            'id': request.json['id'],
        }

    return _mock
